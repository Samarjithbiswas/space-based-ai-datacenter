"""Space environment models: neutral atmosphere, thermal environment (solar/albedo/IR),
orbital-debris flux, ionizing-radiation dose, atomic oxygen.

All first-order but calibrated to primary sources (NRLMSIS 2.1, ESA MASTER/NASA ORDEM,
SHIELDOSE-2/AE8-AP8). See docs/SOURCES.md.
"""
from __future__ import annotations
import numpy as np
from .constants import R_E, S0, ALBEDO, EARTH_IR

# ---- Neutral atmosphere: NRLMSIS 2.1 anchors, three solar-activity scenarios [kg/m^3] ----
_ALT = np.array([450, 500, 550, 600, 650, 700, 800]) * 1e3
_RHO = {
    "min": np.array([1.3e-13, 6.0e-14, 3.5e-14, 2.0e-14, 1.1e-14, 6.8e-15, 3.5e-15]),
    "mod": np.array([1.8e-12, 9.0e-13, 4.8e-13, 3.0e-13, 1.6e-13, 8.3e-14, 2.7e-14]),
    "max": np.array([6.0e-12, 4.0e-12, 2.9e-12, 2.1e-12, 1.2e-12, 7.1e-13, 2.6e-13]),
}


def density(alt_km: float, scenario: str = "mod") -> float:
    """Neutral mass density [kg/m^3] (log-linear interpolation of NRLMSIS anchors)."""
    h = np.clip(alt_km * 1e3, _ALT[0], _ALT[-1])
    return float(np.exp(np.interp(h, _ALT, np.log(_RHO[scenario]))))


def earth_view_factor(alt_km: float) -> float:
    """Orientation-averaged (spherical-body) Earth view factor:

        F = 0.5 * (1 - sqrt(1 - (R_E/r)^2))

    This is the fraction of solid angle the Earth subtends, i.e. the view factor from an
    isotropic body (a sphere) or the orientation-averaged value for a flat surface (Modest,
    Radiative Heat Transfer). It is the representative value used here for external-load sizing.
    Note that the Earth view factor is orientation-dependent: a nadir-facing flat plate sees more
    (see earth_view_factor_nadir), and a deep-space-facing radiator sees less. The cross-check
    research (Curtis/Gilmore/Modest corpus) could not tie a single closed form to one primary
    citation, so this value is used as an estimate, not asserted as the unique textbook result."""
    r = R_E + alt_km * 1e3
    return float(0.5 * (1 - np.sqrt(1 - (R_E / r) ** 2)))


def earth_view_factor_nadir(alt_km: float) -> float:
    """Earth view factor for a flat plate facing nadir, F = (R_E/r)^2 (differential planar
    element to a sphere; Modest, Radiative Heat Transfer, Appendix). Upper bound on the Earth
    load for a downward-facing surface; a real radiator is oriented away from Earth to reduce it."""
    r = R_E + alt_km * 1e3
    return float((R_E / r) ** 2)


def thermal_loads(alt_km: float, area_m2: float, alpha_s: float = 0.15,
                  emissivity: float = 0.90, sun_incidence_deg: float = 90.0):
    """External heat loads on a surface [W]: direct solar, Earth albedo, Earth IR.

    sun_incidence_deg = 90 -> edge-on to sun (no direct solar). Returns a dict.
    """
    F = earth_view_factor(alt_km)
    cos_i = max(0.0, np.cos(np.radians(sun_incidence_deg)))
    q_solar = S0 * alpha_s * cos_i * area_m2
    q_albedo = S0 * ALBEDO * F * alpha_s * area_m2
    q_earth_ir = EARTH_IR * F * emissivity * area_m2
    return {"solar": q_solar, "albedo": q_albedo, "earth_ir": q_earth_ir,
            "total": q_solar + q_albedo + q_earth_ir, "view_factor": F}


# ---- Orbital debris flux at SSO (NASA ORDEM 3.1 / ESA MASTER-8 band) [per m^2 per yr] ----
DEBRIS_FLUX = {"1cm": {"lo": 1e-5, "mid": 3e-5, "hi": 1e-4},
               "1mm": {"lo": 1e-3, "mid": 3e-3, "hi": 1e-2}}


def debris_flux(size: str = "1cm", band: str = "mid") -> float:
    """Cumulative debris flux [impacts/m^2/yr] for objects larger than `size`."""
    return DEBRIS_FLUX[size][band]


# ---- Ionizing radiation: TID dose-depth (SHIELDOSE-2/AE8-AP8 class) [rad(Si)/yr] ----
def tid_dose_rate(al_mm: float, band: str = "mid") -> float:
    """Annual TID behind Al shielding: D(x)=D0 exp(-x/lambda)+D_inf, calibrated to a
    ~100-160 rad/yr proton floor (SIRI-1 600 km SSO; Suncatcher 67 MeV proton test)."""
    lam = 1.7
    lo = 2.0e4 * np.exp(-al_mm / lam) + 100.0
    hi = 3.8e4 * np.exp(-al_mm / lam) + 160.0
    return {"lo": lo, "hi": hi, "mid": 0.5 * (lo + hi)}[band]


def seu_rate(n_bits: float, sigma_seu: float = 5e-10) -> float:
    """Single-event upset rate [upsets/day] = sigma_seu[per bit-day] * N_bits.
    Quiet-LEO SRAM baseline ~5e-10/bit/day; spikes ~100x in solar proton events."""
    return sigma_seu * n_bits
