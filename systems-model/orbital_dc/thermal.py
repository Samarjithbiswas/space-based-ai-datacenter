"""Thermal subsystem: radiator sizing, junction resistance network, transient (eclipse)
response, and an exact reproduction of the Part I baseline (for cross-validation).
"""
from __future__ import annotations
import numpy as np
from .constants import SIGMA, T_CMB


def radiator_area(heat_W: float, temp_C: float, emissivity: float = 0.90,
                  sides: int = 2, parasitic: float = 0.12) -> float:
    """Required radiator area [m^2] from the Stefan-Boltzmann balance (double-sided)."""
    T = temp_C + 273.15
    return heat_W / (emissivity * SIGMA * T**4 * sides * (1 - parasitic))


def radiator_temperature(heat_W: float, area_m2: float, emissivity: float = 0.85,
                         sides: int = 1, tol: float = 0.01) -> float:
    """Radiator temperature [C] by Newton-Raphson on f(T)=Q - eps*sig*A_eff*T^4.
    Default sides=1, eps=0.85 reproduces the Part I single-sided convention."""
    A_eff = area_m2 * sides
    T = 300.0
    for _ in range(60):
        f = heat_W - emissivity * SIGMA * A_eff * (T**4 - T_CMB**4)
        fp = -4 * emissivity * SIGMA * A_eff * T**3
        step = f / fp
        T -= step
        if abs(step) < tol:
            break
    return float(T - 273.15)


def resistance_network(r_jc=0.150, r_tim=0.040, r_base=0.060, r_pipe=0.080, r_rad=0.020):
    """Series junction-to-radiator thermal resistance [K/W]."""
    return r_jc + r_tim + r_base + r_pipe + r_rad


def junction_temp(t_radiator_C: float, chip_W: float, r_th: float) -> float:
    """Junction temperature [C] = T_rad + Q * R_th."""
    return t_radiator_C + chip_W * r_th


def interface_delta_T(chip_W: float, r_th: float = 0.30) -> float:
    """Junction-to-radiator rise [K]. Exceeds the 125 C budget for chip_W*r_th>125."""
    return chip_W * r_th


def eclipse_transient(t_s, radiator_mass_kg=54.0, cp=900.0, area_m2=4.0,
                      emissivity=0.85, T0_K=294.4, delta_solar_W=-100.0):
    """Lumped-capacitance eclipse response. Returns radiator temperature [K] at time t_s.

    tau = m*cp/(h_rad*A), h_rad = 4*eps*sigma*T0^3 (linearized radiation), and
    Delta T_ss = delta_solar / (h_rad*A).  Bi << 0.1 so lumped capacitance is valid.
    """
    h_rad = 4 * emissivity * SIGMA * T0_K**3
    tau = radiator_mass_kg * cp / (h_rad * area_m2)
    dT_ss = delta_solar_W / (h_rad * area_m2)
    return float(T0_K + dT_ss * (1 - np.exp(-np.asarray(t_s) / tau))), float(tau)


# =======================================================================================
#  PART I BASELINE  -- exact reproduction (single-sided, eps=0.85, Newton-Raphson)
#  This is the authoritative parameter set; values match the published study to <0.1 C.
# =======================================================================================
def report_i_baseline():
    """Reproduce the Part I steady-state design point. Returns a dict of the key results."""
    Q_total = 1450.0          # 4x300 TPU + 150 avionics + 100 parasitic (optimized orientation)
    A = 4.0                   # m^2 total radiator (two 2 m^2 panels), used as single-side emitter
    eps = 0.85                # Z-93 end-of-life
    T_rad = radiator_temperature(Q_total, A, emissivity=eps, sides=1)   # ~21.4 C
    R_before = resistance_network(r_jc=.150, r_tim=.040, r_base=.060, r_pipe=.080, r_rad=.020)  # 0.350
    R_after = resistance_network(r_jc=.150, r_tim=.020, r_base=.060, r_pipe=.050, r_rad=.020)   # 0.300
    Tj = junction_temp(T_rad, 300.0, R_after)                          # ~111.4 C
    # single-heat-pipe failure: pipe resistance up 8/7 -> +0.011 K/W on the system total
    dR_fail = 0.080 * (8 / 7 - 1)
    R_fail = R_after + dR_fail
    Tj_fail = junction_temp(T_rad, 300.0, R_fail)                      # ~114.7 C
    return {"Q_total_W": Q_total, "radiator_area_m2": A, "emissivity": eps,
            "T_radiator_C": T_rad, "R_before_KW": R_before, "R_after_KW": R_after,
            "T_junction_C": Tj, "dR_failed_pipe_KW": dR_fail,
            "R_failed_KW": R_fail, "T_junction_failed_C": Tj_fail}
