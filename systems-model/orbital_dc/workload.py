"""Time-domain workload simulation with closed-loop thermal throttling.

This is the higher-fidelity piece: instead of a static "delivered PFLOPS = peak x MFU",
it integrates the radiator temperature over an orbit while a time-varying compute load
heats the die, throttles the chip when the junction exceeds its limit, and accounts for
eclipse power and SEU-checkpoint overhead. The result is the *actually delivered* useful
compute, the throttle loss, and the junction-temperature trace.

Couples: thermal (lumped radiator + junction resistance), compute (peak/MFU/availability),
power (eclipse), radiation (checkpoint overhead). Nonlinear forward-Euler integration.
"""
from __future__ import annotations
import numpy as np
from .constants import SIGMA
from .orbit import period
from .compute import PEAK_TFLOPS, EST_TDP_W
from .radiation import availability


def throttle_factor(T_j, T_throttle=110.0, T_max=125.0):
    """Fraction of full clock allowed at junction temperature T_j (1 -> 0 across the band)."""
    return float(np.clip((T_max - T_j) / (T_max - T_throttle), 0.0, 1.0))


def simulate_orbit(n_chips=4, chip="h100", alt_km=650.0, radiator_area_m2=8.0,
                   r_th=0.30, mfu=0.30, protection="ecc_checkpoint",
                   base_util=0.9, idle_frac=0.25, radiator_areal_mass=5.0, cp=900.0,
                   emissivity=0.90, parasitic_W=120.0, avionics_W=150.0,
                   eclipse_frac=0.0, dt=5.0):
    """Integrate one orbit; return junction trace and delivered-compute summary.

    The chip self-regulates: when T_j exceeds T_throttle the effective utilization (and thus
    both power and FLOPS) is scaled by throttle_factor, so the loop finds a steady throttled
    operating point if the radiator is undersized.
    """
    P_tdp = EST_TDP_W[chip]
    peak_pflops = n_chips * PEAK_TFLOPS[chip] / 1e3
    avail = availability(protection)["usable_compute"]
    A_eff = 2 * radiator_area_m2 * (1 - 0.12)        # double-sided, parasitic derate
    C = radiator_area_m2 * radiator_areal_mass * cp  # thermal capacitance [J/K]

    T_orbit = period(alt_km)
    n = int(T_orbit / dt)
    T_rad = 300.0                                     # K, start near equilibrium
    delivered, ideal, Tj_trace = 0.0, 0.0, []

    for k in range(n):
        # workload duty cycle (square-ish bursts) -> commanded utilization
        phase = (k * dt) / T_orbit
        u_cmd = base_util if (phase % 0.5) < 0.35 else idle_frac
        # chip power before throttle, junction temp, throttle, effective utilization
        P_chip_full = idle_frac * P_tdp + u_cmd * (P_tdp - idle_frac * P_tdp)
        T_j = (T_rad - 273.15) + P_chip_full * r_th
        thr = throttle_factor(T_j)
        u_eff = u_cmd * thr
        P_chip = idle_frac * P_tdp + u_eff * (P_tdp - idle_frac * P_tdp)
        # heat balance (eclipse: external solar off, but compute continues on battery)
        ext = parasitic_W * (0.0 if (phase % 1.0) < eclipse_frac else 1.0)
        Q_in = n_chips * P_chip + avionics_W + ext
        T_rad += dt * (Q_in - emissivity * SIGMA * A_eff * T_rad**4) / C
        # delivered useful compute this step
        delivered += peak_pflops * u_eff * mfu * avail * dt
        ideal += peak_pflops * u_cmd * mfu * dt
        Tj_trace.append((T_rad - 273.15) + P_chip * r_th)

    Tj = np.array(Tj_trace)
    return {"chip": chip, "delivered_PFLOPS_mean": delivered / (n * dt),
            "ideal_PFLOPS_mean": ideal / (n * dt),
            "throttle_loss_frac": float(1 - delivered / ideal) if ideal > 0 else 0.0,
            "Tj_mean_C": float(Tj.mean()), "Tj_peak_C": float(Tj.max()),
            "throttled": bool(Tj.max() > 110.0),
            "radiation_availability": avail}
