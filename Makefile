.PHONY: help install dev seed run test lint clean docker-up docker-down setup

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

dev: ## Install with dev dependencies
	pip install -e ".[dev]"

seed: ## Create and populate the sample SQLite database
	python -m src.database.seed

run: ## Launch the Streamlit UI
	streamlit run src/ui/app.py --server.port=$${STREAMLIT_PORT:-8501}

test: ## Run unit tests with coverage
	pytest --cov=src --cov-report=term-missing

lint: ## Lint with ruff
	ruff check src/ tests/
	ruff format --check src/ tests/

clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage dist build *.egg-info

docker-up: ## Start with Docker Compose
	docker compose up --build -d

docker-down: ## Stop Docker Compose services
	docker compose down

setup: ## One-command project setup
	python -m venv venv && . venv/bin/activate && pip install -e ".[dev]" && cp -n .env.example .env && make seed && echo "Ready! Edit .env with your API key, then: make run"
