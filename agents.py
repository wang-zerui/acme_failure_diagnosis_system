# agents.py
import logging
import yaml
from collections import Counter
from typing import List, Optional, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import BaseOutputParser, PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from pydantic import ValidationError

from models import LogPatternRule, DiagnosisResult


class YAMLOutputParser(BaseOutputParser[Dict[str, Any]]):
    """Custom YAML output parser for LLM responses."""

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse YAML text into a dictionary."""
        try:
            # Remove markdown code blocks if present
            text = text.strip()
            if text.startswith("```yaml") or text.startswith("```"):
                lines = text.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                text = '\n'.join(lines)

            # Parse YAML safely
            result = yaml.safe_load(text)
            if result is None:
                raise ValueError("YAML parsing resulted in None")
            return result

        except (yaml.YAMLError, yaml.scanner.ScannerError) as e:
            # Try to fix common YAML issues and reparse
            try:
                # Replace problematic double quotes with single quotes for regex patterns
                fixed_text = self._fix_yaml_escaping(text)
                result = yaml.safe_load(fixed_text)
                if result is None:
                    raise ValueError("YAML parsing resulted in None after fix attempt")
                return result
            except Exception:
                raise ValueError(f"Failed to parse YAML even after fix attempt: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse YAML: {e}")

    def _fix_yaml_escaping(self, text: str) -> str:
        """Attempt to fix common YAML escaping issues."""
        lines = text.split('\n')
        fixed_lines = []

        for line in lines:
            # If line contains regex field with double quotes, convert to single quotes
            if 'regex:' in line and '"' in line:
                # Extract the value part
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key, value = parts
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        # Remove outer double quotes and replace with single quotes
                        inner_value = value[1:-1]
                        fixed_line = f"{key}: '{inner_value}'"
                        fixed_lines.append(fixed_line)
                        continue
            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def get_format_instructions(self) -> str:
        """Instructions for the LLM to format output as YAML."""
        return """Please format your response as valid YAML. Use single quotes for string values containing special characters like regex patterns. Do not include markdown code blocks or additional formatting."""


class PydanticYAMLParser(BaseOutputParser):
    """YAML parser that validates against a Pydantic model."""

    def __init__(self, pydantic_object):
        super().__init__()
        self._pydantic_object = pydantic_object
        self._yaml_parser = YAMLOutputParser()

    def parse(self, text: str):
        """Parse YAML and validate with Pydantic model."""
        try:
            parsed_dict = self._yaml_parser.parse(text)
            return self._pydantic_object(**parsed_dict)
        except ValidationError as e:
            raise ValueError(f"Pydantic validation failed: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse and validate YAML: {e}")

    def get_format_instructions(self) -> str:
        """Get format instructions including YAML format and schema."""
        schema = self._pydantic_object.schema()
        yaml_example = self._generate_yaml_example(schema)

        return f"""Please respond in YAML format with the following structure:

{yaml_example}

Important:
- Use proper YAML syntax with indentation
- Boolean values should be true/false (lowercase)
- Null values should be null or ~
- Strings with special characters should be quoted
- Do not include markdown code blocks"""

    def _generate_yaml_example(self, schema: Dict[str, Any]) -> str:
        """Generate a YAML example from Pydantic schema."""
        properties = schema.get('properties', {})
        yaml_lines = []

        for field_name, field_info in properties.items():
            field_type = field_info.get('type', 'string')
            description = field_info.get('description', '')

            if field_type == 'boolean':
                example_value = 'true'
            elif field_type == 'string':
                if 'null' in str(field_info.get('anyOf', [])):
                    example_value = 'null'
                elif field_name == 'regex':
                    # Use single quotes for regex patterns
                    example_value = "'pattern_regex_here'"
                else:
                    example_value = f'"{field_name}_value"'
            elif field_type == 'integer':
                example_value = '0'
            elif field_type == 'number':
                example_value = '0.0'
            else:
                example_value = f'"{field_name}_value"'

            comment = f"  # {description}" if description else ""
            yaml_lines.append(f"{field_name}: {example_value}{comment}")

        return '\n'.join(yaml_lines)

# --- Prompts ---

LOG_AGENT_PROMPT = """
You are an expert log analysis agent. Your task is to analyze a given log line and determine if it follows a common, repetitive pattern that is NOT an error.
Examples of such patterns include:
- Training metric logs (e.g., "[METRIC] ... step=10, loss=2.3, ...")
- Initialization messages (e.g., "[INFO] ... System initialization ...")
- Debug or framework messages (e.g., "[DEBUG] ... Memory allocation check ...")

Analyze the following log line:
`{log_line}`

{format_instructions}
"""

FAILURE_AGENT_PROMPT = """
You are a Failure Diagnosis Agent for a large-model training platform.
Your goal is to analyze a compressed error log to determine the root cause of a job failure.
Use the provided context from similar past failures to improve your diagnosis.

**Context from similar past failures:**
{context}

**Current compressed error log to diagnose:**
```
{question}
```

**Your task:**
1.  Identify the root cause of the failure.
2.  Classify the error type (e.g., `NVLinkError`, `LossSpike`, `OOMError`).
3.  Determine if it's a `user_mistake` (like a data issue) or an `infrastructure_failure` (like a hardware problem).
4.  Provide a clear, actionable mitigation suggestion for the user or operations team.
5.  Indicate if the failure is likely automatically recoverable (e.g., rolling back for a loss spike).
6.  Generate a new, concise Python regex that can be used to detect this specific error in the future. This regex will be added to a rule-based system for faster diagnosis. It should be specific to the core error signature.

{format_instructions}
"""

class LogAgent:
    """Analyzes logs to generate new filter rules."""

    def __init__(self, llm_provider):
        self.parser = PydanticYAMLParser(pydantic_object=LogPatternRule)
        self.prompt = ChatPromptTemplate.from_template(
            template=LOG_AGENT_PROMPT,
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        self.chain = self.prompt | llm_provider | self.parser

    def generate_filter_rule(self, log_line: str, self_consistency_n: int = 3) -> Optional[str]:
        """
        Uses an LLM to generate a regex for a given log line.
        Implements self-consistency by generating multiple responses and taking a majority vote.
        """
        logging.info(f"LogAgent analyzing line: '{log_line.strip()}'")

        # Self-consistency: Run multiple times
        try:
            responses = self.chain.batch([{"log_line": log_line}] * self_consistency_n)
            valid_rules = [resp.regex for resp in responses if resp.is_pattern and resp.regex]
        except Exception as e:
            logging.warning(f"LogAgent error during batch processing: {e}")
            # Fallback to single request
            try:
                response = self.chain.invoke({"log_line": log_line})
                valid_rules = [response.regex] if response.is_pattern and response.regex else []
            except Exception as fallback_e:
                logging.error(f"LogAgent fallback failed: {fallback_e}")
                return None

        if not valid_rules:
            logging.info("LogAgent found no consistent pattern.")
            return None

        # Vote and Eval: Choose the most frequent valid regex
        most_common_rule = Counter(valid_rules).most_common(1)[0][0]
        logging.info(f"LogAgent consensus rule: {most_common_rule}")
        return most_common_rule

class FailureAgent:
    """Diagnoses failures using a RAG pipeline and contributes back to the rule system."""

    def __init__(self, llm_provider, vector_store: FAISS):
        self.parser = PydanticYAMLParser(pydantic_object=DiagnosisResult)
        self.retriever = vector_store.as_retriever()

        self.prompt = ChatPromptTemplate.from_template(
            template=FAILURE_AGENT_PROMPT,
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        self.rag_chain = (
            RunnableParallel(
                {"context": self.retriever, "question": RunnablePassthrough()}
            )
            | self.prompt
            | llm_provider
            | self.parser
        )

    def diagnose_failure(self, compressed_log: str) -> DiagnosisResult:
        """Runs the RAG chain to diagnose the failure."""
        logging.info("FailureAgent: Diagnosing failure using RAG pipeline...")
        try:
            return self.rag_chain.invoke(compressed_log)
        except Exception as e:
            logging.error(f"FailureAgent diagnosis failed: {e}")
            # Return a default diagnosis
            return DiagnosisResult(
                root_cause=f"Failed to diagnose failure due to parsing error: {str(e)}",
                error_type="UnknownError",
                source="unknown",
                is_recoverable=False,
                mitigation="Manual investigation required due to diagnosis system error",
                new_rule_regex=None
            )
