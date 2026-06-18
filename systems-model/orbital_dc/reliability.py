"""Reliability and constellation availability. No on-orbit repair, so availability is
bought through redundancy, over-provisioning, and graceful degradation.
Sources: MIL-HDBK-217F, NASA SSRI, CubeSat reliability studies, Starlink attrition data.
"""
from __future__ import annotations
import numpy as np
from math import comb


def reliability(t_years: float, mtbf_hours: float) -> float:
    """Exponential (constant-hazard) reliability R(t) = exp(-t/MTBF)."""
    return float(np.exp(-(t_years * 8766.0) / mtbf_hours))


def k_of_n(k: int, n: int, p: float) -> float:
    """System reliability when >=k of n identical units (each reliability p) survive."""
    return float(sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1)))


def spares_for_availability(target_avail: float, p_node: float, n_required: int) -> int:
    """Smallest n such that P(>=n_required of n survive) >= target_avail."""
    n = n_required
    while k_of_n(n_required, n, p_node) < target_avail and n < 10 * n_required + 50:
        n += 1
    return n


def expected_capacity_fraction(n_deployed: int, n_required: int, p_node: float) -> float:
    """Expected fraction of required capacity available (no replenishment),
    min(1, n_deployed * p / n_required). The meaningful fleet-level metric;
    use k_of_n() for strict within-satellite chip redundancy instead."""
    return float(min(1.0, n_deployed * p_node / n_required))


def constellation_availability(n_deployed: int, n_required: int, mtbf_hours: float = 150000.0,
                               t_years: float = 5.0) -> dict:
    """Expected fraction of required capacity available at time t (no replenishment).

    Note: operational constellations sustain capacity by continuous replenishment at the
    annual_replacement_rate; this snapshot is the worst case without it.
    """
    p = reliability(t_years, mtbf_hours)
    return {"per_node_reliability": p,
            "capacity_availability": expected_capacity_fraction(n_deployed, n_required, p),
            "over_provision_frac": (n_deployed - n_required) / n_required}


def annual_replacement_rate(design_life_years: float) -> float:
    """Steady-state replacement-to-sustain rate ~ 1/life (e.g. 5 yr -> 20%/yr)."""
    return 1.0 / design_life_years
