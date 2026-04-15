# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `inventory-optimization` workspace member (scaffold) — placeholder for inventory optimization algorithms.

### Changed
- Renamed `routing-optmization/` → `route-optimization/` (fixed typo, aligned with module naming convention).
- Added uv workspace scaffolding (`pyproject.toml`, `src/<package>/__init__.py`) to `route-optimization` and `inventory-optimization` to match the `demand-forecasting` module structure.
- Root `pyproject.toml` workspace members updated to include all three modules.

## [0.1.0] - 2026-04-15

### Added

- **Demand Forecasting module** (`demand-forecasting/xgBoost.py`): XGBoost regressor that predicts retail store demand (units sold) from `retail_store_inventory.csv`. Includes temporal feature engineering, native categorical encoding, chronological train/test split, MAE/RMSE evaluation, CSV export of predictions, and matplotlib visualizations (actual vs. predicted and feature importance).
- **Routing Optimization module** (`routing-optmization/nearestneighbor-2opt.py`): TSP solver using Nearest Neighbor construction heuristic followed by 2-opt local search. Processes two distance matrix scenarios and prints optimized routes with total distances.
- `pyproject.toml` project configuration targeting Python 3.12+.
