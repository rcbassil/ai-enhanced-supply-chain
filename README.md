# AI-Enhanced Supply Chain

A Python toolkit applying machine learning and combinatorial optimization to supply chain problems. Currently covers two modules: demand forecasting with XGBoost and delivery route optimization with Nearest Neighbor + 2-opt.

## Modules

### Demand Forecasting (`demand-forecasting/`)

Uses an XGBoost regressor to predict retail store demand (units sold) from historical inventory data.

**Input:** `retail_store_inventory.csv` — columns include `Date`, `Store ID`, `Product ID`, `Category`, `Region`, `Weather Condition`, `Seasonality`, `Units Sold`, and `Demand Forecast`.

**How it works:**
- Extracts temporal features from `Date` (year, month, day, day-of-week)
- Encodes categorical columns natively via XGBoost's `enable_categorical`
- Trains an 80/20 chronological split (no shuffle) to respect time ordering
- Evaluates with MAE and RMSE on the held-out test set
- Appends `Predicted_Demand_Forecast` to the original data and saves it to `retail_forecast_with_original_values.csv`
- Plots actual vs. predicted demand (first 100 validation points) and a top-15 feature importance chart

**Run:**
```bash
cd demand-forecasting
python xgBoost.py
```

**Output:** `retail_forecast_with_original_values.csv` + two matplotlib charts.

---

### Routing Optimization (`routing-optmization/`)

Solves the Travelling Salesman Problem (TSP) for delivery routes using a Nearest Neighbor construction heuristic followed by 2-opt local search refinement.

**Input:** `distance_matrix_1.csv` and `distance_matrix_2.csv` — square distance matrices where node `0` represents the warehouse.

**How it works:**
1. **Nearest Neighbor** — greedily builds an initial route by always visiting the closest unvisited node.
2. **2-opt** — iteratively reverses sub-segments of the route whenever doing so reduces total distance, until no improvement is found.

**Run:**
```bash
cd routing-optmization
python nearestneighbor-2opt.py
```

**Output:** Optimized route sequence and total distance printed to stdout for each distance matrix.

---

## Requirements

- Python 3.12+
- `pandas`, `numpy`
- `xgboost`
- `scikit-learn`
- `matplotlib`

Install dependencies (example with pip):
```bash
pip install pandas numpy xgboost scikit-learn matplotlib
```

## Project Structure

```
ai-enhanced-supply-chain/
├── demand-forecasting/
│   ├── xgBoost.py                          # XGBoost demand forecasting model
│   └── retail_store_inventory.csv          # Input dataset
├── routing-optmization/
│   ├── nearestneighbor-2opt.py             # Nearest Neighbor + 2-opt TSP solver
│   ├── distance_matrix_1.csv               # Distance matrix scenario 1
│   └── distance_matrix_2.csv               # Distance matrix scenario 2
├── main.py
└── pyproject.toml
```
