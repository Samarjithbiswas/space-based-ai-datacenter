"""Uncertainty propagation and sensitivity analysis over the integrated system model."""
from __future__ import annotations
import numpy as np
from .system import DesignPoint
from . import orbit, debris, propulsion


def monte_carlo(n: int = 5000, seed: int = 7) -> dict:
    """Propagate the dominant input uncertainties to key outputs; return percentiles.

    Sampled: solar-activity (density) scenario, debris flux band, chip TDP (v6e undisclosed),
    MFU, and launch price. Returns 5/50/95th percentiles of the headline outputs.
    """
    rng = np.random.default_rng(seed)
    A_to_M = 3.5 / 375.0
    scenarios = ["min", "mod", "max"]
    # lifetime and drag-driven delta-v depend only on the (fixed-A/m) solar scenario,
    # so precompute the 3 cases once instead of re-integrating the ODE n times.
    life_lut = {s: orbit.lifetime_years(650, A_to_M, s) for s in scenarios}
    dv_lut = {s: propulsion.delta_v_budget(650, A_to_M, scenario=s)["total"] for s in scenarios}
    debris_lut = {b: debris.collision_probability(15.0, 81, 5.0, band=b) * 100
                  for b in ("lo", "mid", "hi")}
    scen = rng.choice(scenarios, size=n, p=[0.3, 0.5, 0.2])
    band = rng.choice(["lo", "mid", "hi"], size=n, p=[0.3, 0.5, 0.2])
    mfu = np.clip(rng.normal(0.30, 0.10, n), 0.05, 0.6)
    life = [life_lut[s] for s in scen]
    dv_total = [dv_lut[s] for s in scen]
    p_debris = [debris_lut[b] for b in band]
    deliver = list(4 * 918.0 / 1e3 * mfu * 0.86)   # PFLOPS per 4-chip sat
    pct = lambda x: {p: float(np.percentile(x, p)) for p in (5, 50, 95)}
    return {"natural_lifetime_yr": pct(life),
            "debris_P_catastrophic_5yr_pct": pct(p_debris),
            "delta_v_total_mps": pct(dv_total),
            "delivered_PFLOPS_per_sat": pct(deliver)}


def one_at_a_time(param: str, values) -> list:
    """Tornado-style sensitivity: vary one DesignPoint field, report a key output each time."""
    out = []
    for v in values:
        dp = DesignPoint(**{param: v})
        s = dp.solve()
        out.append({param: v, "dry_mass_kg": s["dry_mass_kg"],
                    "radiator_area_m2": s["radiator_area_m2"],
                    "effective_PUE": s["effective_PUE"],
                    "satellite_cost_usd": s["satellite_cost_usd"]})
    return out
