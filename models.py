# models.py
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class LogPatternRule(BaseModel):
    """A rule to identify a repetitive, non-error log pattern."""
    is_pattern: bool = Field(description="True if the log line follows a common, repetitive pattern, otherwise False.")
    regex: Optional[str] = Field(description="A Python-compatible regex to match this pattern. Null if is_pattern is False.")
    description: str = Field(description="A brief description of what this pattern represents (e.g., 'Training metric log').")

class DiagnosisResult(BaseModel):
    """The structured result of a failure diagnosis."""
    root_cause: str = Field(description="A concise summary of the root cause of the failure.")
    error_type: str = Field(description="A specific error category, e.g., 'NVLinkError', 'LossSpike', 'OOMError'.")
    source: Literal['user_mistake', 'infrastructure_failure', 'unknown'] = Field(description="The origin of the failure.")
    is_recoverable: bool = Field(description="True if the system can likely recover from this automatically.")
    mitigation: str = Field(description="A suggested action for users or an operations team to resolve the issue.")
    new_rule_regex: Optional[str] = Field(description="A new, concise Python regex to detect this specific error in the future for rule-based matching. Null if no clear rule can be generated.")
