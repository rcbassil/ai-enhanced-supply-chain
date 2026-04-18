import json
from pathlib import Path

import numpy as np
import pandas as pd
from ortools.linear_solver import pywraplp

DATA_DIR = Path(__file__).parents[3] / "data"
DEFAULT_INPUT_CSV = DATA_DIR / "inventory_s001_north_may_2022.csv"
DEFAULT_OUTPUT_CSV_1 = DATA_DIR / "inventory_optimization_results_scenario_1.csv"
DEFAULT_OUTPUT_CSV_2 = DATA_DIR / "inventory_optimization_results_scenario_2.csv"


def load_sustainability_config() -> dict:
    config_path = DATA_DIR / "sustainability_config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {"storage_emission_factor": 0.12, "emissions_target_reduction": 0.15}


def solve_inventory_allocation(file_path, total_stock_limit=100):
    # Load the dataset
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()  # Clean column names

    products = df["Product"].tolist()
    prices = df["Price"].tolist()
    demands = df["Predicted Demand Forecast"].tolist()
    num_products = len(products)

    # Revenue Maximization (Linear Programming via OR-Tools)
    solver = pywraplp.Solver.CreateSolver("GLOP")
    if not solver:
        return

    # Variables: x[i] is the number of units of product i to stock
    x = [solver.NumVar(0, demands[i], f"x_{i}") for i in range(num_products)]

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
    remainders = [q - i for q, i in zip(exact_quotas, integer_parts, strict=False)]

    # Distribute remaining units to those with largest remainders
    leftover = total_stock_limit - sum(integer_parts)
    # Get indices of sorted remainders (descending)
    top_indices = np.argsort(remainders)[::-1][:leftover]

    for idx in top_indices:
        integer_parts[idx] += 1

    # Results
    df["LP_Max_Revenue_Stock"] = lp_results
    df["Prop_Stock_LRM"] = integer_parts

    # Load Sustainability Config
    config = load_sustainability_config()
    storage_factor = config.get("storage_emission_factor", 0.12)
    reduction_target = config.get("emissions_target_reduction", 0.15)

    df["LP_Revenue"] = df["LP_Max_Revenue_Stock"] * df["Price"]
    df["Prop_Revenue"] = df["Prop_Stock_LRM"] * df["Price"]

    # Calculate CO2 for existing scenarios
    df["LP_Max_CO2"] = df["LP_Max_Revenue_Stock"] * storage_factor
    df["Prop_CO2"] = df["Prop_Stock_LRM"] * storage_factor

    total_lp_co2 = df["LP_Max_CO2"].sum()
    co2_cap = total_lp_co2 * (1 - reduction_target)

    # --- Carbon-Efficient Allocation ---
    # Goal: Maximize revenue while capping CO2 at 85% of LP Max CO2
    ce_solver = pywraplp.Solver.CreateSolver("GLOP")
    if ce_solver:
        ce_x = [ce_solver.NumVar(0, demands[i], f"ce_x_{i}") for i in range(num_products)]
        ce_solver.Add(sum(ce_x) <= total_stock_limit)
        # Carbon Cap Constraint
        ce_solver.Add(sum(ce_x[i] * storage_factor for i in range(num_products)) <= co2_cap)

        ce_objective = ce_solver.Objective()
        for i in range(num_products):
            ce_objective.SetCoefficient(ce_x[i], prices[i])
        ce_objective.SetMaximization()

        ce_status = ce_solver.Solve()
        if ce_status == pywraplp.Solver.OPTIMAL:
            df["Carbon_Efficient_Stock"] = [round(v.solution_value(), 2) for v in ce_x]
            df["Carbon_Efficient_Revenue"] = df["Carbon_Efficient_Stock"] * df["Price"]
            df["Carbon_Efficient_CO2"] = df["Carbon_Efficient_Stock"] * storage_factor

    return df


def solve_biased_allocation(file_path, bias_pct=0.20, total_capacity=100):
    # Load Data
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    total_demand = df["Predicted Demand Forecast"].sum()

    # Calculate Fair Share (100% Proportional baseline)
    df["Fair_Share"] = (df["Predicted Demand Forecast"] / total_demand) * total_capacity

    # Setup Linear Programming Solver (OR-Tools)
    solver = pywraplp.Solver.CreateSolver("GLOP")
    stocks = []

    for i, row in df.iterrows():
        # Constraint: Must receive at least (1 - bias) of the Fair Share
        lower_bound = row["Fair_Share"] * (1 - bias_pct)
        # Constraint: Cannot exceed forecasted demand
        upper_bound = min(row["Predicted Demand Forecast"], total_capacity)
        stocks.append(solver.NumVar(lower_bound, upper_bound, f"s_{i}"))

    # Constraint: Total capacity must be exactly 100
    solver.Add(solver.Sum(stocks) == total_capacity)

    # Objective: Maximize Revenue (Price * Stock)
    objective = solver.Objective()
    for i, row in df.iterrows():
        objective.SetCoefficient(stocks[i], row["Price"])
    objective.SetMaximization()

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        df["Optimized_Float"] = [s.solution_value() for s in stocks]

        # Largest Remainder Method (Integer Rounding)
        df["Final_Stock"] = df["Optimized_Float"].apply(np.floor).astype(int)
        df["Remainder"] = df["Optimized_Float"] - df["Final_Stock"]

        leftover = total_capacity - df["Final_Stock"].sum()
        top_indices = df.sort_values(by="Remainder", ascending=False).head(int(leftover)).index
        df.loc[top_indices, "Final_Stock"] += 1

        # Final Metrics
        df["Revenue"] = df["Final_Stock"] * df["Price"]
        return df[["Product", "Price", "Predicted Demand Forecast", "Final_Stock", "Revenue"]]


def run(
    input_path: Path = DEFAULT_INPUT_CSV,
    output_path_1: Path = DEFAULT_OUTPUT_CSV_1,
    output_path_2: Path = DEFAULT_OUTPUT_CSV_2,
    stock_limit: int = 100,
) -> None:
    results = solve_inventory_allocation(input_path, total_stock_limit=stock_limit)

    print("--- Allocation Comparison ---")
    print(
        results[
            [
                "Product",
                "Price",
                "LP_Max_Revenue_Stock",
                "Prop_Stock_LRM",
                "Carbon_Efficient_Stock",
            ]
        ]
    )

    print(f"\nTotal Revenue (LP Max): ${results['LP_Revenue'].sum():,.2f}")
    print(f"Total CO2 (LP Max): {results['LP_Max_CO2'].sum():,.2f} kg")

    print(f"\nTotal Revenue (Carbon-Efficient): ${results['Carbon_Efficient_Revenue'].sum():,.2f}")
    print(f"Total CO2 (Carbon-Efficient): {results['Carbon_Efficient_CO2'].sum():,.2f} kg")

    print(f"\nTotal Revenue (Proportional): ${results['Prop_Revenue'].sum():,.2f}")
    print(f"Total CO2 (Proportional): {results['Prop_CO2'].sum():,.2f} kg")

    summary = pd.DataFrame(
        [
            {
                "Product": "TOTAL (LP Max)",
                "LP_Revenue": results["LP_Revenue"].sum(),
                "LP_Max_CO2": results["LP_Max_CO2"].sum(),
            },
            {
                "Product": "TOTAL (Proportional)",
                "Prop_Revenue": results["Prop_Revenue"].sum(),
                "Prop_CO2": results["Prop_CO2"].sum(),
            },
            {
                "Product": "TOTAL (Carbon-Efficient)",
                "Carbon_Efficient_Revenue": results["Carbon_Efficient_Revenue"].sum(),
                "Carbon_Efficient_CO2": results["Carbon_Efficient_CO2"].sum(),
            },
        ]
    )
    pd.concat([results, summary], ignore_index=True).to_csv(output_path_1, index=False)
    print(f"\nResults saved to '{output_path_1.name}'.")

    # Run for 20% bias
    results = solve_biased_allocation(input_path, bias_pct=0.20)
    print("\n--- 20% Bias Allocation ---")
    print(results[["Product", "Price", "Predicted Demand Forecast", "Final_Stock", "Revenue"]])
    print(f"Total Revenue: ${results['Revenue'].sum():,.2f}")

    summary = pd.DataFrame([{"Product": "TOTAL Revenue", "Revenue": results["Revenue"].sum()}])

    pd.concat([results, summary], ignore_index=True).to_csv(output_path_2, index=False)
    print(f"\nResults saved to '{output_path_2.name}'.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Inventory Optimization Pipeline")
    parser.add_argument(
        "--input",
        type=str,
        default=str(DEFAULT_INPUT_CSV),
        help="Path to input dataset CSV",
    )
    parser.add_argument(
        "--output1",
        type=str,
        default=str(DEFAULT_OUTPUT_CSV_1),
        help="Path to save scenario 1 results",
    )
    parser.add_argument(
        "--output2",
        type=str,
        default=str(DEFAULT_OUTPUT_CSV_2),
        help="Path to save scenario 2 results",
    )
    parser.add_argument("--limit", type=int, default=100, help="Total stock capacity limit")
    args = parser.parse_args()

    run(Path(args.input), Path(args.output1), Path(args.output2), stock_limit=args.limit)
