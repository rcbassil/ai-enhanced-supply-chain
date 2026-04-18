# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **Automated Testing Suite**: implemented a comprehensive test suite using `pytest`.
  - `tests/test_demand_forecasting.py`: validation for data preprocessing and XGBoost model building.
  - `tests/test_inventory_optimization.py`: tests for allocation strategies and sustainability configuration.
  - `tests/test_routing_optimization.py`: verification of TSP heuristics and emission calculations.
- **Test Configuration**: added `pytest.ini` at the workspace root to manage member paths and suppress `ortools` deprecation warnings.
- **Development Dependencies**: added `pytest`, `pytest-mock`, `matplotlib`, `pre-commit`, and `ruff` to `pyproject.toml`.
- **Pre-commit Integration**: added `.pre-commit-config.yaml` with hooks for linting, formatting, and automated testing.
- **Ruff Configuration**: integrated `ruff` as the primary linter and formatter, with custom rules in `pyproject.toml`.

### Changed

- **Pipeline Triggers**: updated GitHub Actions workflow to only run automatically on pull requests targeting the `main` branch. Removed automatic runs on every `push`.
- **Dataset Path Decoupling**: refactored all pipeline modules (`demand-forecasting`, `inventory-optimization`, `routing-optimization`) to remove hardcoded file paths. Input and output paths are now dynamic and configurable.
- **Demand Forecasting**: removed `Demand Forecast` column from `data/retail_store_inventory.csv` and from model training. The dataset now includes richer features — `Inventory Level`, `Units Ordered`, `Price`, `Discount`, `Holiday/Promotion`, and `Competitor Pricing` — replacing the former forecast column.

### Added

- **Command-Line Interface (CLI) Support**: all optimization pipelines now support standard command-line arguments (`--input`, `--output`) via `argparse`.
  - Packages can be executed with custom paths: `uv run demand-forecasting --input path/to/data.csv`.
  - Packages also support `python -m <package> --input ...` syntax with arguments handled in `__init__.py`.
- **Dynamic GitHub Pipeline**: updated `.github/workflows/pipeline.yml` to support manual execution with custom dataset paths.
  - Added `workflow_dispatch` with inputs for custom forecast, inventory, and routing data.
  - Automatic fallback to default paths for triggered runs (push/pull request).
- **Sustainability Metrics Integration**: introduced carbon footprint tracking across the supply chain.
  - New `data/sustainability_config.json` for managing global emission factors (shipping and storage) and reduction targets.
  - **Routing Carbon Tracking**: routing solver now calculates kg CO2 emissions based on optimized distance and persists results to `data/routing_optimization_results.csv`.
  - **Carbon-Efficient Inventory Allocation**: new optimization scenario that maximizes revenue while capping total storage emissions at a threshold (configurable, default 85% of LP Max emissions).
  - Enhanced `query.py` with expanded toolset: added `run_routing_solver` and updated `run_inventory_solver` to return comprehensive carbon data to the AI assistant.
- **Natural language query interface** (`query.py`): interactive CLI powered by Claude Opus 4.6 (Anthropic SDK) that lets users ask questions about supply chain data and optimization results in plain English.
  - Four tools available to Claude at runtime: `list_data_files`, `read_data_file`, `run_inventory_solver`, `run_routing_solver`.
  - Streaming responses with adaptive thinking enabled.
  - Multi-turn conversation with `clear` and `exit` commands.
- `anthropic>=0.50.0` added as a root workspace dependency in `pyproject.toml`.

### Added (prior)

- **Inventory Optimization module** implemented with two scenarios:
  - Scenario 1 (`solve_inventory_allocation`): LP revenue maximisation (OR-Tools GLOP) vs Proportional Allocation (Largest Remainder Method) — output to `data/inventory_optimization_results_scenario_1.csv`.
  - Scenario 2 (`solve_biased_allocation`): biased LP allocation guaranteeing each product at least 80% of its fair share — output to `data/inventory_optimization_results_scenario_2.csv`.
- Total revenue summary rows appended to both output CSVs.
- `data/inventory_s001_north_may_2022.csv` — inventory dataset for store S001, North region, May 2022.
- `ortools` added as a dependency to `inventory-optimization/pyproject.toml` and `routing-optimization/pyproject.toml`.
- `inventory-optimization` workspace member with `src/inventory_optimization/` package layout (`__init__.py`, `__main__.py`, `solver.py`).
- `routing-optimization` module refactored into proper package: `solver.py` with typed functions (`load_matrix`, `nearest_neighbor`, `two_opt`, `optimize`, `run`), `__init__.py`, and `__main__.py`.
- `demand-forecasting` module refactored into proper package: `model.py` with typed functions (`load_data`, `build_model`, `evaluate`, `plot_results`, `run`), `__init__.py`, and `__main__.py`.
- Runtime dependencies declared in each module's `pyproject.toml` (`demand-forecasting`: pandas, numpy, xgboost, scikit-learn, matplotlib; `routing-optimization`: pandas, numpy, ortools).
- Fixed hardcoded CSV paths — now resolved relative to `__file__` via `pathlib.Path`.
- Introduced shared `data/` directory at the workspace root; all CSV inputs and outputs centralised there.
- Moved `retail_store_inventory.csv` from `demand-forecasting/` to `data/`.
- Moved `distance_matrix_1.csv` and `distance_matrix_2.csv` from `routing-optimization/` to `data/`.
- `demand-forecasting` writes forecast output to `data/retail_forecast_with_original_values.csv` for use as input to `inventory-optimization`.
- All modules runnable via `uv run <module-name>` or `uv run python -m <package>` from the workspace root.
- GitHub Actions pipeline (`.github/workflows/pipeline.yml`) running modules sequentially: demand-forecasting → inventory-optimization → routing-optimization.

### Changed

- Renamed `routing-optmization/` → `routing-optimization/` (fixed typo).
- Removed top-level scripts `xgBoost.py`, `xgboost_model.py`, `nearestneighbor_2opt.py`, and `linear_programming.py` — logic moved into `src/` packages.
- Root `pyproject.toml` workspace members updated to include all three modules.
- `demand-forecasting` plots saved to `data/` as PNGs instead of calling `plt.show()`.

## [0.1.0] - 2026-04-15

### Added

- **Demand Forecasting module** (`demand-forecasting/xgBoost.py`): XGBoost regressor that predicts retail store demand (units sold) from `retail_store_inventory.csv`. Includes temporal feature engineering, native categorical encoding, chronological train/test split, MAE/RMSE evaluation, CSV export of predictions, and matplotlib visualizations (actual vs. predicted and feature importance).
- **Routing Optimization module** (`routing-optmization/nearestneighbor-2opt.py`): TSP solver using Nearest Neighbor construction heuristic followed by 2-opt local search. Processes two distance matrix scenarios and prints optimized routes with total distances.
- `pyproject.toml` project configuration targeting Python 3.12+.
