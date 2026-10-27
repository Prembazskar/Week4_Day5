
import json
from pathlib import Path

import streamlit as st

from crew import run_customer_support


# ==========================================
# Streamlit Page Configuration
# ==========================================

st.set_page_config(
    page_title="AI Customer Support Agent",
    page_icon="🤖",
    layout="wide"
)


# ==========================================
# Application Title
# ==========================================

st.title("🤖 AI Customer Support Agent")
st.caption("Multi-Agent System using CrewAI + Streamlit")

st.markdown(
    """
    Welcome to the AI-powered Customer Support System.

    This application uses three specialized AI agents:

    - 💬 **Assistant Agent** - Answers customer questions.
    - 🌐 **Web Search Agent** - Researches when needed.
    - 📝 **Entry Agent** - Creates customer support records.
    """
)

st.divider()


# ==========================================
# Session State
# ==========================================

if "support_result" not in st.session_state:
    st.session_state.support_result = None

if "last_query" not in st.session_state:
    st.session_state.last_query = ""


# ==========================================
# Sidebar
# ==========================================

with st.sidebar:

    st.header("⚙️ System Information")

    st.success("CrewAI Multi-Agent System")

    st.markdown("### Agents")
    st.write("💬 Assistant Agent")
    st.write("🌐 Web Search Agent")
    st.write("📝 Entry Agent")

    st.divider()

    st.markdown("### Technologies")
    st.write("Python")
    st.write("CrewAI")
    st.write("Streamlit")
    st.write("OpenAI")
    st.write("Serper API")

    st.divider()

    if st.button("🗑️ Clear Current Result"):
        st.session_state.support_result = None
        st.session_state.last_query = ""
        st.rerun()


# ==========================================
# Customer Query Form
# ==========================================

st.subheader("💬 Ask Customer Support")

with st.form("customer_support_form"):

    customer_query = st.text_area(
        "Enter your customer question:",
        placeholder=(
            "Example: What is HTTPS?\n"
            "Or: What is the latest Python release?"
        ),
        height=120
    )

    submitted = st.form_submit_button(
        "🚀 Submit Query",
        use_container_width=True
    )


# ==========================================
# Execute CrewAI Workflow
# ==========================================

if submitted:

    if not customer_query.strip():

        st.warning("Please enter a customer question.")

    else:

        st.session_state.support_result = None

        with st.spinner(
            "AI agents are processing your question..."
        ):

            try:

                result = run_customer_support(
                    customer_query.strip()
                )

                st.session_state.support_result = result
                st.session_state.last_query = customer_query

                st.success(
                    "Customer support workflow completed!"
                )

            except Exception as error:

                st.error(
                    f"Error while processing query: {error}"
                )


# ==========================================
# Display Results
# ==========================================

result = st.session_state.support_result

if result:

    st.divider()

    st.subheader("✅ Final Customer Support Answer")

    st.info(result.get("final_answer", "No answer available"))

    st.divider()

    # Agent Execution Summary

    st.subheader("📊 Agent Execution Summary")

    web_used = (
        result.get("web_search_response") != "Not Required"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Assistant Agent",
            "Executed"
        )

    with col2:
        st.metric(
            "Web Search Agent",
            "Executed" if web_used else "Skipped"
        )

    with col3:
        st.metric(
            "Entry Agent",
            "Executed"
        )

    st.divider()

    # Detailed Agent Responses

    st.subheader("🔍 Agent Responses")

    with st.expander("💬 Assistant Agent Response"):
        st.write(
            result.get("assistant_response", "")
        )

    with st.expander("🌐 Web Search Agent Response"):
        st.write(
            result.get("web_search_response", "")
        )

    with st.expander("📝 Entry Agent Record"):
        st.json(
            result.get("entry_agent_output", {})
        )

    st.divider()

    # Download Current Support Record

    st.subheader("📥 Download Support Record")

    st.download_button(
        label="Download JSON Record",
        data=json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        ),
        file_name="customer_support_record.json",
        mime="application/json",
        use_container_width=True
    )


# ==========================================
# Saved Support History
# ==========================================

st.divider()

st.subheader("📁 Previous Customer Support Records")

records_file = (
    Path(__file__).resolve().parent
    / "outputs"
    / "support_records.json"
)

if records_file.exists():

    try:

        content = records_file.read_text(
            encoding="utf-8"
        ).strip()

        records = json.loads(content) if content else []

        if not isinstance(records, list):
            records = []

        if records:

            st.write(
                f"Total saved records: {len(records)}"
            )

            for index, record in enumerate(
                reversed(records),
                start=1
            ):

                query = record.get(
                    "customer_query",
                    "Unknown Query"
                )

                with st.expander(
                    f"{index}. {query[:80]}"
                ):

                    st.write(
                        "**Customer Query:**",
                        query
                    )

                    st.write(
                        "**Final Answer:**"
                    )

                    st.write(
                        record.get("final_answer", "")
                    )

                    st.caption(
                        record.get("timestamp", "")
                    )

        else:

            st.info("No previous support records found.")

    except (json.JSONDecodeError, OSError):

        st.warning(
            "Unable to read saved support records."
        )

else:

    st.info(
        "Support history will appear after your first query."
    )


# ==========================================
# Footer
# ==========================================

st.divider()

st.caption(
    "Built using Python, CrewAI, Streamlit, OpenAI and Serper."
)
