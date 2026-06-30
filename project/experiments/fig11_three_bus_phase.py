"""Extension: phase boundary Gamma*(S) for M=2 vs M=3 (symmetric speedups),
plus a mean/RMS comparison, to quantify how adding a third bus shifts the
onset of chaos.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from nagatani.analysis import mean_headway, rms_headway, transition_loading
from nagatani.plotting import save, setup_style
from nagatani.simulation import simulate


def _critical_speedup(M, num_trips=1200, transient=1000):
    """Bisect on S to find the largest speedup for which Gamma=0 is still
    regular. Above this S, *no* loading value yields regular motion: the
    speedup mechanism itself destabilises the system (overcompensation)."""
    from nagatani.analysis import is_chaotic

    def chaotic_at_zero(S):
        res = simulate(G=0.0, S=S, M=M, num_trips=num_trips, transient=transient)
        return is_chaotic(res)

    lo, hi = 0.0, 5.0
    while not chaotic_at_zero(hi):
        hi *= 1.5
    for _ in range(25):
        mid = 0.5 * (lo + hi)
        if chaotic_at_zero(mid):
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def run(out_name: str = "fig11_three_bus_phase.png") -> Path:
    setup_style()
    S_values = np.linspace(0.05, 3.0, 30)

    Gc_M2 = np.array([
        transition_loading(S=S, G_min=0.0, G_max=2.0, tol=3e-3,
                            num_trips=1000, transient=900, M=2)
        for S in S_values
    ])
    Gc_M3 = np.array([
        transition_loading(S=S, G_min=0.0, G_max=2.0, tol=3e-3,
                            num_trips=1200, transient=1000, M=3)
        for S in S_values
    ])

    S_crit_M2 = _critical_speedup(2)
    S_crit_M3 = _critical_speedup(3)
    print(f"Critical speedup (regular region vanishes): M=2 -> S={S_crit_M2:.4f}, M=3 -> S={S_crit_M3:.4f}")

    # Mean/RMS headway comparison at fixed symmetric S=0.3 across Gamma.
    S_fixed = 0.3
    Gs = np.linspace(0.0, 1.0, 150)
    mean_M2, rms_M2 = [], []
    mean_M3, rms_M3 = [], []
    for G in Gs:
        r2 = simulate(G=G, S=S_fixed, M=2, num_trips=1000, transient=900)
        r3 = simulate(G=G, S=S_fixed, M=3, num_trips=1200, transient=1000)
        mean_M2.append(mean_headway(r2)[0])
        rms_M2.append(rms_headway(r2)[0])
        mean_M3.append(mean_headway(r3)[0])
        rms_M3.append(rms_headway(r3)[0])

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    ax = axes[0]
    ax.plot(Gc_M2, S_values, "o-", ms=4, label="$M=2$", color="#1f77b4")
    ax.plot(Gc_M3, S_values, "s-", ms=4, label="$M=3$", color="#d62728")
    ax.axhline(S_crit_M2, color="#1f77b4", ls=":", lw=1)
    ax.axhline(S_crit_M3, color="#d62728", ls=":", lw=1)
    ax.annotate(rf"$S_c={S_crit_M2:.2f}$", (0.85, S_crit_M2), color="#1f77b4",
                fontsize=8, va="bottom")
    ax.annotate(rf"$S_c={S_crit_M3:.2f}$", (0.85, S_crit_M3), color="#d62728",
                fontsize=8, va="top")
    ax.set_xlabel(r"$\Gamma^*$ (transition loading)")
    ax.set_ylabel(r"$S$ (symmetric speedup)")
    ax.set_title(r"Phase boundary: $M=2$ vs $M=3$" "\n(dotted: $S_c$ where regular region vanishes)")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 3.0)
    ax.legend(loc="lower right")

    ax = axes[1]
    ax.plot(Gs, mean_M2, color="#1f77b4", label="$M=2$, bus 1")
    ax.plot(Gs, mean_M3, color="#d62728", label="$M=3$, bus 1")
    ax.set_xlabel(r"$\Gamma$")
    ax.set_ylabel("Mean headway")
    ax.set_title(rf"Mean headway ($S={S_fixed}$ symmetric)")
    ax.legend()

    ax = axes[2]
    ax.plot(Gs, rms_M2, color="#1f77b4", label="$M=2$, bus 1")
    ax.plot(Gs, rms_M3, color="#d62728", label="$M=3$, bus 1")
    ax.set_xlabel(r"$\Gamma$")
    ax.set_ylabel("RMS headway")
    ax.set_title(rf"RMS headway ($S={S_fixed}$ symmetric)")
    ax.legend()

    fig.suptitle(r"Fig. 11 — Effect of bus count $M$ on the chaos boundary and headway statistics")
    fig.tight_layout()
    out = save(fig, out_name)

    # Print a short numeric summary for the report text.
    idx = np.argmin(np.abs(S_values - 0.3))
    print(f"At S={S_values[idx]:.2f}: Gamma*(M=2)={Gc_M2[idx]:.4f}, Gamma*(M=3)={Gc_M3[idx]:.4f}")
    idx_g = np.argmin(np.abs(Gs - 0.3))
    print(f"At Gamma={Gs[idx_g]:.2f}: mean_H(M=2)={mean_M2[idx_g]:.4f}, mean_H(M=3)={mean_M3[idx_g]:.4f}")

    return out


if __name__ == "__main__":
    run()
