"""Complete the required search functions; preserve their signatures.
See the accompanying CHW1.pdf for the provided interfaces and recording contract.
"""
from collections import deque
from heapq import heappop, heappush
from itertools import count
from .contracts import reconstruct_path
from .heuristics import heuristic

def bfs(grid, mode, recorder):
    start = grid.start
    goal = grid.goals[0]

    queue = deque([start])
    discovered_set = {start}
    parents = {start: None}
    g_cost = {start: 0}

    while queue:
        current = queue.popleft()
        current_g = g_cost[current]

        if current == goal:
            recorder.expand(
                current,
                current_g,
                len(queue),
                discovered=(),
                h=0,
            )
            path = reconstruct_path(parents, current)
            return recorder.finish(path, current_g)

        newly_discovered = []
        for nxt in grid.neighbors(current):
            if nxt not in discovered_set:
                discovered_set.add(nxt)
                parents[nxt] = current
                g_cost[nxt] = current_g + grid.cost(nxt, mode)
                queue.append(nxt)
                newly_discovered.append(nxt)

        recorder.expand(
            current,
            current_g,
            len(queue),
            discovered=newly_discovered,
            h=0,
        )

    return recorder.finish()

def ucs(grid, mode, recorder):
    start = grid.start
    goal = grid.goals[0]

    counter = count()
    pq = [(0, next(counter), start)]
    best_g = {start: 0}
    parents = {start: None}
    closed = set()

    while pq:
        current_g, _, current = heappop(pq)

        if current in closed or current_g > best_g.get(current, float("inf")):
            continue

        closed.add(current)

        if current == goal:
            recorder.expand(
                current,
                current_g,
                len(pq),
                discovered=(),
                h=0,
            )
            path = reconstruct_path(parents, current)
            return recorder.finish(path, current_g)

        newly_discovered = []
        for nxt in grid.neighbors(current):
            if nxt in closed:
                continue
            tentative_g = current_g + grid.cost(nxt, mode)
            if tentative_g < best_g.get(nxt, float("inf")):
                best_g[nxt] = tentative_g
                parents[nxt] = current
                heappush(pq, (tentative_g, next(counter), nxt))
                newly_discovered.append(nxt)

        recorder.expand(
            current,
            current_g,
            len(pq),
            discovered=newly_discovered,
            h=0,
        )

    return recorder.finish()

def astar(grid, mode, recorder):
    """TODO: implement A* and return a SearchResult."""
    raise NotImplementedError("Complete astar() and the heuristic")
