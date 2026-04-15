import pandas as pd
import numpy as np
from ortools.linear_solver import pywraplp
from pathlib import Path

DATA_DIR = Path(__file__).parents[3] / "data"  # workspace root / data
INPUT_CSV = DATA_DIR / "inventory_s001_north_may_2022.csv"
OUTPUT_CSV = DATA_DIR / "inventory_optimization_results_scenario_1.csv"

def solve_inventory_allocation(file_path):
    # Load the dataset
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()  # Clean column names
    
    total_stock_limit = 100
    products = df['Product'].tolist()
    prices = df['Price'].tolist()
    demands = df['Predicted Demand Forecast'].tolist()
    num_products = len(products)

    # Revenue Maximization (Linear Programming via OR-Tools)
    solver = pywraplp.Solver.CreateSolver('GLOP')
    if not solver:
        return
    
    # Variables: x[i] is the number of units of product i to stock
    x = [solver.NumVar(0, demands[i], f'x_{i}') for i in range(num_products)]
    
    # Constraint: Total stock must not exceed 100
    solver.Add(sum(x) <= total_stock_limit)
    
    # Objective: Maximize total revenue
    objective = solver.Objective()
    for i in range(num_products):
        objective.SetCoefficient(x[i], prices[i])
    objective.SetMaximization()
    
    status = solver.Solve()
    
    lp_results = []
    if status == pywraplp.Solver.OPTIMAL:
        for i in range(num_products):
            lp_results.append(round(x[i].solution_value(), 2))
    
    # Proportional Allocation (Largest Remainder Method)
    total_demand = sum(demands)
    # Calculate exact quotas
    exact_quotas = [(d / total_demand) * total_stock_limit for d in demands]
    
    # Integer parts
    integer_parts = [int(np.floor(q)) for q in exact_quotas]
    remainders = [q - i for q, i in zip(exact_quotas, integer_parts)]
    
    # Distribute remaining units to those with largest remainders
    leftover = total_stock_limit - sum(integer_parts)
    # Get indices of sorted remainders (descending)
    top_indices = np.argsort(remainders)[::-1][:leftover]
    
    for idx in top_indices:
        integer_parts[idx] += 1
    
    # Results
    df['LP_Max_Revenue_Stock'] = lp_results
    df['Prop_Stock_LRM'] = integer_parts
    
    df['LP_Revenue'] = df['LP_Max_Revenue_Stock'] * df['Price']
    df['Prop_Revenue'] = df['Prop_Stock_LRM'] * df['Price']
    
    return df


def run() -> None:
    results = solve_inventory_allocation(INPUT_CSV)

    print("--- Allocation Comparison ---")
    print(results[['Product', 'Price', 'Predicted Demand Forecast', 'LP_Max_Revenue_Stock', 'Prop_Stock_LRM']])
    print(f"\nTotal Revenue (LP Max): ${results['LP_Revenue'].sum():,.2f}")
    print(f"Total Revenue (Proportional): ${results['Prop_Revenue'].sum():,.2f}")

    results.to_csv(OUTPUT_CSV, index=False)
    print(f"\nResults saved to '{OUTPUT_CSV.name}'.")

if __name__ == "__main__":
    run()
