import pandas as pd
import numpy as np

# Load the distance matrix
df1 = pd.read_csv('distance_matrix_1.csv', index_col=0)
dist_matrix1 = df1.values

df2 = pd.read_csv('distance_matrix_2.csv', index_col=0)
dist_matrix2 = df2.values

print(f"Distance Matrix 1: \n{dist_matrix1}")
print(f"Distance Matrix 2: \n{dist_matrix2}")

# Calculates the total distance of a route returning to the start
def calculate_total_distance(route, matrix):
    dist = 0
    for i in range(len(route) - 1):
        dist += matrix[route[i], route[i+1]]
    dist += matrix[route[-1], route[0]]
    return dist

# Generates an initial route using the Nearest Neighbor heuristic
def nearest_neighbor(matrix):
    num_nodes = matrix.shape[0]
    visited = [False] * num_nodes
    route = [0] # Start at Warehouse
    visited[0] = True
    
    for _ in range(num_nodes - 1):
        current = route[-1]
        next_node = -1
        min_dist = float('inf')
        for j in range(num_nodes):
            if not visited[j] and matrix[current, j] < min_dist:
                min_dist = matrix[current, j]
                next_node = j
        route.append(next_node)
        visited[next_node] = True
    return route

# Refines the route using the 2-opt local search algorithm
def two_opt_optimization(route, matrix):
    best_route = route
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route)):
                if j - i == 1: continue # Skip adjacent edges
                
                # Create a new route by reversing the segment between i and j
                new_route = route[:]
                new_route[i:j] = route[i:j][::-1]
                
                if calculate_total_distance(new_route, matrix) < calculate_total_distance(best_route, matrix):
                    best_route = new_route
                    improved = True
        route = best_route
    return best_route

# Get Initial Route
initial_route1 = nearest_neighbor(dist_matrix1)
initial_route2 = nearest_neighbor(dist_matrix2)

# Optimize with 2-opt
optimized_route1 = two_opt_optimization(initial_route1, dist_matrix1)
total_dist1 = calculate_total_distance(optimized_route1, dist_matrix1)

optimized_route2 = two_opt_optimization(initial_route2, dist_matrix2)
total_dist2 = calculate_total_distance(optimized_route2, dist_matrix2)

# Format the sequence to show the return to warehouse
final_sequence1 = optimized_route1 + [0]
final_sequence2 = optimized_route2 + [0]

print(f"Optimized Sequence 1: {final_sequence1}")
print(f"Total Distance 1: {total_dist1}")

print(f"Optimized Sequence 2: {final_sequence2}")
print(f"Total Distance 2: {total_dist2}")