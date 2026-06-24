# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This is a course project (Mathematical Modelling 2025.2) that reproduces all figures of:

> Takashi Nagatani (2006), *Chaos control and schedule of shuttle buses*, Physica A 371, 683–691.

The actual code lives in the `project/` subdirectory. The repo root also contains the source paper PDF and a working notebook (`reimplement.ipynb`), but all development happens under `project/`.

## Commands (run from `project/`)

```bash
make setup            # create .venv and pip install -e ".[dev]"
make figures          # regenerate all figures (Fig. 2-8) into results/
make test             # run pytest
make lint             # ruff check src experiments tests
make notebook         # open notebooks/reproduction.ipynb in JupyterLab
make clean            # remove results/*.png, .venv, __pycache__, .pytest_cache
```

To regenerate a single figure:

```bash
.venv/bin/python -m experiments.fig2_time_headway
```

To run a single test:

```bash
.venv/bin/python -m pytest tests/test_simulation.py::test_diverges_above_two
```

`conftest.py` adds `src/` to `sys.path`, so `nagatani` is importable without an editable install when running pytest directly.

## Architecture

The whole simulation is one non-linear map (Eq. 5 of the paper), derived in `project/docs/derivation.md`:

```
T_i(m+1) = T_i(m) + G * H_i(m) + 1 / (1 + S_i * H_i(m))
H_i(m)   = T_i(m) - T_{i'}(m')
```

where `T_i(m)` is bus `i`'s arrival time at the origin on trip `m`, `G` is the loading parameter, `S_i` is bus `i`'s speedup parameter, and `i'`/`m'` are the predecessor bus/trip — *not fixed in advance* because buses can overtake each other.

- **`src/nagatani/simulation.py`** — the core. `simulate(G, S, M=2, num_trips, transient, initial_arrivals)` runs an event-driven simulation using a min-heap of `(T, bus_id, trip)` events: pop the next-arriving bus, treat the previously-popped bus as its predecessor, compute headway `H` and tour time `DT = G*H + 1/(1+S_i*H)`, push the bus's next arrival back onto the heap. Returns a `SimulationResult` (frozen dataclass) with `headway`, `tour_time`, `arrival_time` arrays of shape `(M, num_trips)`. `.steady_state(transient=...)` drops initial transient trips (paper uses 900). `headway_diverged()` flags `G > 2` divergence.
- **`src/nagatani/analysis.py`** — statistics over `SimulationResult`: `mean_headway`, `mean_tour_time`, `rms_headway`, `rms_tour_time`, `is_chaotic` (RMS threshold heuristic), and `transition_loading` (bisection search for the regular/chaotic boundary `G*` given symmetric `S`, used for the Fig. 8 phase diagram).
- **`src/nagatani/plotting.py`** — shared matplotlib style (`setup_style()`) and `save(fig, name)` which writes PNGs (300 dpi) to `results/`.
- **`experiments/fig*.py`** — one script per paper figure (Fig. 2–8), each importing `simulate`/analysis functions and `nagatani.plotting`, exposing a `run(...)` function and a `__main__` entry point that calls it with paper-matching defaults. New figures should follow this same `run()` + `__main__` pattern.

### Key parameters used throughout

- `M` = number of buses (paper studies `M=2`)
- `G` = loading parameter, `S = (S1, S2, ...)` per-bus speedup
- `transient = 900`, `num_trips = 1000` reproduces the paper's `m = 900–1000` steady-state window
- `G >= 2` is expected to diverge (see "Why divergence at G = 2" in `docs/derivation.md`)

## Team workflow notes (`project/docs/team_split.md`)

The work is split three ways: simulator + tests + derivation, analysis/phase-diagram (Fig. 6–8), and Fig. 2–5 + notebook + report. Keep this division in mind when figuring out which files a change is likely to touch.
