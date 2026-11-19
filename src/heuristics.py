"""REQUIRED: design a heuristic satisfying the contract in CHW1.pdf."""


def heuristic(position, goal):
    """Manhattan distance between current position and goal."""
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])