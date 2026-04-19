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


def preprocess_input(
    df: pd.DataFrame, store: str = None, region: str = None, date_filter: str = None
) -> pd.DataFrame:
    """Detects and transforms forecast module output into solver-ready format."""
    df.columns = df.columns.str.strip()

    if "Product ID" in df.columns and "Predicted_Demand_Forecast" in df.columns:
        if store:
            df = df[df["Store ID"] == store]
        if region:
            df = df[df["Region"] == region]
        if date_filter:
            df = df[df["Date"].str.startswith(date_filter)]

        # Group by Month if Date exists
        groupby_cols = ["Product ID"]
        if "Date" in df.columns:
            df["Month"] = pd.to_datetime(df["Date"]).dt.to_period("M").astype(str)
            groupby_cols.append("Month")

        df = (
            df.groupby(groupby_cols)
            .agg({"Price": "mean", "Predicted_Demand_Forecast": "sum"})
            .reset_index()
        )

        # Mapping to solver columns
        if "Month" in df.columns:
            df.columns = ["Product", "Month", "Price", "Predicted Demand Forecast"]
        else:
            df.columns = ["Product", "Price", "Predicted Demand Forecast"]

    return df


def solve_inventory_allocation(df, total_stock_limit=500):
    if total_stock_limit <= 0:
        raise ValueError(f"total_stock_limit must be a positive integer, got {total_stock_limit}")
    # If a path was passed instead of a DataFrame, load it
    if isinstance(df, (str, Path)):
        df = pd.read_csv(df)
        df = preprocess_input(df)

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

    # Constraint: Total stock must not exceed 500
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
    remainders = [q - i for q, i in zip(exact_quotas, integer_parts, strict=True)]

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

        df["Carbon_Efficient_Stock"] = np.nan
        df["Carbon_Efficient_Revenue"] = np.nan
        df["Carbon_Efficient_CO2"] = np.nan

        ce_status = ce_solver.Solve()
        if ce_status == pywraplp.Solver.OPTIMAL:
            df["Carbon_Efficient_Stock"] = [round(v.solution_value(), 2) for v in ce_x]
            df["Carbon_Efficient_Revenue"] = df["Carbon_Efficient_Stock"] * df["Price"]
            df["Carbon_Efficient_CO2"] = df["Carbon_Efficient_Stock"] * storage_factor

    return df


def solve_biased_allocation(df, bias_pct=0.20, total_capacity=500):
    # If a path was passed instead of a DataFrame, load it
    if isinstance(df, (str, Path)):
        df = pd.read_csv(df)
        df = preprocess_input(df)

    total_demand = df["Predicted Demand Forecast"].sum()

    # Calculate Fair Share (100% Proportional baseline)
    df["Fair_Share"] = (df["Predicted Demand Forecast"] / total_demand) * total_capacity

    # Setup Linear Programming Solver (OR-Tools)
    solver = pywraplp.Solver.CreateSolver("GLOP")
    stocks = []

    for _idx, (i, row) in enumerate(df.iterrows()):
        # Constraint: Must receive at least (1 - bias) of the Fair Share
        lower_bound = row["Fair_Share"] * (1 - bias_pct)
        # Constraint: Cannot exceed forecasted demand
        upper_bound = min(row["Predicted Demand Forecast"], total_capacity)
        stocks.append(solver.NumVar(lower_bound, upper_bound, f"s_{i}"))

    # Constraint: Total capacity must be exactly 500
    solver.Add(solver.Sum(stocks) == total_capacity)

    # Objective: Maximize Revenue (Price * Stock)
    objective = solver.Objective()
    for idx, (_i, row) in enumerate(df.iterrows()):
        objective.SetCoefficient(stocks[idx], row["Price"])
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
    stock_limit: int = 500,
    **filters,
) -> None:
    # 1. Load and initial preprocess
    df_raw = pd.read_csv(input_path)
    df_pre = preprocess_input(df_raw, **filters)

    # 2. Sequential optimization per Month (if multi-period)
    if "Month" in df_pre.columns:
        months = sorted(df_pre["Month"].unique())
        results_1_list = []
        results_2_list = []

        print(
            f"Detected {len(months)} months. Running batch optimization (Limit: {stock_limit}/mo)..."
        )
        for month in months:
            month_df = df_pre[df_pre["Month"] == month].copy()
            r1 = solve_inventory_allocation(month_df, total_stock_limit=stock_limit)
            r2 = solve_biased_allocation(month_df, bias_pct=0.20, total_capacity=stock_limit)
            results_1_list.append(r1)
            results_2_list.append(r2)

        results_final_1 = pd.concat(results_1_list, ignore_index=True)
        results_final_2 = pd.concat(results_2_list, ignore_index=True)
    else:
        results_final_1 = solve_inventory_allocation(df_pre, total_stock_limit=stock_limit)
        results_final_2 = solve_biased_allocation(df_pre, bias_pct=0.20, total_capacity=stock_limit)

    print("--- Allocation Summary ---")
    results_count = len(results_final_1)
    period_count = results_final_1.get("Month", pd.Series(["Single"])).nunique()
    print(f"Processed {results_count} allocation targets across {period_count} periods.")
    print(
        results_final_1[
            [
                "Product",
                "Price",
                "Predicted Demand Forecast",
                "LP_Max_Revenue_Stock",
                "Prop_Stock_LRM",
            ]
        ].head(20)
    )

    results_final_1.to_csv(output_path_1, index=False)
    print(f"\nScenario 1 results saved to '{output_path_1.name}'.")

    results_final_2.to_csv(output_path_2, index=False)
    print(f"Scenario 2 results saved to '{output_path_2.name}'.")

    # Global Revenue totals
    prop_rev = (
        results_final_1["Prop_Revenue"].sum() if "Prop_Revenue" in results_final_1.columns else 0
    )
    prop_co2 = results_final_1["Prop_CO2"].sum() if "Prop_CO2" in results_final_1.columns else 0
    bias_rev = results_final_2["Revenue"].sum() if "Revenue" in results_final_2.columns else 0

    print(f"\nTotal Revenue (Scenario 1 - Proportional): ${prop_rev:,.2f}")
    print(f"Total CO2 (Scenario 1 - Proportional): {prop_co2:,.2f} kg")
    print(f"Total Revenue (Scenario 2 - 20% Bias): ${bias_rev:,.2f}")


def main() -> None:
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
    parser.add_argument("--limit", type=int, default=500, help="Total stock capacity limit")
    parser.add_argument("--store", type=str, help="Filter by Store ID (for forecast input)")
    parser.add_argument("--region", type=str, help="Filter by Region (for forecast input)")
    parser.add_argument("--date", type=str, help="Filter by Date/Month prefix (e.g. '2022-05')")
    args = parser.parse_args()

    filters = {
        "store": args.store,
        "region": args.region,
        "date_filter": args.date,
    }

    run(Path(args.input), Path(args.output1), Path(args.output2), stock_limit=args.limit, **filters)


if __name__ == "__main__":
    main()
