"""Seed script — creates and populates the sample SQLite database.

Run directly:  python -m src.database.seed
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DATABASE_PATH = Path("data/sample.db")

# ── Schema ──────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    city        TEXT    NOT NULL,
    country     TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    price       REAL    NOT NULL CHECK (price >= 0),
    stock       INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id  INTEGER NOT NULL REFERENCES customers(id),
    order_date   TEXT    NOT NULL DEFAULT (date('now')),
    status       TEXT    NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'shipped', 'delivered', 'cancelled'))
);

CREATE TABLE IF NOT EXISTS order_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id    INTEGER NOT NULL REFERENCES orders(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    unit_price  REAL    NOT NULL CHECK (unit_price >= 0)
);
"""

# ── Sample Data ─────────────────────────────────────────────────────────────

CUSTOMERS = [
    ("Alice Johnson", "alice@example.com", "New York", "US", "2024-01-15"),
    ("Bob Smith", "bob@example.com", "London", "UK", "2024-02-20"),
    ("Carlos Rivera", "carlos@example.com", "Mexico City", "MX", "2024-03-05"),
    ("Diana Chen", "diana@example.com", "Shanghai", "CN", "2024-03-18"),
    ("Eva Müller", "eva@example.com", "Berlin", "DE", "2024-04-01"),
    ("Frank Tanaka", "frank@example.com", "Tokyo", "JP", "2024-04-22"),
    ("Grace Kim", "grace@example.com", "Seoul", "KR", "2024-05-10"),
    ("Hassan Ali", "hassan@example.com", "Dubai", "AE", "2024-06-01"),
    ("Iris Santos", "iris@example.com", "São Paulo", "BR", "2024-06-15"),
    ("James O'Brien", "james@example.com", "Dublin", "IE", "2024-07-03"),
]

PRODUCTS = [
    ("Laptop Pro 15", "Electronics", 1299.99, 45),
    ("Wireless Mouse", "Electronics", 29.99, 200),
    ("Mechanical Keyboard", "Electronics", 89.99, 120),
    ("USB-C Hub", "Electronics", 49.99, 80),
    ("Standing Desk", "Furniture", 549.99, 30),
    ("Ergonomic Chair", "Furniture", 399.99, 25),
    ("Monitor Arm", "Furniture", 79.99, 60),
    ("Notebook Pack (3)", "Office", 12.99, 300),
    ("Ballpoint Pens (10)", "Office", 8.99, 500),
    ("Desk Lamp", "Office", 34.99, 90),
    ("Webcam HD", "Electronics", 59.99, 110),
    ("Noise-Cancelling Headphones", "Electronics", 199.99, 55),
]

ORDERS = [
    (1, "2024-06-10", "delivered"),
    (1, "2024-08-22", "delivered"),
    (2, "2024-07-01", "delivered"),
    (3, "2024-07-15", "shipped"),
    (4, "2024-08-05", "delivered"),
    (5, "2024-08-20", "shipped"),
    (6, "2024-09-01", "pending"),
    (7, "2024-09-10", "pending"),
    (8, "2024-09-15", "cancelled"),
    (9, "2024-10-01", "delivered"),
    (2, "2024-10-10", "shipped"),
    (4, "2024-10-20", "pending"),
    (10, "2024-11-01", "delivered"),
    (3, "2024-11-15", "delivered"),
    (5, "2024-12-01", "pending"),
]

ORDER_ITEMS = [
    (1, 1, 1, 1299.99),
    (1, 2, 2, 29.99),
    (2, 5, 1, 549.99),
    (2, 7, 1, 79.99),
    (3, 3, 1, 89.99),
    (3, 4, 2, 49.99),
    (4, 12, 1, 199.99),
    (4, 11, 1, 59.99),
    (5, 1, 2, 1299.99),
    (5, 6, 1, 399.99),
    (6, 8, 5, 12.99),
    (6, 9, 3, 8.99),
    (7, 10, 2, 34.99),
    (7, 2, 1, 29.99),
    (8, 1, 1, 1299.99),
    (8, 12, 2, 199.99),
    (9, 6, 1, 399.99),
    (10, 3, 2, 89.99),
    (10, 4, 1, 49.99),
    (11, 5, 1, 549.99),
    (11, 10, 1, 34.99),
    (12, 11, 3, 59.99),
    (12, 2, 5, 29.99),
    (13, 1, 1, 1299.99),
    (13, 3, 1, 89.99),
    (14, 12, 1, 199.99),
    (14, 8, 10, 12.99),
    (15, 7, 2, 79.99),
]


def seed(db_path: Path = DATABASE_PATH) -> None:
    """Create tables and insert sample data."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing DB for idempotent seeding
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.executescript(SCHEMA)

    cur.executemany(
        "INSERT INTO customers (name, email, city, country, created_at) VALUES (?, ?, ?, ?, ?)",
        CUSTOMERS,
    )
    cur.executemany(
        "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
        PRODUCTS,
    )
    cur.executemany(
        "INSERT INTO orders (customer_id, order_date, status) VALUES (?, ?, ?)",
        ORDERS,
    )
    cur.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        ORDER_ITEMS,
    )

    conn.commit()
    conn.close()

    print(f"✅ Seeded database at {db_path}")
    print(f"   • {len(CUSTOMERS)} customers")
    print(f"   • {len(PRODUCTS)} products")
    print(f"   • {len(ORDERS)} orders")
    print(f"   • {len(ORDER_ITEMS)} order items")


if __name__ == "__main__":
    seed()
