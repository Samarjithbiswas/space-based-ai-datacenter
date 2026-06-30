"""Integrated system model: ties every subsystem into a self-consistent design point.

A DesignPoint takes top-level choices (chips, altitude, radiator temperature, shielding,
utilization, protection, launch price) and closes the power -> array -> mass -> thermal ->
delta-v -> reliability -> economics chain into one consistent satellite, then aggregates
to a constellation.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from . import (orbit, thermal, power, radiation, debris, propulsion, reliability, compute,
               economics, groundlink, structures, workload, finance, adcs)
from .constants import ALT_KM, N_SATS, SPACING_M
from .compute import EST_TDP_W

RADIATOR_AREAL_MASS = 5.0   # kg/m^2 modular tile
ARRAY_AREAL_W_BOL = 350.0
DRAG_AREA_M2 = 3.5          # compact attitude, arrays feathered


@dataclass
class DesignPoint:
    n_chips: int = 4
    chip: str = "tpu_v6e"
    alt_km: float = ALT_KM
    radiator_temp_C: float = 45.0
    shielding_mm: float = 10.0
    mfu: float = 0.30
    protection: str = "ecc_checkpoint"
    scenario: str = "mod"
    launch_usd_per_kg: float = 300.0
    extra: dict = field(default_factory=dict)

    def solve(self) -> dict:
        chip_W = EST_TDP_W[self.chip]
        compute_W = self.n_chips * chip_W
        avail = radiation.availability(self.protection)["usable_compute"]

        # --- power ---
        pwr = power.power_budget(compute_W)
        total_W = pwr["total"]
        array_area = power.array_area_for_load(total_W)
        array_m = power.array_mass(array_area, ARRAY_AREAL_W_BOL)
        battery_m = power.battery_mass(total_W, eclipse_min=5.0)

        # --- thermal ---
        q_thermal = compute_W + pwr["avionics"] + 100.0   # + parasitic
        radiator_area = thermal.radiator_area(q_thermal, self.radiator_temp_C)
        radiator_m = radiator_area * RADIATOR_AREAL_MASS
        interface_dT = thermal.interface_delta_T(chip_W)        # active cooling flag if >125

        # --- radiation ---
        tid = radiation.cumulative_tid(self.shielding_mm, 5.0)
        tid_margin = radiation.tid_margin(self.shielding_mm, 5.0)
        shield_m = radiation.shielding_mass(self.shielding_mm, area_m2=2.0)

        # --- structures: structure mass + inertia from geometry (feeds ADCS) ---
        supported = radiator_m + array_m + battery_m + shield_m + self.n_chips * 3.0 + 45.0
        struct_m = structures.structural_mass(supported, 0.20)
        inertia = structures.spacecraft_inertia(bus_mass=struct_m)
        gg_torque = adcs.gravity_gradient_torque(self.alt_km, inertia["inertia_diff"])

        # --- mass budget (dry) ---
        masses = {"structure": struct_m, "thermal": radiator_m, "power": array_m + battery_m,
                  "adcs": 30.0, "shielding": shield_m, "avionics": 45.0,
                  "payload_chips": self.n_chips * 3.0, "harness": 28.0}
        dry_mass = sum(masses.values())
        a_to_m = DRAG_AREA_M2 / dry_mass

        # --- propulsion / disposal ---
        dv = propulsion.delta_v_budget(self.alt_km, a_to_m)
        prop_m = propulsion.propellant_mass(dv["total"], 1500.0, dry_mass)   # electric
        masses["propulsion"] = prop_m + 10.0
        launch_mass = dry_mass + prop_m + 10.0

        # --- lifetime / debris ---
        # natural decay assumes the satellite is abandoned with its propellant, so use launch mass
        life = orbit.lifetime_years(self.alt_km, DRAG_AREA_M2 / launch_mass, self.scenario)
        p_debris5 = debris.collision_probability(15.0, N_SATS, 5.0)
        cascade = debris.cascade_neighbor_probability(SPACING_M)

        # --- compute: time-domain throttled delivery (couples thermal+compute) ---
        wl = workload.simulate_orbit(n_chips=self.n_chips, chip=self.chip, alt_km=self.alt_km,
                                     radiator_area_m2=max(radiator_area, 2.0), mfu=self.mfu,
                                     protection=self.protection)
        delivered = wl["delivered_PFLOPS_mean"]
        eff_pue = compute.effective_pue(compute_W, total_W, avail)

        # --- ground segment ---
        gl = groundlink.ground_downlink(self.alt_km)

        # --- economics: LCOE of compute (discounted) ---
        sat_cost = economics.satellite_cost(self.launch_usd_per_kg)
        opex_yr = 0.15 * sat_cost["total"]
        lcoe = finance.lcoe_per_pflop_hr(sat_cost["total"], opex_yr, max(delivered, 1e-6))

        return {
            "compute_W": compute_W, "total_power_W": total_W, "electrical_PUE": pwr["electrical_PUE"],
            "effective_PUE": eff_pue, "array_area_m2": array_area,
            "radiator_area_m2": radiator_area, "interface_dT_C": interface_dT,
            "active_cooling_required": interface_dT > 125.0,
            "tid_5yr_rad": tid, "tid_margin": tid_margin,
            "inertia_max_kgm2": inertia["I_max"], "gravity_gradient_torque_Nm": gg_torque,
            "dry_mass_kg": dry_mass, "launch_mass_kg": launch_mass, "mass_breakdown": masses,
            "delta_v_total_mps": dv["total"], "propellant_kg": prop_m,
            "natural_lifetime_yr": life, "meets_disposal_rule": life <= 5.0,
            "debris_P_catastrophic_5yr": p_debris5, "cascade_neighbor_P": cascade,
            "delivered_PFLOPS": delivered, "throttle_loss_frac": wl["throttle_loss_frac"],
            "Tj_peak_C": wl["Tj_peak_C"], "usable_compute_frac": avail,
            "ground_downlink_TB_day": gl["daily_volume_TB"], "ground_availability": gl["availability"],
            "satellite_cost_usd": sat_cost["total"], "lcoe_usd_per_pflop_hr": lcoe,
        }


def constellation(dp: DesignPoint | None = None, n_sats: int = N_SATS) -> dict:
    """Aggregate a DesignPoint to a constellation: total compute, power, cost, availability."""
    dp = dp or DesignPoint()
    s = dp.solve()
    avail = reliability.constellation_availability(
        n_deployed=int(n_sats * 1.2), n_required=n_sats, mtbf_hours=150000.0)
    capex = economics.constellation_capex(n_sats, dp.launch_usd_per_kg)
    return {"n_sats": n_sats, "fleet_PFLOPS": s["delivered_PFLOPS"] * n_sats,
            "fleet_power_MW": s["total_power_W"] * n_sats / 1e6,
            "capex_usd": capex, "tco_10yr_usd": economics.tco_10yr(n_sats, dp.launch_usd_per_kg),
            "capacity_availability": avail["capacity_availability"], "per_sat": s}
