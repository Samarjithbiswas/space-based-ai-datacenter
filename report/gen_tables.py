"""Generate Markdown results tables from the orbital_dc model (numbers are real, not typed)."""
import sys
sys.path.insert(0, "../systems-model")
from orbital_dc import orbit, thermal, environment, debris, propulsion, comms, compute, power
from orbital_dc.system import DesignPoint, constellation

P = print
def row(*c): P("| " + " | ".join(str(x) for x in c) + " |")

P("### T1 Orbital parameters vs altitude")
row("Alt (km)", "v (km/s)", "Period (min)", "beta* (deg)", "Lifetime mod (yr)")
row(*["---"]*5)
for h in [400, 500, 600, 650, 700, 800, 1000]:
    row(h, f"{orbit.velocity(h)/1e3:.2f}", f"{orbit.period(h)/60:.1f}",
        f"{orbit.critical_beta(h):.1f}", f"{orbit.lifetime_years(h,3.5/233,'mod'):.0f}")

P("\n### T2 Radiator area (m2) vs heat load and temperature (double-sided)")
row("Heat load", "20 C", "40 C", "60 C"); row(*["---"]*4)
for q,lab in [(1e3,"1 kW"),(1e4,"10 kW"),(1e5,"100 kW"),(1e6,"1 MW")]:
    row(lab, f"{thermal.radiator_area(q,20):,.0f}", f"{thermal.radiator_area(q,40):,.0f}", f"{thermal.radiator_area(q,60):,.0f}")

P("\n### T3 Interface dT and passive feasibility vs chip (R_th=0.30 K/W)")
row("Chip", "TDP (W)", "Interface dT (C)", "Passive OK (<125)"); row(*["---"]*4)
for c,p in [("TPU v6e",200),("TPU",300),("H100",700),("B200",1000),("GB200",1200)]:
    dt=thermal.interface_delta_T(p); row(c,p,f"{dt:.0f}","yes" if dt<125 else "NO")

P("\n### T4 Cumulative TID rad(Si) vs aluminium shielding")
row("Al (mm)","5-yr (rad)","10-yr (rad)"); row(*["---"]*3)
for x in [1,3,5,10,15,20]:
    row(x, f"{environment.tid_dose_rate(x)*5:,.0f}", f"{environment.tid_dose_rate(x)*10:,.0f}")

P("\n### T5 Catastrophic debris probability (%) for the 81-sat cluster vs mission years")
row("Years","lo flux","mid","hi"); row(*["---"]*4)
for t in [1,2,3,5,7,10]:
    row(t, f"{debris.collision_probability(15,81,t,band='lo')*100:.1f}",
        f"{debris.collision_probability(15,81,t,band='mid')*100:.1f}",
        f"{debris.collision_probability(15,81,t,band='hi')*100:.1f}")

P("\n### T6 In-cluster cascade neighbor-hit probability (%) vs spacing")
row("Spacing (m)","P_hit (%)"); row(*["---"]*2)
for d in [100,150,200,300,500,1000]:
    row(d, f"{debris.cascade_neighbor_probability(d)*100:.1f}")

P("\n### T7 Per-satellite delta-v budget and propellant")
dv = propulsion.delta_v_budget(650, 3.5/233)
for k,v in dv.items(): row(k.replace('_',' '), f"{v:.1f} m/s")
P("")
row("Propulsion","Isp (s)","Propellant (kg) for total dv"); row(*["---"]*3)
for s,isp in [("Cold gas",70),("Hydrazine",220),("Electric",1500)]:
    row(s,isp,f"{propulsion.propellant_mass(dv['total'],isp,220):.0f}")

P("\n### T8 Optical link budget vs range (D=0.1 m, lambda=1.55 um)")
row("Range","Telescope gain (dB)","Free-space loss (dB)"); row(*["---"]*3)
for r,lab in [(150,"150 m"),(1e3,"1 km"),(1e5,"100 km"),(1e6,"1000 km"),(1e7,"10000 km")]:
    row(lab, f"{comms.telescope_gain_dB(0.1):.0f}", f"{comms.free_space_loss_dB(r):.0f}")

P("\n### T9 Mass budget (reference 4-chip satellite)")
s = DesignPoint().solve()
row("Subsystem","Mass (kg)"); row(*["---"]*2)
for k,v in sorted(s["mass_breakdown"].items(), key=lambda kv:-kv[1]):
    row(k, f"{v:.0f}")
row("**Dry total**", f"**{s['dry_mass_kg']:.0f}**")
row("Launch mass", f"{s['launch_mass_kg']:.0f}")

P("\n### T10 Power budget (reference satellite)")
pb = power.power_budget(s["compute_W"])
row("Consumer","Power (W)"); row(*["---"]*2)
for k,v in pb.items():
    if k!="electrical_PUE": row(k, f"{v:.0f}")
row("electrical PUE", f"{pb['electrical_PUE']:.2f}")

P("\n### T11 Reference design-point summary")
for k in ["compute_W","total_power_W","effective_PUE","radiator_area_m2","tid_5yr_rad","tid_margin",
          "natural_lifetime_yr","debris_P_catastrophic_5yr","delivered_PFLOPS","throttle_loss_frac",
          "ground_downlink_TB_day","lcoe_usd_per_pflop_hr"]:
    row(k.replace('_',' '), f"{s[k]:.3f}" if isinstance(s[k],float) else s[k])

P("\n### T12 Constellation summary (81 satellites)")
c = constellation()
for k in ["fleet_PFLOPS","fleet_power_MW","capex_usd","tco_10yr_usd","capacity_availability"]:
    row(k.replace('_',' '), f"{c[k]:,.2f}" if isinstance(c[k],float) else c[k])
