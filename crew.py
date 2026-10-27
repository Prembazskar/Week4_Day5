
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from crewai import Crew, Process

from agents import (
    assistant_agent,
    web_search_agent,
    entry_agent
)

from tasks import (
    create_assistant_task,
    create_web_search_task,
    create_entry_task
)


# ==========================================
# Output Directory
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "support_records.json"


# ==========================================
# Run Single CrewAI Agent
# ==========================================

def run_single_agent(agent, task):
    """Execute a single CrewAI agent."""

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    return result.raw.strip()


# ==========================================
# Parse Entry Agent Response
# ==========================================

def parse_entry_response(response):
    """Convert Entry Agent output to dictionary."""

    cleaned = response.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        cleaned,
        flags=re.IGNORECASE
    ).strip()

    try:
        data = json.loads(cleaned)

        if not isinstance(data, dict):
            raise ValueError("Expected JSON object")

        return data

    except (json.JSONDecodeError, ValueError):
        print("Warning: Entry Agent returned non-JSON output.")

        return {
            "raw_entry_response": response
        }


# ==========================================
# Detect Web Search Requirement
# ==========================================

def needs_web_search(assistant_response):
    """
    Check whether the Assistant Agent
    requested web research.
    """

    response = assistant_response.strip().upper()

    return response == "NEED_WEB_SEARCH"


# ==========================================
# Load Existing Support Records
# ==========================================

def load_existing_records():
    """Safely load existing customer support records."""

    if not OUTPUT_FILE.exists():
        return []

    content = OUTPUT_FILE.read_text(
        encoding="utf-8"
    ).strip()

    if not content:
        print("Support records file is empty.")
        return []

    try:
        records = json.loads(content)

        if not isinstance(records, list):
            raise ValueError("Expected a JSON list")

        return records

    except (json.JSONDecodeError, ValueError):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        backup_file = OUTPUT_DIR / (
            f"support_records_backup_{timestamp}.json"
        )

        shutil.copy2(OUTPUT_FILE, backup_file)

        print("Warning: Invalid support records JSON.")
        print("Backup created:", backup_file)

        return []


# ==========================================
# Save Customer Support Record
# ==========================================

def save_support_record(record):
    """Append a customer support record to JSON."""

    existing_records = load_existing_records()

    existing_records.append(record)

    # Write through a temporary file
    # to reduce the risk of partial writes.
    temp_file = OUTPUT_DIR / "support_records.tmp"

    temp_file.write_text(
        json.dumps(
            existing_records,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    temp_file.replace(OUTPUT_FILE)

    print("\nSupport record saved:", OUTPUT_FILE)


# ==========================================
# Main Customer Support Workflow
# ==========================================

def run_customer_support(customer_query):
    """
    Run the conditional multi-agent workflow:

    1. Assistant Agent
    2. Web Search Agent (conditional)
    3. Entry Agent
    4. Save Support Record
    """

    customer_query = customer_query.strip()

    if not customer_query:
        raise ValueError(
            "Customer query cannot be empty."
        )

    print("\n====================================")
    print("CUSTOMER SUPPORT MULTI-AGENT SYSTEM")
    print("====================================")

    print("\n========== CUSTOMER QUERY ==========")
    print(customer_query)

    # ======================================
    # STEP 1: Assistant Agent
    # ======================================

    print("\n========== ASSISTANT AGENT ==========")

    assistant_task = create_assistant_task(
        customer_query
    )

    assistant_response = run_single_agent(
        assistant_agent,
        assistant_task
    )

    assistant_response = assistant_response.strip()

    print("\nAssistant Response:")
    print(assistant_response)

    # ======================================
    # STEP 2: Conditional Web Search
    # ======================================

    web_search_required = needs_web_search(
        assistant_response
    )

    print("\nWeb Search Required:", web_search_required)

    web_search_response = "Not Required"

    if web_search_required:

        print("\n========== WEB SEARCH AGENT ==========")

        web_task = create_web_search_task(
            customer_query
        )

        web_search_response = run_single_agent(
            web_search_agent,
            web_task
        )

        print("\nWeb Search Response:")
        print(web_search_response)

    else:

        print("\nWeb Search Agent skipped.")

    # ======================================
    # STEP 3: Entry Agent
    # ======================================

    print("\n========== ENTRY AGENT ==========")

    entry_task = create_entry_task(
        customer_query,
        assistant_response,
        web_search_response
    )

    entry_response = run_single_agent(
        entry_agent,
        entry_task
    )

    entry_record = parse_entry_response(
        entry_response
    )

    print("\nEntry Agent Record:")
    print(
        json.dumps(
            entry_record,
            indent=4,
            ensure_ascii=False
        )
    )

    # ======================================
    # STEP 4: Determine Final Answer
    # ======================================

    if web_search_required:
        final_answer = web_search_response
    else:
        final_answer = assistant_response

    # ======================================
    # STEP 5: Create Support Record
    # ======================================

    record = {
        "timestamp": (
            datetime.now()
            .astimezone()
            .isoformat()
        ),
        "customer_query": customer_query,
        "assistant_response": assistant_response,
        "web_search_response": web_search_response,
        "final_answer": final_answer,
        "entry_agent_output": entry_record
    }

    # ======================================
    # STEP 6: Save Support Record
    # ======================================

    save_support_record(record)

    # ======================================
    # STEP 7: Final Output
    # ======================================

    print("\n========== EXECUTION SUMMARY ==========")

    print("Assistant Agent: Executed")

    print(
        "Web Search Agent:",
        "Executed" if web_search_required else "Skipped"
    )

    print("Entry Agent: Executed")

    print("\n========== FINAL ANSWER ==========")
    print(final_answer)

    return record


# ==========================================
# Run from Terminal
# ==========================================

if __name__ == "__main__":

    query = input(
        "\nEnter customer query: "
    ).strip()

    result = run_customer_support(query)

    print("\n========== FINAL RECORD ==========")

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )
