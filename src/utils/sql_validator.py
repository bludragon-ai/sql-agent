"""SQL safety validation — blocks dangerous statements unless explicitly allowed."""

from __future__ import annotations

import re

# Statements that mutate data or schema.
_WRITE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|MERGE)\b", re.I),
    re.compile(r"\bSELECT\b[^;]*\bINTO\b", re.I),  # catches SELECT … INTO (table creation)
    re.compile(r";\s*\w", re.I),     # multiple statements (injection vector)
]

# Always blocked regardless of settings — prevents catastrophic operations.
_ALWAYS_BLOCKED: list[re.Pattern[str]] = [
    re.compile(r"\bATTACH\b", re.I),
    re.compile(r"\bDETACH\b", re.I),
    re.compile(r"\bPRAGMA\s+(?!table_info|table_list|database_list)", re.I),
]


class UnsafeSQLError(Exception):
    """Raised when a query fails safety validation."""


def validate_sql(sql: str, *, allow_writes: bool = False) -> str:
    """Validate and return the SQL string, or raise ``UnsafeSQLError``.

    Parameters
    ----------
    sql:
        The raw SQL to check.
    allow_writes:
        If *True*, mutation statements are permitted (but always-blocked
        patterns still apply).

    Returns
    -------
    str
        The original SQL, stripped of leading/trailing whitespace.
    """
    cleaned = sql.strip().rstrip(";")

    # Always-blocked patterns
    for pattern in _ALWAYS_BLOCKED:
        if pattern.search(cleaned):
            raise UnsafeSQLError(
                f"Blocked: query matches forbidden pattern ({pattern.pattern})"
            )

    # Write-pattern check
    if not allow_writes:
        for pattern in _WRITE_PATTERNS:
            if pattern.search(cleaned):
                raise UnsafeSQLError(
                    "Write operations are disabled. Set ALLOW_WRITE_QUERIES=true to enable."
                )

    return cleaned
