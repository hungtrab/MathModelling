"""Reproduce Fig. 4: tour times DT_1(m), DT_2(m) vs G for S1=0.5, S2=0.2."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from nagatani.plotting import save, setup_style
from nagatani.simulation import simulate


def run(*, G_min: float = 0.0, G_max: float = 2.0, n_G: int = 401, num_trips: int = 1000,
        transient: int = 900, xlim: tuple[float, float] | None = None,
        out_name: str = "fig4_tour_time.png") -> Path:
    setup_style()
    Gs = np.linspace(G_min, G_max, n_G)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    for bus, ax in enumerate(axes):
        DT_all, G_all = [], []
        for G in Gs:
            res = simulate(G=G, S=(0.5, 0.2), M=2, num_trips=num_trips, transient=transient)
            dt = res.tour_time[bus]
            dt = dt[np.isfinite(dt)]
            if dt.size:
                DT_all.append(dt)
                G_all.append(np.full_like(dt, G))
        if G_all:
            ax.plot(np.concatenate(G_all), np.concatenate(DT_all),
                    ".", ms=0.4, color="black", alpha=0.6)
        ax.set_xlabel(r"$G$")
        ax.set_ylabel(rf"$\Delta T_{{{bus + 1}}}(m)$")
        ax.set_title(rf"({chr(ord('a') + bus)}) Bus {bus + 1}")
        if xlim is not None:
            ax.set_xlim(*xlim)

    fig.suptitle(r"Fig. 4 — Tour times vs $G$ ($S_1=0.5,\ S_2=0.2$, trips 900–1000)")
    fig.tight_layout()
    return save(fig, out_name)


if __name__ == "__main__":
    run()
