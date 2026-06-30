# Chaos Control of Shuttle Buses — Reproduction

A Python reproduction of:

> Takashi Nagatani (2006). *Chaos control and schedule of shuttle buses*. **Physica A** 371, 683–691. <https://doi.org/10.1016/j.physa.2006.04.056>

The paper studies `M` shuttle buses that may freely overtake each other on a single route. With a **loading parameter** `G` (ride boarding rate) and **speedup parameter** `S_i` (per-bus catch-up factor), the bus dynamics is reduced to a simple non-linear map that exhibits regular, periodic, and **deterministic chaos** depending on the parameters. We reproduce all figures of the paper from a single, well-tested simulator.

---

## 1. Quick start — reproducing everything

```bash
make setup              # 1. create .venv and install this package (editable) + dev deps
make figures-paper      # 2. reproduce the paper's Fig. 2-8 (M=2)            -> results/
make figures-extension  # 3. reproduce our M=3 extension, Fig. 9-11         -> results/
make test                # 4. run the test suite (pytest)
```

`make figures` runs both `figures-paper` and `figures-extension` in one go. `make setup` is a
prerequisite of every other target and is run automatically if you forget it.

If you don't have `make`, the equivalent manual steps from `project/` are:

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest                              # tests
.venv/bin/python -m experiments.fig2_time_headway        # any single figure
```

### Regenerating one figure at a time

Every script in `experiments/` is runnable on its own and always prints the path it wrote to. Run with `-m` from `project/` (so the `nagatani` package on `src/` resolves), e.g.:

```bash
.venv/bin/python -m experiments.fig2_time_headway     # Fig. 2: bifurcation diagrams (M=2)
.venv/bin/python -m experiments.fig3_zoom             # Fig. 3: zoom 0<G<0.5
.venv/bin/python -m experiments.fig4_tour_time        # Fig. 4: tour times
.venv/bin/python -m experiments.fig5_zoom             # Fig. 5: tour-time zoom
.venv/bin/python -m experiments.fig6_return_map       # Fig. 6: return maps
.venv/bin/python -m experiments.fig7_mean_rms         # Fig. 7: mean/RMS + Points 1-3
.venv/bin/python -m experiments.fig8_phase_diagram    # Fig. 8: phase diagram (M=2)
.venv/bin/python -m experiments.fig9_three_bus_bifurcation  # Fig. 9a/9b/9c: M=3 bifurcations
.venv/bin/python -m experiments.fig10_three_bus_returnmap   # Fig. 10: M=3 return map (2-valued)
.venv/bin/python -m experiments.fig11_three_bus_phase       # Fig. 11: M=2 vs M=3 phase boundary
```

`fig9_three_bus_bifurcation.py` regenerates all three speedup cases (A/B/C) by default
(`python -m experiments.fig9_three_bus_bifurcation` calls `run_all()`); to regenerate a single
case, import it and call `bifurcation_case(S, title, out_name)` directly, or `run(case="B")`.

To run a single test instead of the whole suite:

```bash
.venv/bin/python -m pytest tests/test_simulation.py::test_diverges_above_two
```

All figure output goes to `results/` (PNG, 300 dpi). `conftest.py` adds `src/` to `sys.path`, so
`import nagatani` works without `pip install -e .` if you only want to run `pytest` directly.

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

## 3. Extension: M=3 buses (not in the paper)

The map above is implemented with no assumption on `M`; `simulate(G, S, M=3, ...)` runs exactly
the same algorithm, just with the predecessor `i'` now chosen among two other buses instead of
one. `experiments/fig9_three_bus_bifurcation.py` exposes a shared, M-agnostic helper,
`nagatani.bifurcation_sweep(M, S, Gs, ...)`, used by every bifurcation figure (Fig. 2 included).

| Figure | Quantity | Parameters |
|---|---|---|
| Fig. 9a/9b/9c | Bifurcation diagrams, one column per bus, `M=3` | Case A `S=(0,0,0)`, Case B `S=(0.2,0.2,0.2)`, Case C `S=(0.5,0.3,0.2)` — direct M=3 analogues of Fig. 2(a)/(b)/(d) |
| Fig. 10 | Bus 1's return map, `M=3`, points coloured by predecessor identity | `S=(0.5,0.3,0.2)`; `G ∈ {0.2, 0.3, 0.5, 0.8}` |
| Fig. 11 | Phase boundary `Γ*(S)` for `M=2` vs `M=3`, plus mean/RMS comparison and the critical speedup `S_c` (regular region vanishes) | symmetric `S`, and `S=0.3` fixed for the mean/RMS panels |

See `report/main.tex` Section 6 for the full write-up and `slides/main_en.tex` for the
presentation version of these results.

---

## 4. Repository layout

```
project/
├── README.md
├── pyproject.toml          # package metadata + deps
├── Makefile                # convenient commands
├── src/nagatani/
│   ├── __init__.py
│   ├── simulation.py       # core non-linear map iterator (any M >= 2)
│   ├── analysis.py         # mean/rms, transition detection, bifurcation_sweep(M, S, ...)
│   └── plotting.py         # consistent matplotlib style
├── experiments/            # one script per figure; each is runnable standalone
│   ├── fig2_time_headway.py        # M=2, paper Fig. 2
│   ├── fig3_zoom.py                # M=2, paper Fig. 3
│   ├── fig4_tour_time.py           # M=2, paper Fig. 4
│   ├── fig5_zoom.py                # M=2, paper Fig. 5
│   ├── fig6_return_map.py          # M=2, paper Fig. 6
│   ├── fig7_mean_rms.py            # M=2, paper Fig. 7 (+ Points 1/2/3)
│   ├── fig8_phase_diagram.py       # M=2, paper Fig. 8
│   ├── fig9_three_bus_bifurcation.py   # M=3 extension, Cases A/B/C
│   ├── fig10_three_bus_returnmap.py    # M=3 extension, predecessor-coloured return map
│   └── fig11_three_bus_phase.py        # M=3 extension, phase boundary + critical S_c
├── notebooks/reproduction.ipynb
├── tests/test_simulation.py
├── results/                # generated figures (PNG, git-ignored — regenerate with `make figures`)
└── docs/
    ├── derivation.md
    └── team_split.md
```

---

## 5. How the simulator works (1-paragraph summary)

`src/nagatani/simulation.py` runs an **event-driven** version of the map. We keep a min-heap of `(T_j, j, m_j)` events and repeatedly pop the next-arriving bus. The bus we popped *immediately before* is its predecessor `i'`. Time headway `H` and tour time `DT` are recorded per bus per trip. The first event has no predecessor — its data is dropped. We discard a configurable transient (default `900` trips) before computing statistics, mirroring the paper's `m = 900–1000` window.

This formulation handles arbitrary `M ≥ 2` and arbitrary per-bus `S_i` with **no code change** —
`M=3` (Section 3 above) calls the exact same `simulate()` function as `M=2`.

---

## 6. Interactive demo

`../sim.html` (repo root, one level up from `project/`) is a standalone, no-build-step browser
demo of the same map. Open it directly in a browser — no server needed. It now generalises to
any `M ∈ [2, 8]`: choosing a bus count regenerates the per-bus `S_i`/`T_i(0)` input rows and the
per-bus return-map grid. Use it to interactively reproduce either the `M=2` paper figures or the
`M=3` extension above by setting `M`, `Γ`, and the `S_i` listed in the table in Section 3.

---

## 7. Reference & team

- Paper: T. Nagatani, *Physica A* 371 (2006) 683–691.
- Code: this repository, MIT License (see `LICENSE`).
- Course: Mathematical Modelling 2025.2, group of 3.

Suggested split — see [`docs/team_split.md`](docs/team_split.md).
