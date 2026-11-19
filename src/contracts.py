"""Provided result/animation contract; contains no search algorithm."""
from dataclasses import dataclass, field, asdict
from time import perf_counter


class SearchLimit(Exception):
    """Search reached the documented resource budget."""


def reconstruct_path(parents, end):
    """Works with positions or augmented states, e.g. (row, col, mask)."""
    path = []
    while end is not None:
        path.append(end)
        end = parents[end]
    return list(reversed(path))


@dataclass
class SearchResult:
    status: str
    path: list = field(default_factory=list)
    cost: object = None
    expanded: int = 0
    generated: int = 1
    frontier_peak: int = 1
    elapsed_ms: float = 0.0
    events: list = field(default_factory=list)
    trace_truncated: bool = False
    message: str = ""

    def as_dict(self):
        result = asdict(self)
        result["steps"] = max(0, len(self.path) - 1)
        return result


class Recorder:
    """generated counts successful queue insertions, including the initial state.

    expanded counts valid pops, including the goal. frontier is physical queue
    size (a heap can include stale entries). Time includes instrumentation but
    excludes HTTP/serialization/animation. Trace truncation never stops search.
    """
    def __init__(self, trace=True, max_expanded=120000, max_events=12000):
        self.started = perf_counter()
        self.trace = trace
        self.max_expanded = max_expanded
        self.max_events = max_events
        self.result = SearchResult("no_path")

    def expand(self, state, g, frontier, discovered=(), h=0):
        if self.result.expanded >= self.max_expanded:
            raise SearchLimit("Search exceeded 120000 expansions; try a smaller map")
        self.result.expanded += 1
        self.result.generated += len(discovered)
        self.result.frontier_peak = max(self.result.frontier_peak, frontier)
        if self.trace and len(self.result.events) < self.max_events:
            self.result.events.append({"state": list(state), "g": g, "h": h,
                                       "frontier": frontier,
                                       "discovered": [list(p) for p in discovered]})
        elif self.trace:
            self.result.trace_truncated = True

    def finish(self, path=(), cost=None, status=None, message=""):
        self.result.path = [list(state[:2]) for state in path]
        self.result.cost = cost
        self.result.status = status or ("found" if path else "no_path")
        self.result.elapsed_ms = round((perf_counter() - self.started) * 1000, 3)
        self.result.message = message
        return self.result
