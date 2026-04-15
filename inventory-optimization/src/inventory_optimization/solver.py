import pandas as pd
import numpy as np
from ortools.linear_solver import pywraplp
from pathlib import Path

DATA_DIR = Path(__file__).parents[3] / "data"  # workspace root / data
INPUT_CSV = DATA_DIR / "inventory_s001_north_may_2022.csv"
OUTPUT_CSV_1 = DATA_DIR / "inventory_optimization_results_scenario_1.csv"
OUTPUT_CSV_2 = DATA_DIR / "inventory_optimization_results_scenario_2.csv"

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

def solve_biased_allocation(file_path, bias_pct=0.20):
    # Load Data
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    
    total_capacity = 100
    total_demand = df['Predicted Demand Forecast'].sum()
    
    # Calculate Fair Share (100% Proportional baseline)
    df['Fair_Share'] = (df['Predicted Demand Forecast'] / total_demand) * total_capacity
    
    # Setup Linear Programming Solver (OR-Tools)
    solver = pywraplp.Solver.CreateSolver('GLOP')
    stocks = []
    
    for i, row in df.iterrows():
        # Constraint: Must receive at least (1 - bias) of the Fair Share
        lower_bound = row['Fair_Share'] * (1 - bias_pct)
        # Constraint: Cannot exceed forecasted demand
        upper_bound = min(row['Predicted Demand Forecast'], total_capacity)
        stocks.append(solver.NumVar(lower_bound, upper_bound, f"s_{i}"))
        
    # Constraint: Total capacity must be exactly 100
    solver.Add(solver.Sum(stocks) == total_capacity)
    
    # Objective: Maximize Revenue (Price * Stock)
    objective = solver.Objective()
    for i, row in df.iterrows():
        objective.SetCoefficient(stocks[i], row['Price'])
    objective.SetMaximization()
    
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        df['Optimized_Float'] = [s.solution_value() for s in stocks]
        
        # Largest Remainder Method (Integer Rounding)
        df['Final_Stock'] = df['Optimized_Float'].apply(np.floor).astype(int)
        df['Remainder'] = df['Optimized_Float'] - df['Final_Stock']
        
        leftover = total_capacity - df['Final_Stock'].sum()
        top_indices = df.sort_values(by='Remainder', ascending=False).head(int(leftover)).index
        df.loc[top_indices, 'Final_Stock'] += 1
        
        # Final Metrics
        df['Revenue'] = df['Final_Stock'] * df['Price']
        return df[['Product', 'Price', 'Predicted Demand Forecast', 'Final_Stock', 'Revenue']]


def run() -> None:
    results = solve_inventory_allocation(INPUT_CSV)

    print("--- Allocation Comparison ---")
    print(results[['Product', 'Price', 'Predicted Demand Forecast', 'LP_Max_Revenue_Stock', 'Prop_Stock_LRM']])
    print(f"\nTotal Revenue (LP Max): ${results['LP_Revenue'].sum():,.2f}")
    print(f"Total Revenue (Proportional): ${results['Prop_Revenue'].sum():,.2f}")

    summary = pd.DataFrame([
        {"Product": "TOTAL (LP Max)", "LP_Revenue": results["LP_Revenue"].sum()},
        {"Product": "TOTAL (Proportional)", "Prop_Revenue": results["Prop_Revenue"].sum()},
    ])
    pd.concat([results, summary], ignore_index=True).to_csv(OUTPUT_CSV_1, index=False)
    print(f"\nResults saved to '{OUTPUT_CSV_1.name}'.")


    # Run for 20% bias
    results = solve_biased_allocation(INPUT_CSV, bias_pct=0.20)
    print("\n--- 20% Bias Allocation ---")
    print(results[['Product', 'Price', 'Predicted Demand Forecast', 'Final_Stock', 'Revenue']])
    print(f"Total Revenue: ${results['Revenue'].sum():,.2f}")

    summary = pd.DataFrame([
        {"Product": "TOTAL Revenue", "Revenue": results["Revenue"].sum()}
    ])

    pd.concat([results, summary], ignore_index=True).to_csv(OUTPUT_CSV_2, index=False)
    print(f"\nResults saved to '{OUTPUT_CSV_2.name}'.")

if __name__ == "__main__":
    run()
