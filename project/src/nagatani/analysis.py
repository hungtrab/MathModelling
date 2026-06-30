"""Statistics over the steady-state window of a simulation.

The paper defines ``H_a, DT_a`` (means) and ``H_v, DT_v`` (root-mean-squares
about the mean) of headways and tour times taken over a window of trips
``m = 900..1000`` (Fig. 7). Here we let the user choose any window via the
``transient`` argument of :func:`nagatani.simulation.simulate`.
"""

from __future__ import annotations

import numpy as np

from .simulation import SimulationResult, simulate


def mean_headway(result: SimulationResult) -> np.ndarray:
    """Per-bus mean of recorded time headways. Shape ``(M,)``."""
    return np.nanmean(result.headway, axis=1)


def mean_tour_time(result: SimulationResult) -> np.ndarray:
    """Per-bus mean of recorded tour times. Shape ``(M,)``."""
    return np.nanmean(result.tour_time, axis=1)


def rms_headway(result: SimulationResult) -> np.ndarray:
    """Per-bus RMS deviation of headways from their mean. Shape ``(M,)``."""
    centred = result.headway - np.nanmean(result.headway, axis=1, keepdims=True)
    return np.sqrt(np.nanmean(centred**2, axis=1))


def rms_tour_time(result: SimulationResult) -> np.ndarray:
    """Per-bus RMS deviation of tour times. Shape ``(M,)``."""
    centred = result.tour_time - np.nanmean(result.tour_time, axis=1, keepdims=True)
    return np.sqrt(np.nanmean(centred**2, axis=1))


def bifurcation_sweep(
    *,
    M: int,
    S: float | tuple[float, ...],
    Gs: np.ndarray,
    num_trips: int = 1000,
    transient: int = 900,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Sweep loading values ``Gs`` and collect every recorded headway per bus.

    Generalises the bifurcation-diagram computation used by Fig. 2 (M=2) to
    arbitrary ``M``. ``S`` may be a scalar (broadcast to all buses) or a
    length-``M`` tuple of per-bus speedups.

    Returns a list of length ``M``; entry ``i`` is a tuple
    ``(G_values, headways)`` of matched 1-D arrays suitable for a scatter
    plot of bus ``i``'s headway against the loading parameter.
    """
    per_bus_G: list[list[np.ndarray]] = [[] for _ in range(M)]
    per_bus_H: list[list[np.ndarray]] = [[] for _ in range(M)]

    for G in Gs:
        res = simulate(G=G, S=S, M=M, num_trips=num_trips, transient=transient)
        for i in range(M):
            h = res.headway[i]
            h = h[np.isfinite(h)]
            if h.size == 0:
                continue
            per_bus_G[i].append(np.full_like(h, G))
            per_bus_H[i].append(h)

    out = []
    for i in range(M):
        if per_bus_G[i]:
            out.append((np.concatenate(per_bus_G[i]), np.concatenate(per_bus_H[i])))
        else:
            out.append((np.array([]), np.array([])))
    return out


def is_chaotic(
    result: SimulationResult,
    *,
    bus_index: int = 0,
    rms_threshold: float = 1e-3,
) -> bool:
    """Heuristic: a bus is in a non-regular regime when its tour-time RMS
    exceeds ``rms_threshold``.

    The paper uses this implicitly to draw transition curves in the phase
    diagram (Fig. 8). The threshold is small because numerical noise around
    a fixed point is essentially machine epsilon for this map.
    """
    return bool(rms_tour_time(result)[bus_index] > rms_threshold)


def transition_loading(
    S: float,
    *,
    G_min: float = 0.0,
    G_max: float = 1.0,
    tol: float = 1e-3,
    rms_threshold: float = 1e-3,
    num_trips: int = 1000,
    transient: int = 900,
    M: int = 2,
) -> float:
    """Find the transition loading ``G*`` between regular and chaotic regimes
    for the symmetric case ``S_1 = S_2 = S``.

    Uses bisection on the binary "is_chaotic" predicate. Returns the smallest
    ``G`` at which the bus 1 RMS exceeds ``rms_threshold``.
    """

    def chaotic(G: float) -> bool:
        res = simulate(G=G, S=S, M=M, num_trips=num_trips, transient=transient)
        return is_chaotic(res, rms_threshold=rms_threshold)

    if chaotic(G_min):
        return G_min
    if not chaotic(G_max):
        # Transition is above the search range.
        return G_max

    lo, hi = G_min, G_max
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if chaotic(mid):
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)
