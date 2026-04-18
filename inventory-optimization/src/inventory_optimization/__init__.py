from inventory_optimization.solver import run, Path, DEFAULT_INPUT_CSV, DEFAULT_OUTPUT_CSV_1, DEFAULT_OUTPUT_CSV_2


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Inventory Optimization Pipeline")
    parser.add_argument("--input", type=str, default=str(DEFAULT_INPUT_CSV), help="Path to input dataset CSV")
    parser.add_argument("--output1", type=str, default=str(DEFAULT_OUTPUT_CSV_1), help="Path to save scenario 1 results")
    parser.add_argument("--output2", type=str, default=str(DEFAULT_OUTPUT_CSV_2), help="Path to save scenario 2 results")
    args = parser.parse_args()

    run(Path(args.input), Path(args.output1), Path(args.output2))
