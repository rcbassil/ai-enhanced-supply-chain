import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parents[3] / "data"
DEFAULT_OUTPUT_CSV = DATA_DIR / "routing_optimization_results.csv"

DEFAULT_DISTANCE_MATRICES = [
    DATA_DIR / "distance_matrix_1.csv",
    DATA_DIR / "distance_matrix_2.csv",
]


def load_sustainability_config() -> dict:
    config_path = DATA_DIR / "sustainability_config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {"shipping_emission_factor": 0.85}


def calculate_emissions(distance: float, factor: float) -> float:
    """Calculate kg CO2 based on distance (km) and emission factor (kg/km)."""
    return distance * factor


def load_matrix(path: Path) -> np.ndarray:
    return pd.read_csv(path, index_col=0).values


def calculate_total_distance(route: list[int], matrix: np.ndarray) -> float:
    if len(route) < 2:
        raise ValueError(f"Route must have at least 2 nodes, got {len(route)}")
    n = matrix.shape[0]
    invalid = [idx for idx in route if idx < 0 or idx >= n]
    if invalid:
        raise ValueError(f"Route contains out-of-bounds indices for {n}x{n} matrix: {invalid}")
    dist = sum(matrix[route[i], route[i + 1]] for i in range(len(route) - 1))
    dist += matrix[route[-1], route[0]]
    return dist


def nearest_neighbor(matrix: np.ndarray) -> list[int]:
    num_nodes = matrix.shape[0]
    visited = [False] * num_nodes
    route = [0]  # Start at warehouse
    visited[0] = True

    for _ in range(num_nodes - 1):
        current = route[-1]
        next_node = min(
            (j for j in range(num_nodes) if not visited[j]),
            key=lambda j: matrix[current, j],
        )
        route.append(next_node)
        visited[next_node] = True

    return route


def two_opt(route: list[int], matrix: np.ndarray) -> list[int]:
    best_route = route
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route)):
                if j - i == 1:
                    continue
                candidate = best_route[:]
                candidate[i:j] = best_route[i:j][::-1]
                if calculate_total_distance(candidate, matrix) < calculate_total_distance(
                    best_route, matrix
                ):
                    best_route = candidate
                    improved = True
    return best_route


def optimize(matrix: np.ndarray) -> tuple[list[int], float]:
    initial_route = nearest_neighbor(matrix)
    optimized_route = two_opt(initial_route, matrix)
    total_distance = calculate_total_distance(optimized_route, matrix)
    return optimized_route + [0], total_distance


def run(
    matrix_paths: list[Path] = DEFAULT_DISTANCE_MATRICES,
    output_path: Path = DEFAULT_OUTPUT_CSV,
) -> None:
    config = load_sustainability_config()
    factor = config.get("shipping_emission_factor", 0.85)

    rows = []
    for i, path in enumerate(matrix_paths, start=1):
        if not path.exists():
            print(f"Warning: File {path} not found. Skipping.")
            continue
        matrix = load_matrix(path)
        sequence, total_distance = optimize(matrix)
        total_emissions = calculate_emissions(total_distance, factor)

        print(f"\nDistance Matrix {i} ({path.name}): \n\n{matrix}")
        print(f"\nOptimized Sequence {i}: {sequence}")
        print(f"\nTotal Distance {i}: {total_distance:.2f} km")
        print(f"Total Carbon Footprint {i}: {total_emissions:.2f} kg CO2")

        rows.append(
            {
                "scenario": i,
                "filename": path.name,
                "sequence": sequence,
                "total_distance": total_distance,
                "total_emissions_kg": total_emissions,
            }
        )

    if not rows:
        raise RuntimeError("No valid distance matrix files found. Cannot produce routing results.")

    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"\nResults saved to '{output_path.name}'.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Routing Optimization Pipeline")
    parser.add_argument(
        "--inputs",
        type=str,
        nargs="+",
        default=[str(p) for p in DEFAULT_DISTANCE_MATRICES],
        help="Path(s) to distance matrix CSV files",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT_CSV),
        help="Path to save routing results CSV",
    )
    args = parser.parse_args()

    run([Path(p) for p in args.inputs], Path(args.output))
