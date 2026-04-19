# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **Spec-kit integration**: adopted the [GitHub Spec Kit](https://github.com/speckit) structure for spec-driven development. Feature specs now live under `specs/` (tooling config under `.specify/`).
- **`specs/001-sustainability-metrics/`**: migrated and reformatted the sustainability metrics feature spec to the spec-kit v0.7.3 template — prioritized user stories with Given/When/Then acceptance scenarios, FR-coded functional requirements, measurable success criteria, and a task list organized by user story with parallel-execution markers.
- **`.specify/`**: spec-kit project config, templates, git extension scripts, and workflow definitions for spec-driven development.
- **`.agent/skills/`**: Claude Code skill definitions for all `speckit.*` commands (`specify`, `plan`, `tasks`, `implement`, `clarify`, `checklist`, `analyze`, git integration skills).
- **`AGENTS.md`**: project context guide for AI coding agents — covers stack, structure, path conventions, run commands, spec-driven workflow, and test coverage.
- **Carbon Cap Early Exit**: the Carbon-Efficient inventory scenario now skips the GLOP solver execution and inherits the LP Max Revenue result if it already satisfies the emissions target reduction.

### Fixed

- **Config input validation**: added strict numeric bounds checking and exception chaining (`raise ... from e`) in both `routing-optimization` and `inventory-optimization` solvers for robust `sustainability_config.json` loading.


### Added

- **Period-Based Batch Optimization**: inventory solver now supports `month` and `week` aggregation periods via a new `--period` CLI flag and `period` parameter on `solve_inventory_allocation`, `solve_biased_allocation`, and `preprocess_input`.
- **Input Auto-Detection** (`_INPUT_DEFAULTS`): `run()` automatically applies file-specific defaults for period and stock limit — `inventory_s001_north_may_2022.csv` defaults to `period=week`, `stock_limit=100`; all other inputs default to `period=month`, `stock_limit=500`.
- **`period` tool parameter**: `run_inventory_solver` tool in `query.py` now exposes a `period` enum (`month`/`week`) so the AI assistant can request specific aggregation granularity.
- **Pipeline `inventory_limit` and `inventory_period` inputs**: GitHub Actions `workflow_dispatch` now accepts `inventory_limit` (default `500`) and `inventory_period` (default `month`) to control inventory optimization behaviour without editing the workflow file.
- **Capacity validation** in `query.py`: tool input `capacity` is validated to be a positive integer before reaching the solver, returning a descriptive error to the model if invalid.

### Changed

- **Default inventory input** changed from `inventory_s001_north_may_2022.csv` to `retail_forecast_with_original_values.csv` (forecast pipeline output), making `uv run inventory-optimization` run monthly batch optimization over the full forecast horizon out of the box.
- **Model ID** updated from `claude-opus-4-6` to `claude-opus-4-7` in `query.py`.
- **`query.py` system prompt** updated to accurately describe the default input, period, and capacity auto-detection behaviour.
- **All READMEs** updated to reflect period-based optimization, auto-detection defaults, corrected run examples, and the chronological sort validation in demand forecasting.

### Fixed

- **Path traversal** in `query.py` `read_data_file` tool: filename is resolved with `.resolve()` and validated against `DATA_DIR` to prevent directory escape.
- **`ImportError`** in `query.py`: corrected stale import `OUTPUT_CSV` → `DEFAULT_OUTPUT_CSV` from routing solver.
- **`Path` re-export** removed from `inventory_optimization/__init__.py` (was unintentionally exposing `pathlib.Path` as a public API symbol).
- **`zip(strict=False)` → `zip(strict=True)`** in proportional allocation remainder calculation to surface length mismatches immediately.
- **`total_stock_limit <= 0` validation** added to `solve_inventory_allocation`.
- **`total_demand <= 0` guard** added to both `solve_inventory_allocation` and `solve_biased_allocation` to prevent division-by-zero.
- **`solve_inventory_allocation`** now raises `RuntimeError` on solver creation failure instead of returning `None` silently.
- **`lp_results`** initialised to `[np.nan] * num_products` so a non-OPTIMAL LP solve produces `NaN` columns instead of a length-mismatch `ValueError`.
- **`solve_biased_allocation`** now raises `RuntimeError` on non-OPTIMAL solve and on solver creation failure; removed dead `if status == OPTIMAL` guard that could never be reached.
- **`leftover` clamped** with `max(0, ...)` in both solvers to prevent negative slice indices corrupting the Largest Remainder distribution.
- **Carbon-Efficient columns** (`Carbon_Efficient_Stock/Revenue/CO2`) initialised to `NaN` before the `if ce_solver:` block so they always exist on the returned DataFrame.
- **Route bounds/length checks** added to `calculate_total_distance` in routing solver.
- **`RuntimeError`** raised when all routing matrix files are missing instead of writing an empty CSV.
- **Date sort validation** added to demand forecasting `run()`: raises `ValueError` if input data is not chronologically ordered before the train/test split.
- **`max_tokens`** in `query.py` made configurable via `CLAUDE_MAX_TOKENS` environment variable (default `4096`).
- **Filters `TypeError`** fixed: `solve_inventory_allocation` and `solve_biased_allocation` now accept `store`, `region`, and `date_filter` kwargs and forward them to `preprocess_input` when loading from a file path.
- **`test_nearest_neighbor`** assertion made robust: replaced exact route equality check with `route[0] == 0` and full-node-coverage check.

---

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
- **Cross-Module Pipeline Integration**: the GitHub Actions workflow now automatically pipes the `demand-forecasting` output into the `inventory-optimization` module. The inventory step now performs a **monthly batch optimization** over the entire horizon, applying a baseline capacity of **500 units per month**.
- **Inventory Solver Refactoring**:
  - Redesigned the core execution loop to support multi-period sequential optimization.
  - Decoupled `total_stock_limit` from the core logic; it is now a globally configurable parameter available via CLI (`--limit`).
  - Synchronized and standardized CLI arguments (`--input`, `--limit`, `--store`, `--region`, `--date`) across all module and package entry points.
- **Reporting Improvements**:
  - Terminal summary output now prioritizes **Proportional Allocation** metrics (Revenue and CO2) for Scenario 1.
  - Updated the AI query tool to ensure consistency between natural language summaries and CLI outputs.
- **Pipeline Triggers**: updated GitHub Actions workflow to only run automatically on pull requests targeting the `main` branch.
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
