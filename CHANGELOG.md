# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `inventory-optimization` workspace member with `src/inventory_optimization/` package layout (`__init__.py`, `__main__.py`, `solver.py` placeholder).
- `routing-optimization` module refactored into proper package: `solver.py` with typed functions (`load_matrix`, `nearest_neighbor`, `two_opt`, `optimize`, `run`), `__init__.py`, and `__main__.py`.
- `demand-forecasting` module refactored into proper package: `model.py` with typed functions (`load_data`, `build_model`, `evaluate`, `plot_results`, `run`), `__init__.py`, and `__main__.py`.
- Runtime dependencies declared in each module's `pyproject.toml` (`demand-forecasting`: pandas, numpy, xgboost, scikit-learn, matplotlib; `routing-optimization`: pandas, numpy).
- Fixed hardcoded CSV paths — now resolved relative to `__file__` via `pathlib.Path`.
- Introduced shared `data/` directory at the workspace root; all CSV inputs and outputs centralised there.
- Moved `retail_store_inventory.csv` from `demand-forecasting/` to `data/`.
- Moved `distance_matrix_1.csv` and `distance_matrix_2.csv` from `routing-optimization/` to `data/`.
- `demand-forecasting` writes forecast output to `data/retail_forecast_with_original_values.csv` for use as input to `inventory-optimization`.
- All modules runnable via `uv run <module-name>` or `uv run python -m <package>` from the workspace root.

### Changed
- Renamed `routing-optmization/` → `routing-optimization/` (fixed typo).
- Removed top-level scripts `xgBoost.py`, `xgboost_model.py`, `nearestneighbor_2opt.py`, and `linear_programming.py` — logic moved into `src/` packages.
- Root `pyproject.toml` workspace members updated to include all three modules.

## [0.1.0] - 2026-04-15

### Added
- **Demand Forecasting module** (`demand-forecasting/xgBoost.py`): XGBoost regressor that predicts retail store demand (units sold) from `retail_store_inventory.csv`. Includes temporal feature engineering, native categorical encoding, chronological train/test split, MAE/RMSE evaluation, CSV export of predictions, and matplotlib visualizations (actual vs. predicted and feature importance).
- **Routing Optimization module** (`routing-optmization/nearestneighbor-2opt.py`): TSP solver using Nearest Neighbor construction heuristic followed by 2-opt local search. Processes two distance matrix scenarios and prints optimized routes with total distances.
- `pyproject.toml` project configuration targeting Python 3.12+.
