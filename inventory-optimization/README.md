# inventory-optimization

Inventory allocation module using Linear Programming (LP) and Proportional Allocation to maximise revenue under a stock constraint. Produces two scenario outputs.

## How it works

**Scenario 1 — LP vs Proportional comparison** (`solve_inventory_allocation`):

1. **LP Revenue Maximisation** — OR-Tools GLOP solver finds the optimal stock allocation that maximises total revenue without exceeding the stock limit
2. **Proportional Allocation (Largest Remainder Method)** — distributes stock proportionally to predicted demand, using the largest remainder method to resolve rounding

**Scenario 2 — Biased allocation** (`solve_biased_allocation`):

- Each product is guaranteed at least `(1 - bias%) × fair share` of the stock
- Within those bounds, LP maximises revenue
- Default bias: 20%

## Input

`data/inventory_s001_north_may_2022.csv` — requires `Predicted Demand Forecast` from the demand-forecasting module. Run that first:

```bash
uv run demand-forecasting
```

Expected columns:

| Column | Description |
|---|---|
| Product | Product identifier |
| Price | Unit price |
| Predicted Demand Forecast | Forecasted demand (from demand-forecasting output) |

## Output

**`data/inventory_optimization_results_scenario_1.csv`** — LP vs proportional comparison:

| Column | Description |
|---|---|
| LP_Max_Revenue_Stock | Units to stock per LP solution |
| Prop_Stock_LRM | Units to stock per proportional allocation |
| LP_Revenue | Revenue under LP strategy |
| Prop_Revenue | Revenue under proportional strategy |
| TOTAL (LP Max) | Total revenue summary row |
| TOTAL (Proportional) | Total revenue summary row |

**`data/inventory_optimization_results_scenario_2.csv`** — biased allocation:

| Column | Description |
|---|---|
| Final_Stock | Units to stock after LP + LRM rounding |
| Revenue | Revenue per product |
| TOTAL Revenue | Total revenue summary row |

## Run

From the workspace root:

```bash
uv run inventory-optimization
# or
uv run python -m inventory_optimization
```

## Package structure

```
src/inventory_optimization/
├── __init__.py    # exposes main()
├── __main__.py    # enables python -m
└── solver.py      # solve_inventory_allocation, solve_biased_allocation, run
```
