"""Tests for database seeding and connection."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.config import Settings
from src.database.connection import execute_query
from src.database.seed import seed


@pytest.fixture()
def seeded_db(tmp_path: Path) -> Path:
    """Seed a temporary database and return its path."""
    db_path = tmp_path / "test.db"
    seed(db_path)
    return db_path


def test_seed_creates_database(seeded_db: Path):
    assert seeded_db.exists()


def test_seed_customer_count(seeded_db: Path):
    settings = Settings(database_path=str(seeded_db))
    rows = execute_query(settings, "SELECT COUNT(*) AS cnt FROM customers")
    assert rows[0]["cnt"] == 10


def test_seed_product_count(seeded_db: Path):
    settings = Settings(database_path=str(seeded_db))
    rows = execute_query(settings, "SELECT COUNT(*) AS cnt FROM products")
    assert rows[0]["cnt"] == 12


def test_seed_order_count(seeded_db: Path):
    settings = Settings(database_path=str(seeded_db))
    rows = execute_query(settings, "SELECT COUNT(*) AS cnt FROM orders")
    assert rows[0]["cnt"] == 15


def test_seed_order_item_count(seeded_db: Path):
    settings = Settings(database_path=str(seeded_db))
    rows = execute_query(settings, "SELECT COUNT(*) AS cnt FROM order_items")
    assert rows[0]["cnt"] == 28


def test_query_with_join(seeded_db: Path):
    settings = Settings(database_path=str(seeded_db))
    rows = execute_query(
        settings,
        """
        SELECT c.name, COUNT(o.id) AS order_count
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id
        ORDER BY order_count DESC
        LIMIT 3
        """,
    )
    assert len(rows) == 3
    assert rows[0]["order_count"] >= rows[1]["order_count"]
