# Tasks: Sustainability Metrics Integration

This file tracks the implementation of the sustainability feature. Do not move to a new task until the previous one is verified.

## Phase 1: Configuration & Data
- [x] **Task 1**: Create the global configuration file.
  - Create `data/sustainability_config.json` with base emission factors.
  - *Verification*: Verify the file exists and is valid JSON.

## Phase 2: Routing Optimization
- [x] **Task 2**: Add carbon tracking to the routing solver.
  - Modify `routing-optimization/src/routing_optimization/solver.py` to load config and calculate emissions per km.
  - Print total CO2 in the console output.
  - *Verification*: Run `uv run routing-optimization` and check for "Total Carbon Footprint" in logs.

- [x] **Task 3**: Persist routing emissions data.
  - Update the output CSV logic to save `total_emissions_kg`.
  - *Verification*: Open `data/routing_optimization_results.csv` and ensure the column is present.

## Phase 3: Inventory Optimization
- [x] **Task 4**: Implement storage carbon tracking in the inventory solver.
  - Modify `inventory-optimization/src/inventory_optimization/solver.py` to calculate storage emissions.
  - *Verification*: Run the solver and ensure no regressions in current revenue calculations.

- [x] **Task 5**: Implement the "Carbon-Aware" allocation scenario.
  - Add a new solver function that caps emissions at 85% of the "LP Max Revenue" level.
  - Compare results between Max Revenue and Carbon-Aware scenarios.
  - *Verification*: Compare `inventory_optimization_results_scenario_1.csv` and verify the new scenario results are saved.

## Phase 4: Natural Language Interface
- [x] **Task 6**: Expose sustainability metrics to `query.py`.
  - Update the tool definitions in `query.py` to include CO2 data in tool responses.
  - Update Claude's system instructions to explain how to interpret carbon metrics.
  - *Verification*: Run `uv run python query.py` and ask: "What is the CO2 footprint for distance matrix 1?"

## Phase 5: Final Review
- [x] **Task 7**: Run the full pipeline.
  - Run all three modules in sequence.
  - *Verification*: Ensure all data flows correctly from demand -> inventory -> routing results with no errors.
