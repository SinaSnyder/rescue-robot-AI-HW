"""Prepare one configured run and print its actual results to the terminal."""
import math
from .generator import generate
from .model import Grid
from .registry import ROOT, capabilities, run_search


def prepare_session(setup, algorithm=None, map_file=None, mode=None, weight=None, trace=True):
    algorithm = setup.ALGORITHM if algorithm is None else algorithm
    mode = setup.COST_MODE if mode is None else mode
    weight = setup.HEURISTIC_WEIGHT if weight is None else weight
    labels = {item["id"]: item["label"] for item in capabilities()}
    if algorithm not in labels:
        raise ValueError("Unknown ALGORITHM: " + str(algorithm))
    for name in ("SEARCH_STEPS_PER_SECOND", "ROBOT_STEPS_PER_SECOND"):
        value = getattr(setup, name)
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError(name + " must be a finite positive number")
    if type(setup.SHOW_SEARCH) is not bool or type(setup.GUARANTEE_PATH) is not bool:
        raise ValueError("SHOW_SEARCH and GUARANTEE_PATH must be True or False")
    if not isinstance(setup.COMPARE_ALGORITHMS, (tuple, list)) or any(
            name not in labels for name in setup.COMPARE_ALGORITHMS):
        raise ValueError("COMPARE_ALGORITHMS must contain known algorithm names")
    if map_file is not None or setup.MAP_SOURCE == "file":
        grid = Grid.load(ROOT / (setup.MAP_FILE if map_file is None else map_file))
    elif setup.MAP_SOURCE == "generated":
        grid = generate(seed=setup.SEED, width=setup.WIDTH, height=setup.HEIGHT,
                        wall_density=setup.WALL_DENSITY, victims=setup.VICTIMS,
                        solvable=setup.GUARANTEE_PATH)
    else:
        raise ValueError('MAP_SOURCE must be "file" or "generated"')
    result = run_search(grid, algorithm, mode, weight, trace=trace)
    session = {"map": grid.as_dict(), "algorithm": labels[algorithm], "mode": mode,
               "weight": weight if algorithm == "weighted_astar" else None,
               "result": result.as_dict(), "playback": {
                   "show_search": setup.SHOW_SEARCH,
                   "search_speed": setup.SEARCH_STEPS_PER_SECOND,
                   "robot_speed": setup.ROBOT_STEPS_PER_SECOND}}
    return grid, result, session


def print_result(grid, result, algorithm, mode, weight=None):
    """Print once per Python run, independently of animation playback."""
    found = result.status == "found"
    print("\nRescue Robot - search result", flush=True)
    print("Map:           {} ({} x {})".format(grid.name, grid.width, grid.height))
    print("Algorithm:     " + algorithm)
    print("Cost mode:     " + mode)
    if weight is not None:
        print("Weight:        " + str(weight))
    print("Status:        " + result.status.upper())
    print("Path cost:     " + (str(result.cost) if found else "N/A"))
    print("Path length:   " + (str(len(result.path) - 1) + " moves" if found else "N/A"))
    print("Expanded:      " + str(result.expanded))
    print("Generated:     " + str(result.generated))
    print("Peak frontier: " + str(result.frontier_peak))
    print("Search time:   {:.3f} ms (includes Python recording; excludes animation)".format(result.elapsed_ms))
    if result.message:
        print("Message:       " + result.message)
    if result.trace_truncated:
        print("Animation:     trace truncated; final search result shown above")
    print(flush=True)


def print_comparison(grid, setup, selected, selected_result, mode, weight, trace=True):
    if not setup.COMPARE_ALGORITHMS:
        return
    print("Comparison - same map and cost mode; all times include the same recording setting")
    print("{:<18} {:<18} {:>8} {:>8} {:>10} {:>10} {:>10}".format(
        "Algorithm", "Status", "Cost", "Moves", "Expanded", "Generated", "Time/ms"))
    for algorithm in setup.COMPARE_ALGORITHMS:
        if len(grid.goals) > 1 and algorithm != "multi_rescue":
            print("{:<18} single goal only".format(algorithm))
            continue
        result = selected_result if algorithm == selected else run_search(
            grid, algorithm, mode, weight, trace=trace)
        found = result.status == "found"
        print("{:<18} {:<18} {:>8} {:>8} {:>10} {:>10} {:>10.3f}".format(
            algorithm, result.status, result.cost if found else "N/A",
            len(result.path) - 1 if found else "N/A", result.expanded,
            result.generated, result.elapsed_ms))
    print(flush=True)
