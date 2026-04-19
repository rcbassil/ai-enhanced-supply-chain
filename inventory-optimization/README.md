# inventory-optimization

Inventory allocation module using Linear Programming (LP) and Proportional Allocation to maximize revenue under a stock constraint. It is fully integrated with the Demand Forecasting module and supports **Period-Based Batch Optimization** (monthly or weekly) over multi-period datasets.

## How it works

The solver automatically processes multi-period datasets (e.g., multi-year forecasts) by grouping data by `Month` or `Week` and running independent optimization cycles for each period.

**Scenario 1 — Fair vs. Optimal** (`solve_inventory_allocation`):

1. **LP Revenue Maximization** — OR-Tools GLOP solver finds the optimal stock allocation that maximizes total revenue without exceeding the stock limit.
2. **Proportional Allocation (Largest Remainder Method)** — Distributes stock proportionally to predicted demand, ensuring a "fair share" baseline.
3. **Carbon-Efficient Allocation** — An LP variant that maximizes revenue while capping total storage CO2 emissions at a threshold (default 85% of LP Max emissions).

**Scenario 2 — Guaranteed Minimum** (`solve_biased_allocation`):

- Each product is guaranteed at least `(1 - bias%) × fair share` of the stock.
- Within those bounds, LP maximizes revenue.
- Default bias: 20%.

## Input

`data/retail_forecast_with_original_values.csv` — automatically aggregated and processed from the demand-forecasting output. Run forecasting first:

```bash
uv run demand-forecasting
```

### Supported CLI Flags

| Argument | Description |
|---|---|
| `--limit` | Total stock capacity per period (default: 100 for `inventory_s001_north_may_2022.csv`, 500 otherwise) |
| `--period` | Aggregation period: `month` or `week` (default: `week` for `inventory_s001_north_may_2022.csv`, `month` otherwise) |
| `--store` | Filter by Store ID (e.g., S001) |
| `--region` | Filter by Region (e.g., North) |
| `--date` | Filter by date prefix (e.g., 2022-05) |

### Input auto-detection

The default input is `data/retail_forecast_with_original_values.csv` (monthly, limit 500). When `--input data/inventory_s001_north_may_2022.csv` is passed, `--period` and `--limit` automatically default to `week` and `100` respectively — no extra flags needed.

## Output

Per-period results are concatenated into the final output files:

**`data/inventory_optimization_results_scenario_1.csv`**:
- Includes `LP_Max_Revenue_Stock`, `Prop_Stock_LRM`, and `Carbon_Efficient_Stock`.
- Contains Revenue and CO2 metrics for all three sub-scenarios.

**`data/inventory_optimization_results_scenario_2.csv`**:
- Includes `Final_Stock` and `Revenue` based on the biased allocation strategy.

## Run

From the workspace root:

```bash
# Default: forecast output, monthly aggregation, limit 500
uv run inventory-optimization

# Weekly store-specific file (auto-applies week + limit 100)
uv run inventory-optimization --input data/inventory_s001_north_may_2022.csv

# Override period and limit explicitly
uv run inventory-optimization --period week --limit 200 --region North
```

## Package structure

```
src/inventory_optimization/
├── __init__.py    # exposes main()
├── __main__.py    # enables python -m
└── solver.py      # solve_inventory_allocation, solve_biased_allocation, run
```
