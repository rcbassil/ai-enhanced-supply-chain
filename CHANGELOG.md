# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0] - 2026-04-15

### Added

- **Demand Forecasting module** (`demand-forecasting/xgBoost.py`): XGBoost regressor that predicts retail store demand (units sold) from `retail_store_inventory.csv`. Includes temporal feature engineering, native categorical encoding, chronological train/test split, MAE/RMSE evaluation, CSV export of predictions, and matplotlib visualizations (actual vs. predicted and feature importance).
- **Routing Optimization module** (`routing-optmization/nearestneighbor-2opt.py`): TSP solver using Nearest Neighbor construction heuristic followed by 2-opt local search. Processes two distance matrix scenarios and prints optimized routes with total distances.
- `pyproject.toml` project configuration targeting Python 3.12+.
