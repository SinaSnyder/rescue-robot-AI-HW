import unittest
from pathlib import Path
from src.heuristics import heuristic
from src.model import Grid
from src.registry import run_search


class StudentSearchTests(unittest.TestCase):
    def setUp(self):
        self.maps_dir = Path(__file__).resolve().parent.parent / "maps"

    def test_weighted_trap_optimal_cost(self):
        grid = Grid.load(self.maps_dir / "weighted_trap.json")
        bfs_res = run_search(grid, "bfs", "terrain")
        ucs_res = run_search(grid, "ucs", "terrain")
        astar_res = run_search(grid, "astar", "terrain")

        self.assertEqual(bfs_res.status, "found")
        self.assertEqual(ucs_res.status, "found")
        self.assertEqual(astar_res.status, "found")
        self.assertEqual(ucs_res.cost, astar_res.cost)
        self.assertLessEqual(ucs_res.cost, bfs_res.cost)

    def test_public_no_solution_map(self):
        grid = Grid.load(self.maps_dir / "no_solution.json")
        for alg in ("bfs", "ucs", "astar"):
            for mode in ("uniform", "terrain"):
                with self.subTest(alg=alg, mode=mode):
                    res = run_search(grid, alg, mode)
                    self.assertEqual(res.status, "no_path")
                    self.assertEqual(res.path, [])
                    self.assertIsNone(res.cost)

    def test_heuristic_properties(self):
        goal = (3, 4)
        self.assertEqual(heuristic(goal, goal), 0)
        for pos in [(0, 0), (3, 4), (5, 1), (2, 7)]:
            h_val = heuristic(pos, goal)
            self.assertGreaterEqual(h_val, 0)
            manhattan = abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
            self.assertLessEqual(h_val, manhattan)


if __name__ == "__main__":
    unittest.main(verbosity=2)