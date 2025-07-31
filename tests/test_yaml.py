#!/usr/bin/env python3
"""Test script for YAML parser functionality."""

try:
    import yaml
    print("✅ PyYAML import successful")

    # Test basic YAML parsing
    test_yaml = """
is_pattern: true
regex: '\\[METRIC\\].*step=\\d+'
description: 'Training metric log pattern'
"""

    result = yaml.safe_load(test_yaml)
    print("✅ Basic YAML parsing successful:", result)

except ImportError as e:
    print("❌ PyYAML not available:", e)
    print("Please install with: pip install pyyaml")
except Exception as e:
    print("❌ YAML parsing error:", e)

# Test importing our custom parsers
try:
    from agents import YAMLOutputParser, PydanticYAMLParser
    from models import LogPatternRule

    # Test YAML parser
    yaml_parser = YAMLOutputParser()
    test_yaml = """is_pattern: true
regex: '\\[METRIC\\].*step=\\d+'
description: 'Training metric log pattern'
"""

    result = yaml_parser.parse(test_yaml)
    print("✅ Custom YAML parsing successful:", result)

    # Test Pydantic YAML parser
    pydantic_parser = PydanticYAMLParser(LogPatternRule)
    model_result = pydantic_parser.parse(test_yaml)
    print("✅ Pydantic YAML parsing successful:", model_result)

    # Test format instructions
    instructions = pydantic_parser.get_format_instructions()
    print("✅ Format instructions generated (length:", len(instructions), ")")

except Exception as e:
    print("❌ Custom parser test failed:", e)
    import traceback
    traceback.print_exc()
