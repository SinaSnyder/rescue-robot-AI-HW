"""Run the experiment configured in run_setup.py and open its animation."""
import argparse
import json
import run_setup
from src.runner import prepare_session, print_result, print_comparison

def main():
    parser = argparse.ArgumentParser(description="Rescue Robot | AI search laboratory")
    parser.add_argument("--cli", action="store_true")
    parser.add_argument("--snapshot", metavar="PNG", help="Save the final Pygame frame without opening a window")
    parser.add_argument("--map", default=None)
    parser.add_argument("--algorithm", default=None)
    parser.add_argument("--mode", choices=["uniform", "terrain"], default=None)
    parser.add_argument("--weight", type=float, default=None)
    args = parser.parse_args()
    try:
        grid, result, session = prepare_session(run_setup, args.algorithm, args.map,
                                               args.mode, args.weight, trace=not args.cli)
    except (ValueError, OSError, TypeError) as exc:
        print("Setup error: {}. Check run_setup.py.".format(exc), flush=True)
        return 2
    if args.cli:
        print(json.dumps(result.as_dict(), indent=2))
        return 0 if result.status in ("found", "no_path") else 2
    print_result(grid, result, session["algorithm"], session["mode"], session["weight"])
    print_comparison(grid, run_setup, args.algorithm or run_setup.ALGORITHM, result,
                     session["mode"], args.weight if args.weight is not None else run_setup.HEURISTIC_WEIGHT)
    try:
        from src.visualizer import animate, save_snapshot
    except ModuleNotFoundError as exc:
        if exc.name != "pygame":
            raise
        print("Pygame is not installed in this interpreter. Run: python -m pip install -r requirements.txt", flush=True)
        return 2
    try:
        if args.snapshot:
            from pathlib import Path
            save_snapshot(session, run_setup.WINDOW_SIZE, Path(args.snapshot))
        else:
            animate(session, run_setup.WINDOW_SIZE, run_setup.FPS)
    except (OSError, ValueError) as exc:
        print("Could not open the Pygame viewer: {}".format(exc), flush=True)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
