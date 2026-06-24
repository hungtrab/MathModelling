"""Event-driven simulator for the Nagatani (2006) shuttle bus map.

The dimensionless map (Eq. 5 of the paper) is::

    T_i(m+1) = T_i(m) + G * H + 1 / (1 + S_i * H)

with the time headway::

    H = T_i(m) - T_{i'}(m')

where ``i'`` is the bus that arrived at the origin immediately *before* bus
``i`` at trip ``m``.

Because buses are allowed to overtake each other freely, the *order* of
arrivals at the origin changes over time. We therefore run an event-driven
simulation: at each step we pop the next-arriving bus from a min-heap, treat
the previously popped bus as its predecessor, and push the bus's next
arrival time back onto the heap.

This implementation supports:

*   Arbitrary number of buses ``M >= 2``.
*   Arbitrary per-bus speed-up parameters ``S_i``.
*   A common loading parameter ``G``.
"""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Sequence

import numpy as np

# A diverging headway means the loading-speedup balance has broken down.
# We hard-cap to avoid overflow in 1 / (1 + S * H) when S < 0 (not used in
# the paper but useful for robustness).
_HEADWAY_CAP = 1e12


@dataclass(frozen=True)
class SimulationResult:
    """Per-bus headway and tour-time histories.

    Attributes
    ----------
    headway:
        ``(M, num_trips)`` array. ``headway[i, m]`` is the time headway of
        bus ``i`` at its ``m``-th recorded trip. The first headway for each
        bus is undefined (no predecessor) and is filled with ``NaN``.
    tour_time:
        ``(M, num_trips)`` array of tour times (``T_i(m+1) - T_i(m)``).
        ``NaN`` when not yet defined (last entry of each bus).
    arrival_time:
        ``(M, num_trips)`` array of arrival times ``T_i(m)``.
    M:
        Number of buses.
    G:
        Loading parameter used.
    S:
        Per-bus speed-up parameters.
    """

    headway: np.ndarray
    tour_time: np.ndarray
    arrival_time: np.ndarray
    M: int
    G: float
    S: np.ndarray

    def steady_state(self, *, transient: int = 900) -> "SimulationResult":
        """Return a copy with the first ``transient`` trips dropped."""
        return SimulationResult(
            headway=self.headway[:, transient:],
            tour_time=self.tour_time[:, transient:],
            arrival_time=self.arrival_time[:, transient:],
            M=self.M,
            G=self.G,
            S=self.S,
        )


def _initial_arrivals(M: int) -> np.ndarray:
    """Evenly spaced initial arrival times in (0, 1)."""
    # Spacing 1/M means the first 'pop' has predecessor at T = 0 (we drop it
    # because the predecessor isn't a real bus).
    return np.arange(1, M + 1, dtype=float) / (M + 1)


def simulate(
    G: float,
    S: float | Sequence[float],
    *,
    M: int = 2,
    num_trips: int = 1000,
    transient: int = 0,
    initial_arrivals: np.ndarray | None = None,
) -> SimulationResult:
    """Iterate the Nagatani map for ``M`` buses over ``num_trips`` trips.

    Parameters
    ----------
    G:
        Loading parameter.
    S:
        Speed-up parameter. A scalar broadcasts to all buses; otherwise a
        sequence of length ``M``.
    M:
        Number of buses (default 2 — the case studied in the paper).
    num_trips:
        Number of trips per bus to record.
    transient:
        Drop this many initial trips before returning. Mirrors the paper's
        steady-state window (e.g. ``900`` to keep trips 900–1000).
    initial_arrivals:
        Optional initial arrival times ``T_i(0)``. Defaults to evenly
        spaced values in ``(0, 1)``.

    Returns
    -------
    SimulationResult
        Headway, tour-time and arrival-time arrays of shape ``(M, num_trips - transient)``.
    """
    if M < 2:
        raise ValueError("M must be >= 2 (at least two buses are required for overtaking).")
    if num_trips < 1:
        raise ValueError("num_trips must be positive.")

    if np.isscalar(S):
        S_arr = np.full(M, float(S))
    else:
        S_arr = np.asarray(S, dtype=float)
        if S_arr.shape != (M,):
            raise ValueError(f"S must be scalar or length {M}, got {S_arr.shape}")

    if initial_arrivals is None:
        T0 = _initial_arrivals(M)
    else:
        T0 = np.asarray(initial_arrivals, dtype=float)
        if T0.shape != (M,):
            raise ValueError(f"initial_arrivals must have length {M}")

    # Per-bus storage. Pre-allocate one extra trip so we can compute tour
    # time as t[m+1] - t[m] without bounds checks.
    arrival = np.full((M, num_trips + 1), np.nan)
    headway = np.full((M, num_trips), np.nan)
    arrival[:, 0] = T0

    # Trip counter per bus.
    m_counter = np.zeros(M, dtype=int)

    # Event heap: (T, bus_id, trip_at_pop). The trip_at_pop is the trip
    # number that this T corresponds to for that bus.
    heap: list[tuple[float, int, int]] = []
    for i in range(M):
        heappush(heap, (T0[i], i, 0))

    prev_T: float | None = None  # arrival time of the previously popped bus

    # We pop M * num_trips events total (each bus is popped num_trips times).
    total_events = M * num_trips
    for step in range(total_events):
        T_i, i, m = heappop(heap)

        if prev_T is None:
            # First event: no predecessor in the simulation, skip recording.
            prev_T = T_i
            # We still advance bus i but with H=0 to seed it (this is a
            # transient that will be discarded — paper uses transient=900).
            H = 0.0
        else:
            H = T_i - prev_T

        # Defensive cap.
        H = float(np.clip(H, -_HEADWAY_CAP, _HEADWAY_CAP))

        # Tour time = G*H + 1/(1+S_i*H)
        denom = 1.0 + S_arr[i] * H
        if abs(denom) < 1e-15:
            # Singular regime — record divergence and stop pushing this bus.
            DT = np.inf
        else:
            DT = G * H + 1.0 / denom

        T_next = T_i + DT

        if m < num_trips:
            headway[i, m] = H
            # arrival[:, 0] is initial; record next arrival at column m+1.
            arrival[i, m + 1] = T_next

        m_counter[i] += 1
        prev_T = T_i

        if m_counter[i] < num_trips:
            heappush(heap, (T_next, i, m + 1))

    # tour_time[i, m] = arrival[i, m+1] - arrival[i, m]
    tour_time = np.diff(arrival, axis=1)

    result = SimulationResult(
        headway=headway,
        tour_time=tour_time,
        arrival_time=arrival[:, :num_trips],
        M=M,
        G=float(G),
        S=S_arr,
    )

    if transient > 0:
        result = result.steady_state(transient=transient)
    return result


def headway_diverged(result: SimulationResult, *, threshold: float = 1e6) -> bool:
    """Return True if any recorded headway exceeded ``threshold``.

    The paper notes that for ``G > 2`` the time headway diverges. This is a
    convenience check used to label the divergent regime in plots.
    """
    return bool(np.any(np.abs(result.headway) > threshold))
