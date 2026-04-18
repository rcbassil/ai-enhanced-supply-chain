import numpy as np
from routing_optimization.solver import (
    calculate_emissions,
    calculate_total_distance,
    nearest_neighbor,
    optimize,
)


def test_calculate_total_distance():
    matrix = np.array([[0, 10, 20], [10, 0, 15], [20, 15, 0]])
    route = [0, 1, 2]
    # 0->1 (10) + 1->2 (15) + 2->0 (20) = 45
    assert calculate_total_distance(route, matrix) == 45


def test_nearest_neighbor():
    matrix = np.array([[0, 5, 10], [5, 0, 8], [10, 8, 0]])
    route = nearest_neighbor(matrix)
    assert route == [0, 1, 2]


def test_optimize():
    matrix = np.array([[0, 10, 20], [10, 0, 5], [20, 5, 0]])
    sequence, distance = optimize(matrix)
    # Expected: 0 -> 1 -> 2 -> 0 => 10 + 5 + 20 = 35
    assert sequence == [0, 1, 2, 0]
    assert distance == 35


def test_calculate_emissions():
    assert calculate_emissions(100, 0.5) == 50.0
    assert calculate_emissions(200, 0.85) == 170.0
