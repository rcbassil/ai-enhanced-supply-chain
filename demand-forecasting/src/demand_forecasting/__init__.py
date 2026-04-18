from demand_forecasting.model import run, Path, DEFAULT_INPUT_CSV, DEFAULT_OUTPUT_CSV


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Demand Forecasting Pipeline")
    parser.add_argument("--input", type=str, default=str(DEFAULT_INPUT_CSV), help="Path to input dataset CSV")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_CSV), help="Path to save forecast results CSV")
    args = parser.parse_args()
    
    run(Path(args.input), Path(args.output))
