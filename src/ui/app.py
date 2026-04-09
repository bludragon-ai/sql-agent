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

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp { background-color: #000000; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'JetBrains Mono', monospace;
        color: #d4a853;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        font-weight: 500;
    }

    .stApp h1 { color: white; font-weight: 700; }
    .stApp .stMarkdown p { color: #a3a3a3; }

    [data-testid="stChatInput"] textarea {
        background-color: #111111 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: #e5e5e5 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: rgba(212,168,83,0.3) !important;
    }

    .stButton > button {
        background-color: rgba(212,168,83,0.1);
        color: #d4a853;
        border: 1px solid rgba(212,168,83,0.3);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: rgba(212,168,83,0.2);
        border-color: rgba(212,168,83,0.5);
    }

    .stTable, .stDataFrame {
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        overflow: hidden;
    }
    .stTable th, [data-testid="stDataFrame"] th {
        background-color: #111111 !important;
        color: #d4a853 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .stTable td, [data-testid="stDataFrame"] td {
        background-color: #0a0a0a !important;
        color: #a3a3a3 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
        border-top: 1px solid rgba(255,255,255,0.04) !important;
    }

    /* Code blocks for SQL display */
    .stCodeBlock, pre, code {
        background-color: #0a0a0a !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    hr { border-color: rgba(255,255,255,0.06) !important; }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #000000; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }

    [data-testid="stChatMessage"] {
        background-color: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
    }

    [data-testid="stMetric"] label {
        font-family: 'JetBrains Mono', monospace;
        color: #d4a853;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
    }

    /* Sidebar sample questions */
    [data-testid="stSidebar"] .stButton > button {
        background-color: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        color: #a3a3a3;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        text-transform: none;
        letter-spacing: normal;
        text-align: left;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(255,255,255,0.05);
        border-color: rgba(212,168,83,0.3);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<p style="font-family: JetBrains Mono, monospace; color: #d4a853; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 4px;">Interactive Demo</p>', unsafe_allow_html=True)
    st.title("🗄️ SQL Agent")
    st.markdown('<p style="font-family: JetBrains Mono, monospace; color: rgba(212,168,83,0.8); font-size: 0.85rem;">Natural Language Database Interface</p>', unsafe_allow_html=True)
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
