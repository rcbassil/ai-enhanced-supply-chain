# demand-forecasting

XGBoost regressor that predicts retail store demand (units sold) from historical inventory data.

## How it works

1. Loads `data/retail_store_inventory.csv` from the workspace root
2. Extracts temporal features from `Date` (year, month, day, day-of-week)
3. Encodes categorical columns natively via XGBoost's `enable_categorical`
4. Trains on 80% of the data using a chronological split (no shuffle)
5. Evaluates with MAE and RMSE on the held-out 20% test set
6. Writes predictions to `data/retail_forecast_with_original_values.csv`
7. Plots actual vs. predicted demand and a top-15 feature importance chart

## Input

`data/retail_store_inventory.csv` — expected columns:

| Column | Type |
|---|---|
| Date | date string |
| Store ID | categorical |
| Product ID | categorical |
| Category | categorical |
| Region | categorical |
| Inventory Level | numeric (feature) |
| Units Sold | numeric (target) |
| Units Ordered | numeric (feature) |
| Price | numeric (feature) |
| Discount | numeric (feature) |
| Weather Condition | categorical |
| Holiday/Promotion | numeric (feature) |
| Competitor Pricing | numeric (feature) |
| Seasonality | categorical |

## Output

- `data/retail_forecast_with_original_values.csv` — original data with an added `Predicted_Demand_Forecast` column
- Two matplotlib charts (actual vs. predicted, feature importance)

## Run

From the workspace root:

```bash
uv run demand-forecasting
# or
uv run python -m demand_forecasting
```

## Package structure

```
src/demand_forecasting/
├── __init__.py    # exposes main()
├── __main__.py    # enables python -m
└── model.py       # load_data, build_model, evaluate, plot_results, run
```
