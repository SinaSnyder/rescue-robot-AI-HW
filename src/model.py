"""Provided environment. Coordinates are (row, column); cost is paid on entry."""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

Position = Tuple[int, int]
COSTS = {".": 1, "r": 5, "h": 10}


@dataclass(frozen=True)
class Grid:
    cells: Tuple[str, ...]
    start: Position
    goals: Tuple[Position, ...]
    name: str = "Custom mission"

    def __post_init__(self):
        if not self.cells or not all(isinstance(row, str) for row in self.cells):
            raise ValueError("cells must be a nonempty list of strings")
        w = len(self.cells[0])
        if not 1 <= w <= 60 or not 1 <= len(self.cells) <= 60:
            raise ValueError("Map dimensions must be between 1 and 60")
        if any(len(row) != w or set(row) - set(".#rh") for row in self.cells):
            raise ValueError("Rows must have equal width; allowed terrain: . # r h")
        if not 1 <= len(self.goals) <= 6 or len(set(self.goals)) != len(self.goals):
            raise ValueError("Provide 1 to 6 distinct goals")
        for p in (self.start,) + self.goals:
            if len(p) != 2 or any(type(v) is not int for v in p) or not self.walkable(p):
                raise ValueError("Start/goals must be integer [row,col] on traversable cells")
        if not isinstance(self.name, str) or len(self.name) > 120:
            raise ValueError("name must be a string of at most 120 characters")

    @property
    def height(self):
        return len(self.cells)

    @property
    def width(self):
        return len(self.cells[0])

    def walkable(self, p):
        r, c = p
        return 0 <= r < self.height and 0 <= c < self.width and self.cells[r][c] != "#"

    def neighbors(self, p):
        """Deterministic tie order: up, right, down, left. No diagonal moves."""
        r, c = p
        for q in ((r - 1, c), (r, c + 1), (r + 1, c), (r, c - 1)):
            if self.walkable(q):
                yield q

    def cost(self, p, mode="terrain"):
        if mode not in ("uniform", "terrain"):
            raise ValueError("Unknown cost mode")
        return 1 if mode == "uniform" else COSTS[self.cells[p[0]][p[1]]]

    def as_dict(self):
        return {"name": self.name, "cells": list(self.cells), "start": list(self.start),
                "goals": [list(p) for p in self.goals]}

    @classmethod
    def from_dict(cls, data):
        try:
            if not isinstance(data, dict) or not isinstance(data.get("cells"), list):
                raise ValueError("cells must be a list of strings")
            if not isinstance(data.get("start"), list) or not isinstance(data.get("goals"), list):
                raise ValueError("start and goals must be JSON arrays")
            return cls(tuple(data["cells"]), tuple(data["start"]),
                       tuple(tuple(p) for p in data["goals"]), data.get("name", "Custom mission"))
        except (KeyError, TypeError, IndexError) as exc:
            raise ValueError("Invalid map: expected cells, start and goals") from exc

    @classmethod
    def load(cls, path):
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
