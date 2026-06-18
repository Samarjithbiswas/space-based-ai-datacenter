"""
Pytest suite for orbital_dc.

Mixes (a) worked-example checks that pin published numbers, (b) property tests
(monotonicity, bounds, conservation), and (c) integration tests that the system
model closes. Parametrized to exercise the full input ranges.
"""
import math
import pytest
from orbital_dc import (orbit, thermal, power, adcs, comms, radiation, debris,
                        propulsion, reliability, compute, economics, environment)
from orbital_dc.system import DesignPoint, constellation

# ----------------------------------------------------------------- worked examples
def test_orbital_velocity():
    assert orbit.velocity(650) == pytest.approx(7534.76, abs=1.0)

def test_orbital_period():
    assert orbit.period(650) / 60 == pytest.approx(97.58, abs=0.1)

def test_sso_inclination():
    assert orbit.sso_inclination(650) == pytest.approx(97.8, abs=0.6)

def test_critical_beta():
    assert orbit.critical_beta(650) == pytest.approx(65.15, abs=0.2)

def test_part_i_baseline():
    b = thermal.report_i_baseline()
    assert b["T_radiator_C"] == pytest.approx(21.4, abs=0.6)
    assert b["T_junction_C"] == pytest.approx(111.4, abs=0.8)
    assert b["T_junction_failed_C"] == pytest.approx(114.7, abs=0.8)

def test_radiator_area_1mw():
    assert thermal.radiator_area(1e6, 20) == pytest.approx(1508.0, abs=6.0)

def test_interface_saturation():
    assert thermal.interface_delta_T(700) == pytest.approx(210.0, abs=0.1)
    assert thermal.interface_delta_T(1200) > 125  # passive impossible

def test_dose_10mm():
    assert radiation.cumulative_tid(10, 5) == pytest.approx(1054.0, abs=25.0)

def test_debris_probability():
    assert debris.collision_probability(15, 81, 5) * 100 == pytest.approx(16.66, abs=0.3)

def test_cascade():
    assert debris.cascade_neighbor_probability(150) * 100 == pytest.approx(8.51, abs=0.2)

def test_deorbit_dv():
    assert propulsion.deorbit_delta_v(650) == pytest.approx(131.6, abs=0.5)

def test_propellant():
    assert propulsion.propellant_mass(189.5, 220) == pytest.approx(34.4, abs=0.3)
    assert propulsion.propellant_mass(189.5, 1500) == pytest.approx(4.9, abs=0.2)

def test_comms_gain_loss():
    assert comms.telescope_gain_dB(0.1) == pytest.approx(106.2, abs=1.0)
    # 1000 km link is ~74 dB worse than 200 m (why the formation is tight)
    assert comms.free_space_loss_dB(1e6) - comms.free_space_loss_dB(200) == pytest.approx(74, abs=3)

def test_latency_vacuum_vs_fiber():
    assert comms.latency_ms(1000, "vacuum") < comms.latency_ms(1000, "fiber")

def test_power_array():
    assert power.array_power(1.0, "eol", 70.0) == pytest.approx(253.0, abs=5.0)

def test_economics_crossover():
    assert economics.launch_crossover_usd_per_kg() == pytest.approx(2650.6, abs=5.0)

def test_adcs_requires_fsm():
    p = adcs.pointing_budget()
    assert not p["link_closes_bus_only"]
    assert p["link_closes_with_fsm"]

# ----------------------------------------------------------------- property tests
@pytest.mark.parametrize("alt", [450, 500, 550, 600, 650, 700, 800])
def test_velocity_decreases_with_altitude(alt):
    assert orbit.velocity(alt) < orbit.velocity(alt - 50)

@pytest.mark.parametrize("alt", [500, 600, 650, 700, 800])
def test_lifetime_increases_with_altitude(alt):
    am = 3.5 / 375
    assert orbit.lifetime_years(alt, am, "mod") > orbit.lifetime_years(alt - 50, am, "mod")

@pytest.mark.parametrize("scen", ["min", "mod", "max"])
def test_density_scenarios_ordered(scen):
    assert environment.density(650, "min") < environment.density(650, "mod") < environment.density(650, "max")

@pytest.mark.parametrize("Q", [1e3, 1e4, 1e5, 1e6])
def test_radiator_area_linear(Q):
    # doubling load doubles area (linearity, no economy of scale)
    assert thermal.radiator_area(2 * Q, 20) == pytest.approx(2 * thermal.radiator_area(Q, 20), rel=1e-9)

@pytest.mark.parametrize("x", [1, 3, 5, 10, 15, 20])
def test_dose_decreases_with_shielding(x):
    assert environment.tid_dose_rate(x) < environment.tid_dose_rate(x - 1)

@pytest.mark.parametrize("d", [100, 150, 200, 300, 500, 1000])
def test_cascade_decreases_with_spacing(d):
    if d > 100:
        assert debris.cascade_neighbor_probability(d) < debris.cascade_neighbor_probability(d - 50)

@pytest.mark.parametrize("t", [1, 2, 5, 10])
def test_collision_prob_increases_with_time(t):
    assert debris.collision_probability(15, 81, t) >= debris.collision_probability(15, 81, t - 1)

@pytest.mark.parametrize("isp", [70, 220, 1500])
def test_propellant_positive_and_monotonic(isp):
    assert propulsion.propellant_mass(190, isp) > 0
    assert propulsion.propellant_mass(380, isp) > propulsion.propellant_mass(190, isp)

@pytest.mark.parametrize("mtbf", [30000, 50000, 100000, 200000])
def test_reliability_bounds(mtbf):
    r = reliability.reliability(5, mtbf)
    assert 0 < r < 1
    assert reliability.reliability(10, mtbf) < r

@pytest.mark.parametrize("prot", ["none", "ecc_checkpoint", "ecc_sel_tmr", "full_tmr"])
def test_availability_table(prot):
    a = radiation.availability(prot)
    assert 0 < a["usable_compute"] <= 1
    assert a["usable_compute"] + a["throughput_tax"] == pytest.approx(1.0)

def test_ecc_checkpoint_is_sweet_spot():
    assert (radiation.availability("ecc_checkpoint")["usable_compute"]
            > radiation.availability("full_tmr")["usable_compute"])

@pytest.mark.parametrize("chip", ["tpu_v6e", "h100", "b200"])
def test_perf_per_watt_positive(chip):
    assert compute.perf_per_watt(chip) > 0

@pytest.mark.parametrize("mfu", [0.1, 0.3, 0.5])
def test_delivered_scales_with_mfu(mfu):
    base = compute.delivered_pflops(4, "tpu_v6e", 0.1)
    assert compute.delivered_pflops(4, "tpu_v6e", mfu) == pytest.approx(base * (mfu / 0.1), rel=1e-9)

@pytest.mark.parametrize("price", [3770, 1500, 600, 300, 100])
def test_satellite_cost_decreases_with_price(price):
    assert economics.satellite_cost(price)["total"] >= economics.satellite_cost(price - 50)["total"] - 1e-6

@pytest.mark.parametrize("k,n", [(3, 4), (75, 81), (80, 89)])
def test_k_of_n_bounds(k, n):
    assert 0 <= reliability.k_of_n(k, n, 0.9) <= 1

# ----------------------------------------------------------------- integration
def test_design_point_closes():
    s = DesignPoint().solve()
    assert s["dry_mass_kg"] > 0
    assert s["delivered_PFLOPS"] > 0
    assert s["natural_lifetime_yr"] > 5  # 650 km fails the 5-yr rule
    assert not s["meets_disposal_rule"]
    assert s["debris_P_catastrophic_5yr"] > 0

@pytest.mark.parametrize("chip,active", [("tpu_v6e", False), ("h100", True), ("b200", True)])
def test_active_cooling_flag(chip, active):
    assert DesignPoint(chip=chip).solve()["active_cooling_required"] is active

def test_constellation_aggregates():
    c = constellation()
    assert c["fleet_PFLOPS"] > 0
    assert 0 < c["capacity_availability"] <= 1
    assert c["capex_usd"] > 0
