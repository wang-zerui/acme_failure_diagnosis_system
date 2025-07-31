# main.py
import time
import logging
from typing import List, Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

import config
from components import LogFilter, RuleBasedDiagnosis, RecoveryProcess
from agents import LogAgent, FailureAgent
from models import DiagnosisResult

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def simulate_log_stream(log_file_path: str, chunk_size: int):
    """Yields chunks of log lines from a file to simulate a real-time stream."""
    with open(log_file_path, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines), chunk_size):
            yield lines[i:i + chunk_size]
            # time.sleep(0.5) # Simulate time delay between chunks

def main():
    """Main orchestration logic for the failure diagnosis system."""

    # --- 1. Initialize Components ---
    print("--- System Initialization ---")

    # LLMs and Embeddings
    log_agent_llm = ChatOpenAI(model=config.LOG_AGENT_MODEL, temperature=0, request_timeout=60)
    failure_agent_llm = ChatOpenAI(model=config.FAILURE_AGENT_MODEL, temperature=0, request_timeout=120)
    embeddings = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)

    # Vector Store for RAG
    # Load existing vector store or create a new one
    if config.VECTOR_STORE_DIR.exists() and any(config.VECTOR_STORE_DIR.iterdir()):
        logging.info(f"Loading existing Vector Store from {config.VECTOR_STORE_DIR}")
        vector_store = FAISS.load_local(str(config.VECTOR_STORE_DIR), embeddings, allow_dangerous_deserialization=True)
    else:
        logging.info("Creating new Vector Store.")
        # Create an empty store with a dummy document
        vector_store = FAISS.from_texts(["Initial document for schema"], embeddings)
        vector_store.save_local(str(config.VECTOR_STORE_DIR))

    # Core system components
    log_filter = LogFilter()
    rule_based_diagnosis = RuleBasedDiagnosis()
    recovery_process = RecoveryProcess()

    # Agents
    log_agent = LogAgent(llm_provider=log_agent_llm)
    failure_agent = FailureAgent(llm_provider=failure_agent_llm, vector_store=vector_store)

    print("--- Initialization Complete. Starting Log Processing Simulation. ---\n")

    # --- 2. Real-time Log Processing Simulation ---
    failure_log = None
    log_stream = simulate_log_stream(config.LOG_FILE_PATH, config.LOG_CHUNK_SIZE)

    for i, log_chunk in enumerate(log_stream):
        print(f"\n--- Processing Log Chunk {i+1} ---")

        # Step 2a: Continuous Log Compression
        filtered_out, potential_issues = log_filter.filter_log_chunk(log_chunk)
        logging.info(f"LogFilter: Removed {len(filtered_out)} lines, passing {len(potential_issues)} for analysis.")

        if not potential_issues:
            print("No issues detected in this chunk.")
            continue

        # Step 2b: Update Filter Rules with Log Agent
        # Analyze one of the non-error, non-filtered lines to learn new patterns.
        unmatched_non_error_lines = [line for line in potential_issues if "ERROR" not in line.upper()]
        if unmatched_non_error_lines:
            line_to_learn = unmatched_non_error_lines[0] # Analyze the first one
            new_rule = log_agent.generate_filter_rule(line_to_learn)
            if new_rule:
                log_filter.add_rule(new_rule)

        # Step 2c: Detect Failure Occurrence
        error_lines = [line for line in potential_issues if "ERROR" in line.upper()]
        if error_lines:
            print(f"\n🚨 FAILURE DETECTED! 🚨")
            failure_log = "".join(potential_issues) # Use all potential issues as context
            break # Stop processing logs and move to diagnosis

    # --- 3. LLM-assisted Automated Diagnosis ---
    if failure_log:
        diagnosis: Optional[DiagnosisResult] = None

        # Step 3a: Attempt Rule-based Diagnosis first
        print("\n--- Starting Failure Diagnosis ---")
        print("1. Attempting fast Rule-based Diagnosis...")

        rule_diagnosis_result = rule_based_diagnosis.diagnose(failure_log)

        if rule_diagnosis_result:
            print("✅ Rule-based diagnosis successful.")
            diagnosis = DiagnosisResult(**rule_diagnosis_result)
        else:
            # Step 3b: Escalate to Failure Agent
            print("⚠️ No matching rule found. Escalating to LLM-based Failure Agent.")

            # The agent performs retrieval from the vector store and diagnosis
            diagnosis = failure_agent.diagnose_failure(failure_log)

            # Continuous Learning: Update diagnosis rules and vector store
            print("\n--- Continuous Learning & System Improvement ---")
            if diagnosis.new_rule_regex:
                rule_based_diagnosis.add_rule(diagnosis.new_rule_regex, diagnosis.dict())
                print(f"✅ New diagnosis rule added for '{diagnosis.error_type}'.")

            # Add the new failure and its diagnosis to the vector store for future retrieval
            doc = Document(page_content=failure_log, metadata={"error_type": diagnosis.error_type, "source": diagnosis.source})
            vector_store.add_documents([doc])
            vector_store.save_local(str(config.VECTOR_STORE_DIR))
            print(f"✅ Failure log added to Vector Store for future context.")

        # --- 4. Display Diagnosis and Attempt Recovery ---
        if diagnosis:
            print("\n--- FINAL DIAGNOSIS ---")
            print(f"  Root Cause: {diagnosis.root_cause}")
            print(f"  Error Type: {diagnosis.error_type}")
            print(f"  Source: {diagnosis.source}")
            print(f"  Mitigation: {diagnosis.mitigation}")
            print(f"  Auto-Recoverable: {'Yes' if diagnosis.is_recoverable else 'No'}")
            print("------------------------\n")

            if diagnosis.is_recoverable:
                recovery_process.attempt_recovery(diagnosis=diagnosis)
            else:
                logging.warning("--> Manual recovery required. Notifying operations team.")
    else:
        print("\n--- Job simulation finished without unrecoverable errors. ---")

if __name__ == "__main__":
    main()
