# AI-Enhanced Supply Chain

A Python toolkit applying machine learning and combinatorial optimization to supply chain problems. Organized as a uv workspace with three modules: demand forecasting, inventory optimization, and routing optimization.

## Project Structure

```
ai-enhanced-supply-chain/
├── data/
│   ├── retail_store_inventory.csv               # Input: raw retail inventory data
│   ├── retail_forecast_with_original_values.csv # Generated: demand output → inventory input
│   ├── inventory_s001_north_may_2022.csv                  # Input: inventory data for store S001
│   ├── inventory_optimization_results_scenario_1.csv     # Generated: LP vs proportional
│   ├── inventory_optimization_results_scenario_2.csv     # Generated: biased allocation
│   ├── distance_matrix_1.csv                    # Input: routing scenario 1
│   ├── distance_matrix_2.csv                    # Input: routing scenario 2
│   └── sustainability_config.json               # Input: emission factors and targets
├── demand-forecasting/
│   ├── src/demand_forecasting/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── model.py                    # XGBoost demand forecasting logic
│   └── pyproject.toml
├── inventory-optimization/
│   ├── src/inventory_optimization/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── solver.py                   # LP + proportional allocation solver
│   └── pyproject.toml
├── routing-optimization/
│   ├── src/routing_optimization/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── solver.py                   # Nearest Neighbor + 2-opt TSP solver
│   └── pyproject.toml
├── specs/
│   ├── constitution.md                          # Project principles and coding standards
│   └── 001-sustainability-metrics/              # Sustainability metrics feature spec
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── .specify/                                    # Spec-kit tooling config, templates, extensions
├── .agent/skills/                               # Claude Code skill definitions (speckit commands)
├── AGENTS.md                                    # Project context guide for AI coding agents
├── query.py                            # Natural language query interface (Claude Opus 4.7)
├── main.py
└── pyproject.toml                      # uv workspace root
```

## Architecture

![Architecture Diagram](docs/architecture.drawio.svg)

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
# Install all workspace members and their dependencies
uv sync --all-packages
```

## Testing

The project uses `pytest` for automated testing.

```bash
# Run all tests
uv run pytest
```

Tests cover demand forecasting, inventory allocation logic, routing optimization heuristics, and sustainability metric calculations.

## Code Quality

The project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting, managed via [pre-commit](https://pre-commit.com/).

### Pre-commit Hooks

Hooks are configured to run automatically on every commit to ensure:

- Code is formatted according to project standards.
- Linting errors are identified and auto-fixed where possible.
- All tests pass before a commit is finalized.

To run hooks manually:

```bash
uv run pre-commit run --all-files
```

Ruff configuration (line length, rule selection) is located in `pyproject.toml`.

## Modules

### Demand Forecasting (`demand-forecasting/`)

Uses an XGBoost regressor to predict retail store demand (units sold) from historical inventory data.

**Input:** `data/retail_store_inventory.csv` — columns include `Date`, `Store ID`, `Product ID`, `Category`, `Region`, `Inventory Level`, `Units Sold`, `Units Ordered`, `Price`, `Discount`, `Weather Condition`, `Holiday/Promotion`, `Competitor Pricing`, and `Seasonality`.

**How it works:**

- Extracts temporal features from `Date` (year, month, day, day-of-week)
- Encodes categorical columns natively via XGBoost's `enable_categorical`
- Trains an 80/20 chronological split (no shuffle) to respect time ordering
- Evaluates with MAE and RMSE on the held-out test set
- Appends `Predicted_Demand_Forecast` to the original data and saves it to `data/retail_forecast_with_original_values.csv`
- Plots actual vs. predicted demand (first 100 validation points) and a top-15 feature importance chart

**Run:**

```bash
# Basic run
uv run demand-forecasting
# Run with custom data path
uv run demand-forecasting --input data/custom_inventory.csv
```

**Output:** `data/retail_forecast_with_original_values.csv` + two matplotlib charts.

---

### Routing Optimization (`routing-optimization/`)

Solves the Travelling Salesman Problem (TSP) for delivery routes using a Nearest Neighbor construction heuristic followed by 2-opt local search refinement.

**Input:** `data/distance_matrix_1.csv` and `data/distance_matrix_2.csv` — square distance matrices where node `0` represents the warehouse.

**How it works:**

1. **Nearest Neighbor** — greedily builds an initial route by always visiting the closest unvisited node.
2. **2-opt** — iteratively reverses sub-segments of the route whenever doing so reduces total distance, until no improvement is found.

**Run:**

```bash
# Run with default matrices
uv run routing-optimization
# Run with specific matrix files
uv run routing-optimization --inputs data/distance_matrix_1.csv data/distance_matrix_2.csv
```

**Output:**

- Optimized route sequence and total distance (km).
- **Total Carbon Footprint** (kg CO2) per route based on shipping emission factors.
- `data/routing_optimization_results.csv` including CO2 metrics.

---

### Inventory Optimization (`inventory-optimization/`)

Allocates stock across products to maximize revenue under a total stock constraint. It is fully integrated with the Demand Forecasting module, allowing for batch multi-period optimization.

**Input:** `data/retail_forecast_with_original_values.csv` — automatically aggregated and processed from the forecasting output.

**How it works:**

1. **Period-Based Batch Optimization** — Groups data by `month` or `week` and runs an independent optimization per period. Defaults to monthly (limit 500) for the forecast output; automatically uses weekly (limit 100) for `inventory_s001_north_may_2022.csv`.
2. **Scenario 1 (Fair vs. Optimal)** — Compares LP Revenue Maximization (OR-Tools GLOP) vs. Proportional Allocation (Largest Remainder Method). Proportional results are highlighted in summaries.
3. **Carbon-Efficient** — Maximizes revenue while capping total storage CO2 emissions at a threshold (default 85% of LP Max emissions).
4. **Scenario 2 (Guaranteed Minimum)** — Biased LP allocation guaranteeing each product at least 80% of its fair share.

**Run:**

```bash
# Default: forecast output, monthly aggregation, limit 500
uv run inventory-optimization

# Weekly store-specific file (auto-applies week + limit 100)
uv run inventory-optimization --input data/inventory_s001_north_may_2022.csv

# Override explicitly
uv run inventory-optimization --period week --limit 200 --store S001 --region North
```

**Output:**

- `data/inventory_optimization_results_scenario_1.csv` (LP, Prop, and Carbon-Efficient).
- `data/inventory_optimization_results_scenario_2.csv`.
- Terminal summary of **Total Proportional Revenue** and **Total CO2**.

---

## GitHub Actions Pipeline

The project includes a multi-stage CI/CD pipeline in `.github/workflows/pipeline.yml`.

- **Automated**: Runs automatically on **Pull Requests** targeting the `main` branch.
- **Manual Trigger**: Supports `workflow_dispatch` with automated data hand-offs between stages.

**Sequence:**
`Demand Forecasting` ➔ `Inventory Optimization` ➔ `Routing Optimization`

**Manual trigger inputs (`workflow_dispatch`):**

| Input              | Description                                 | Default                                                 |
| ------------------ | ------------------------------------------- | ------------------------------------------------------- |
| `forecast_input`   | Input CSV for demand forecasting            | `data/retail_store_inventory.csv`                       |
| `inventory_input`  | Input CSV for inventory optimization        | `data/retail_forecast_with_original_values.csv`         |
| `inventory_limit`  | Stock capacity limit per period             | `500`                                                   |
| `inventory_period` | Aggregation period (`month` or `week`)      | `month`                                                 |
| `routing_inputs`   | Space-separated paths for distance matrices | `data/distance_matrix_1.csv data/distance_matrix_2.csv` |

---

### Natural Language Query (`query.py`)

An interactive CLI that lets you ask questions about the supply chain data and optimization results in plain English, powered by Claude Opus 4.7.

**How it works:**

- Claude can call four tools: list data files, read CSVs, run the inventory solver (with CO2 data), or run the routing solver (with CO2 data).
- Integrated with sustainability metrics from `data/sustainability_config.json`.
- Responses stream token-by-token; adaptive thinking is enabled for complex reasoning
- Conversation is multi-turn — Claude remembers context within a session

**Setup:** Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Run:**

```bash
uv run python query.py
```

**Example questions:**

- _"Optimize inventory for Store S001 in May 2022 using the latest forecasts"_
- _"Which product generates the most revenue under LP max allocation?"_
- _"How much CO2 do we save by switching to the Carbon-Efficient inventory scenario?"_
- _"What is the total carbon footprint for the whole sequence?"_
- _"Explain the fairness tradeoff in the 20% biased scenario"_
- _"Why does LP ignore P3 even though it has the highest demand?"_

Type `clear` to reset the conversation or `exit` to quit.
