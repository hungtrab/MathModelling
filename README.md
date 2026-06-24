# Chaos Control and Schedule of Shuttle Buses

Course project for **Mathematical Modelling 2025.2** (Hanoi University of Science and Technology) reproducing all figures of:

> Takashi Nagatani (2006). *Chaos control and schedule of shuttle buses*. Physica A 371, 683–691. <https://doi.org/10.1016/j.physa.2006.04.056>

The paper models `M` shuttle buses that freely overtake each other on a single route between an Origin and a Destination. With a **loading parameter** Γ (passenger boarding rate) and a per-bus **speedup parameter** S_i, the dynamics reduce to a single non-linear map

```
T_i(m+1) = T_i(m) + Γ·H_i(m) + 1/(1 + S_i·H_i(m))
H_i(m)   = T_i(m) - T_{i'}(m')
```

that exhibits regular motion, period-adding bifurcations, and deterministic chaos depending on (Γ, S). This repository reproduces every figure in the paper from a single, tested event-driven simulator, and includes a written report, presentation slides, and a browser-based interactive demo.

## Repository layout

```
.
├── project/                    Python simulator, tests, and all paper figures
│   ├── src/nagatani/            simulation.py, analysis.py, plotting.py
│   ├── experiments/             one script per figure (fig2 … fig8)
│   ├── tests/                   pytest suite
│   ├── notebooks/                reproduction.ipynb
│   └── docs/                    derivation.md, team_split.md
├── report/                      LaTeX report (main.tex / main.pdf)
├── slides/                      LaTeX beamer slides (main.tex VN / main_en.tex EN)
├── sim.html                     Standalone interactive browser demo (no build step)
├── reimplement.ipynb            Working notebook used during development
├── Chaos control and schedule of shuttle buses.pdf   Source paper
└── shuttle_bus_paper_vietnamese_guide_with_figures.pdf   Vietnamese reading guide
```

## Quick start

### Run the simulator and regenerate all figures

```bash
cd project
make setup       # create .venv and install the package
make figures     # regenerate Fig. 2–8 into project/results/
make test        # run the test suite
```

See [`project/README.md`](project/README.md) for the full command reference and a description of the non-linear map and simulator architecture.

### Try the interactive demo

Open `sim.html` directly in a browser — no build step required. It steps through the simulation trip-by-trip, animates the buses on the route, and plots live return maps. Parameters Γ, S₁, S₂, T₁(0), T₂(0), total trips, and how many trailing trips to plot are all adjustable.

### Build the report or slides

```bash
cd report && latexmk -pdf main.tex      # -> main.pdf
cd slides && latexmk -pdf main_en.tex   # -> main_en.pdf (English)
cd slides && latexmk -pdf main.tex      # -> main.pdf (Vietnamese)
```

The custom HUST beamer theme lives in `slides/hust_theme/`.

## Team

Tran Quang Hung, Le Gia Huy, Nguyen Hoang Son Tung — supervised by PhD. Bui Quoc Trung.
