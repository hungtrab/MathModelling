"""Extension: bifurcation diagrams for M=3 buses, for several speedup cases.

The paper only studies M=2. The simulator's M parameter already generalises
(simulation.py imposes no restriction on M >= 2); this script exercises that
generality across three speedup configurations for three buses, directly
paralleling the M=2 cases of Fig. 2(a)/(b)/(d):

  Case A: S = (0, 0, 0)          -- no speedup at all (cf. Fig. 2a, M=2)
  Case B: S = (0.2, 0.2, 0.2)    -- equal, moderate speedup (cf. Fig. 2b, M=2)
  Case C: S = (0.5, 0.3, 0.2)    -- graded/asymmetric speedup (cf. Fig. 2d, M=2)

`bifurcation_case` is the single building block (one M, one S-tuple, one
figure); `run` calls it once per case so each is its own named output, and
`run_all` is a convenience wrapper for `make figures`.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from nagatani import bifurcation_sweep
from nagatani.plotting import save, setup_style

CASES = {
    "A": dict(S=(0.0, 0.0, 0.0), out="fig9a_three_bus_S0.png",
              title=r"Case A: $S=(0,0,0)$ — no speedup"),
    "B": dict(S=(0.2, 0.2, 0.2), out="fig9b_three_bus_S0.2.png",
              title=r"Case B: $S=(0.2,0.2,0.2)$ — equal moderate speedup"),
    "C": dict(S=(0.5, 0.3, 0.2), out="fig9c_three_bus_graded.png",
              title=r"Case C: $S=(0.5,0.3,0.2)$ — graded speedup"),
}


def bifurcation_case(
    S: tuple[float, ...],
    title: str,
    out_name: str,
    *,
    M: int = 3,
    num_trips: int = 1200,
    transient: int = 1000,
    n_full: int = 250,
    n_zoom: int = 200,
) -> Path:
    """Generate one M-bus bifurcation figure (full range + zoom) for a given S."""
    setup_style()
    Gs_full = np.linspace(0.0, 2.0, n_full)
    Gs_zoom = np.linspace(0.0, 0.5, n_zoom)

    full = bifurcation_sweep(M=M, S=S, Gs=Gs_full, num_trips=num_trips, transient=transient)
    zoom = bifurcation_sweep(M=M, S=S, Gs=Gs_zoom, num_trips=num_trips, transient=transient)

    fig, axes = plt.subplots(2, M, figsize=(4.3 * M, 6.5), sharey="row")
    if M == 1:
        axes = axes.reshape(2, 1)
    colors = plt.cm.tab10(np.linspace(0, 1, max(M, 3)))

    for i in range(M):
        ax = axes[0, i]
        G_used, H_used = full[i]
        ax.scatter(G_used, H_used, s=0.3, color=colors[i], alpha=0.5)
        ax.set_xlabel(r"$\Gamma$")
        ax.set_title(f"Bus {i+1} ($S_{{{i+1}}}={S[i]}$)")
        if i == 0:
            ax.set_ylabel("Headway")
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 6)

        ax2 = axes[1, i]
        G_used_z, H_used_z = zoom[i]
        ax2.scatter(G_used_z, H_used_z, s=0.3, color=colors[i], alpha=0.5)
        ax2.set_xlabel(r"$\Gamma$")
        if i == 0:
            ax2.set_ylabel("Headway")
        ax2.set_xlim(0, 0.5)
        ax2.set_ylim(0, 2)

    fig.suptitle(f"{title} — full range (top), zoom $0<\\Gamma<0.5$ (bottom)")
    fig.tight_layout()
    return save(fig, out_name)


def run(case: str = "C", out_name: str | None = None) -> Path:
    """Default entry point (kept for `python -m experiments.fig9...`):
    regenerates Case C (the original graded-speedup M=3 figure)."""
    cfg = CASES[case]
    return bifurcation_case(cfg["S"], cfg["title"], out_name or cfg["out"])


def run_all() -> list[Path]:
    """Regenerate all three M=3 speedup cases (A, B, C)."""
    return [bifurcation_case(cfg["S"], cfg["title"], cfg["out"]) for cfg in CASES.values()]


if __name__ == "__main__":
    run_all()
