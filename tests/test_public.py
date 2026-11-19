"""Public acceptance tests. In the starter, unimplemented work is skipped."""
import unittest
from src.generator import generate
from src.model import Grid
from src.registry import run_search


class EnvironmentTests(unittest.TestCase):
    def test_seed_is_reproducible(self):
        self.assertEqual(generate(81), generate(81))
        self.assertNotEqual(generate(81).cells, generate(82).cells)

    def test_invalid_maps_are_rejected(self):
        for data in [dict(cells=["..", "."], start=[0,0], goals=[[0,1]]),
                     dict(cells=[".#"], start=[0,1], goals=[[0,0]]),
                     dict(cells=[".."], start=[0,0], goals=[[0,1],[0,1]])]:
            with self.assertRaises(ValueError):
                Grid.from_dict(data)

    def test_entry_cost_and_neighbors(self):
        grid = Grid((".rh", ".#."), (0,0), ((0,2),))
        self.assertEqual(list(grid.neighbors((0,0))), [(0,1),(1,0)])
        self.assertEqual(grid.cost((0,1)), 5)
        self.assertEqual(grid.cost((0,1), "uniform"), 1)


class SearchTests(unittest.TestCase):
    def run_algorithm(self, grid, algorithm, mode="terrain"):
        result = run_search(grid, algorithm, mode)
        if result.status == "not_implemented":
            self.skipTest("Student TODO: " + algorithm)
        return result

    def test_bfs_shortest_steps(self):
        grid = Grid((".hhh.", "....."), (0,0), ((0,4),))
        result = self.run_algorithm(grid, "bfs")
        self.assertEqual(result.as_dict()["steps"], 4)
        self.assertEqual(result.cost, 31)

    def test_ucs_cheapest_detour(self):
        grid = Grid((".hhh.", "....."), (0,0), ((0,4),))
        result = self.run_algorithm(grid, "ucs")
        self.assertEqual(result.cost, 6)
        self.assertEqual(result.as_dict()["steps"], 6)

    def test_astar_cheapest_detour(self):
        grid = Grid((".hhh.", "....."), (0,0), ((0,4),))
        result = self.run_algorithm(grid, "astar")
        self.assertEqual(result.cost, 6)

    def test_no_solution(self):
        grid = Grid((".#.",), (0,0), ((0,2),))
        for algorithm in ("bfs", "ucs", "astar"):
            with self.subTest(algorithm=algorithm):
                result = self.run_algorithm(grid, algorithm)
                self.assertEqual(result.status, "no_path")
                self.assertEqual(result.path, [])
                self.assertIsNone(result.cost)

    def test_start_is_goal(self):
        grid = Grid(("h",), (0,0), ((0,0),))
        for algorithm in ("bfs", "ucs", "astar"):
            with self.subTest(algorithm=algorithm):
                result = self.run_algorithm(grid, algorithm)
                self.assertEqual(result.path, [[0,0]])
                self.assertEqual(result.cost, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
