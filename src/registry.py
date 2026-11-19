"""Provided plugin boundary: disabled bonuses are never imported or executed."""
import importlib
import json
import math
from pathlib import Path
from .contracts import Recorder, SearchLimit

ROOT = Path(__file__).resolve().parents[1]
ALGORITHMS = [
    ("bfs", "BFS", "FIFO / minimum steps", False),
    ("ucs", "UCS", "g(n) / minimum cost", False),
    ("astar", "A*", "g(n) + h(n)", False),
    ("greedy", "Greedy", "h(n) / bonus", True),
    ("weighted_astar", "Weighted A*", "g(n) + w × h(n) / bonus", True),
    ("multi_rescue", "Multi Rescue", "UCS on (r, c, mask) / bonus", True),
]


def capabilities():
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    return [{"id": key, "label": label, "formula": formula, "bonus": bonus,
             "enabled": not bonus or config.get("bonus", {}).get(key) is True}
            for key, label, formula, bonus in ALGORITHMS]


def run_search(grid, algorithm, mode="terrain", weight=2.0, trace=True):
    if mode not in ("uniform", "terrain"):
        raise ValueError("Cost mode must be uniform or terrain")
    entries = {item["id"]: item for item in capabilities()}
    if algorithm not in entries:
        raise ValueError("Unknown algorithm")
    recorder = Recorder(trace=trace)
    item = entries[algorithm]
    if not item["enabled"]:
        return recorder.finish(status="disabled", message="Optional bonus is disabled in config.json")
    if algorithm != "multi_rescue" and len(grid.goals) != 1:
        raise ValueError("Single-goal algorithms require exactly one victim. Use Multi Rescue or remove extra victims.")
    if algorithm == "weighted_astar" and (not isinstance(weight, (int, float)) or
            not math.isfinite(weight) or not 1 <= weight <= 5):
        raise ValueError("Weight must be finite and between 1 and 5")
    try:
        module = importlib.import_module(".bonus" if item["bonus"] else ".search", __package__)
        function = getattr(module, algorithm)
        recorder = Recorder(trace=trace)
        if algorithm == "weighted_astar":
            return function(grid, mode, recorder, weight=weight)
        return function(grid, mode, recorder)
    except NotImplementedError as exc:
        return recorder.finish(status="not_implemented", message=str(exc) or "Complete the student TODO first")
    except SearchLimit as exc:
        return recorder.finish(status="limit", message=str(exc))
