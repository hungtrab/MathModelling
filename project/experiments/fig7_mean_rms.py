"""Reproduce Fig. 7: mean and RMS of headways and tour times vs G.

S1 = 0.5, S2 = 0.2. Two two-panel figures: (a)/(b) for means with full and
zoomed range, (c)/(d) for RMS values likewise.

Transition points (matching the paper):
  Point 1 — onset of non-regular motion (RMS first exceeds threshold)
  Point 2 — H₁ RMS crosses H₂ RMS
  Point 3 — tour-time RMS reaches its local minimum before increasing
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from nagatani import (
    mean_headway,
    mean_tour_time,
    rms_headway,
    rms_tour_time,
)
from nagatani.plotting import save, setup_style
from nagatani.simulation import simulate


def _scan(Gs, S=(0.5, 0.2), num_trips=1000, transient=900):
    H_mean = np.zeros((len(Gs), 2))
    DT_mean = np.zeros((len(Gs), 2))
    H_rms = np.zeros((len(Gs), 2))
    DT_rms = np.zeros((len(Gs), 2))
    for k, G in enumerate(Gs):
        res = simulate(G=G, S=S, M=2, num_trips=num_trips, transient=transient)
        H_mean[k] = mean_headway(res)
        DT_mean[k] = mean_tour_time(res)
        H_rms[k] = rms_headway(res)
        DT_rms[k] = rms_tour_time(res)
    return H_mean, DT_mean, H_rms, DT_rms


def _find_transition_points(Gs, H_rms, DT_rms):
    """Find the three transition points from RMS data."""
    # Point 1: first Γ where max RMS of headway exceeds threshold
    rms_max = np.maximum(H_rms[:, 0], H_rms[:, 1])
    pt1_idx = np.argmax(rms_max > 0.01)
    pt1 = Gs[pt1_idx] if pt1_idx > 0 else None

    # Point 2: first Γ (after point 1) where H1_rms crosses H2_rms
    diff = H_rms[:, 0] - H_rms[:, 1]
    pt2 = None
    start = pt1_idx + 5 if pt1_idx > 0 else 5
    for i in range(start, len(diff) - 1):
        if diff[i] * diff[i + 1] < 0:
            # linear interpolation
            t = diff[i] / (diff[i] - diff[i + 1])
            pt2 = Gs[i] + t * (Gs[i + 1] - Gs[i])
            break

    # Point 3: local minimum of tour-time RMS (sum of both buses) after point 1
    dt_rms_sum = DT_rms[:, 0] + DT_rms[:, 1]
    pt3 = None
    search_start = pt1_idx + 3 if pt1_idx > 0 else 3
    for i in range(search_start, len(dt_rms_sum) - 1):
        if dt_rms_sum[i] <= dt_rms_sum[i - 1] and dt_rms_sum[i] <= dt_rms_sum[i + 1] and dt_rms_sum[i] > 0.001:
            pt3 = Gs[i]
            break
    # fallback: first Γ after point 1 where tour-time RMS starts rising
    if pt3 is None:
        for i in range(search_start + 2, len(dt_rms_sum) - 1):
            if dt_rms_sum[i] > dt_rms_sum[i - 1] > dt_rms_sum[i - 2] and dt_rms_sum[i] > 0.005:
                pt3 = Gs[i - 1]
                break

    return pt1, pt2, pt3


def _annotate(ax, text, xy, xytext, color="black"):
    ax.annotate(
        text, xy=xy, xytext=xytext,
        fontsize=9, fontweight="bold", color=color,
        arrowprops=dict(arrowstyle="->", color=color, lw=1.2),
        ha="center", va="bottom",
    )


def run(out_name: str = "fig7_mean_rms.png") -> Path:
    setup_style()
    Gs_full = np.linspace(0.0, 2.0, 401)
    Gs_zoom = np.linspace(0.0, 0.5, 251)

    H_mean_f, DT_mean_f, H_rms_f, DT_rms_f = _scan(Gs_full)
    H_mean_z, DT_mean_z, H_rms_z, DT_rms_z = _scan(Gs_zoom)

    pt1, pt2, pt3 = _find_transition_points(Gs_zoom, H_rms_z, DT_rms_z)

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))

    (a, b), (c, d) = axes

    # --- (a) Means, full range ---
    a.plot(Gs_full, H_mean_f[:, 0], label=r"$H_{1a}$")
    a.plot(Gs_full, H_mean_f[:, 1], label=r"$H_{2a}$")
    a.plot(Gs_full, DT_mean_f[:, 0], "--", label=r"$\Delta T_{1a}$")
    a.plot(Gs_full, DT_mean_f[:, 1], "--", label=r"$\Delta T_{2a}$")
    a.set_xlabel("G")
    a.set_ylim(0, 3)
    a.set_ylabel("Mean values")
    a.set_title("(a) Means, full range")
    a.legend(fontsize=8)

    # --- (b) Means, zoom ---
    b.plot(Gs_zoom, H_mean_z[:, 0], label=r"$H_{1a}$")
    b.plot(Gs_zoom, H_mean_z[:, 1], label=r"$H_{2a}$")
    b.plot(Gs_zoom, DT_mean_z[:, 0], "--", label=r"$\Delta T_{1a}$")
    b.plot(Gs_zoom, DT_mean_z[:, 1], "--", label=r"$\Delta T_{2a}$")
    b.set_xlabel("G")
    b.set_ylim(0, 1.5)
    b.set_ylabel("Mean values")
    b.set_title(r"(b) Means, zoom $0<G<0.5$")
    b.legend(fontsize=8)

    # --- (c) RMS, full range ---
    c.plot(Gs_full, H_rms_f[:, 0], label=r"$H_{1v}$")
    c.plot(Gs_full, H_rms_f[:, 1], label=r"$H_{2v}$")
    c.plot(Gs_full, DT_rms_f[:, 0], "--", label=r"$\Delta T_{1v}$")
    c.plot(Gs_full, DT_rms_f[:, 1], "--", label=r"$\Delta T_{2v}$")
    c.set_xlabel("G")
    c.set_ylim(0, 1.5)
    c.set_ylabel("Rms's")
    c.set_title("(c) RMS, full range")
    c.legend(fontsize=8)

    # --- (d) RMS, zoom ---
    d.plot(Gs_zoom, H_rms_z[:, 0], label=r"$H_{1v}$")
    d.plot(Gs_zoom, H_rms_z[:, 1], label=r"$H_{2v}$")
    d.plot(Gs_zoom, DT_rms_z[:, 0], "--", label=r"$\Delta T_{1v}$")
    d.plot(Gs_zoom, DT_rms_z[:, 1], "--", label=r"$\Delta T_{2v}$")
    d.set_xlabel("G")
    d.set_ylim(0, 0.75)
    d.set_ylabel("Rms's")
    d.set_title(r"(d) RMS, zoom $0<G<0.5$")
    d.legend(fontsize=8)

    # --- Annotate transition points ---
    if pt1 is not None:
        # find y values at point 1 in zoom data
        i1 = np.argmin(np.abs(Gs_zoom - pt1))
        # (b) mean plot
        y1_mean = max(H_mean_z[i1, 0], H_mean_z[i1, 1])
        _annotate(b, "Point 1", (pt1, y1_mean), (pt1 + 0.06, y1_mean + 0.25))
        # (d) RMS plot
        y1_rms = max(H_rms_z[i1, 0], H_rms_z[i1, 1])
        _annotate(d, "Point 1", (pt1, y1_rms + 0.02), (pt1 + 0.04, y1_rms + 0.18))

    if pt2 is not None:
        i2 = np.argmin(np.abs(Gs_zoom - pt2))
        # (b) mean plot
        y2_mean = H_mean_z[i2, 0]
        _annotate(b, "Point 2", (pt2, y2_mean), (pt2 - 0.05, y2_mean - 0.30))
        # (d) RMS plot
        y2_rms = H_rms_z[i2, 0]
        _annotate(d, "2", (pt2, y2_rms), (pt2 + 0.01, y2_rms - 0.12))

    if pt3 is not None:
        i3 = np.argmin(np.abs(Gs_zoom - pt3))
        # (b) mean plot
        y3_mean = max(DT_mean_z[i3, 0], DT_mean_z[i3, 1])
        _annotate(b, "Point 3", (pt3, y3_mean), (pt3 + 0.06, y3_mean + 0.20))
        # (d) RMS plot
        y3_rms = max(DT_rms_z[i3, 0], DT_rms_z[i3, 1])
        _annotate(d, "Point 3", (pt3, y3_rms), (pt3 + 0.06, y3_rms + 0.18))

    fig.suptitle(r"Fig. 7 — Mean and RMS of headways and tour times ($S_1=0.5,\ S_2=0.2$)")
    fig.tight_layout()
    return save(fig, out_name)


if __name__ == "__main__":
    run()
