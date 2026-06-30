"""Validation suite for orbital_dc. Asserts worked examples and internal consistency.
Run: python validate.py   (exit 0 = all pass)."""
from orbital_dc import orbit, thermal, power, adcs, comms, radiation, debris, propulsion, \
    reliability, compute, economics
from orbital_dc.system import DesignPoint, constellation

C = []
def chk(name, val, exp, tol, unit=""):
    ok = abs(val - exp) <= tol; C.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:42s} = {val:12.4f} {unit:6s} (exp {exp} +/- {tol})")

print("=" * 86)
print(" orbital_dc VALIDATION")
print("=" * 86)

# orbit
chk("orbit.velocity(650)",            orbit.velocity(650),            7534.76, 1.0, "m/s")
chk("orbit.period(650)/60",           orbit.period(650) / 60,         97.58,   0.1, "min")
chk("orbit.sso_inclination(650)",     orbit.sso_inclination(650),     97.8,    0.6, "deg")
chk("orbit.critical_beta(650)",       orbit.critical_beta(650),       65.15,   0.2, "deg")
life = orbit.lifetime_years(650, 3.5/233, "mod")
ok = 8 <= life <= 18; C.append(ok)
print(f"  [{'PASS' if ok else 'FAIL'}] orbit.lifetime_years(650,mod)              = {life:12.4f} yr     (exp 8-18)")

# thermal (Part I reproduction)
b = thermal.report_i_baseline()
chk("Part I T_radiator",              b["T_radiator_C"],              21.4,    0.6, "C")
chk("Part I T_junction",              b["T_junction_C"],              111.4,   0.8, "C")
chk("Part I T_junction (pipe fail)",  b["T_junction_failed_C"],       114.7,   0.8, "C")
chk("thermal.radiator_area(1MW,20)",  thermal.radiator_area(1e6, 20), 1508.0,  6.0, "m2")
chk("thermal.interface_delta_T(700)", thermal.interface_delta_T(700), 210.0,   0.1, "K")

# power / comms / adcs
chk("power.array_power(1 m2,eol,70C)", power.array_power(1.0, "eol", 70.0), 253.0, 4.0, "W")
chk("comms.telescope_gain(0.1 m)",     comms.telescope_gain_dB(0.1),   106.2,   1.0, "dB")
chk("comms.latency vacuum 1000 km",    comms.latency_ms(1000, "vacuum"), 3.336, 0.01, "ms")
ptr = adcs.pointing_budget()
ok = (not ptr["link_closes_bus_only"]) and ptr["link_closes_with_fsm"]; C.append(ok)
print(f"  [{'PASS' if ok else 'FAIL'}] adcs FSM required to close optical link     = {str(ok):>12s}")

# radiation / debris / propulsion
chk("radiation.cumulative_tid(10,5)", radiation.cumulative_tid(10, 5), 1054.0, 25.0, "rad")
chk("debris.collision_prob(15,81,5)", debris.collision_probability(15, 81, 5)*100, 16.66, 0.3, "%")
chk("debris.cascade_neighbor(150)",   debris.cascade_neighbor_probability(150)*100, 8.51, 0.2, "%")
chk("propulsion.deorbit_dv(650)",     propulsion.deorbit_delta_v(650), 131.6,  0.5, "m/s")
chk("propulsion.propellant(189.5,1500)", propulsion.propellant_mass(189.5,1500), 2.85, 0.2, "kg")

# reliability
chk("reliability R(5yr,50000h)",      reliability.reliability(5, 50000), 0.417, 0.01)

# economics
chk("economics.launch_crossover",     economics.launch_crossover_usd_per_kg(), 4721.0, 5.0, "$/kg")

# integrated system closes
s = DesignPoint().solve()
ok = s["dry_mass_kg"] > 0 and s["delivered_PFLOPS"] > 0 and s["natural_lifetime_yr"] > 5; C.append(ok)
print(f"  [{'PASS' if ok else 'FAIL'}] system.DesignPoint().solve() closes         = {str(ok):>12s}")
con = constellation()
ok = con["fleet_PFLOPS"] > 0 and 0 < con["capacity_availability"] <= 1; C.append(ok)
print(f"  [{'PASS' if ok else 'FAIL'}] system.constellation() aggregates           = {str(ok):>12s}")

print("=" * 86)
print(f"  {sum(C)}/{len(C)} checks passed.")
print("=" * 86)
raise SystemExit(0 if sum(C) == len(C) else 1)
