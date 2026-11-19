"""Complete the required search functions; preserve their signatures.
See the accompanying CHW1.pdf for the provided interfaces and recording contract.
"""
from collections import deque
from heapq import heappop, heappush
from itertools import count
from .contracts import reconstruct_path
from .heuristics import heuristic

def bfs(grid, mode, recorder):
    """TODO: implement BFS and return a SearchResult."""
    raise NotImplementedError("Complete bfs() in src/search.py")

def ucs(grid, mode, recorder):
    """TODO: implement UCS and return a SearchResult."""
    raise NotImplementedError("Complete ucs() in src/search.py")

def astar(grid, mode, recorder):
    """TODO: implement A* and return a SearchResult."""
    raise NotImplementedError("Complete astar() and the heuristic")
