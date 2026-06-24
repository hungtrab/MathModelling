# Chaos Control of Shuttle Buses — Reproduction

A Python reproduction of:

> Takashi Nagatani (2006). *Chaos control and schedule of shuttle buses*. **Physica A** 371, 683–691. <https://doi.org/10.1016/j.physa.2006.04.056>

The paper studies `M` shuttle buses that may freely overtake each other on a single route. With a **loading parameter** `G` (ride boarding rate) and **speedup parameter** `S_i` (per-bus catch-up factor), the bus dynamics is reduced to a simple non-linear map that exhibits regular, periodic, and **deterministic chaos** depending on the parameters. We reproduce all figures of the paper from a single, well-tested simulator.

---

## 1. Quick start

```bash
make setup            # creates .venv and installs deps
make figures          # reproduces Fig. 2, 3, 4, 5, 6, 7, 8 → results/
make test             # runs unit tests
make notebook         # opens the reproduction notebook
```

To regenerate a specific figure only:

```bash
python -m experiments.fig2_time_headway
python -m experiments.fig6_return_map
```

All output goes to `results/` (PNG, 300 dpi).

---

## 2. The non-linear map (Eq. 5 of the paper)

Each bus `i ∈ {1, …, M}` has a dimensionless arrival time `T_i(m)` at the origin at trip `m`. The map is

```
T_i(m+1) = T_i(m) + G * (T_i(m) - T_{i'}(m'))
                  + 1 / (1 + S_i * (T_i(m) - T_{i'}(m')))
```

where `i'` is the bus that arrived at the origin **immediately before** bus `i` at trip `m`, and `m'` its corresponding trip number.

We define the **time headway** `H_i(m) = T_i(m) - T_{i'}(m')` and the **tour time** `DT_i(m) = T_i(m+1) - T_i(m)`.

| Figure | Quantity | Parameters |
|---|---|---|
| Fig. 2 | `H_1(m)` vs `G ∈ [0, 2]` for trips `m = 900–1000` | (a) `S₁=S₂=0`, (b) `S₁=S₂=0.2`, (c) `S₁=0.3, S₂=0.2`, (d) `S₁=0.5, S₂=0.2` |
| Fig. 3 | Same as Fig. 2 zoomed to `G ∈ [0, 0.5]` | — |
| Fig. 4 | Tour times `DT_1(m), DT_2(m)` vs `G` | `S₁=0.5, S₂=0.2` |
| Fig. 5 | Fig. 4 zoomed to `G ∈ [0, 0.5]` | — |
| Fig. 6 | Return map `H₁(m+1)` vs `H₁(m)`, `m = 1000–2000` | `S₁=0.5, S₂=0.2`; `G ∈ {0.2, 0.3, 0.5, 0.8}` |
| Fig. 7 | Mean (`H_a, DT_a`) and RMS (`H_v, DT_v`) vs `G` | `S₁=0.5, S₂=0.2` |
| Fig. 8 | Phase diagram in `(G, S₁)` for `S₁ = S₂` (transition between regular and chaotic) | — |

---

## 3. Repository layout

```
project/
├── README.md
├── pyproject.toml          # package metadata + deps
├── Makefile                # convenient commands
├── src/nagatani/
│   ├── __init__.py
│   ├── simulation.py       # core non-linear map iterator
│   ├── analysis.py         # mean/rms, transition detection
│   └── plotting.py         # consistent matplotlib style
├── experiments/            # one script per paper figure
│   ├── fig2_time_headway.py
│   ├── fig3_zoom.py
│   ├── fig4_tour_time.py
│   ├── fig5_zoom.py
│   ├── fig6_return_map.py
│   ├── fig7_mean_rms.py
│   └── fig8_phase_diagram.py
├── notebooks/reproduction.ipynb
├── tests/test_simulation.py
├── results/                # generated figures (PNG)
└── docs/
    ├── derivation.md
    └── team_split.md
```

---

## 4. How the simulator works (1-paragraph summary)

`src/nagatani/simulation.py` runs an **event-driven** version of the map. We keep a min-heap of `(T_j, j, m_j)` events and repeatedly pop the next-arriving bus. The bus we popped *immediately before* is its predecessor `i'`. Time headway `H` and tour time `DT` are recorded per bus per trip. The first event has no predecessor — its data is dropped. We discard a configurable transient (default `900` trips) before computing statistics, mirroring the paper's `m = 900–1000` window.

This formulation handles arbitrary `M ≥ 2` and arbitrary per-bus `S_i`.

---

## 5. Reference & team

- Paper: T. Nagatani, *Physica A* 371 (2006) 683–691.
- Code: this repository, MIT License (see `LICENSE`).
- Course: Mathematical Modelling 2025.2, group of 3.

Suggested split — see [`docs/team_split.md`](docs/team_split.md).
