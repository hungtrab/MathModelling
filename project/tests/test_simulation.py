"""Sanity checks for the Nagatani simulator."""

import numpy as np
import pytest

from nagatani.simulation import simulate
from nagatani.analysis import (
    mean_headway,
    rms_headway,
    rms_tour_time,
    transition_loading,
)


def test_zero_loading_zero_speedup_is_periodic():
    """G=0, S=0 -> tour time = 1/(1+0) = 1, perfect periodic motion."""
    res = simulate(G=0.0, S=0.0, M=2, num_trips=200, transient=50)
    # Tour times should all be 1.0.
    np.testing.assert_allclose(res.tour_time[~np.isnan(res.tour_time)], 1.0, atol=1e-9)


def test_low_loading_small_speedup_regular():
    """In the regular regime (small G, finite S), tour time RMS is tiny."""
    res = simulate(G=0.05, S=0.2, M=2, num_trips=1500, transient=500)
    rms = rms_tour_time(res)
    assert np.all(rms < 1e-6), f"expected near-zero RMS in regular regime, got {rms}"


def test_chaotic_regime_high_rms():
    """At G=0.5, S1=0.5, S2=0.2 the system should fluctuate (Fig. 3d)."""
    res = simulate(G=0.5, S=(0.5, 0.2), M=2, num_trips=2000, transient=900)
    rms = rms_tour_time(res)
    assert rms[0] > 1e-3, "bus 1 RMS should be non-trivial in chaotic regime"


def test_diverges_above_two():
    """Paper states divergence for G >= 2."""
    res = simulate(G=2.5, S=(0.5, 0.2), M=2, num_trips=200, transient=0)
    finite_h = res.headway[np.isfinite(res.headway)]
    if finite_h.size:
        # Headways should grow without bound — at least very large.
        assert np.max(np.abs(finite_h)) > 10.0


def test_three_buses_runs():
    """The simulator generalises to M >= 3."""
    res = simulate(G=0.1, S=0.3, M=3, num_trips=300, transient=100)
    assert res.M == 3
    assert res.headway.shape[0] == 3


def test_transition_bisection_monotone():
    """transition_loading should be monotone-decreasing in S in the regime tested."""
    Gc_low = transition_loading(S=0.1, G_min=0.0, G_max=1.0, tol=5e-3)
    Gc_high = transition_loading(S=0.5, G_min=0.0, G_max=1.0, tol=5e-3)
    # Higher speed-up suppresses chaos, so the transition moves to higher G.
    assert Gc_high >= Gc_low - 0.05  # allow some numerical slack


def test_invalid_input():
    with pytest.raises(ValueError):
        simulate(G=0.1, S=0.0, M=1, num_trips=10)
    with pytest.raises(ValueError):
        simulate(G=0.1, S=[0.1, 0.2, 0.3], M=2, num_trips=10)
