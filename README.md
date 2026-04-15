# AI-Enhanced Supply Chain 🚧👷

A Python toolkit applying machine learning and combinatorial optimization to supply chain problems. Organized as a uv workspace with three modules: demand forecasting, inventory optimization, and routing optimization.

## Modules

### Demand Forecasting (`demand-forecasting/`)

Uses an XGBoost regressor to predict retail store demand (units sold) from historical inventory data.

**Input:** `data/retail_store_inventory.csv` — columns include `Date`, `Store ID`, `Product ID`, `Category`, `Region`, `Weather Condition`, `Seasonality`, `Units Sold`, and `Demand Forecast`.

**How it works:**
- Extracts temporal features from `Date` (year, month, day, day-of-week)
- Encodes categorical columns natively via XGBoost's `enable_categorical`
- Trains an 80/20 chronological split (no shuffle) to respect time ordering
- Evaluates with MAE and RMSE on the held-out test set
- Appends `Predicted_Demand_Forecast` to the original data and saves it to `data/retail_forecast_with_original_values.csv`
- Plots actual vs. predicted demand (first 100 validation points) and a top-15 feature importance chart

**Run:**
```bash
uv run demand-forecasting
# or
uv run python -m demand_forecasting
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
uv run routing-optimization
# or
uv run python -m routing_optimization
```

**Output:** Optimized route sequence and total distance printed to stdout for each distance matrix.

---

### Inventory Optimization (`inventory-optimization/`)

Placeholder module for inventory optimization algorithms (e.g. EOQ, safety stock, reorder point models).

**Run:**
```bash
uv run inventory-optimization
# or
uv run python -m inventory_optimization
```

---

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
# Install all workspace members and their dependencies
uv sync --all-packages
```

## Project Structure

```
ai-enhanced-supply-chain/
├── data/
│   ├── retail_store_inventory.csv               # Input: raw retail inventory data
│   ├── retail_forecast_with_original_values.csv # Generated: demand output → inventory input
│   ├── distance_matrix_1.csv                    # Input: routing scenario 1
│   └── distance_matrix_2.csv                    # Input: routing scenario 2
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
│   │   └── solver.py                   # Inventory optimization logic (WIP)
│   └── pyproject.toml
├── routing-optimization/
│   ├── src/routing_optimization/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── solver.py                   # Nearest Neighbor + 2-opt TSP solver
│   └── pyproject.toml
├── main.py
└── pyproject.toml                      # uv workspace root
```
