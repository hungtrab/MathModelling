# Chaos Control and Schedule of Shuttle Buses

Course project for **Mathematical Modelling 2025.2** (Hanoi University of Science and Technology) reproducing all figures of:

> Takashi Nagatani (2006). *Chaos control and schedule of shuttle buses*. Physica A 371, 683–691. <https://doi.org/10.1016/j.physa.2006.04.056>

The paper models `M` shuttle buses that freely overtake each other on a single route between an Origin and a Destination. With a **loading parameter** Γ (passenger boarding rate) and a per-bus **speedup parameter** S_i, the dynamics reduce to a single non-linear map

```
T_i(m+1) = T_i(m) + Γ·H_i(m) + 1/(1 + S_i·H_i(m))
H_i(m)   = T_i(m) - T_{i'}(m')
```

that exhibits regular motion, period-adding bifurcations, and deterministic chaos depending on (Γ, S). This repository reproduces every figure in the paper from a single, tested event-driven simulator, extends the study from `M=2` to `M=3` buses, and includes a written report, presentation slides, and a browser-based interactive demo that generalises to any `M ∈ [2, 8]`.

## Repository layout

```
.
├── project/                    Python simulator, tests, and all figures (paper + extension)
│   ├── src/nagatani/            simulation.py, analysis.py (incl. bifurcation_sweep), plotting.py
│   ├── experiments/             fig2..fig8 (paper, M=2), fig9..fig11 (extension, M=3)
│   ├── tests/                   pytest suite
│   ├── notebooks/                reproduction.ipynb
│   └── docs/                    derivation.md, team_split.md
├── report/                      LaTeX report (main.tex / main.pdf)
├── slides/                      LaTeX beamer slides (main.tex VN / main_en.tex EN)
├── sim.html                     Standalone interactive browser demo (no build step, any M)
├── reimplement_2bus.ipynb       Standalone notebook: paper Fig. 2-8 (M=2)
├── reimplement_3bus.ipynb       Standalone notebook: M=3 extension (Fig. 9-11)
├── requirements.txt             Deps for the two notebooks above (numpy, matplotlib, tqdm, jupyter)
├── Chaos control and schedule of shuttle buses.pdf   Source paper
└── shuttle_bus_paper_vietnamese_guide_with_figures.pdf   Vietnamese reading guide
```

## Quick start

### Just want to read/run the notebooks (lightest path)

```bash
pip install -r requirements.txt
jupyter notebook reimplement_2bus.ipynb   # paper reproduction, M=2, Fig. 2-8
jupyter notebook reimplement_3bus.ipynb   # M=3 extension, Fig. 9-11
```

Both notebooks are fully self-contained (the nonlinear-map simulator is defined inline in the
first code cell of each — no dependency on `project/src`) and already contain saved outputs, so
they can be read without re-running. Re-running top-to-bottom regenerates every figure as a PNG
next to the notebook.

### Run the simulator and regenerate all figures

```bash
cd project
make setup               # create .venv and install the package
make figures-paper       # regenerate the paper's Fig. 2-8 (M=2) into project/results/
make figures-extension   # regenerate the M=3 extension's Fig. 9-11 into project/results/
make figures              # both of the above
make test                 # run the test suite
```

See [`project/README.md`](project/README.md) for the full command reference (including how to
regenerate a single figure or run a single test) and a description of the non-linear map and
simulator architecture.

### Try the interactive demo

Open `sim.html` directly in a browser — no build step required. It steps through the simulation
trip-by-trip, animates the buses on the route, and plots one live return map per bus. The number
of buses `M` (2-8) is itself an adjustable parameter: changing it regenerates the per-bus
`S_i`/`T_i(0)` inputs and the return-map grid, so the same page reproduces both the paper's `M=2`
figures and the `M=3` extension. Γ, total trips, and how many trailing trips to plot are also
adjustable.

### Build the report or slides

```bash
cd report && latexmk -pdf main.tex      # -> main.pdf
cd slides && latexmk -pdf main_en.tex   # -> main_en.pdf (English)
cd slides && latexmk -pdf main.tex      # -> main.pdf (Vietnamese)
```

The custom HUST beamer theme lives in `slides/hust_theme/`.

## Team

Tran Quang Hung, Le Gia Huy, Nguyen Hoang Son Tung — supervised by PhD. Bui Quoc Trung.
