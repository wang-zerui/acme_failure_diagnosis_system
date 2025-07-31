# config.py
import os
from pathlib import Path

# --- General Configuration ---
# IMPORTANT: Set your OpenAI API key here or as an environment variable
# os.environ["OPENAI_API_KEY"] = "sk-..."  # Uncomment and add your API key

# --- Model Configuration ---
# Use a powerful model like GPT-4 for better reasoning
LOG_AGENT_MODEL = "gpt-4o"
FAILURE_AGENT_MODEL = "claude-3-5-sonnet-20241022"
VOTER_AGENT_MODEL = "gpt-4o-mini"  # Can be a faster model for voting
EMBEDDING_MODEL = "text-embedding-ada-002"

# --- File & Directory Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RULES_DIR = BASE_DIR / "rules"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"

LOG_FILE_PATH = DATA_DIR / "sample.log"
FILTER_RULES_PATH = RULES_DIR / "filter_rules.json"
DIAGNOSIS_RULES_PATH = RULES_DIR / "diagnosis_rules.json"

# --- Simulation Configuration ---
LOG_CHUNK_SIZE = 20  # Number of log lines to process in each iteration
