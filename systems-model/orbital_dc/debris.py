"""Orbital-debris collision risk and in-cluster fragmentation cascade."""
from __future__ import annotations
import numpy as np
from .environment import debris_flux


def collision_probability(cross_section_m2: float, n_sats: int, years: float,
                          size: str = "1cm", band: str = "mid") -> float:
    """Poisson probability of >=1 catastrophic impact in the cluster,
    P = 1 - exp(-Phi*A*N*t)."""
    flux = debris_flux(size, band)
    return float(1 - np.exp(-flux * cross_section_m2 * n_sats * years))


def cascade_neighbor_probability(spacing_m: float, n_fragments: int = 2000,
                                 target_radius_m: float = 2.0) -> float:
    """Probability a neighbor is struck by >=1 lethal fragment (expanding-shell model),
    P_hit = 1 - exp(-N_f*r_t^2/(4*d^2))."""
    return float(1 - np.exp(-n_fragments * target_radius_m**2 / (4 * spacing_m**2)))


def expected_secondary_hits(spacing_m: float, n_neighbors: int = 80, **kw) -> float:
    """Expected number of neighbors hit by one fragmentation (cascade seed)."""
    return float(n_neighbors * cascade_neighbor_probability(spacing_m, **kw))
