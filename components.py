# components.py
import re
import json
import logging
from typing import List, Tuple, Dict, Any, Optional

from config import FILTER_RULES_PATH, DIAGNOSIS_RULES_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LogFilter:
    """Filters logs using a dynamically updated set of regular expressions."""

    def __init__(self):
        self.rules: List[str] = self._load_rules(FILTER_RULES_PATH)
        logging.info(f"LogFilter initialized with {len(self.rules)} rules.")

    def _load_rules(self, path) -> List[str]:
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return []

    def _save_rules(self):
        with open(FILTER_RULES_PATH, 'w') as f:
            json.dump(self.rules, f, indent=2)

    def add_rule(self, regex: str):
        if regex and regex not in self.rules:
            self.rules.append(regex)
            self._save_rules()
            logging.info(f"Added new filter rule: {regex}")

    def filter_log_chunk(self, log_lines: List[str]) -> Tuple[List[str], List[str]]:
        """
        Filters a chunk of log lines.
        Returns a tuple of (filtered_lines, error_or_unmatched_lines).
        """
        filtered_out = []
        passed_through = []

        # Simple heuristic: if a line contains "ERROR", treat it as a potential failure.
        # This is a basic pre-filter before more complex analysis.
        error_lines = [line for line in log_lines if "ERROR" in line.upper()]

        for line in log_lines:
            if "ERROR" in line.upper():
                continue # Handled above

            is_match = any(re.search(rule, line) for rule in self.rules)
            if is_match:
                filtered_out.append(line)
            else:
                passed_through.append(line)

        # Unmatched lines + explicit error lines are sent for diagnosis/rule generation
        unfiltered_log = passed_through + error_lines

        # Further filter out lines that contain only whitespace and newlines
        whitespace_lines = [line for line in unfiltered_log if not line.strip()]
        unfiltered_log = [line for line in unfiltered_log if line.strip()]

        # Add whitespace lines to filtered_out
        filtered_out.extend(whitespace_lines)

        return filtered_out, unfiltered_log

class RuleBasedDiagnosis:
    """Performs fast diagnosis using a set of pre-defined error rules."""

    def __init__(self):
        self.rules: List[Dict[str, Any]] = self._load_rules(DIAGNOSIS_RULES_PATH)
        logging.info(f"RuleBasedDiagnosis initialized with {len(self.rules)} rules.")

    def _load_rules(self, path) -> List[Dict[str, Any]]:
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return []

    def _save_rules(self):
        with open(DIAGNOSIS_RULES_PATH, 'w') as f:
            json.dump(self.rules, f, indent=4)

    def add_rule(self, regex: str, diagnosis: Dict[str, Any]):
        if not any(rule['regex'] == regex for rule in self.rules):
            self.rules.append({"regex": regex, "diagnosis": diagnosis})
            self._save_rules()
            logging.info(f"Added new diagnosis rule for regex: {regex}")

    def diagnose(self, compressed_log: str) -> Optional[Dict[str, Any]]:
        """Tries to match the log against known failure patterns."""
        for rule in self.rules:
            if re.search(rule['regex'], compressed_log, re.DOTALL):
                logging.info(f"Matched diagnosis rule: {rule['regex']}")
                return rule['diagnosis']
        return None

class RecoveryProcess:
    """Placeholder for the automatic recovery process."""

    def attempt_recovery(self, diagnosis: "DiagnosisResult"):
        """
        Based on the diagnosis, attempt to perform an automatic recovery action.
        This is a placeholder as requested.
        """
        logging.info(f"--> [Recovery Process] Initiating recovery for: {diagnosis.error_type}")
        if "LossSpike" in diagnosis.error_type:
            logging.info("--> Action: Roll back to an earlier healthy checkpoint and skip bad data batches.")
            # In a real system: self._rollback_and_restart()
        elif "NVLinkError" in diagnosis.error_type or "NCCL" in diagnosis.error_type:
            logging.info("--> Action: Cordon off the faulty node identified in the diagnosis.")
            # In a real system: self._run_nccl_test_and_cordon_node()
        else:
            logging.warning("--> No automatic recovery procedure defined for this error.")

        print("\n" + "="*30 + " RECOVERY SIMULATION COMPLETE " + "="*30 + "\n")
