# Plan: Sustainability Metrics Integration

This plan outlines the technical steps to implement sustainability tracking and optimization as defined in [spec.md](./spec.md).

## 1. Data Schema & Configuration
We will introduce a central configuration file to store emission factors. This ensures the model is adaptable to different transport types or storage facilities.

- **Target File**: `data/sustainability_config.json`
- **Fields**:
  - `shipping_emission_factor`: kg CO2 per kilometer (default: 0.85)
  - `storage_emission_factor`: kg CO2 per unit per month (default: 0.12)
  - `emissions_target_reduction`: % reduction for carbon-aware scenarios (default: 0.15)

## 2. Shared Utilities
Create a shared utility or helper within each module to load these configs. Since the project uses a workspace structure, we will put the loader logic in a reusable way or simply implement it in each module's `solver.py` for now to minimize cross-module dependencies.

## 3. Routing Optimization Updates
Modify `routing-optimization/src/routing_optimization/solver.py`:
- **New Logic**: Implement `calculate_emissions(distance: float, factor: float) -> float`.
- **Output**:
  - Print `Total Carbon Footprint (kg CO2)` to stdout.
  - Append `total_emissions_kg` to `routing_optimization_results.csv`.

## 4. Inventory Optimization Updates
Modify `inventory-optimization/src/inventory_optimization/solver.py`:
- **New Metric**: Calculate total storage carbon cost based on allocated stock.
- **New Scenario (Carbon-Aware Allocation)**:
  - Implement a three-way comparison in `solve_inventory_allocation`:
    1. LP Revenue Max
    2. Proportional
    3. **Carbon-Efficient**: LP that maximizes revenue while capping total CO2 emissions at a threshold (e.g., 90% of the LP Max scenario's emissions).
- **Output**: Save emission metrics to the results CSVs.

## 5. Natural Language Interface (`query.py`)
Enhance the interactive query tool:
- Add a new tool `get_sustainability_metrics` or update existing tools to return carbon data.
- Update Claude's system prompt in `query.py` to handle sustainability-related questions (e.g., "What is the greenest route?").

## 6. Verification
- Run `uv run routing-optimization` and verify CO2 output.
- Run `uv run inventory-optimization` and verify the new scenario results.
- Ask `query.py` "Which product has the highest carbon footprint per unit?"
