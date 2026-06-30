"""Sensitivity and robustness analysis (beyond the paper).

Two experiments:
  fig_sensitivity_ic.png  — same bifurcation diagram reproduced from 6 different
                            initial conditions; confirms the attractor is unique.
  fig_sensitivity_noise.png — bifurcation diagrams under additive Gaussian noise
                              on the headway at each trip; quantifies how robust
                              the chaos structure is to small perturbations.

Usage (from project/):
    .venv/bin/python -m experiments.fig_sensitivity
"""

from __future__ import annotations

import heapq

import numpy as np
import matplotlib.pyplot as plt

from nagatani.plotting import setup_style, save

# ── shared parameters matching the paper (S=(0.5,0.2) case) ─────────────────
G_AXIS = np.linspace(0.01, 1.8, 200)
S1, S2 = 0.5, 0.2
NUM_TRIPS = 1200
TRANSIENT = 1000
RNG_SEED = 42


# ── noise-aware simulator (inline, does not modify the package) ──────────────
def _simulate_noisy(G: float, S: tuple[float, float],
                    initial_arrivals: tuple[float, float],
                    noise_sigma: float = 0.0,
                    num_trips: int = NUM_TRIPS,
                    transient: int = TRANSIENT,
                    rng: np.random.Generator | None = None) -> np.ndarray:
    """Run M=2 simulation with optional additive N(0,sigma²) noise on H.

    Returns steady-state headway array for Bus 0 of shape (num_trips - transient,).
    Noise is added *after* computing the true headway but *before* computing
    the tour time — it models per-trip timing uncertainty.
    """
    if rng is None:
        rng = np.random.default_rng(RNG_SEED)

    T0, T1 = initial_arrivals
    heap: list[tuple[float, int, int]] = []
    heapq.heappush(heap, (T0, 0, 0))
    heapq.heappush(heap, (T1, 1, 0))

    prev_T: float = min(T0, T1) - 1.0 / 2  # so first headway ≈ 0.5
    S_arr = [S[0], S[1]]

    h_bus0: list[float] = []
    trip_count = [0, 0]

    total = 2 * num_trips
    for _ in range(total):
        T_cur, bus, m = heapq.heappop(heap)
        H = T_cur - prev_T

        # add noise before applying the map
        if noise_sigma > 0.0:
            H = H + rng.normal(0.0, noise_sigma)
            H = max(H, 1e-6)          # keep headway positive

        denom = 1.0 + S_arr[bus] * H
        if abs(denom) < 1e-15:
            break
        DT = G * H + 1.0 / denom
        T_next = T_cur + DT

        if m >= transient and bus == 0:
            h_bus0.append(H)

        prev_T = T_cur
        trip_count[bus] += 1
        if trip_count[bus] < num_trips:
            heapq.heappush(heap, (T_next, bus, m + 1))

    return np.array(h_bus0)


# ── Figure A: sensitivity to initial conditions ───────────────────────────────
def run_ic():
    """Six different initial conditions → should all yield the same attractor."""
    ic_cases = [
        ((1/3, 2/3), "default (1/3, 2/3)"),
        ((0.1, 0.9), "(0.1, 0.9)"),
        ((0.4, 0.6), "(0.4, 0.6) — close"),
        ((0.05, 0.5), "(0.05, 0.5)"),
        ((0.2, 0.8), "(0.2, 0.8)"),
        ((0.25, 0.75), "(0.25, 0.75)"),
    ]
    colors = plt.cm.tab10(np.linspace(0, 0.6, len(ic_cases)))

    setup_style()
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), sharex=True, sharey=True)
    fig.suptitle(
        r"Sensitivity to Initial Conditions: $H_1(m)$ vs $\Gamma$"
        "\n" r"$M=2,\; S_1=0.5,\; S_2=0.2$, six different $T_i(0)$",
        fontsize=11,
    )

    rng = np.random.default_rng(RNG_SEED)
    for ax, (ic, label), col in zip(axes.flat, ic_cases, colors):
        for G in G_AXIS:
            h = _simulate_noisy(G, (S1, S2), ic, noise_sigma=0.0, rng=rng)
            if len(h) == 0:
                continue
            if np.max(np.abs(h)) > 1e4:
                break
            ax.scatter([G] * len(h), h, s=0.3, color=col, rasterized=True)
        ax.set_title(label, fontsize=8)
        ax.set_xlim(0, 1.85)
        ax.set_ylim(0, 1.5)
        ax.set_xlabel(r"$\Gamma$", fontsize=9)
        ax.set_ylabel(r"$H_1(m)$", fontsize=9)

    fig.tight_layout()
    save(fig, "fig_sensitivity_ic")
    print("Saved fig_sensitivity_ic.png")


# ── Figure B: robustness to additive noise ────────────────────────────────────
def run_noise():
    """Four noise levels: sigma = 0, 0.005, 0.02, 0.05."""
    noise_levels = [0.0, 0.005, 0.02, 0.05]
    titles = [
        r"$\sigma=0$ (clean)",
        r"$\sigma=0.005$",
        r"$\sigma=0.02$",
        r"$\sigma=0.05$",
    ]
    ic = (1/3, 2/3)

    setup_style()
    fig, axes = plt.subplots(2, 2, figsize=(10, 8), sharex=True, sharey=True)
    fig.suptitle(
        r"Robustness to Additive Noise on $H$"
        "\n" r"$M=2,\; S_1=0.5,\; S_2=0.2$; noise $\xi \sim \mathcal{N}(0,\sigma^2)$ added per trip",
        fontsize=11,
    )

    for ax, sigma, title in zip(axes.flat, noise_levels, titles):
        rng = np.random.default_rng(RNG_SEED)
        for G in G_AXIS:
            h = _simulate_noisy(G, (S1, S2), ic, noise_sigma=sigma, rng=rng)
            if len(h) == 0:
                continue
            if np.max(np.abs(h)) > 1e4:
                break
            ax.scatter([G] * len(h), h, s=0.3, c="steelblue", rasterized=True)
        ax.set_title(title, fontsize=10)
        ax.set_xlim(0, 1.85)
        ax.set_ylim(0, 1.5)
        ax.set_xlabel(r"$\Gamma$", fontsize=9)
        ax.set_ylabel(r"$H_1(m)$", fontsize=9)

    # annotate first panel with transition markers
    Gamma_star = S2 / (1 + S2)   # ≈ 0.167, Point 1
    axes[0, 0].axvline(Gamma_star, color="red", lw=0.8, ls="--", alpha=0.7)
    axes[0, 0].text(Gamma_star + 0.02, 1.35, r"$\Gamma^*$", color="red", fontsize=8)

    fig.tight_layout()
    save(fig, "fig_sensitivity_noise")
    print("Saved fig_sensitivity_noise.png")


# ── main ─────────────────────────────────────────────────────────────────────
def run():
    run_ic()
    run_noise()


if __name__ == "__main__":
    run()
