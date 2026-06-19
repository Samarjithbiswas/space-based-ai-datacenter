"""Design margins, mass-growth allowances, and technology-readiness levels.

These are the standard systems-engineering allowances a conceptual design must carry. Values are
taken from named references and should be applied on top of the current-best-estimate (CBE)
outputs of the other modules.

Sources:
  - AIAA S-120-2006, Mass Properties Control for Space Systems (per-category mass-growth allowance)
  - NASA GSFC Integrated Design Center practice (system-level mass margin, power margin)
  - NASA Systems Engineering Handbook, NASA/SP-2016-6105 (TRL scale; margins tracked as technical
    performance measures rather than fixed numbers)
Caveat: published studies (e.g. NRO/DoD mass-growth data) find the AIAA allowances can be
optimistic, so these are lower bounds, not guarantees.
"""
from __future__ import annotations

# AIAA S-120-2006 mass-growth allowance for "Estimated" design maturity, by hardware category
AIAA_MGA = {
    "electronics_small": 0.30,   # 0-5 kg
    "electronics_large": 0.20,   # > 15 kg
    "structures": 0.25,
    "mechanisms": 0.25,
    "thermal": 0.25,
    "battery": 0.25,
    "solar_array": 0.30,
    "propulsion": 0.25,
    "harness": 0.60,
    "default": 0.25,
}

SYSTEM_MASS_MARGIN_PREPHASE_A = 0.30   # NASA GSFC IDC, applied above per-item MGA
POWER_MARGIN_MIN = 0.30                # min contingency over CBE loads at worst-case EOL (GSFC)

# NASA SP-2016-6105 Technology Readiness Levels
TRL = {
    1: "Basic principles observed and reported",
    2: "Technology concept and/or application formulated",
    3: "Analytical and experimental proof-of-concept",
    4: "Component validated in a laboratory environment",
    5: "Component validated in a relevant environment",
    6: "System/subsystem prototype demonstrated in a relevant environment",
    7: "System prototype demonstrated in a space environment",
    8: "Actual system flight qualified through test and demonstration",
    9: "Actual system flight proven through successful mission operations",
}


def mass_with_growth(cbe_masses: dict, category_map: dict | None = None,
                     system_margin: float = SYSTEM_MASS_MARGIN_PREPHASE_A) -> dict:
    """Apply per-item AIAA mass-growth allowance plus a system-level margin to a CBE mass budget.

    cbe_masses: {item: mass_kg}; category_map: {item: AIAA_MGA key} (defaults to 'default').
    Returns the grown per-item masses, the subtotal with item MGA, and the predicted mass with the
    system margin on top.
    """
    category_map = category_map or {}
    grown = {}
    for item, m in cbe_masses.items():
        mga = AIAA_MGA.get(category_map.get(item, "default"), AIAA_MGA["default"])
        grown[item] = m * (1 + mga)
    subtotal = sum(grown.values())
    predicted = subtotal * (1 + system_margin)
    return {"grown_items_kg": grown, "subtotal_with_item_MGA_kg": subtotal,
            "predicted_mass_kg": predicted, "system_margin": system_margin}


def power_with_margin(cbe_power_W: float, margin: float = POWER_MARGIN_MIN) -> float:
    """Required generated power = CBE load times (1 + margin), at worst-case end of life."""
    return cbe_power_W * (1 + margin)
