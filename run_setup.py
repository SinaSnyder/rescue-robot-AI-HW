"""Edit this file, save it, then run main.py again (for example in VS Code)."""

# Search: "bfs", "ucs", "astar", "greedy", "weighted_astar", "multi_rescue".
# Bonus algorithms also need their own flag enabled in config.json.
ALGORITHM = "bfs"
COST_MODE = "uniform"              # "terrain" (1/5/10) or "uniform" (all 1)
HEURISTIC_WEIGHT = 2.0              # Weighted A* only; from 1 to 5

# Map: "file" loads MAP_FILE; "generated" uses the seed and settings below.
MAP_SOURCE = "file"
MAP_FILE = "maps/easy_01.json"    # Relative to this project's folder
SEED = 2026
WIDTH = 28
HEIGHT = 18
WALL_DENSITY = 0.22
VICTIMS = 1                        # More than one requires multi_rescue
GUARANTEE_PATH = True

# Animation only; these do not change the search result or its measured time.
SHOW_SEARCH = True                 # False: animate only the robot's route
SEARCH_STEPS_PER_SECOND = 100
ROBOT_STEPS_PER_SECOND = 6

# Optional extra searches, printed in the terminal. Empty means no comparison.
# Example: ("bfs", "ucs", "astar")
COMPARE_ALGORITHMS = ()

# Native Pygame window. No browser or local server is started.
WINDOW_SIZE = (1180, 860)
FPS = 60
