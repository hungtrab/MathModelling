"""Reproduce Fig. 6: return map H_1(m+1) vs H_1(m) for trips m=1000..2000.

S1 = 0.5, S2 = 0.2; G in {0.2, 0.3, 0.5, 0.8}.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from nagatani.plotting import save, setup_style
from nagatani.simulation import simulate

GS = [0.2, 0.3, 0.5, 0.8]


def run(*, num_trips: int = 2000, transient: int = 1000,
        out_name: str = "fig6_return_map.png") -> Path:
    setup_style()
    fig, axes = plt.subplots(2, 2, figsize=(9, 8))

    for ax, G in zip(axes.ravel(), GS):
        res = simulate(G=G, S=(0.5, 0.2), M=2, num_trips=num_trips, transient=transient)
        h1 = res.headway[0]
        h1 = h1[np.isfinite(h1)]
        if h1.size < 2:
            continue
        ax.plot(h1[:-1], h1[1:], ".", ms=1.0, color="black")
        ax.set_xlabel(r"$H_1(m)$")
        ax.set_ylabel(r"$H_1(m+1)$")
        ax.set_title(rf"$G = {G}$")
        # Square aspect for return maps.
        ax.set_aspect("equal", adjustable="datalim")

    fig.suptitle(r"Fig. 6 — Return map of $H_1(m)$ ($S_1=0.5,\ S_2=0.2$, trips 1000–2000)")
    fig.tight_layout()
    return save(fig, out_name)


if __name__ == "__main__":
    run()
