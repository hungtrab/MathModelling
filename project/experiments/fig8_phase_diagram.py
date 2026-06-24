"""Reproduce Fig. 8: phase diagram in (G, S) for the symmetric case S1=S2.

Plots transition points (regular -> chaotic) for a grid of S values.
Above each transition point the motion is regular; below it is periodic /
chaotic.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from nagatani.analysis import transition_loading
from nagatani.plotting import save, setup_style


def run(out_name: str = "fig8_phase_diagram.png") -> Path:
    setup_style()
    S_values = np.linspace(0.0, 1.0, 41)

    transitions = []
    for S in S_values:
        Gc = transition_loading(S=S, G_min=0.0, G_max=2.0,
                                tol=2e-3, num_trips=1000, transient=900)
        transitions.append(Gc)

    transitions = np.asarray(transitions)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(transitions, S_values, "o-", color="black", ms=4)
    ax.set_xlabel("G  (loading)")
    ax.set_ylabel(r"$S_1=S_2$  (speed-up)")
    ax.set_title("Fig. 8 — Phase diagram: regular (above) vs periodic/chaotic (below)")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)

    # Annotate regions.
    ax.text(0.7, 0.8, "Regular", ha="center")
    ax.text(0.2, 0.1, "Periodic / Chaotic", ha="center")

    return save(fig, out_name)


if __name__ == "__main__":
    run()
