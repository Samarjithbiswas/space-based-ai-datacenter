"""Electrical power subsystem: triple-junction solar array (BOL/EOL + temperature derate),
Li-ion battery sizing for the dawn-dusk duty cycle, and the end-to-end power budget.

Sources: Azur/Spectrolab datasheets, NASA SoA Power 2024, NASA Li-ion guidelines.
"""
from __future__ import annotations
from .constants import S0

# Triple-junction GaInP/GaAs/Ge
ETA_BOL = 0.296          # beginning-of-life efficiency  (Azur 3G30)
ETA_EOL_5YR = 0.275      # ~5e14 e/cm^2 fluence, ~5-yr LEO  (~93% of BOL)
TEMP_COEFF = -0.0023     # relative efficiency change per degC  (~-0.23 %rel/C)
PACKING = 0.85           # cell packing factor on the panel
PATH_EFF = 0.88          # array -> load path (MPPT * harness * regulation)
ARRAY_SPECIFIC_W_PER_KG = 110.0   # ROSA-class wing-level


def array_power(area_m2: float, life: str = "eol", op_temp_C: float = 70.0) -> float:
    """Generated electrical power [W] at the load, including degradation and temperature."""
    eta = ETA_EOL_5YR if life == "eol" else ETA_BOL
    eta *= (1 + TEMP_COEFF * (op_temp_C - 28.0))     # derate from 28 C reference
    return float(S0 * area_m2 * eta * PACKING * PATH_EFF)


def array_area_for_load(load_W: float, life: str = "eol", op_temp_C: float = 70.0) -> float:
    """Array planform area [m^2] required to deliver load_W at the load."""
    return load_W / (array_power(1.0, life, op_temp_C))


def array_mass(area_m2: float, areal_W_bol: float = 350.0) -> float:
    """Array mass [kg] from wing-level specific power."""
    return area_m2 * areal_W_bol / ARRAY_SPECIFIC_W_PER_KG


def battery_mass(load_W: float, eclipse_min: float, dod: float = 0.30,
                 specific_energy_Wh_kg: float = 160.0) -> float:
    """Battery mass [kg] to carry the load through the worst-case eclipse.
    Dawn-dusk SSO: eclipse_min is small (seasonal), so this stays light."""
    energy_Wh = load_W * (eclipse_min / 60.0) / dod
    return float(energy_Wh / specific_energy_Wh_kg)


def power_budget(compute_W: float, avionics_W: float = 150.0, adcs_W: float = 80.0,
                 comms_W: float = 50.0, thermal_W: float = 20.0,
                 contingency_frac: float = 0.15) -> dict:
    """Spacecraft power budget [W] and the resulting electrical PUE (total/compute)."""
    base = compute_W + avionics_W + adcs_W + comms_W + thermal_W
    total = base * (1 + contingency_frac)
    return {"compute": compute_W, "avionics": avionics_W, "adcs": adcs_W, "comms": comms_W,
            "thermal_control": thermal_W, "contingency": total - base, "total": total,
            "electrical_PUE": total / compute_W}
