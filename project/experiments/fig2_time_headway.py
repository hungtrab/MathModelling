"""Reproduce Fig. 2: H_1(m) vs G for trips m=900..1000.

Four panels:
  (a) S1 = S2 = 0
  (b) S1 = S2 = 0.2
  (c) S1 = 0.3, S2 = 0.2
  (d) S1 = 0.5, S2 = 0.2

Range G in [0, 2] sampled at 401 points.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from nagatani.plotting import save, setup_style
from nagatani.simulation import simulate

CASES = [
    ("(a) $S_1=S_2=0$", (0.0, 0.0)),
    ("(b) $S_1=S_2=0.2$", (0.2, 0.2)),
    ("(c) $S_1=0.3,\\ S_2=0.2$", (0.3, 0.2)),
    ("(d) $S_1=0.5,\\ S_2=0.2$", (0.5, 0.2)),
]


def run(*, G_min: float = 0.0, G_max: float = 2.0, n_G: int = 401, num_trips: int = 1000,
        transient: int = 900, xlim: tuple[float, float] | None = None,
        out_name: str = "fig2_time_headway.png") -> Path:
    setup_style()
    Gs = np.linspace(G_min, G_max, n_G)

    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharey=False)
    for ax, (label, (S1, S2)) in zip(axes.ravel(), CASES):
        H1_all = []
        G_used = []
        for G in Gs:
            res = simulate(G=G, S=(S1, S2), M=2, num_trips=num_trips, transient=transient)
            h = res.headway[0]
            h = h[np.isfinite(h)]
            if h.size == 0:
                continue
            # Plot every recorded headway as a tiny dot at this G.
            G_used.append(np.full_like(h, G))
            H1_all.append(h)

        if G_used:
            G_used = np.concatenate(G_used)
            H1_all = np.concatenate(H1_all)
            ax.plot(G_used, H1_all, ".", ms=0.4, color="black", alpha=0.6)

        ax.set_title(label)
        ax.set_xlabel(r"$G$")
        ax.set_ylabel(r"$H_1(m)$")
        if xlim is not None:
            ax.set_xlim(*xlim)

    fig.suptitle("Fig. 2 — Time headway $H_1(m)$ vs loading parameter $G$ (trips 900–1000)")
    fig.tight_layout()
    return save(fig, out_name)


if __name__ == "__main__":
    run()
