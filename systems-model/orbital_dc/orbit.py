"""Orbital mechanics: Kepler, sun-synchronous geometry, eclipse, J2 precession,
drag decay, and linearized relative (formation) dynamics.
"""
from __future__ import annotations
import numpy as np
from .constants import MU, R_E, J2
from .environment import density


def velocity(alt_km: float) -> float:
    """Circular orbital speed [m/s]."""
    return float(np.sqrt(MU / (R_E + alt_km * 1e3)))


def period(alt_km: float) -> float:
    """Circular orbital period [s] (Kepler's third law)."""
    a = R_E + alt_km * 1e3
    return float(2 * np.pi * np.sqrt(a**3 / MU))


def sso_inclination(alt_km: float) -> float:
    """Sun-synchronous inclination [deg] from the J2 nodal-precession match (360 deg/yr)."""
    a = R_E + alt_km * 1e3
    n = np.sqrt(MU / a**3)
    rate = 2 * np.pi / (365.2422 * 86400)        # required nodal precession [rad/s]
    cos_i = -rate * 2 * a**2 * (1 - 0) ** 2 / (3 * n * J2 * R_E**2)
    return float(np.degrees(np.arccos(np.clip(cos_i, -1, 1))))


def critical_beta(alt_km: float) -> float:
    """Beta angle [deg] below which eclipses occur, beta* = asin(R_E/(R_E+h))."""
    return float(np.degrees(np.arcsin(R_E / (R_E + alt_km * 1e3))))


def eclipse_fraction(alt_km: float, beta_deg: float) -> float:
    """Fraction of the orbit in eclipse for a given beta angle (0 if |beta|>=beta*)."""
    bstar = critical_beta(alt_km)
    if abs(beta_deg) >= bstar:
        return 0.0
    h = alt_km * 1e3
    arg = np.sqrt(h**2 + 2 * R_E * h) / ((R_E + h) * np.cos(np.radians(beta_deg)))
    return float((1 / np.pi) * np.arccos(np.clip(arg, -1, 1)))


def lifetime_years(alt_km: float, area_to_mass: float, scenario: str = "mod",
                   cd: float = 2.2) -> float:
    """Natural orbital lifetime [yr] integrating circular-orbit drag decay
    da/dt = -C_D (A/m) rho sqrt(mu a)  to re-entry at 120 km."""
    a = R_E + alt_km * 1e3
    t, yr, dt = 0.0, 3.15576e7, 3600 * 6
    while a > R_E + 120e3 and t < 2000 * yr:
        h = (a - R_E) / 1e3
        a += -cd * area_to_mass * density(h, scenario) * np.sqrt(MU * a) * dt
        t += dt
        dt = 3600 * 48 if (a - R_E) > 500e3 else (3600 * 12 if (a - R_E) > 300e3 else 3600 * 2)
    return t / yr


# ---------------------------------------------------------------------------------------
# Relative (formation) dynamics: Clohessy-Wiltshire / Hill equations about a circular orbit
# ---------------------------------------------------------------------------------------
def cw_drift(alt_km: float, delta_bc_frac: float, hours: float) -> float:
    """Along-track drift [m] between two satellites whose ballistic coefficients differ by
    delta_bc_frac, from the secular CW response to a differential along-track acceleration.

    A differential drag acceleration da produces along-track drift x(t) ~ 1.5 * da * t^2
    (the dominant secular term of the CW solution). Used to size formation-keeping cadence.
    """
    from .environment import density
    v = velocity(alt_km)
    rho = density(alt_km)
    # nominal drag accel for A/m ~ 0.008; differential is delta_bc_frac of it
    a_drag = 0.5 * rho * v**2 * 2.2 * 0.008
    da = a_drag * delta_bc_frac
    t = hours * 3600.0
    return float(1.5 * da * t**2)


def cw_natural_frequency(alt_km: float) -> float:
    """Mean motion n [rad/s]; the CW radial/cross-track modes oscillate at n."""
    a = R_E + alt_km * 1e3
    return float(np.sqrt(MU / a**3))
