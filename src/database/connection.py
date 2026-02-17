"""Database connection utilities."""

from __future__ import annotations

from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, text

from src.config import Settings


def get_sql_database(settings: Settings) -> SQLDatabase:
    """Return a LangChain ``SQLDatabase`` wrapper for the configured DB."""
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
    )
    return SQLDatabase(engine=engine)


def execute_query(settings: Settings, sql: str) -> list[dict]:
    """Execute *sql* against the database and return rows as dicts."""
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
    )
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]
