import argparse
import json
from pathlib import Path
from src.generator import generate

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reproducible Rescue Robot map generator")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--width", type=int, default=24)
    parser.add_argument("--height", type=int, default=16)
    parser.add_argument("--victims", type=int, default=1)
    parser.add_argument("--wall-density", type=float, default=0.22)
    parser.add_argument("--allow-unsolvable", action="store_true")
    parser.add_argument("--output", default="maps/generated.json")
    args = parser.parse_args()
    grid = generate(args.seed, args.width, args.height, args.wall_density, args.victims, not args.allow_unsolvable)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(grid.as_dict(), indent=2), encoding="utf-8")
    print("Saved {}".format(path))
