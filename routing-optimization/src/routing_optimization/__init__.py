from routing_optimization.solver import (
    DEFAULT_DISTANCE_MATRICES,
    DEFAULT_OUTPUT_CSV,
    Path,
    run,
)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Routing Optimization Pipeline")
    parser.add_argument(
        "--inputs",
        type=str,
        nargs="+",
        default=[str(p) for p in DEFAULT_DISTANCE_MATRICES],
        help="Path(s) to distance matrix CSV files",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT_CSV),
        help="Path to save routing results CSV",
    )
    args = parser.parse_args()

    run([Path(p) for p in args.inputs], Path(args.output))
