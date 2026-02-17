# 🗄️ SQL Agent

> **Ask questions about your data in plain English.** This agent translates natural language into SQL, executes queries against a database, and returns results with clear explanations.

Built with [LangChain](https://python.langchain.com/), [Streamlit](https://streamlit.io/), and [SQLite](https://sqlite.org/).

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3-orange.svg)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Chat UI                     │
│              (src/ui/app.py)                            │
└──────────────────────┬──────────────────────────────────┘
                       │ user question
                       ▼
┌─────────────────────────────────────────────────────────┐
│                     SQL Agent                           │
│              (src/agent/sql_agent.py)                   │
│                                                         │
│  1. Question  ──▶  LLM generates SQL                   │
│  2. SQL       ──▶  Safety validator                     │
│  3. Validated ──▶  Execute against DB                   │
│  4. Results   ──▶  LLM explains findings                │
└───────┬──────────────┬──────────────┬───────────────────┘
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌───────────┐ ┌──────────────┐
│  LLM Factory │ │ Validator │ │   Database   │
│  Anthropic / │ │ Read-only │ │   SQLite     │
│  OpenAI      │ │ by default│ │   (sample)   │
└──────────────┘ └───────────┘ └──────────────┘
```

## Features

- 🔤 **Natural language → SQL** — ask questions in English, get answers from your database
- 🛡️ **Safety first** — read-only by default, blocks DROP/DELETE/UPDATE, prevents SQL injection
- 🔀 **Multi-provider** — switch between Anthropic and OpenAI with a single env var
- 📊 **Rich UI** — Streamlit chat with SQL display, data tables, and explanations
- 🐳 **Dockerized** — one command to run
- 🧪 **Tested** — unit tests for validation, database, and config

## Quick Start

### Prerequisites

- Python 3.11+
- An API key for [Anthropic](https://console.anthropic.com/) or [OpenAI](https://platform.openai.com/)

### Setup

```bash
# Clone
git clone https://github.com/bludragon-ai/sql-agent.git
cd sql-agent

# Create virtual environment
python -m venv venv && source venv/bin/activate

# Install
make install

# Configure
cp .env.example .env
# Edit .env with your API key

# Seed the sample database
make seed

# Run
make run
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Docker

```bash
cp .env.example .env
# Edit .env with your API key

make docker-up
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `anthropic` | LLM provider (`anthropic` or `openai`) |
| `LLM_MODEL` | auto | Model name (defaults: `claude-sonnet-4-20250514` / `gpt-4o`) |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `DATABASE_PATH` | `data/sample.db` | Path to SQLite database |
| `ALLOW_WRITE_QUERIES` | `false` | Enable INSERT/UPDATE/DELETE |
| `STREAMLIT_PORT` | `8501` | Streamlit server port |

## Sample Queries

Try these with the included sample database:

| Question | What it does |
|---|---|
| *"How many customers do we have per country?"* | Aggregation with GROUP BY |
| *"What are the top 5 best-selling products by revenue?"* | JOIN + aggregation + ORDER BY |
| *"Show me all orders placed by Alice Johnson"* | Filtered JOIN across 3 tables |
| *"What is the average order value by status?"* | Computed metrics with grouping |
| *"Which customers have never placed an order?"* | LEFT JOIN with NULL check |

## Sample Database

The seed script creates a small business dataset:

- **customers** (10 rows) — name, email, city, country
- **products** (12 rows) — name, category, price, stock
- **orders** (15 rows) — customer_id, date, status
- **order_items** (28 rows) — order_id, product_id, quantity, unit_price

## Project Structure

```
sql-agent/
├── src/
│   ├── agent/
│   │   ├── llm.py           # LLM factory (Anthropic/OpenAI)
│   │   ├── prompts.py       # Prompt templates
│   │   └── sql_agent.py     # Core agent orchestration
│   ├── database/
│   │   ├── connection.py    # SQLAlchemy/LangChain DB wrapper
│   │   └── seed.py          # Sample data seeder
│   ├── ui/
│   │   └── app.py           # Streamlit chat interface
│   ├── utils/
│   │   └── sql_validator.py # SQL safety checks
│   └── config.py            # Centralised settings
├── tests/
├── data/                    # SQLite database location
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── .env.example
```

## Development

```bash
# Install with dev dependencies
make dev

# Run tests
make test

# Lint
make lint
```

## Safety Model

The SQL validator enforces three layers of protection:

1. **Read-only by default** — only `SELECT` queries pass validation
2. **Write opt-in** — set `ALLOW_WRITE_QUERIES=true` to enable mutations
3. **Always blocked** — `ATTACH`, `DETACH`, and dangerous `PRAGMA` statements are never allowed, even with writes enabled

Multi-statement queries (`;` followed by another statement) are also blocked to prevent injection.

## License

[MIT](LICENSE)
