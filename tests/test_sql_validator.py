"""Tests for SQL safety validation."""

import pytest

from src.utils.sql_validator import UnsafeSQLError, validate_sql


class TestReadOnlyMode:
    """Default mode — only SELECT allowed."""

    def test_simple_select(self):
        assert validate_sql("SELECT * FROM users") == "SELECT * FROM users"

    def test_select_with_joins(self):
        sql = "SELECT u.name, o.id FROM users u JOIN orders o ON u.id = o.user_id"
        assert validate_sql(sql) == sql

    def test_blocks_insert(self):
        with pytest.raises(UnsafeSQLError, match="Write operations"):
            validate_sql("INSERT INTO users (name) VALUES ('x')")

    def test_blocks_update(self):
        with pytest.raises(UnsafeSQLError, match="Write operations"):
            validate_sql("UPDATE users SET name = 'x'")

    def test_blocks_delete(self):
        with pytest.raises(UnsafeSQLError, match="Write operations"):
            validate_sql("DELETE FROM users WHERE id = 1")

    def test_blocks_drop(self):
        with pytest.raises(UnsafeSQLError, match="Write operations"):
            validate_sql("DROP TABLE users")

    def test_blocks_multiple_statements(self):
        with pytest.raises(UnsafeSQLError, match="Write operations"):
            validate_sql("SELECT 1; DROP TABLE users")

    def test_strips_trailing_semicolon(self):
        assert validate_sql("SELECT 1;") == "SELECT 1"


class TestWriteMode:
    """Write mode enabled — mutations allowed (except always-blocked)."""

    def test_allows_insert(self):
        sql = "INSERT INTO users (name) VALUES ('x')"
        assert validate_sql(sql, allow_writes=True) == sql

    def test_allows_update(self):
        sql = "UPDATE users SET name = 'x'"
        assert validate_sql(sql, allow_writes=True) == sql


class TestAlwaysBlocked:
    """Patterns blocked regardless of settings."""

    def test_blocks_attach(self):
        with pytest.raises(UnsafeSQLError, match="forbidden"):
            validate_sql("ATTACH DATABASE 'x.db' AS x", allow_writes=True)

    def test_blocks_detach(self):
        with pytest.raises(UnsafeSQLError, match="forbidden"):
            validate_sql("DETACH DATABASE x", allow_writes=True)
