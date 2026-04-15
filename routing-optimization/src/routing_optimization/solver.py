import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parents[3] / "data"  # workspace root / data
OUTPUT_CSV = DATA_DIR / "routing_optimization_results.csv"

DISTANCE_MATRICES = [
    DATA_DIR / "distance_matrix_1.csv",
    DATA_DIR / "distance_matrix_2.csv",
]


def load_matrix(path: Path) -> np.ndarray:
    return pd.read_csv(path, index_col=0).values


def calculate_total_distance(route: list[int], matrix: np.ndarray) -> float:
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
                if calculate_total_distance(candidate, matrix) < calculate_total_distance(best_route, matrix):
                    best_route = candidate
                    improved = True
    return best_route


def optimize(matrix: np.ndarray) -> tuple[list[int], float]:
    initial_route = nearest_neighbor(matrix)
    optimized_route = two_opt(initial_route, matrix)
    total_distance = calculate_total_distance(optimized_route, matrix)
    return optimized_route + [0], total_distance


def run() -> None:
    rows = []
    for i, path in enumerate(DISTANCE_MATRICES, start=1):
        matrix = load_matrix(path)
        sequence, total_distance = optimize(matrix)
        print(f"\nDistance Matrix {i}: \n\n{matrix}")
        print(f"\nOptimized Sequence {i}: {sequence}")
        print(f"\nTotal Distance {i}: {total_distance}")
        rows.append({"scenario": i, "sequence": sequence, "total_distance": total_distance})

    pd.DataFrame(rows).to_csv(OUTPUT_CSV, index=False)
    print(f"\nResults saved to '{OUTPUT_CSV.name}'.")


if __name__ == "__main__":
    run()
