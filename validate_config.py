#!/usr/bin/env python3
"""
Configuration validation script for the Failure Diagnosis System.
Checks system configuration and provides helpful error messages.
"""

import os
import sys
from pathlib import Path


def check_openai_key():
    """Check if OpenAI API key is properly configured."""
    print("🔑 Checking OpenAI API key...")

    # Check environment variable
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key and env_key.startswith("sk-"):
        print("✅ OpenAI API key found in environment variables.")
        return True

    # Check config.py
    try:
        import config
        # This will trigger the os.environ assignment if uncommented
        config_key = os.getenv("OPENAI_API_KEY")
        if config_key and config_key.startswith("sk-"):
            print("✅ OpenAI API key configured in config.py.")
            return True
    except ImportError:
        print("❌ Could not import config.py")
        return False

    print("❌ OpenAI API key not found or invalid.")
    print("   Please set OPENAI_API_KEY environment variable or configure in config.py")
    print("   Get your key from: https://platform.openai.com/api-keys")
    return False


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\n📦 Checking dependencies...")

    required_packages = [
        ("langchain", "langchain"),
        ("langchain_openai", "langchain-openai"),
        ("faiss", "faiss-cpu"),
        ("pydantic", "pydantic"),
        ("tenacity", "tenacity")
    ]

    missing_packages = []

    for import_name, pip_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {pip_name}")
        except ImportError:
            print(f"❌ {pip_name}")
            missing_packages.append(pip_name)

    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("✅ All dependencies installed.")
    return True


def check_file_structure():
    """Check if all required files and directories exist."""
    print("\n📁 Checking file structure...")

    required_structure = {
        "files": [
            "main.py",
            "agents.py",
            "components.py",
            "config.py",
            "models.py",
            "requirements.txt",
            "README.md"
        ],
        "directories": [
            "data",
            "rules",
            "vector_store"
        ],
        "data_files": [
            "data/sample_job.log",
            "rules/filter_rules.json",
            "rules/diagnosis_rules.json"
        ]
    }

    all_good = True

    # Check files
    for file_path in required_structure["files"]:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_good = False

    # Check directories
    for dir_path in required_structure["directories"]:
        if Path(dir_path).is_dir():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/")
            all_good = False

    # Check data files
    for file_path in required_structure["data_files"]:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_good = False

    return all_good


def check_configuration():
    """Check configuration settings."""
    print("\n⚙️  Checking configuration...")

    try:
        import config

        # Check model configurations
        models_to_check = [
            ("LOG_AGENT_MODEL", config.LOG_AGENT_MODEL),
            ("FAILURE_AGENT_MODEL", config.FAILURE_AGENT_MODEL),
            ("EMBEDDING_MODEL", config.EMBEDDING_MODEL)
        ]

        for model_name, model_value in models_to_check:
            if model_value:
                print(f"✅ {model_name}: {model_value}")
            else:
                print(f"❌ {model_name}: Not set")
                return False

        # Check paths
        paths_to_check = [
            ("LOG_FILE_PATH", config.LOG_FILE_PATH),
            ("FILTER_RULES_PATH", config.FILTER_RULES_PATH),
            ("DIAGNOSIS_RULES_PATH", config.DIAGNOSIS_RULES_PATH),
            ("VECTOR_STORE_DIR", config.VECTOR_STORE_DIR)
        ]

        for path_name, path_value in paths_to_check:
            if path_value and isinstance(path_value, Path):
                print(f"✅ {path_name}: {path_value}")
            else:
                print(f"❌ {path_name}: Invalid path")
                return False

        print("✅ Configuration looks good.")
        return True

    except ImportError:
        print("❌ Could not import config.py")
        return False
    except AttributeError as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_basic_functionality():
    """Test basic system functionality."""
    print("\n🧪 Testing basic functionality...")

    try:
        # Test model imports
        from models import LogPatternRule, DiagnosisResult
        print("✅ Models import successfully")

        # Test component imports
        from components import LogFilter, RuleBasedDiagnosis, RecoveryProcess
        print("✅ Components import successfully")

        # Test agent imports (may fail without API key)
        try:
            from agents import LogAgent, FailureAgent
            print("✅ Agents import successfully")
        except Exception as e:
            print(f"⚠️  Agents import warning: {e}")

        # Test basic model creation
        test_rule = LogPatternRule(
            is_pattern=True,
            regex=r"\[INFO\].*",
            description="Test pattern"
        )
        print("✅ Model creation works")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def provide_recommendations():
    """Provide recommendations based on the checks."""
    print("\n💡 Recommendations:")
    print("-" * 20)

    print("1. Make sure your OpenAI API key is valid and has sufficient credits")
    print("2. Consider using GPT-3.5-turbo for testing to reduce costs")
    print("3. Monitor your API usage during development")
    print("4. Keep your API key secure and never commit it to version control")
    print("5. Run the test suite with: python test_system.py")


def main():
    """Main validation function."""
    print("🔍 Failure Diagnosis System Configuration Check")
    print("=" * 50)

    checks = [
        ("OpenAI API Key", check_openai_key),
        ("Dependencies", check_dependencies),
        ("File Structure", check_file_structure),
        ("Configuration", check_configuration),
        ("Basic Functionality", test_basic_functionality)
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results.append((check_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary:")

    passed = 0
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {check_name}: {status}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{len(results)}")

    if passed == len(results):
        print("🎉 All checks passed! System is ready to run.")
        print("Run the system with: python main.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        provide_recommendations()

    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
