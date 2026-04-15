# routing-optimization

TSP solver for delivery route optimization using a Nearest Neighbor construction heuristic followed by 2-opt local search refinement.

## How it works

1. Loads distance matrices from `data/` at the workspace root
2. Builds an initial route with the **Nearest Neighbor** heuristic — greedily visits the closest unvisited node, starting from the warehouse (node `0`)
3. Refines the route with **2-opt** — iteratively reverses sub-segments until no improvement is found
4. Prints the optimized sequence and total distance for each scenario

## Input

`data/distance_matrix_1.csv` and `data/distance_matrix_2.csv` — square matrices where:
- Row/column indices are node IDs
- Node `0` is the warehouse
- Cell values are distances between nodes

## Output

Optimized route sequence and total distance printed to stdout for each distance matrix.

## Run

From the workspace root:

```bash
uv run routing-optimization
# or
uv run python -m routing_optimization
```

## Package structure

```
src/routing_optimization/
├── __init__.py    # exposes main()
├── __main__.py    # enables python -m
└── solver.py      # load_matrix, nearest_neighbor, two_opt, optimize, run
```
