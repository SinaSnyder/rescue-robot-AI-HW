"""Optional functions. Enable completed sections in config.json and rerun main.py."""
from heapq import heappop, heappush
from itertools import count
from .contracts import reconstruct_path
from .heuristics import heuristic

def greedy(grid, mode, recorder):
    """Greedy Best-First Search using heuristic priority and cycle prevention."""
    start = grid.start
    goal = grid.goals[0]

    counter = count()
    start_h = heuristic(start, goal)
    pq = [(start_h, next(counter), start)]
    visited = {start}
    parents = {start: None}
    g_cost = {start: 0}

    while pq:
        current_h, _, current = heappop(pq)
        current_g = g_cost[current]

        if current == goal:
            recorder.expand(
                current,
                current_g,
                len(pq),
                discovered=(),
                h=current_h,
            )
            path = reconstruct_path(parents, current)
            return recorder.finish(path, current_g)

        newly_discovered = []
        for nxt in grid.neighbors(current):
            if nxt not in visited:
                visited.add(nxt)
                parents[nxt] = current
                g_cost[nxt] = current_g + grid.cost(nxt, mode)
                nxt_h = heuristic(nxt, goal)
                heappush(pq, (nxt_h, next(counter), nxt))
                newly_discovered.append(nxt)

        recorder.expand(
            current,
            current_g,
            len(pq),
            discovered=newly_discovered,
            h=current_h,
        )

    return recorder.finish()


def weighted_astar(grid, mode, recorder, weight=2.0):
    """Weighted A* search with priority f = g + weight * h."""
    if not 1 <= weight <= 5:
        raise ValueError("weight must be between 1 and 5")

    start = grid.start
    goal = grid.goals[0]

    counter = count()
    start_h = heuristic(start, goal)
    pq = [(weight * start_h, next(counter), start)]
    best_g = {start: 0}
    parents = {start: None}
    closed = set()

    while pq:
        _, _, current = heappop(pq)

        if current in closed:
            continue

        current_g = best_g[current]
        current_h = heuristic(current, goal)
        closed.add(current)

        if current == goal:
            recorder.expand(
                current,
                current_g,
                len(pq),
                discovered=(),
                h=current_h,
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
                nxt_f = tentative_g + weight * heuristic(nxt, goal)
                heappush(pq, (nxt_f, next(counter), nxt))
                newly_discovered.append(nxt)

        recorder.expand(
            current,
            current_g,
            len(pq),
            discovered=newly_discovered,
            h=current_h,
        )

    return recorder.finish()


def _multi_heuristic(pos, goals, mask):
    """Admissible heuristic: minimum Manhattan distance to any unrescued victim."""
    rem = [
        heuristic(pos, g)
        for i, g in enumerate(goals)
        if not (mask & (1 << i))
    ]
    return min(rem) if rem else 0


def multi_rescue(grid, mode, recorder):
    """Minimum-cost rescue of all victims using A* over (row, col, rescued_mask)."""
    goals = grid.goals
    goal_index = {g: i for i, g in enumerate(goals)}
    all_rescued_mask = (1 << len(goals)) - 1

    start_pos = grid.start
    start_mask = 0
    if start_pos in goal_index:
        start_mask |= 1 << goal_index[start_pos]

    start_state = (start_pos[0], start_pos[1], start_mask)
    counter = count()
    start_h = _multi_heuristic(start_pos, goals, start_mask)

    pq = [(start_h, next(counter), start_state)]
    best_g = {start_state: 0}
    parents = {start_state: None}
    closed = set()

    while pq:
        _, _, current = heappop(pq)

        if current in closed:
            continue

        r, c, mask = current
        current_g = best_g[current]
        current_h = _multi_heuristic((r, c), goals, mask)
        closed.add(current)

        if mask == all_rescued_mask:
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
        for nr, nc in grid.neighbors((r, c)):
            next_mask = mask
            if (nr, nc) in goal_index:
                next_mask |= 1 << goal_index[(nr, nc)]
            nxt_state = (nr, nc, next_mask)

            if nxt_state in closed:
                continue

            tentative_g = current_g + grid.cost((nr, nc), mode)
            if tentative_g < best_g.get(nxt_state, float("inf")):
                best_g[nxt_state] = tentative_g
                parents[nxt_state] = current
                nxt_f = tentative_g + _multi_heuristic((nr, nc), goals, next_mask)
                heappush(pq, (nxt_f, next(counter), nxt_state))
                newly_discovered.append(nxt_state)

        recorder.expand(
            current,
            current_g,
            len(pq),
            discovered=newly_discovered,
            h=current_h,
        )

    return recorder.finish()
