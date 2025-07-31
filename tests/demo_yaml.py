#!/usr/bin/env python3
"""
Demonstration of YAML parsing functionality in the agents.
This script shows how the LogAgent and FailureAgent now use YAML format instead of JSON.
"""

from agents import YAMLOutputParser, PydanticYAMLParser
from models import LogPatternRule, DiagnosisResult

def demonstrate_yaml_parsing():
    """Demonstrate YAML parsing capabilities."""
    print("🔧 YAML Parser Demonstration")
    print("=" * 50)

    # Test 1: Basic YAML parsing
    print("\n1. Basic YAML Parsing:")
    yaml_parser = YAMLOutputParser()

    sample_yaml = """
is_pattern: true
regex: '\\[INFO\\].*System initialization.*'
description: 'System initialization log pattern'
"""

    try:
        result = yaml_parser.parse(sample_yaml)
        print("✅ Parsed successfully:")
        for key, value in result.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 2: LogPatternRule with YAML
    print("\n2. LogPatternRule YAML Parsing:")
    log_parser = PydanticYAMLParser(LogPatternRule)

    try:
        log_rule = log_parser.parse(sample_yaml)
        print(f"✅ LogPatternRule created: {log_rule}")
        print(f"   Pattern detected: {log_rule.is_pattern}")
        print(f"   Regex: {log_rule.regex}")
        print(f"   Description: {log_rule.description}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 3: DiagnosisResult with YAML
    print("\n3. DiagnosisResult YAML Parsing:")
    diagnosis_parser = PydanticYAMLParser(DiagnosisResult)

    diagnosis_yaml = """
root_cause: 'Loss spike due to corrupted data batch'
error_type: 'LossSpike'
source: 'user_mistake'
is_recoverable: true
mitigation: 'Roll back to previous checkpoint and skip problematic data batches'
new_rule_regex: 'Loss spike detected.*loss increased.*from.*to'
"""

    try:
        diagnosis = diagnosis_parser.parse(diagnosis_yaml)
        print(f"✅ DiagnosisResult created: {diagnosis.error_type}")
        print(f"   Root cause: {diagnosis.root_cause}")
        print(f"   Source: {diagnosis.source}")
        print(f"   Recoverable: {diagnosis.is_recoverable}")
        print(f"   Mitigation: {diagnosis.mitigation}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 4: Format instructions generation
    print("\n4. Format Instructions Generation:")

    print("\n   LogPatternRule instructions:")
    log_instructions = log_parser.get_format_instructions()
    print("   " + "\n   ".join(log_instructions.split('\n')[:10]) + "...")

    print("\n   DiagnosisResult instructions:")
    diagnosis_instructions = diagnosis_parser.get_format_instructions()
    print("   " + "\n   ".join(diagnosis_instructions.split('\n')[:10]) + "...")

    # Test 5: Error handling
    print("\n5. Error Handling Test:")

    malformed_yaml = """
    is_pattern: true
    regex: [METRIC].*step=\\d+  # Missing quotes
    description: "Invalid YAML
    """

    try:
        yaml_parser.parse(malformed_yaml)
        print("❌ Should have failed with malformed YAML")
    except Exception as e:
        print(f"✅ Correctly caught error: {type(e).__name__}")


def show_yaml_advantages():
    """Show advantages of YAML over JSON."""
    print("\n" + "=" * 50)
    print("🎯 YAML vs JSON Advantages:")
    print("-" * 30)
    print("✅ More human-readable format")
    print("✅ Better support for multi-line strings")
    print("✅ Comments allowed for clarity")
    print("✅ No need to escape quotes in most cases")
    print("✅ More flexible string quoting options")
    print("✅ Native boolean and null value support")

    print("\n📝 Example comparison:")
    print("\nJSON format:")
    print('''
{
  "is_pattern": true,
  "regex": "\\\\[METRIC\\\\].*step=\\\\d+",
  "description": "Training metric log"
}''')

    print("\nYAML format:")
    print('''
is_pattern: true
regex: '\\[METRIC\\].*step=\\d+'
description: 'Training metric log'
''')


if __name__ == "__main__":
    demonstrate_yaml_parsing()
    show_yaml_advantages()

    print("\n" + "=" * 50)
    print("🎉 YAML integration demonstration complete!")
    print("The agents now use YAML format for structured output parsing.")
    print("Run 'python main.py' to see it in action with the full system!")
