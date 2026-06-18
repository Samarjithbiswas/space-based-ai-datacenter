"""Free-space optical communications link budget (inter-satellite and ground), latency,
and constellation fabric capacity.

P_rx = P_tx + G_tx + G_rx - L_fs - L_point - L_atm - L_optics  (all dB)
Sources: NASA TBIRD/LCRD, arXiv:2204.13177, MathWorks link-budget, Suncatcher paper.
"""
from __future__ import annotations
import numpy as np
from .constants import C_LIGHT, N_FIBER, R_E


def telescope_gain_dB(aperture_m: float, wavelength_m: float = 1.55e-6) -> float:
    """Optical antenna gain [dB], G = (pi*D/lambda)^2."""
    g = (np.pi * aperture_m / wavelength_m) ** 2
    return float(10 * np.log10(g))


def free_space_loss_dB(range_m: float, wavelength_m: float = 1.55e-6) -> float:
    """Free-space path loss [dB], L = (4*pi*R/lambda)^2."""
    return float(10 * np.log10((4 * np.pi * range_m / wavelength_m) ** 2))


def link_margin_dB(p_tx_W, aperture_m, range_m, rx_sensitivity_dBm,
                   pointing_loss_dB=3.0, atmos_loss_dB=0.0, optics_loss_dB=3.0,
                   wavelength_m=1.55e-6):
    """Received power and margin [dB] for a symmetric optical link."""
    p_tx_dBm = 10 * np.log10(p_tx_W * 1e3)
    g = telescope_gain_dB(aperture_m, wavelength_m)
    p_rx = (p_tx_dBm + 2 * g - free_space_loss_dB(range_m, wavelength_m)
            - pointing_loss_dB - atmos_loss_dB - optics_loss_dB)
    return {"p_rx_dBm": float(p_rx), "margin_dB": float(p_rx - rx_sensitivity_dBm),
            "telescope_gain_dB": g, "fspl_dB": free_space_loss_dB(range_m, wavelength_m)}


def latency_ms(distance_km: float, medium: str = "vacuum") -> float:
    """One-way latency [ms]. Vacuum ISL mesh vs terrestrial fiber (n=1.4675)."""
    v = C_LIGHT if medium == "vacuum" else C_LIGHT / N_FIBER
    return float(distance_km * 1e3 / v * 1e3)


def fabric_capacity_tbps(per_link_tbps: float = 1.6, n_sats: int = 81,
                         links_per_sat: int = 4) -> float:
    """Aggregate internal mesh capacity [Tbps] ~ per_link * n_sats * links/sat / 2."""
    return float(per_link_tbps * n_sats * links_per_sat / 2)
