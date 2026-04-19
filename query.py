#!/usr/bin/env python3
"""Query the supply chain project with natural language using Claude."""

import json
import os
from pathlib import Path

import anthropic

DATA_DIR = Path(__file__).parent / "data"

if not os.environ.get("ANTHROPIC_API_KEY"):
    raise EnvironmentError("ANTHROPIC_API_KEY environment variable is missing.")

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an AI assistant for an AI-enhanced supply chain project.
The project uses linear programming (OR-Tools) to optimize inventory allocation and routing.

You have access to tools that let you read CSV data files and run optimization solvers.

Key concepts:
- LP Max Revenue: maximizes total revenue (concentrates on high-price items).
- Proportional (LRM): allocates stock proportionally to demand forecasts.
- Carbon-Efficient Allocation: maximizes revenue while capping total CO2 emissions (storage carbon).
- Routing Optimization: calculates the shortest distance and carbon footprint (shipping carbon) for deliveries.

The data covers Store S001 North, May 2022. Total stock limit is 100 units.
Emission factors are configurable in `data/sustainability_config.json`.

When answering, use the tools to fetch real data and compare sustainability metrics when asked."""

tools = [
    {
        "name": "list_data_files",
        "description": "List all CSV data files available in the project data directory.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "read_data_file",
        "description": "Read a CSV data file and return its contents as a table.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "CSV filename (e.g. 'inventory_s001_north_may_2022.csv')",
                }
            },
            "required": ["filename"],
        },
    },
    {
        "name": "run_inventory_solver",
        "description": (
            "Run the inventory optimization solver and return fresh results. "
            "Scenario 1: LP Max Revenue vs Proportional vs Carbon-Efficient "
            "allocation. Scenario 2: 20% biased allocation "
            "(fairness-constrained LP)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "scenario": {
                    "type": "integer",
                    "enum": [1, 2],
                    "description": "1 for LP Max/Prop/Carbon-Efficient, 2 for 20% biased allocation",
                },
                "capacity": {
                    "type": "integer",
                    "description": "Total stock capacity limit (default: 500)",
                },
                "store": {
                    "type": "string",
                    "description": "Store ID to filter (e.g. S001)",
                },
                "region": {
                    "type": "string",
                    "description": "Region to filter (e.g. North)",
                },
                "date": {
                    "type": "string",
                    "description": "Date prefix to filter (e.g. 2022-05)",
                },
            },
            "required": ["scenario"],
        },
    },
    {
        "name": "run_routing_solver",
        "description": (
            "Run the routing optimization solver to find the best sequence "
            "and calculate CO2 emissions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


def execute_tool(name: str, tool_input: dict) -> str:
    from inventory_optimization.solver import DATA_DIR

    if name == "list_data_files":
        files = sorted(DATA_DIR.glob("*.csv"))
        if not files:
            return "No CSV files found in data directory."
        return "\n".join(f.name for f in files)

    elif name == "read_data_file":
        filename = tool_input["filename"]
        path = DATA_DIR / filename
        if not path.exists():
            available = ", ".join(f.name for f in sorted(DATA_DIR.glob("*.csv")))
            return f"File '{filename}' not found. Available files: {available}"
        try:
            import pandas as pd

            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            return df.to_string(index=False)
        except Exception as e:
            return f"Error reading file: {e}"

    elif name == "run_inventory_solver":
        scenario = tool_input["scenario"]
        capacity = tool_input.get("capacity", 500)
        filters = {
            "store": tool_input.get("store"),
            "region": tool_input.get("region"),
            "date_filter": tool_input.get("date"),
        }
        try:
            from inventory_optimization.solver import (
                DATA_DIR,
                solve_biased_allocation,
                solve_inventory_allocation,
            )

            # Default to forecasting output if it exists
            FORECAST_OUTPUT = DATA_DIR / "retail_forecast_with_original_values.csv"
            input_file = (
                FORECAST_OUTPUT
                if FORECAST_OUTPUT.exists()
                else (DATA_DIR / "inventory_s001_north_may_2022.csv")
            )

            if scenario == 1:
                df = solve_inventory_allocation(input_file, total_stock_limit=capacity, **filters)
                cols = [
                    "Product",
                    "Price",
                    "LP_Max_Revenue_Stock",
                    "Prop_Stock_LRM",
                    "Carbon_Efficient_Stock",
                    "LP_Revenue",
                    "Carbon_Efficient_Revenue",
                    "LP_Max_CO2",
                    "Carbon_Efficient_CO2",
                ]
                df_display = df[[c for c in cols if c in df.columns]]

                return (
                    df_display.to_string(index=False)
                    + f"\n\nTotal Proportional Revenue: ${df['Prop_Revenue'].sum():,.2f}"
                    + f"\nTotal Proportional CO2: {df['Prop_CO2'].sum():,.2f} kg"
                    + "\n\nTotal Carbon-Efficient Revenue: "
                    + f"${df['Carbon_Efficient_Revenue'].sum():,.2f}"
                    + f"\nTotal Carbon-Efficient CO2: {df['Carbon_Efficient_CO2'].sum():,.2f} kg"
                )
            else:
                df = solve_biased_allocation(input_file, total_capacity=capacity, **filters)
                total = df["Revenue"].sum()
                return df.to_string(index=False) + f"\n\nTotal Revenue (20% bias): ${total:,.2f}"
        except Exception as e:
            return f"Error running solver: {e}"

    elif name == "run_routing_solver":
        try:
            from routing_optimization.solver import OUTPUT_CSV as ROUTING_CSV
            from routing_optimization.solver import run as run_routing

            run_routing()
            import pandas as pd

            df = pd.read_csv(ROUTING_CSV)
            return df.to_string(index=False)
        except Exception as e:
            return f"Error running routing solver: {e}"

    return f"Unknown tool: {name}"


def query(user_message: str, history: list[dict]) -> list[dict]:
    """Send a message and stream the response, handling tool calls in a loop."""
    history = history + [{"role": "user", "content": user_message}]

    while True:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=history,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
            response = stream.get_final_message()

        history.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            print()
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n[Tool: {block.name}({json.dumps(block.input)})]", flush=True)
                    result = execute_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )
            history.append({"role": "user", "content": tool_results})

    return history


def main():
    print("Supply Chain Query Interface (Claude Opus 4.6)")
    print("Type 'exit' or 'quit' to quit, 'clear' to reset conversation\n")

    history = []
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in ("exit", "quit"):
            break
        if user_input.lower() == "clear":
            history = []
            print("[Conversation cleared]\n")
            continue
        if not user_input:
            continue

        print("Claude: ", end="", flush=True)
        history = query(user_input, history)
        print()


if __name__ == "__main__":
    main()
