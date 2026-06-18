"""Structures and mass closure: derive the inertia tensor from geometry, size primary
structure from launch loads, and check deployable-panel fundamental frequency.

This replaces the fixed mass/inertia assumptions: ADCS disturbance torques and momentum
sizing can now be fed a geometry-derived inertia instead of a guessed Iz-Ix.
Sources: standard spacecraft structural design; plate vibration theory (Blevins).
"""
from __future__ import annotations
import numpy as np
from .constants import G0


def box_inertia(mass_kg: float, dx: float, dy: float, dz: float) -> tuple:
    """Principal moments of inertia [kg m^2] of a uniform box (Ix, Iy, Iz)."""
    Ix = mass_kg / 12.0 * (dy**2 + dz**2)
    Iy = mass_kg / 12.0 * (dx**2 + dz**2)
    Iz = mass_kg / 12.0 * (dx**2 + dy**2)
    return Ix, Iy, Iz


def panel_inertia_about_bus(mass_kg: float, length: float, offset: float) -> float:
    """Inertia [kg m^2] of a deployed panel about the bus axis (rod + parallel axis)."""
    return mass_kg * (length**2 / 12.0 + offset**2)


def spacecraft_inertia(bus_mass=120.0, bus_dims=(0.9, 0.9, 1.2),
                       array_mass=24.0, array_len=4.0, array_offset=2.4,
                       radiator_mass=20.0, radiator_len=2.0, radiator_offset=1.4) -> dict:
    """Assemble a diagonal inertia tensor [kg m^2] from bus + two arrays + radiators.
    Returns the tensor and the max principal-axis difference used for gravity-gradient torque."""
    Ix, Iy, Iz = box_inertia(bus_mass, *bus_dims)
    # arrays extend along x, radiators along -y: add about transverse axes
    Iy += 2 * panel_inertia_about_bus(array_mass, array_len, array_offset)
    Iz += 2 * panel_inertia_about_bus(array_mass, array_len, array_offset)
    Ix += panel_inertia_about_bus(radiator_mass, radiator_len, radiator_offset)
    Iz += panel_inertia_about_bus(radiator_mass, radiator_len, radiator_offset)
    I = sorted([Ix, Iy, Iz])
    return {"Ix": Ix, "Iy": Iy, "Iz": Iz, "I_min": I[0], "I_max": I[2],
            "inertia_diff": I[2] - I[0]}


def structural_mass(supported_mass_kg: float, structural_fraction: float = 0.20) -> float:
    """Primary-structure mass [kg] as a fraction of supported mass (typical 0.15-0.25)."""
    return supported_mass_kg * structural_fraction


def launch_load_margin(member_area_m2: float, supported_mass_kg: float,
                       g_load: float = 8.5, yield_MPa: float = 276.0) -> dict:
    """Quasi-static launch-load stress check on a primary member.
    Stress = (m * g_load * g0) / A; margin = yield/stress."""
    force = supported_mass_kg * g_load * G0
    stress_MPa = force / member_area_m2 / 1e6
    return {"stress_MPa": float(stress_MPa), "yield_MPa": yield_MPa,
            "safety_factor": float(yield_MPa / stress_MPa), "ok": yield_MPa / stress_MPa > 1.25}


def panel_fundamental_frequency(side_m: float, thickness_m: float, areal_mass: float,
                                E_Pa: float = 69e9, nu: float = 0.33,
                                boundary: float = 3.52) -> float:
    """Fundamental natural frequency [Hz] of a deployed panel (clamped-edge plate).
        f1 = (beta / 2pi) * sqrt( D / (rho_areal * a^4) ),  D = E t^3 / (12 (1-nu^2))
    boundary=3.52 (cantilever) .. 35.99 (clamped square); use a conservative value."""
    D = E_Pa * thickness_m**3 / (12 * (1 - nu**2))
    return float((boundary / (2 * np.pi)) * np.sqrt(D / (areal_mass * side_m**4)))
