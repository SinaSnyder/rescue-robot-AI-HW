import json
import statistics
import subprocess
import sys

maps = [
    "maps/two_rows.json",
    "maps/easy_01.json",
    "maps/easy_02.json",
    "maps/medium_01.json",
    "maps/weighted_trap.json",
    "maps/no_solution.json",
    "maps/seed11.json",
    "maps/seed25.json",
    "maps/seed42.json",
    "maps/seed81.json",
    "maps/seed105.json",
]

algorithms = ["bfs", "ucs", "astar"]
modes = ["uniform", "terrain"]

rows = []
for m in maps:
    for mode in modes:
        for alg in algorithms:
            times = []
            last_data = None
            for _ in range(3):
                proc = subprocess.run(
                    [sys.executable, "main.py", "--cli", "--map", m, "--algorithm", alg, "--mode", mode],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                data = json.loads(proc.stdout)
                times.append(data["elapsed_ms"])
                last_data = data
            med_ms = round(statistics.median(times), 3)
            cost_str = "Not found" if last_data["cost"] is None else str(last_data["cost"])
            steps_str = "Not found" if last_data["status"] == "no_path" else str(last_data["steps"])
            rows.append((m, mode, alg, last_data["status"], cost_str, steps_str,
                         last_data["generated"], last_data["expanded"], last_data["frontier_peak"], med_ms))

print("map | mode | alg | status | cost | steps | generated | expanded | frontier_peak | median_ms")
for r in rows:
    print(" | ".join(str(x) for x in r))