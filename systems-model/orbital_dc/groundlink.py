"""Ground segment and network: satellite-to-ground optical/RF downlink with a real
atmospheric + cloud-availability model, ground-station contact geometry, daily data volume,
and end-to-end mesh latency vs terrestrial fiber.

Higher-fidelity additions over the inter-satellite `comms` module:
  - slant-path atmospheric attenuation via air mass = 1/sin(elevation)
  - cloud-cover outage solved by ground-station site diversity
  - contact-time geometry from the elevation mask
Sources: NASA TBIRD/LCRD; FSO link-budget literature (arXiv:2204.13177); standard astrodynamics.
"""
from __future__ import annotations
import numpy as np
from .constants import R_E, C_LIGHT, N_FIBER
from .orbit import period
from .comms import telescope_gain_dB, free_space_loss_dB


def air_mass(elevation_deg: float) -> float:
    """Relative atmospheric path length vs zenith (plane-parallel), 1/sin(elevation)."""
    el = max(np.radians(elevation_deg), np.radians(2.0))
    return float(1.0 / np.sin(el))


def atmospheric_loss_dB(elevation_deg: float, zenith_clear_dB: float = 2.0) -> float:
    """Clear-sky slant attenuation [dB] at 1.55 um = zenith loss x air mass."""
    return float(zenith_clear_dB * air_mass(elevation_deg))


def site_diversity_availability(n_stations: int, p_clear_single: float = 0.55) -> float:
    """Probability at least one of n independent ground stations is cloud-free,
    1 - (1 - p_clear)^n. Cloud is opaque at optical wavelengths, so this is the
    dominant ground-link availability driver."""
    return float(1.0 - (1.0 - p_clear_single) ** n_stations)


def contact_time_s(alt_km: float, elevation_mask_deg: float = 10.0) -> float:
    """Maximum ground-station contact duration per overhead pass [s].

    Earth-central half-angle to the elevation mask:
        lambda = arccos[(R_E/(R_E+h)) cos(eps)] - eps
    Contact arc = 2 lambda; time = (lambda/pi) * orbital period.
    """
    h = alt_km * 1e3
    eps = np.radians(elevation_mask_deg)
    lam = np.arccos((R_E / (R_E + h)) * np.cos(eps)) - eps
    return float(max(lam, 0.0) / np.pi * period(alt_km))


def ground_downlink(alt_km: float, p_tx_W: float = 1.0, aperture_m: float = 0.3,
                    rx_aperture_m: float = 0.6, data_rate_gbps: float = 100.0,
                    rx_sensitivity_dBm: float = -35.5, elevation_mask_deg: float = 20.0,
                    n_ground_stations: int = 4, p_clear_single: float = 0.55,
                    passes_per_day: int = 6) -> dict:
    """Optical downlink budget + availability + daily delivered volume."""
    slant = (R_E + alt_km * 1e3)            # worst-case ~ altitude+ (overhead); use range ~ alt/sin(mask)
    rng = alt_km * 1e3 / np.sin(np.radians(elevation_mask_deg))
    p_tx_dBm = 10 * np.log10(p_tx_W * 1e3)
    p_rx = (p_tx_dBm + telescope_gain_dB(aperture_m) + telescope_gain_dB(rx_aperture_m)
            - free_space_loss_dB(rng) - atmospheric_loss_dB(elevation_mask_deg) - 3.0)
    margin = p_rx - rx_sensitivity_dBm
    avail = site_diversity_availability(n_ground_stations, p_clear_single)
    t_contact = contact_time_s(alt_km, elevation_mask_deg)
    daily_volume_TB = (data_rate_gbps * 1e9 * t_contact * passes_per_day * avail) / 8 / 1e12
    return {"range_m": rng, "p_rx_dBm": float(p_rx), "margin_dB": float(margin),
            "link_closes": margin > 0, "availability": avail,
            "contact_time_s": t_contact, "daily_volume_TB": float(daily_volume_TB)}


def mesh_latency_ms(path_km: float, hops: int = 0, altitude_km: float = 650.0) -> dict:
    """End-to-end latency [ms]: LEO vacuum mesh vs terrestrial fiber, with up/down hops."""
    updown = 2 * altitude_km * 1e3 / C_LIGHT * 1e3
    space = path_km * 1e3 / C_LIGHT * 1e3 + updown
    fiber = path_km * 1e3 / (C_LIGHT / N_FIBER) * 1e3
    return {"leo_mesh_ms": float(space), "fiber_ms": float(fiber),
            "mesh_wins": space < fiber, "crossover_advantage_ms": float(fiber - space)}
