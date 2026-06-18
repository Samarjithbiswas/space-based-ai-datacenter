"""Attitude determination & control and optical pointing.

Key result: the bus alone (star-tracker + reaction-wheel jitter ~ several urad) cannot hold a
sub-urad laser link; a coarse-gimbal + fine-steering-mirror terminal is mandatory.
Sources: SDA OCT standard, GRACE-FO LRI, Mynaric/TESAT, NASA NTRS, AIAA SmallSat.
"""
from __future__ import annotations
import numpy as np
from .constants import R_E, MU

ARCSEC_TO_URAD = 4.84814   # 1 arcsec = 4.848 urad


def diffraction_divergence(aperture_m: float, wavelength_m: float = 1.55e-6) -> float:
    """Full-angle diffraction-limited beam divergence [rad], Theta ~ 2.44 lambda/D (Airy)."""
    return float(2.44 * wavelength_m / aperture_m)


def beam_spot_radius(divergence_rad: float, range_m: float) -> float:
    """Far-field beam spot radius [m] ~ (divergence/2) * range."""
    return float(0.5 * divergence_rad * range_m)


def pointing_loss_dB(jitter_rad: float, divergence_rad: float) -> float:
    """Pointing loss [dB] for a Gaussian beam, L = exp(-2*theta_err^2/theta_div^2)."""
    ratio = np.exp(-2 * (jitter_rad / divergence_rad) ** 2)
    return float(-10 * np.log10(max(ratio, 1e-12)))


def star_tracker_knowledge_urad(accuracy_arcsec: float = 2.0) -> float:
    """Absolute attitude knowledge [urad] from a star tracker; ~10 urad at 2 arcsec."""
    return accuracy_arcsec * ARCSEC_TO_URAD


def gravity_gradient_torque(alt_km: float, inertia_diff: float, theta_rad: float = 0.1) -> float:
    """Peak gravity-gradient torque [N m] = 3*n^2*|Iz-Ix|*sin(2 theta)/2."""
    a = R_E + alt_km * 1e3
    n = np.sqrt(MU / a**3)
    return float(1.5 * n**2 * inertia_diff * np.sin(2 * theta_rad))


def aero_torque(alt_km: float, area_m2: float, cp_cg_offset_m: float, cd: float = 2.2) -> float:
    """Aerodynamic disturbance torque [N m] = drag_force * (cp-cg offset)."""
    from .environment import density
    from .orbit import velocity
    v = velocity(alt_km)
    drag = 0.5 * density(alt_km) * v**2 * cd * area_m2
    return float(drag * cp_cg_offset_m)


def pointing_budget(jitter_bus_urad=10.0, jitter_rw_urad=1.0, fsm_residual_urad=0.3):
    """Combine error sources (RSS) and report whether a sub-urad link can close.
    Returns total LOS error [urad] WITH and WITHOUT a fine-steering mirror."""
    without_fsm = np.sqrt(jitter_bus_urad**2 + jitter_rw_urad**2)
    with_fsm = fsm_residual_urad   # the FSM closes the loop on the beacon, replacing bus error
    return {"bus_only_urad": float(without_fsm), "with_fsm_urad": float(with_fsm),
            "link_closes_bus_only": without_fsm < 1.0, "link_closes_with_fsm": with_fsm < 1.0}
