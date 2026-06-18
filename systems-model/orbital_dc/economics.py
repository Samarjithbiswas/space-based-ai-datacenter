"""Techno-economics: per-satellite and constellation cost, launch sensitivity,
10-year total cost of ownership, and the launch-price cross-over."""
from __future__ import annotations
from .constants import LAUNCH_MASS_KG


def satellite_cost(launch_usd_per_kg: float, hardware_usd: float = 1.1e6,
                   launch_mass_kg: float = LAUNCH_MASS_KG) -> dict:
    """Per-satellite cost [USD] split into launch and hardware."""
    launch = launch_usd_per_kg * launch_mass_kg
    return {"launch": launch, "hardware": hardware_usd, "total": launch + hardware_usd}


def launch_crossover_usd_per_kg(hardware_usd: float = 1.1e6,
                                launch_mass_kg: float = LAUNCH_MASS_KG) -> float:
    """Launch price at which launch cost equals hardware cost."""
    return hardware_usd / launch_mass_kg


def constellation_capex(n_sats: int, launch_usd_per_kg: float, ground_usd: float = 15e6,
                        ops_center_usd: float = 8e6, margin: float = 0.20) -> float:
    """Total constellation capital expenditure [USD]."""
    sat = satellite_cost(launch_usd_per_kg)["total"] * n_sats
    return (sat + ground_usd + ops_center_usd) * (1 + margin)


def tco_10yr(n_sats: int, launch_usd_per_kg: float, opex_per_yr_usd: float = 17.1e6) -> float:
    """10-year total cost of ownership [USD]."""
    return constellation_capex(n_sats, launch_usd_per_kg) + opex_per_yr_usd * 10
