<div align="center">

# 🚑 Rescue Robot AI — Uninformed & Informed Search

**Artificial Intelligence & Expert Systems (Fall 2026)**  

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Pygame-Visualizer-2EA44F?style=for-the-badge" alt="Pygame Visualizer" />
  <img src="https://img.shields.io/badge/Tests-11%20Passed-success?style=for-the-badge" alt="Unit Tests" />
  <img src="https://img.shields.io/badge/Algorithms-BFS%20%7C%20UCS%20%7C%20A*-orange?style=for-the-badge" alt="Algorithms" />
  <img src="https://img.shields.io/badge/Bonus-Greedy%20%7C%20Weighted%20A*%20%7C%20Multi--Rescue-8A2BE2?style=for-the-badge" alt="Bonus Tasks" />
</p>

<p>
  <a href="#-overview">Overview</a> •
  <a href="#-benchmark-results">Benchmark Results</a> •
  <a href="#-bonus-algorithms">Bonus Tasks</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-project-structure">Architecture</a>
</p>

</div>

---

## 📌 Overview

A reproducible, unit-tested Python implementation of **Uninformed** and **Informed** search algorithms for a grid-based **Rescue Robot** navigating a damaged building. The environment models traversable terrain types with distinct entry costs (`uniform` vs. `terrain`: normal `.` = `1`, rubble `r` = `5`, hazard `h` = `10`, wall `#` = impassable).

### Implemented Paradigms

<table>
  <tr>
    <th>Category</th>
    <th>Algorithm</th>
    <th>Priority / Strategy</th>
    <th>Optimality</th>
  </tr>
  <tr>
    <td><b>Core (Uninformed)</b></td>
    <td><code>BFS</code></td>
    <td>FIFO Queue (<code>collections.deque</code>) — fewest steps</td>
    <td>Optimal in <code>uniform</code> mode only</td>
  </tr>
  <tr>
    <td><b>Core (Uninformed)</b></td>
    <td><code>UCS</code></td>
    <td>Min-Heap on path cost <code>g(n)</code></td>
    <td>Optimal in both <code>uniform</code> &amp; <code>terrain</code></td>
  </tr>
  <tr>
    <td><b>Core (Informed)</b></td>
    <td><code>A*</code></td>
    <td>Min-Heap on <code>f(n) = g(n) + h(n)</code> (Manhattan heuristic)</td>
    <td>Optimal &amp; consistently admissible</td>
  </tr>
  <tr>
    <td><b>Bonus (Informed)</b></td>
    <td><code>Greedy Best-First</code></td>
    <td>Min-Heap on <code>h(n)</code> with cycle prevention</td>
    <td>Suboptimal (fast exploration)</td>
  </tr>
  <tr>
    <td><b>Bonus (Informed)</b></td>
    <td><code>Weighted A*</code></td>
    <td>Min-Heap on <code>f(n) = g(n) + w·h(n)</code> (<code>1 ≤ w ≤ 5</code>)</td>
    <td>Bounded suboptimality / speed trade-off</td>
  </tr>
  <tr>
    <td><b>Bonus (Multi-Goal)</b></td>
    <td><code>Multi-Rescue A*</code></td>
    <td>Augmented state <code>(row, col, rescued_mask)</code> + min-victim Manhattan heuristic</td>
    <td>Optimal minimum-cost multi-victim tour</td>
  </tr>
</table>

---

## 📊 Benchmark Results

All benchmarks below were executed in headless `--cli` mode on **Python 3.12** across public maps and 5 reproducible random seeds (`16×12`, `wall_density=0.22`). Execution times represent the **median of 3 runs**.

### Terrain Cost Mode Comparison (`BFS` vs `UCS` vs `A*`)

| Map / Seed | Algorithm | Status | Cost | Steps | Generated | Expanded | Peak Frontier | Median Time (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `two_rows.json` | `BFS` | `found` | 31 | 4 | 9 | 8 | 3 | 0.050 |
| `two_rows.json` | `UCS` / `A*` | `found` | **6** | 6 | 10 | **7** | 4 | 0.057 / 0.090 |
| `weighted_trap.json` | `BFS` | `found` | 102 | 12 | 38 | 36 | 3 | 0.193 |
| `weighted_trap.json` | `UCS` / `A*` | `found` | **16** | 16 | 34 / 33 | **33 / 32** | 3 | 0.210 / 0.219 |
| `medium_01.json` | `BFS` | `found` | 51 | 34 | 335 | 327 | 16 | 0.964 |
| `medium_01.json` | `UCS` | `found` | **38** | 34 | 343 | 333 | 20 | 1.288 |
| `medium_01.json` | `A*` | `found` | **38** | 34 | **219** | **176** | 49 | **0.804** |
| `seed42.json` | `BFS` | `found` | 46 | 26 | 154 | 154 | 13 | 0.505 |
| `seed42.json` | `UCS` | `found` | **32** | 28 | 151 | 144 | 25 | 0.537 |
| `seed42.json` | `A*` | `found` | **32** | 28 | **134** | **91** | 43 | **0.495** |
| `seed81.json` | `BFS` | `found` | 54 | 26 | 154 | 154 | 13 | 0.425 |
| `seed81.json` | `UCS` | `found` | **34** | 26 | 139 | 132 | 14 | 0.567 |
| `seed81.json` | `A*` | `found` | **34** | 26 | **103** | **86** | 22 | **0.445** |
| `no_solution.json` | `BFS` / `UCS` / `A*` | `no_path` | N/A | N/A | 47 / 47 / 48 | 47 | 13 | 0.222–0.290 |

> **Key Takeaway:** In `terrain` mode, `BFS` minimizes step count and falls into high-cost hazard traps (e.g., cost `102` vs `16` on `weighted_trap.json`), whereas `UCS` and `A*` find the optimal detour. `A*` significantly reduces node expansions (e.g., `176` vs `333` on `medium_01.json`) using an admissible and consistent Manhattan heuristic.

---

## 🚀 Bonus Algorithms

<details>
<summary><b>1. Weighted A* Weight Sensitivity (Click to expand results)</b></summary>
<br/>

Evaluating `f(n) = g(n) + w · h(n)` across weights `w ∈ {1, 1.5, 2, 3, 5}` in `terrain` mode:

| Map | Weight (`w`) | Cost | Steps | Expanded | Generated | Time (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `medium_01.json` | `1.0` | **38** | 34 | 176 | 219 | 0.880 |
| `medium_01.json` | `1.5` | 40 | 40 | 80 | 137 | 0.663 |
| `medium_01.json` | `2.0` | 42 | 42 | 74 | 130 | 0.462 |
| `medium_01.json` | `3.0` | 48 | 40 | 59 | 119 | 0.404 |
| `medium_01.json` | `5.0` | 48 | 40 | **51** | **107** | **0.383** |
| `seed105.json` | `1.0` | **60** | 34 | 153 | 162 | 0.846 |
| `seed105.json` | `1.5` | **60** | 34 | 130 | 163 | 0.634 |
| `seed105.json` | `2.0` | 62 | 32 | 71 | 109 | 0.637 |
| `seed105.json` | `3.0` | 65 | 30 | 43 | 70 | 0.330 |
| `seed105.json` | `5.0` | 70 | 26 | **32** | **53** | **0.265** |

</details>

<details>
<summary><b>2. Multi-Victim Rescue (<code>multi_rescue</code>) Results (Click to expand)</b></summary>
<br/>

Uses bitmask state `(row, col, rescued_mask)` with an admissible minimum-distance-to-remaining-victim heuristic on `8×8` generated maps (`terrain` mode):

| Map | Victims (`k`) | Optimal Cost | Steps | Expanded | Generated | Peak Frontier | Time (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `multi_v2.json` (`seed=10`) | 2 | **18** | 18 | 49 | 63 | 15 | 0.369 |
| `multi_v3.json` (`seed=20`) | 3 | **25** | 21 | 72 | 88 | 17 | 0.831 |
| `multi_v4.json` (`seed=30`) | 4 | **14** | 14 | 77 | 112 | 36 | 0.550 |

</details>

---

## ⚡ Quick Start

### 1. Setup & Installation
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```
---

### 2. Run Visualizer & CLI
```Bash

# Run with Pygame graphical visualizer
python main.py

# Headless CLI execution
python main.py --cli --map maps/weighted_trap.json --algorithm astar --mode terrain

# Run Weighted A* or Multi-Rescue
python main.py --cli --map maps/seed105.json --algorithm weighted_astar --mode terrain --weight 1.5
python main.py --cli --map maps/multi_v3.json --algorithm multi_rescue --mode terrain

# Save static PNG snapshot
python main.py --map maps/easy_01.json --snapshot result.png
```

### 3. Run Unit Tests
```Bash
python -m unittest discover -s tests -v
```

### 🗂️ Project Structure

```Bash
.
├── main.py                  # Entry point (GUI & CLI)
├── run_setup.py             # Default run configuration
├── config.json              # Bonus module feature flags
├── generate_map.py          # Reproducible map generator CLI
├── requirements.txt         # Dependencies (pygame)
├── report.pdf               # Full analytical & experimental report
├── src/
│   ├── model.py             # Grid environment, neighbors & cost rules
│   ├── contracts.py         # Recorder, SearchResult & path reconstruction
│   ├── heuristics.py        # Admissible & consistent Manhattan heuristic
│   ├── search.py            # Core algorithms: BFS, UCS, A*
│   ├── bonus.py             # Optional: Greedy, Weighted A*, Multi-Rescue
│   ├── generator.py         # Procedural map generator
│   ├── registry.py          # Algorithm dispatcher
│   ├── runner.py            # Execution & metrics printer
│   └── visualizer.py        # Pygame step-by-step animation engine
├── tests/
│   ├── test_public.py       # Public acceptance tests
│   └── test_student.py      # Custom unit tests (traps, no-path, heuristic)
└── maps/                    # JSON benchmark maps & generated seeds
```