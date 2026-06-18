"""Propulsion: drag make-up, controlled de-orbit (Hohmann), the 5-year delta-v budget,
and propellant mass (rocket equation)."""
from __future__ import annotations
import numpy as np
from .constants import MU, R_E, G0
from .orbit import velocity
from .environment import density


def deorbit_delta_v(alt_km: float, perigee_km: float = 180.0) -> float:
    """Delta-v [m/s] for a retrograde Hohmann burn lowering perigee,
    dv = v_c1*(1 - sqrt(2*r2/(r1+r2)))."""
    r1, r2 = R_E + alt_km * 1e3, R_E + perigee_km * 1e3
    v1 = np.sqrt(MU / r1)
    return float(v1 * (1 - np.sqrt(2 * r2 / (r1 + r2))))


def drag_delta_v(alt_km: float, area_to_mass: float, years: float = 5.0,
                 cd: float = 2.2, scenario: str = "mod") -> float:
    """Delta-v [m/s] to make up drag over the mission."""
    v = velocity(alt_km)
    a_drag = 0.5 * density(alt_km, scenario) * v**2 * cd * area_to_mass
    return float(a_drag * years * 3.15576e7)


def delta_v_budget(alt_km: float, area_to_mass: float, years: float = 5.0,
                   formation_mps: float = 8.0, avoidance_maneuvers_per_yr: int = 20,
                   avoidance_dv_each: float = 0.05, margin: float = 0.20,
                   scenario: str = "mod") -> dict:
    """Full per-satellite delta-v budget [m/s]."""
    drag = drag_delta_v(alt_km, area_to_mass, years, scenario=scenario)
    avoid = avoidance_maneuvers_per_yr * years * avoidance_dv_each
    deorbit = deorbit_delta_v(alt_km)
    sub = drag + formation_mps + avoid + deorbit
    total = sub * (1 + margin)
    return {"drag_makeup": drag, "formation_keeping": formation_mps, "collision_avoidance": avoid,
            "deorbit": deorbit, "margin": total - sub, "total": total}


def propellant_mass(delta_v: float, isp_s: float, dry_mass_kg: float = 375.0) -> float:
    """Propellant [kg] from Tsiolkovsky, m_p = m_dry*(exp(dv/(Isp*g0)) - 1)."""
    return float(dry_mass_kg * (np.exp(delta_v / (isp_s * G0)) - 1))
