"""Seeded map generation. A carved corridor guarantees feasibility if requested."""
import random
from .model import Grid


def generate(seed=2026, width=24, height=16, wall_density=0.22, victims=1, solvable=True):
    if type(seed) is not int or any(type(v) is not int for v in (width, height, victims)):
        raise ValueError("Seed, dimensions and victims must be integers")
    if not 4 <= width <= 60 or not 4 <= height <= 60 or not 1 <= victims <= 6:
        raise ValueError("Generator: dimensions 4..60, victims 1..6")
    if not isinstance(wall_density, (int, float)) or not 0 <= wall_density <= 0.6:
        raise ValueError("Wall density must be 0..0.6")
    rng = random.Random(seed)
    cells = []
    for r in range(height):
        row = []
        for c in range(width):
            x = rng.random()
            row.append("#" if x < wall_density else rng.choices([".", "r", "h"], [75, 17, 8])[0])
        cells.append(row)
    start = (0, 0)
    candidates = [(r, c) for r in range(height) for c in range(width) if (r, c) != start]
    first = (height - 1, width - 1)
    candidates.remove(first)
    goals = [first] + rng.sample(candidates, victims - 1)
    if solvable:
        current = start
        for target in goals:
            r, c = current
            while (r, c) != target:
                if cells[r][c] == "#":
                    cells[r][c] = "."
                options = []
                if r != target[0]:
                    options.append((r + (1 if target[0] > r else -1), c))
                if c != target[1]:
                    options.append((r, c + (1 if target[1] > c else -1)))
                r, c = rng.choice(options)
            current = target
    for r, c in [start] + goals:
        cells[r][c] = "."
    return Grid(tuple("".join(row) for row in cells), start, tuple(goals), "Seed {}".format(seed))
