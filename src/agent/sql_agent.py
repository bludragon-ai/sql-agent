"""Core SQL agent — orchestrates question → SQL → results → explanation."""

from __future__ import annotations

from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage

from src.agent.llm import build_llm
from src.agent.prompts import EXPLAIN_PROMPT, SYSTEM_PROMPT
from src.config import Settings
from src.database.connection import execute_query, get_sql_database
from src.utils.sql_validator import UnsafeSQLError, validate_sql


@dataclass
class AgentResponse:
    """Structured response from the SQL agent."""

    question: str
    sql: str
    results: list[dict]
    explanation: str
    error: str | None = None


class SQLAgent:
    """Stateless agent that converts natural language to SQL and explains results.

    Parameters
    ----------
    settings:
        Application settings (provider, keys, DB path, safety flags).
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._llm = build_llm(settings)
        self._db = get_sql_database(settings)

    @property
    def schema(self) -> str:
        """Return the database schema description used for prompting."""
        return self._db.get_table_info()

    def ask(self, question: str) -> AgentResponse:
        """Process a natural-language *question* end-to-end.

        Steps:
        1. Generate SQL via the LLM.
        2. Validate the SQL for safety.
        3. Execute against the database.
        4. Generate a natural-language explanation.
        """
        # ── Step 1: Generate SQL ────────────────────────────────────────
        sql_messages = [
            SystemMessage(content=SYSTEM_PROMPT.format(schema=self.schema)),
            HumanMessage(content=question),
        ]
        raw_sql = self._llm.invoke(sql_messages).content.strip()

        # Strip markdown code fences if the model wraps them
        if raw_sql.startswith("```"):
            lines = raw_sql.split("\n")
            raw_sql = "\n".join(
                line for line in lines if not line.strip().startswith("```")
            ).strip()

        # ── Step 2: Validate ────────────────────────────────────────────
        try:
            sql = validate_sql(raw_sql, allow_writes=self._settings.allow_write_queries)
        except UnsafeSQLError as exc:
            return AgentResponse(
                question=question,
                sql=raw_sql,
                results=[],
                explanation="",
                error=str(exc),
            )

        # ── Step 3: Execute ─────────────────────────────────────────────
        try:
            results = execute_query(self._settings, sql)
        except Exception as exc:
            return AgentResponse(
                question=question,
                sql=sql,
                results=[],
                explanation="",
                error=f"Query execution failed: {exc}",
            )

        # ── Step 4: Explain ─────────────────────────────────────────────
        explain_prompt = EXPLAIN_PROMPT.format(
            question=question,
            sql=sql,
            results=_format_results(results),
        )
        explanation = self._llm.invoke([HumanMessage(content=explain_prompt)]).content

        return AgentResponse(
            question=question,
            sql=sql,
            results=results,
            explanation=explanation,
        )


def _format_results(results: list[dict], max_rows: int = 50) -> str:
    """Convert query results to a string for the explanation prompt."""
    if not results:
        return "(no rows returned)"
    display = results[:max_rows]
    lines = [str(row) for row in display]
    if len(results) > max_rows:
        lines.append(f"... ({len(results) - max_rows} more rows)")
    return "\n".join(lines)
