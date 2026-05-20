# DataAnalystAgent

A lightweight orchestration layer that chains two existing LangGraph projects into a single pipeline:

1. **`data-cleaning-agent`**: LLM-driven data cleaning
2. **`eda-workflow`**: automated first-pass exploratory data analysis

Flow: **raw CSV → PII guardrail → clean data → EDA report**

## Why this project exists

`DataAnalystAgent` demonstrates agent-to-agent orchestration without rewriting either sub-project. The parent graph handles state passing, input guardrails (PII detection), and conditional routing (e.g. blocking the pipeline when PII is found, or skipping EDA when cleaning fails).

## Setup

### Prerequisites
- Python 3.14
- uv
- OpenAI API key

### Install
From this folder:

```bash
uv sync
```

Copy the example environment file and fill in your key:

```bash
cp .env.example .env
```

Then edit `.env` and set your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-key-here
```

## Run example

```bash
uv run python example_usage.py
```

## Run tests

```bash
uv run pytest -q
```

## Project structure

```text
data-analyst-agent/
├── data_analyst_agent/
│   ├── __init__.py
│   ├── guardrails.py
│   └── orchestrator.py
├── tests/
│   └── test_guardrails.py
├── .env.example
├── example_usage.py
├── pyproject.toml
├── uv.lock
└── README.md
```

- **`orchestrator.py`** — Student version with TODOs to complete.
- **`guardrails.py`** — PII column detection guardrail.

## Graph visualization

Running `example_usage.py` generates a `graph.png` diagram of the orchestration graph.

## LangSmith (optional)

To enable tracing, set the LangSmith variables in your `.env` file. If they are not set, the pipeline runs normally without tracing.

## Notes
- Both sub-projects (`data-cleaning-agent` and `eda-workflow`) are linked as **local path dependencies** in `pyproject.toml`. This means they are expected to live in sibling directories (e.g. `../data-cleaning-agent` and `../eda-workflow`). When you run `uv sync`, uv resolves them from those local paths rather than from PyPI.
- A PII guardrail runs before any LLM call and blocks the pipeline if sensitive columns are detected.
- If cleaning fails, EDA is skipped.
