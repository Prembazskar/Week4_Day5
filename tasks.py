
from crewai import Task

from agents import (
    assistant_agent,
    web_search_agent,
    entry_agent
)


# ==========================================
# Task 1: Assistant Task
# ==========================================

def create_assistant_task(customer_query):
    return Task(
        description=f"""
        Customer Query:
        {customer_query}

        Instructions:
        1. Understand the customer's question.
        2. Attempt to answer using your existing knowledge.
        3. If the answer is reliable, provide a clear response.
        4. If the question requires current information,
           external verification, or unknown company data,
           return exactly:

           NEED_WEB_SEARCH

        5. Do not invent information.
        6. Do not use web search.

        IMPORTANT:
        If research is required, your entire response
        must be exactly NEED_WEB_SEARCH.
        """,

        expected_output=(
            "A helpful customer support answer, or exactly "
            "NEED_WEB_SEARCH when external research is required."
        ),

        agent=assistant_agent
    )


# ==========================================
# Task 2: Web Search Task
# ==========================================

def create_web_search_task(customer_query):
    return Task(
        description=f"""
        Customer Query:
        {customer_query}

        Instructions:
        1. Research the customer question using SerperDevTool.
        2. Prefer official and reliable sources.
        3. Identify relevant and up-to-date information.
        4. Provide a clear customer-friendly answer.
        5. Include source URLs when available.
        6. If the information cannot be verified,
           clearly state the limitation.
        """,

        expected_output=(
            "A researched customer support answer with "
            "relevant supporting source URLs."
        ),

        agent=web_search_agent
    )


# ==========================================
# Task 3: Entry Task
# ==========================================

def create_entry_task(
    customer_query,
    assistant_response,
    web_search_response
):
    return Task(
        description=f"""
        Create a customer support record.

        Customer Query:
        {customer_query}

        Assistant Response:
        {assistant_response}

        Web Search Response:
        {web_search_response}

        Instructions:
        1. Preserve the original customer query.
        2. Record the assistant response.
        3. Record the web search response.
        4. If web search was not used, record Not Required.
        5. Create a final customer-friendly answer.
        6. Do not invent missing details.

        Return a structured JSON object with these fields:

        customer_query
        assistant_response
        web_search_response
        final_answer

        Return valid JSON only.
        """,

        expected_output=(
            "A valid JSON object containing customer_query, "
            "assistant_response, web_search_response, "
            "and final_answer."
        ),

        agent=entry_agent
    )
