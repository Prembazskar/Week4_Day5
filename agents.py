
import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from crewai_tools import SerperDevTool

# Load environment variables
load_dotenv()

# Validate API keys
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is missing in .env")

if not os.getenv("SERPER_API_KEY"):
    raise RuntimeError("SERPER_API_KEY is missing in .env")

# Configure OpenAI LLM
llm = LLM(
    model=os.getenv("MODEL", "gpt-4o-mini"),
    temperature=0.2
)

# Configure web search tool
search_tool = SerperDevTool()


# ==========================================
# Agent 1: Assistant Agent
# ==========================================

assistant_agent = Agent(
    role="Customer Support Assistant",

    goal=(
        "Understand customer questions and provide accurate, "
        "helpful answers using existing knowledge. "
        "When reliable information is unavailable or current "
        "verification is necessary, return NEED_WEB_SEARCH."
    ),

    backstory=(
        "You are an experienced customer support specialist. "
        "You explain technical and general questions clearly. "
        "You never invent company policies, prices, product "
        "availability, or other unverified information. "
        "If a question requires current information, "
        "external research, or facts you cannot verify, "
        "you return exactly NEED_WEB_SEARCH."
    ),

    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=3
)


# ==========================================
# Agent 2: Web Search Agent
# ==========================================

web_search_agent = Agent(
    role="Customer Support Web Research Specialist",

    goal=(
        "Research customer questions using web search and "
        "provide accurate, relevant, evidence-based answers."
    ),

    backstory=(
        "You are a professional web research specialist. "
        "You search for trustworthy information using "
        "SerperDevTool. You prioritize official websites "
        "and reliable sources. You avoid unsupported claims "
        "and provide source URLs when available."
    ),

    tools=[search_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=5
)


# ==========================================
# Agent 3: Entry Agent
# ==========================================

entry_agent = Agent(
    role="Customer Support Record Specialist",

    goal=(
        "Create a complete and structured customer support "
        "record containing the customer query, assistant "
        "response, web search response, and final answer."
    ),

    backstory=(
        "You are a customer support documentation specialist. "
        "You maintain clear, accurate records of customer "
        "interactions. You preserve the original query and "
        "agent responses without inventing missing details. "
        "When web search was not used, you record it as "
        "Not Required."
    ),

    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=3
)
