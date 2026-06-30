# Guide On Reproducing Chaos Control and Schedule of Shuttle Buses


## Prerequisites

```bash
pip install -r requirements.txt
```
Requires Python ≥ 3.9.

---

## Files

| File | What it produces |
|---|---|
| `reimplement_2bus.ipynb` | Reproduces paper Figures 2–8 (M=2 buses) |
| `implement_3bus.ipynb` | Our M=3 extension: Figures 9–11 |
| `sensitivity_robustness.ipynb` | Sensitivity to initial conditions + robustness to noise (beyond the paper) |
| `requirements.txt` | `numpy`, `matplotlib`, `tqdm`, `jupyter` |
| `sim.html` | Interactive browser demo (open directly, no server needed) |

---

## `reimplement_2bus.ipynb` — Paper Figures 2–8

Run all cells top-to-bottom. Each figure is
saved as a PNG next to the notebook when the cell executes.

| Cell | Type | What it does |
|---|---|---|
| 1 | Markdown | Section header: setup |
| 2 | Code | *(Optional)* `pip install` one-liner if not using `requirements.txt` |
| 3 | Code | Imports (`numpy`, `matplotlib`, `heapq`, `tqdm`) and global constants: `NUM_TRIPS = 1200`, `DISCARD_TRIPS = 1000` |
| 4 | Markdown | Section header: simulator |
| 5 | Code | **Core simulator** — `simulate_all_metrics(gamma, S_params, ...)`: event-driven min-heap that iterates the nonlinear map `T_i(m+1) = T_i(m) + Γ·H + 1/(1+S_i·H)` for M=2 buses; returns per-bus headway, tour time, and RMS arrays |
| 6 | Markdown | Section header: Figure 2 |
| 7 | Code | **Figure 2** — bifurcation diagram `H₁(m)` vs Γ ∈ [0, 2] for four speedup cases: (a) S=0, (b) S=0.2, (c) S=(0.3, 0.2), (d) S=(0.5, 0.2) |
| 8 | Markdown | Section header: Figure 3 |
| 9 | Code | **Figure 3** — same bifurcation diagram zoomed to Γ ∈ [0, 0.5], showing period-adding bifurcations clearly |
| 10 | Markdown | Section header: Figure 4 |
| 11 | Code | **Figure 4** — tour time `DT₁(m)`, `DT₂(m)` vs Γ for S=(0.5, 0.2); shows asymmetric amplitude between buses |
| 12 | Markdown | Section header: Figure 5 |
| 13 | Code | **Figure 5** — tour time zoomed to Γ ∈ [0, 0.5]; transition points align with Figure 3 |
| 14 | Markdown | Section header: Figure 6 |
| 15 | Code | **Figure 6** — return map `H₁(m+1)` vs `H₁(m)` at Γ ∈ {0.2, 0.3, 0.5, 0.8}; period-11 orbit → piecewise-linear chaos structure |
| 16 | Markdown | Section header: Figure 7 |
| 17 | Code | **Figure 7** — mean and RMS of headway/tour time vs Γ; marks transition Points 1, 2, 3 numerically |
| 18 | Markdown | Section header: Figure 8 |
| 19 | Code | **Figure 8** — phase diagram Γ*(S) for S₁=S₂ (symmetric case); bisection search finds the regular/chaotic boundary for each S value |

---

## `implement_3bus.ipynb` — M=3 Extension (Figures 9–11)

| Cell | Type | What it does |
|---|---|---|
| 1 | Markdown | Section header: setup |
| 2 | Code | *(Optional)* `pip install` one-liner |
| 3 | Code | Imports and constants (`NUM_TRIPS = 1200`, `DISCARD_TRIPS = 1000`) |
| 4 | Markdown | Section header: M=2 simulator (needed for Figure 11 comparison) |
| 5 | Code | `simulate_all_metrics(...)` — same M=2 simulator as in `reimplement_2bus.ipynb`; kept here so this notebook is fully self-contained |
| 6 | Markdown | Section header: M=3 generalisation |
| 7 | Code | **`simulate_M(gamma, S_params, ...)`** — general-M simulator; `len(S_params)` determines the bus count automatically; same nonlinear map, same min-heap, now records predecessor bus identity per event; includes a self-check asserting M=2 output matches `simulate_all_metrics` |
| 8 | Markdown | Section header: Figure 9 |
| 9 | Code | **Figure 9 (a/b/c)** — bifurcation diagrams for M=3, three speedup cases: Case A S=(0,0,0), Case B S=(0.2,0.2,0.2), Case C S=(0.5,0.3,0.2); one column per bus, full range + zoom |
| 10 | Markdown | Section header: Figure 10 |
| 11 | Code | **Figure 10** — M=3 return map for Bus 1 at Γ ∈ {0.2, 0.3, 0.5, 0.8}, points coloured by predecessor identity (Bus 2 orange / Bus 3 green); shows the attractor becomes two-valued at high Γ |
| 12 | Markdown | Section header: Figure 11 |
| 13 | Code | **Figure 11** — phase boundary Γ*(S) for M=2 vs M=3 side-by-side; bisection on S at Γ=0 finds the critical speedup S_c beyond which chaos persists even with zero load (S_c ≈ 2.0 for M=2, S_c ≈ 1.6 for M=3); also plots mean/RMS comparison at S=0.3 |
| 14 | Markdown | **Conclusion** — explicit statement that M=3 generalises M=2: same map, same algorithm, same qualitative insights; only S_c drops and the return map gains a predecessor dimension |

---

## `sensitivity_robustness.ipynb` — Sensitivity & Robustness (Beyond the Paper)

Two experiments using the same M=2 parameters as Figure 2(d) (S₁=0.5, S₂=0.2).
The inline simulator adds an optional `noise_sigma` argument; no external package dependencies beyond `reimplement_2bus.ipynb`.

| Cell | Type | What it does |
|---|---|---|
| 1 | Markdown | Introduction: motivation and model recap |
| 2 | Code | Imports and shared constants: `S1=0.5`, `S2=0.2`, `G_AXIS` (200 points, Γ ∈ [0.01, 1.8]), `RNG_SEED=42` |
| 3 | Code | **`simulate_bus1_headway(..., noise_sigma, rng)`** — event-driven simulator returning steady-state headway of Bus 1; when `noise_sigma > 0`, adds $\xi \sim \mathcal{N}(0,\sigma^2)$ to each headway before evaluating the map; includes a quick sanity-check print |
| 4 | Markdown | Section: Sensitivity to Initial Conditions |
| 5 | Code | **Figure — IC sensitivity** — sweeps Γ ∈ [0.01, 1.8] for six initial-condition pairs ranging from nearly equal (1/3, 2/3) to strongly asymmetric (0.05, 0.5); plots 2×3 grid, each panel in a distinct colour; saves `fig_sensitivity_ic.png` |
| 6 | Markdown | Observation: all panels visually identical → attractor is unique, transient of 1000 trips is sufficient |
| 7 | Markdown | Section: Robustness to Additive Noise |
| 8 | Code | **Figure — noise robustness** — same Γ sweep repeated at σ ∈ {0, 0.005, 0.02, 0.05}; red dashed line marks Γ* ≈ 0.167; saves `fig_sensitivity_noise.png` |
| 9 | Markdown | Observation: chaos survives at 5% noise; fine periodic windows erode first |
| 10 | Markdown | Summary table of both experiments |

---

## Interactive Demo

Open `sim.html` directly in any browser — no installation, no server needed.

- Set **M** (2–8 buses), **Γ**, and per-bus **S_i** / initial arrival time **T_i(0)**.
- Set **Trips** (≥ 1000 recommended) and **Plot last N** to match the paper's
  transient-elimination methodology (paper uses trips 900–1000; default here
  uses last 200 of 1200).
- The page animates buses on the route, shows the live formula update for
  each event, and plots one return map per bus.
- Changing M regenerates the parameter inputs and return-map grid dynamically.
