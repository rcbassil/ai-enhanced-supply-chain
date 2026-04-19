# Agent Guidelines: AI-Enhanced Supply Chain

This file provides context for AI coding agents (Claude Code, Codex, etc.) working in this repository.

## Project Overview

A Python toolkit applying machine learning and combinatorial optimization to supply chain problems. Organized as a `uv` workspace with three independent modules that form a sequential pipeline:

```
Demand Forecasting → Inventory Optimization → Routing Optimization
```

A natural language query interface (`query.py`) lets users interrogate all outputs via Claude.

## Repository Structure

```
ai-enhanced-supply-chain/
├── data/                              # All CSV inputs and outputs live here
│   ├── sustainability_config.json     # Emission factors (shipping & storage)
│   ├── retail_store_inventory.csv     # Raw input for demand forecasting
│   ├── retail_forecast_with_original_values.csv  # Pipeline hand-off: forecasting → inventory
│   ├── inventory_s001_north_may_2022.csv
│   ├── inventory_optimization_results_scenario_1.csv
│   ├── inventory_optimization_results_scenario_2.csv
│   ├── distance_matrix_1.csv
│   └── distance_matrix_2.csv
├── demand-forecasting/src/demand_forecasting/
│   └── model.py                       # XGBoost demand forecasting
├── inventory-optimization/src/inventory_optimization/
│   └── solver.py                      # LP + proportional + carbon-efficient allocation
├── routing-optimization/src/routing_optimization/
│   └── solver.py                      # Nearest Neighbor + 2-opt TSP, CO2 tracking
├── specs/                             # Spec-kit feature specs
│   ├── constitution.md                # Project principles and coding standards
│   └── 001-sustainability-metrics/    # Sustainability metrics feature
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── query.py                           # Natural language interface (Claude Opus 4.7)
├── main.py
└── pyproject.toml                     # uv workspace root
```

## Technology Stack

- **Python** 3.12+
- **uv** — dependency management and workspace coordination
- **XGBoost** — demand forecasting model
- **OR-Tools GLOP** — LP solver for inventory allocation
- **Anthropic SDK** (`anthropic>=0.50.0`) — Claude Opus 4.7 in `query.py`
- **Ruff** — linting and formatting (line length 100, rules E/F/B/I)
- **pytest** — test suite
- **pre-commit** — hooks run trailing-whitespace, ruff lint+format, and pytest on every commit

## Running the Pipeline

```bash
# Install all workspace dependencies
uv sync --all-packages

# Run each module individually
uv run demand-forecasting
uv run inventory-optimization
uv run routing-optimization

# Natural language interface
export ANTHROPIC_API_KEY="sk-ant-..."
uv run python query.py

# Run tests
uv run pytest

# Run pre-commit hooks manually
uv run pre-commit run --all-files
```

## Key Conventions

- **No hardcoded paths** — all file paths are resolved relative to `__file__` via `pathlib.Path`
- **No hardcoded secrets** — API keys via environment variables only (`ANTHROPIC_API_KEY`)
- **Type hints** on all function signatures
- **Google-style docstrings** on all public functions and classes
- **Logic in `src/<module>/solver.py` or `model.py`**, executed via `__main__.py`
- **All data files** (inputs and outputs) go under `data/` — never scatter CSVs across module directories

## Spec-Driven Workflow

Features follow the GitHub Spec Kit process:

1. **`specs/<NNN>-feature-name/spec.md`** — requirements, user stories, acceptance scenarios
2. **`specs/<NNN>-feature-name/plan.md`** — technical architecture and data models
3. **`specs/<NNN>-feature-name/tasks.md`** — granular, ordered implementation tasks
4. **Implement** — code changes referencing task IDs from `tasks.md`

Before starting any new feature, check `specs/` for an existing spec and read `specs/constitution.md`.

## Current Feature in Progress

**`specs/001-sustainability-metrics/`** — carbon footprint tracking across routing and inventory solvers. All tasks are marked complete; the feature is fully implemented and merged.

## Test Coverage

Tests live in `tests/` at the workspace root:

- `test_demand_forecasting.py` — data preprocessing and XGBoost model
- `test_inventory_optimization.py` — allocation strategies and sustainability config
- `test_routing_optimization.py` — TSP heuristics and emission calculations

pytest is configured in `pytest.ini` at the workspace root. All tests must pass before a commit is accepted (enforced by pre-commit hook).
