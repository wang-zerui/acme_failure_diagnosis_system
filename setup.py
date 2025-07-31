#!/usr/bin/env python3
"""
Setup script for the Failure Diagnosis System.
This script helps with initial setup and configuration.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_requirements():
    """Install required Python packages."""
    print("\n📦 Installing required packages...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ All packages installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False


def setup_openai_key():
    """Guide user through OpenAI API key setup."""
    print("\n🔑 OpenAI API Key Setup")
    print("-" * 30)

    # Check if already set in environment
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API key found in environment variables.")
        return True

    print("OpenAI API key not found in environment variables.")
    print("\nYou have two options:")
    print("1. Set as environment variable (recommended)")
    print("2. Set in config.py file")

    choice = input("\nChoose option (1 or 2): ").strip()

    if choice == "1":
        print("\nAdd this to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
        print("export OPENAI_API_KEY='sk-your-api-key-here'")
        print("\nThen restart your terminal or run: source ~/.bashrc")

    elif choice == "2":
        config_path = Path("config.py")
        if config_path.exists():
            print(f"\nEdit {config_path} and uncomment/set:")
            print('os.environ["OPENAI_API_KEY"] = "sk-your-api-key-here"')
        else:
            print("❌ config.py file not found!")
            return False

    else:
        print("❌ Invalid choice. Please run setup again.")
        return False

    print("\n⚠️  Remember to get your API key from: https://platform.openai.com/api-keys")
    return True


def create_directories():
    """Ensure all necessary directories exist."""
    print("\n📁 Creating directories...")

    directories = [
        "data",
        "rules",
        "vector_store"
    ]

    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"✅ Created directory: {dir_name}")
        else:
            print(f"✅ Directory exists: {dir_name}")


def verify_files():
    """Verify all required files are present."""
    print("\n📄 Verifying files...")

    required_files = [
        "main.py",
        "agents.py",
        "components.py",
        "config.py",
        "models.py",
        "requirements.txt",
        "data/sample_job.log",
        "rules/filter_rules.json",
        "rules/diagnosis_rules.json"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")

    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False

    print("✅ All required files present.")
    return True

def main():
    """Main setup function."""
    print("🚀 Failure Diagnosis System Setup")
    print("=" * 40)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Verify files
    if not verify_files():
        print("\n❌ Setup failed: Missing required files.")
        sys.exit(1)

    # Create directories
    create_directories()

    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed: Could not install requirements.")
        sys.exit(1)

    print("\n" + "=" * 40)
    print("🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Make sure your OpenAI API key is configured")
    print("2. Run the system: python main.py")
    print("3. Check the README.md for more details")


if __name__ == "__main__":
    main()
