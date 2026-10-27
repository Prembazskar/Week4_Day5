
from tasks import (
    create_assistant_task,
    create_web_search_task,
    create_entry_task
)

query = "What is HTTPS?"

assistant_task = create_assistant_task(query)
web_task = create_web_search_task(query)

entry_task = create_entry_task(
    customer_query=query,
    assistant_response="HTTPS is a secure version of HTTP.",
    web_search_response="Not Required"
)

print("Assistant Task:", assistant_task.agent.role)
print("Web Search Task:", web_task.agent.role)
print("Entry Task:", entry_task.agent.role)

print("\nAll three tasks created successfully!")
