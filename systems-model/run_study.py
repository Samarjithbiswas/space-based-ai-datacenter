"""End-to-end study runner: solves the integrated design point, aggregates the
constellation, runs the Monte-Carlo, generates all figures, and prints a report.

    python run_study.py
"""
from orbital_dc.system import DesignPoint, constellation
from orbital_dc.montecarlo import monte_carlo, one_at_a_time
from orbital_dc import figures, thermal


def banner(t): print("\n" + "=" * 78 + f"\n {t}\n" + "=" * 78)


def main():
    banner("PART I BASELINE  (reproduced)")
    for k, v in thermal.report_i_baseline().items():
        print(f"  {k:24s}: {v if isinstance(v,(int,float)) else v:.4f}" if isinstance(v, float)
              else f"  {k:24s}: {v}")

    banner("INTEGRATED DESIGN POINT  (4x TPU v6e, 650 km, self-consistent)")
    s = DesignPoint().solve()
    for k in ["compute_W", "total_power_W", "electrical_PUE", "effective_PUE", "array_area_m2",
              "radiator_area_m2", "interface_dT_C", "active_cooling_required", "tid_5yr_rad",
              "tid_margin", "dry_mass_kg", "launch_mass_kg", "delta_v_total_mps", "propellant_kg",
              "natural_lifetime_yr", "meets_disposal_rule", "debris_P_catastrophic_5yr",
              "cascade_neighbor_P", "delivered_PFLOPS", "throttle_loss_frac", "Tj_peak_C",
              "ground_downlink_TB_day", "ground_availability", "inertia_max_kgm2",
              "gravity_gradient_torque_Nm", "lcoe_usd_per_pflop_hr", "satellite_cost_usd"]:
        print(f"  {k:28s}: {s[k]}")

    banner("CONSTELLATION  (81 satellites)")
    c = constellation()
    for k in ["n_sats", "fleet_PFLOPS", "fleet_power_MW", "capex_usd", "tco_10yr_usd",
              "capacity_availability"]:
        print(f"  {k:24s}: {c[k]:,.3f}" if isinstance(c[k], float) else f"  {k:24s}: {c[k]:,}")

    banner("MONTE-CARLO  (5/50/95 percentiles)")
    for metric, p in monte_carlo(4000).items():
        print(f"  {metric:30s}: P5={p[5]:.2f}  P50={p[50]:.2f}  P95={p[95]:.2f}")

    banner("SENSITIVITY  (radiator temperature)")
    for row in one_at_a_time("radiator_temp_C", [20, 40, 60]):
        print(f"  T={row['radiator_temp_C']:>3} C -> radiator {row['radiator_area_m2']:6.1f} m^2, "
              f"dry {row['dry_mass_kg']:.0f} kg, eff PUE {row['effective_PUE']:.2f}")

    banner("FIGURES")
    for f in figures.generate_all():
        print("  wrote figures/" + f)


if __name__ == "__main__":
    main()
