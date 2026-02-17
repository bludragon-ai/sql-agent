"""Streamlit chat UI for the SQL Agent."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.agent.sql_agent import SQLAgent
from src.config import get_settings

# ── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SQL Agent",
    page_icon="🗄️",
    layout="wide",
)

# ── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🗄️ SQL Agent")
    st.caption("Ask questions about your data in plain English.")

    st.divider()
    settings = get_settings()
    st.markdown(f"**Provider:** `{settings.llm_provider}`")
    st.markdown(f"**Model:** `{settings.llm_model}`")
    st.markdown(f"**Database:** `{settings.database_path}`")
    st.markdown(f"**Write queries:** `{'✅' if settings.allow_write_queries else '❌'}`")

    st.divider()
    st.markdown("### Sample questions")
    sample_questions = [
        "How many customers do we have per country?",
        "What are the top 5 best-selling products by revenue?",
        "Show me all orders placed by Alice Johnson",
        "What is the average order value by status?",
        "Which customers have never placed an order?",
    ]
    for q in sample_questions:
        if st.button(q, key=q, use_container_width=True):
            st.session_state["prefill"] = q

# ── Session state ───────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = SQLAgent(settings)

# ── Chat history ────────────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── User input ──────────────────────────────────────────────────────────────

prefill = st.session_state.pop("prefill", None)
prompt = st.chat_input("Ask a question about the database…") or prefill

if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            response = st.session_state.agent.ask(prompt)

        if response.error:
            st.error(f"⚠️ {response.error}")
            st.code(response.sql, language="sql")
            assistant_content = f"Error: {response.error}"
        else:
            # Show SQL
            st.markdown("**Generated SQL:**")
            st.code(response.sql, language="sql")

            # Show results as table
            if response.results:
                st.markdown("**Results:**")
                df = pd.DataFrame(response.results)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Query returned no results.")

            # Show explanation
            st.markdown("**Explanation:**")
            st.markdown(response.explanation)

            assistant_content = (
                f"**SQL:**\n```sql\n{response.sql}\n```\n\n{response.explanation}"
            )

    st.session_state.messages.append({"role": "assistant", "content": assistant_content})
