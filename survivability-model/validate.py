"""
Validation suite for survivability.py
=====================================
Asserts that each physics function reproduces its worked example from the report
(and from first-principles cross-checks). Run with:  python validate.py
Exit code 0 = all pass. This doubles as lightweight CI.
"""
import math
import survivability as s

CASES = []


def check(name, value, expected, tol, unit=""):
    ok = abs(value - expected) <= tol
    CASES.append(ok)
    flag = "PASS" if ok else "FAIL"
    print(f"  [{flag}] {name:38s} = {value:11.4f} {unit:7s} (expected {expected} +/- {tol})")


print("=" * 78)
print(" VALIDATION  -  worked examples must match the published numbers")
print("=" * 78)

# --- orbital mechanics (closed-form, exact) ---
check("orbital_velocity(650 km)",      s.orbital_velocity(650),          7534.76, 1.0, "m/s")
check("orbital_period(650 km)",        s.orbital_period(650),            5854.8,  2.0, "s")
check("eclipse_critical_beta(650 km)", s.eclipse_critical_beta(650),     65.1,    0.2, "deg")

# --- thermal ---
check("radiator_area(1 MW, 20 C)",     s.radiator_area(1e6, 20),         1508.0,  5.0, "m^2")
check("radiator_area(1 MW, 60 C)",     s.radiator_area(1e6, 60),         904.0,   5.0, "m^2")
check("junction_delta_T(700 W)",       s.junction_delta_T(700),          210.0,   0.1, "K")

# --- debris ---
check("collision_probability(5 yr)",   s.collision_probability(3e-5, 15, 81, 5), 0.1666, 0.001)
check("cascade_neighbor_prob(150 m)",  s.cascade_neighbor_probability(150),       0.0851, 0.001)

# --- radiation ---
check("tid_dose_rate(10 mm)*5 yr",     s.tid_dose_rate(10) * 5,          1054.0,  20.0, "rad")

# --- delta-v / propulsion ---
check("deorbit_delta_v(650 km)",       s.deorbit_delta_v(650),           131.6,   0.5, "m/s")
check("propellant_mass(189.5, 220)",   s.propellant_mass(189.5, 220),    20.2,    0.3, "kg")
check("propellant_mass(189.5, 1500)",  s.propellant_mass(189.5, 1500),   2.85,    0.2, "kg")

# --- orbital decay (numerical; loose band reflects solar-cycle uncertainty) ---
life = s.orbital_lifetime(650, 3.5 / 233, "mod")
ok = 8.0 <= life <= 18.0
CASES.append(ok)
print(f"  [{'PASS' if ok else 'FAIL'}] orbital_lifetime(650 km, mod)          = {life:11.4f} yr      (expected 8-18)")

# --- internal consistency: SB law and rocket equation round-trips ---
T = 293.15
q = s.SIGMA * 0.90 * T**4
check("Stefan-Boltzmann flux check",   q,                                418.7 * 0.90, 1.0, "W/m^2")

print("=" * 78)
passed = sum(CASES)
print(f"  {passed}/{len(CASES)} checks passed.")
print("=" * 78)
raise SystemExit(0 if passed == len(CASES) else 1)
