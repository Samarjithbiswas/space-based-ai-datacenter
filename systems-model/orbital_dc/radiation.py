"""Ionizing-radiation effects: cumulative TID vs shielding, shielding mass, and the
SEU-driven compute-availability tax."""
from __future__ import annotations
from .environment import tid_dose_rate, seu_rate

HBM_TOLERANCE_RAD = 2000.0      # Suncatcher: HBM irregularities at ~2 krad(Si)
DESIGN_REQ_RAD = 750.0          # Suncatcher 5-yr requirement


def cumulative_tid(al_mm: float, years: float = 5.0, band: str = "mid") -> float:
    """Cumulative mission TID [rad(Si)]."""
    return tid_dose_rate(al_mm, band) * years


def tid_margin(al_mm: float, years: float = 5.0) -> float:
    """Margin factor against the HBM tolerance (>1 is safe)."""
    return HBM_TOLERANCE_RAD / cumulative_tid(al_mm, years, "mid")


def shielding_mass(al_mm: float, area_m2: float, density_kg_m3: float = 2700.0) -> float:
    """Aluminium shielding mass [kg] for a given thickness over a wrapped area."""
    return area_m2 * (al_mm / 1000.0) * density_kg_m3


def availability(protection: str = "ecc_checkpoint") -> dict:
    """Usable-compute fraction and residual uncorrected-error risk by protection level.
    AI inference tolerates bit-flips, so ECC+checkpoint dominates full TMR."""
    table = {"none": (0.55, 0.40), "ecc_checkpoint": (0.86, 0.06),
             "ecc_sel_tmr": (0.78, 0.02), "full_tmr": (0.50, 0.005)}
    eff, risk = table[protection]
    return {"usable_compute": eff, "uncorrected_risk": risk, "throughput_tax": 1 - eff}
