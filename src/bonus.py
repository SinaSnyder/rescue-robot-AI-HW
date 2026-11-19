"""Optional functions. Enable completed sections in config.json and rerun main.py."""
from heapq import heappop, heappush
from itertools import count
from .contracts import reconstruct_path
from .heuristics import heuristic

def greedy(grid, mode, recorder):
    """TODO: optional Greedy Best First."""
    raise NotImplementedError("Optional: complete greedy()")

def weighted_astar(grid, mode, recorder, weight=2.0):
    """TODO: optional Weighted A*."""
    raise NotImplementedError("Optional: complete weighted_astar()")

def multi_rescue(grid, mode, recorder):
    """TODO: optional minimum-cost rescue of all victims."""
    raise NotImplementedError("Optional: complete multi_rescue()")
