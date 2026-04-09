"""Database connection utilities."""

from __future__ import annotations

from functools import lru_cache

from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, text

from src.config import Settings


@lru_cache(maxsize=4)
def _get_engine(database_url: str):
    return create_engine(database_url, connect_args={"check_same_thread": False})


def get_sql_database(settings: Settings) -> SQLDatabase:
    """Return a LangChain ``SQLDatabase`` wrapper for the configured DB."""
    engine = _get_engine(settings.database_url)
    return SQLDatabase(engine=engine)


def execute_query(settings: Settings, sql: str) -> list[dict]:
    """Execute *sql* against the database and return rows as dicts."""
    engine = _get_engine(settings.database_url)
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]
