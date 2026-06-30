"""Extension: return maps for M=3 buses, colour-coded by predecessor identity.

With M=2 there is only one possible predecessor (the other bus), so the
return map H(m+1) vs H(m) is a clean function of one variable. With M=3,
each bus's predecessor cycles between the *other two* buses depending on
the dynamics, so we colour each point by which bus was the immediate
predecessor to see whether this splits the attractor into sub-branches.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from nagatani.plotting import save, setup_style
from nagatani.simulation import simulate


def _predecessor_identity(result, bus_index):
    """Recover, for each recorded headway of `bus_index`, which other bus
    contributed it by re-deriving arrival order from arrival_time.

    Since SimulationResult does not store predecessor identity directly, we
    reconstruct it: at trip m, bus `bus_index`'s arrival time is
    arrival_time[bus_index, m]; the predecessor is whichever bus has the
    arrival time closest below it among all buses' arrival times.
    """
    M = result.M
    arr = result.arrival_time
    n = arr.shape[1]
    pred = np.full(n, -1, dtype=int)
    all_arrivals = []
    for b in range(M):
        for m in range(n):
            if np.isfinite(arr[b, m]):
                all_arrivals.append((arr[b, m], b, m))
    all_arrivals.sort()
    last_bus = {}
    last_seen = None
    for t, b, m in all_arrivals:
        if b == bus_index and last_seen is not None:
            pred[m] = last_seen
        last_seen = b
    return pred


def run(out_name: str = "fig10_three_bus_returnmap.png") -> Path:
    setup_style()
    S = (0.5, 0.3, 0.2)
    M = 3
    Gs = [0.2, 0.3, 0.5, 0.8]
    colors = {0: "#1f77b4", 1: "#ff7f0e", 2: "#2ca02c"}
    pred_labels = {0: "Bus 1", 1: "Bus 2", 2: "Bus 3"}

    fig, axes = plt.subplots(2, 2, figsize=(9, 8))
    for ax, G in zip(axes.flat, Gs):
        res = simulate(G=G, S=S, M=M, num_trips=2000, transient=1000)
        H = res.headway[0]
        pred = _predecessor_identity(res, 0)
        valid = np.isfinite(H[:-1]) & np.isfinite(H[1:])
        for p in (1, 2):  # bus 0's predecessor is never itself
            mask = valid & (pred[:-1] == p)
            ax.scatter(H[:-1][mask], H[1:][mask], s=2, color=colors[p],
                       label=f"prev. arrival = {pred_labels[p]}", alpha=0.6)
        lim = max(1.5, np.nanmax(H[np.isfinite(H)]) * 1.05) if np.any(np.isfinite(H)) else 1.5
        ax.plot([0, lim], [0, lim], color="gray", lw=0.8)
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_xlabel(r"$H_1(m)$")
        ax.set_ylabel(r"$H_1(m+1)$")
        ax.set_title(rf"$\Gamma = {G}$")
        ax.legend(fontsize=7, loc="upper left")

    fig.suptitle(r"Fig. 10 — Return maps of Bus 1's headway for $M=3$ ($S=(0.5,0.3,0.2)$), coloured by predecessor identity")
    fig.tight_layout()
    return save(fig, out_name)


if __name__ == "__main__":
    run()
