# routing-optimization

TSP solver for delivery route optimization using a Nearest Neighbor construction heuristic followed by 2-opt local search refinement. It includes **Sustainability Metrics** to track the carbon footprint of delivery operations.

## How it works

1. Loads distance matrices from `data/` at the workspace root.
2. Builds an initial route with the **Nearest Neighbor** heuristic — greedily visits the closest unvisited node, starting from the warehouse (node `0`).
3. Refines the route with **2-opt** — iteratively reverses sub-segments until no improvement is found.
4. Calculates **Total Carbon Footprint** (kg CO2) per route based on travel distance and vehicle emission factors.

## Input

`data/distance_matrix_1.csv` and `data/distance_matrix_2.csv` — square matrices where:
- Row/column indices representing location IDs.
- Node `0` is the warehouse.
- Cell values are distances (km) between nodes.

## Output

- Optimized route sequence for each scenario.
- Total distance (km) and Total Carbon Footprint (kg CO2) printed to stdout.
- **`data/routing_optimization_results.csv`**: Contains summarized metrics for each matrix scenario.

## Run

From the workspace root:

```bash
# Default: runs both distance matrices
uv run routing-optimization

# Custom matrix files
uv run routing-optimization --inputs data/distance_matrix_1.csv data/distance_matrix_2.csv
```

## Package structure

```
src/routing_optimization/
├── __init__.py    # exposes main()
├── __main__.py    # enables python -m
└── solver.py      # load_matrix, nearest_neighbor, two_opt, optimize, run
```
