# 🚀 Quick Start Guide

## Project Overview

This is a complete implementation of an LLM-powered failure diagnosis and recovery system for large-scale model training jobs, built with the LangChain framework.

## 📁 Project Structure

```
failure-diagnosis-system/
├── 🐍 Core Python Files
│   ├── main.py              # Main orchestration script
│   ├── agents.py            # LLM-powered LogAgent and FailureAgent
│   ├── components.py        # LogFilter, RuleBasedDiagnosis, RecoveryProcess
│   ├── config.py            # Configuration and settings
│   └── models.py            # Pydantic models for structured output
│
├── 🧪 Testing & Validation
│   ├── test_system.py       # Comprehensive test suite
│   ├── validate_config.py   # Configuration validation
│   └── examples.py          # Extension examples and demos
│
├── 📋 Setup & Management
│   ├── setup.py             # Automated setup script
│   ├── Makefile             # Project management commands
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # Detailed documentation
│
├── 📊 Data & Configuration
│   ├── data/
│   │   └── sample_job.log   # Sample training log for testing
│   ├── rules/
│   │   ├── filter_rules.json      # Auto-generated filter rules
│   │   └── diagnosis_rules.json   # Auto-generated diagnosis rules
│   └── vector_store/        # FAISS vector database (auto-created)
│
└── .gitignore              # Version control exclusions
```

## 🚀 Quick Setup (3 Steps)

### 1. Install Dependencies
```bash
cd failure-diagnosis-system
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key
Choose one option:

**Option A: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Option B: Config File**
Edit `config.py` and uncomment:
```python
os.environ["OPENAI_API_KEY"] = "sk-your-api-key-here"
```

### 3. Run the System
```bash
python main.py
```

## 🎯 Key Features Demonstrated

### 🔄 Continuous Learning
- **First Run**: System learns new patterns, creates rules
- **Second Run**: Uses learned rules for instant diagnosis
- **Progressive Intelligence**: Gets smarter with each failure

### 🧠 Dual Diagnosis Strategy
1. **Fast Rule-Based**: Instant pattern matching
2. **LLM-Powered RAG**: Complex reasoning with historical context

### 📈 System Evolution
- Auto-generates log filter patterns
- Creates diagnosis rules from LLM insights
- Builds vector database of failure knowledge

## 🎮 Available Commands

```bash
make help       # Show all available commands
make install    # Setup dependencies and configuration
make validate   # Check system configuration
make test       # Run comprehensive test suite
make run        # Start the failure diagnosis system
make clean      # Reset system to initial state
make status     # Check current system status
```

## 📋 Expected Workflow

1. **System Initialization** (5-10 seconds)
   - Loads/creates vector store
   - Initializes LLM connections
   - Sets up components

2. **Log Processing Simulation** (30-60 seconds)
   - Processes sample log in chunks
   - Demonstrates filtering and pattern learning
   - Shows real-time failure detection

3. **Failure Diagnosis** (30-90 seconds depending on LLM)
   - First failure: LLM analysis + rule creation
   - Second failure: Instant rule-based diagnosis
   - Recovery strategy execution

4. **System Learning**
   - New rules saved to JSON files
   - Failure context added to vector store
   - System ready for future runs

## 🧪 Testing & Validation

```bash
# Validate system configuration
make validate

# Run comprehensive tests
make test

# Try custom examples
python examples.py
```

## 🔧 Customization Examples

The system is designed to be easily extended:

- **Custom Log Patterns**: Add domain-specific regex patterns
- **New Error Types**: Define custom failure categories
- **Recovery Strategies**: Implement specific recovery actions
- **Agent Behavior**: Modify LLM prompts and logic

See `examples.py` for detailed customization examples.

## 📊 System Intelligence

The system demonstrates several AI techniques:

- **Self-Consistency**: Multiple LLM calls with voting
- **RAG (Retrieval-Augmented Generation)**: Historical context for diagnosis
- **Continuous Learning**: Dynamic rule generation and updates
- **Structured Output**: Pydantic models for reliable parsing

## 🚨 Troubleshooting

**API Key Issues:**
```bash
make validate  # Check configuration
```

**Missing Dependencies:**
```bash
make install  # Reinstall everything
```

**Reset System:**
```bash
make clean    # Clear learned rules and vector store
```

**System Status:**
```bash
make status   # Check current configuration
```

## 💡 Next Steps

1. **Run the Demo**: `make run` to see the system in action
2. **Review Code**: Explore the well-documented source files
3. **Extend System**: Use `examples.py` as a starting point
4. **Integrate**: Connect to your actual training infrastructure

## 🏗️ Production Deployment

For production use:

1. Replace sample logs with real log streams
2. Implement actual recovery procedures
3. Connect to monitoring and alerting systems
4. Scale vector store for large failure databases
5. Add authentication and security measures

---

**🎉 You're all set! Run `make run` to see the system in action.**
