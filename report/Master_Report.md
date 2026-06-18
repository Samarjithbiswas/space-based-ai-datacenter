# Space-Based AI Data Centers: A Complete Engineering Study
## Feasibility, Survivability, Mathematics, Simulations, and Predictions

**Author:** Samarjith Biswas, PhD
**Edition:** June 2026 (verified-data, research-backed)
**Reference architecture:** Google Project Suncatcher ([arXiv:2511.19468](https://arxiv.org/abs/2511.19468))

> This is one self-contained report: the systems analysis, the full mathematical derivations,
> the open simulations that produce every number, and quantitative predictions for 2027-2035.
> Every load-bearing fact is cited to a primary source; every forward number is flagged as a
> projection. All code is open and reproducible.

---

## Executive summary

Space-based AI compute crossed from concept to flight demonstration in 2025-2026. Three programs
anchor the field: **Google Project Suncatcher** (an illustrative 81-satellite, 1 km-radius TPU
constellation in a 650 km dawn-dusk sun-synchronous orbit, two prototypes targeted *by* early
2027 with Planet) [arXiv:2511.19468; blog.google]; **Starcloud**, which flew an NVIDIA H100 in
orbit (Starcloud-1, ~60 kg, 2 Nov 2025) and envisions a 5 GW orbital data center [NVIDIA]; and
**Axiom Space**, whose first Orbital Data Center nodes reached LEO on 11 Jan 2026 with a stated
kW-to-MW scaling goal [Axiom].

The engineering verdict, from first-principles physics and open simulation:

1. **Radiative cooling works and is now flight-proven**, but it does not scale for free:
   radiator area is linear in power (~1,500 m²/MW), and a passive chip-to-radiator chain
   saturates above ~400 W, forcing liquid cooling at the die for H100/Blackwell-class parts.
2. **Radiation is comfortably survivable.** Google's Trillium TPU showed first HBM irregularities
   at 2 krad(Si), ~3x the 750 rad(Si) 5-year requirement, with **no hard failures to 15 krad(Si)**
   [arXiv:2511.19468]. The cost is a single-event-upset throughput tax of order 10-20%.
3. **Orbital debris in a tight formation is the binding, unsolved constraint** (central ~17%
   catastrophic-impact probability per 81-sat cluster over 5 years), and the sub-200 m spacing
   that enables the optical links is what makes a fragmentation cascade and collision-avoidance
   dangerous: the "formation paradox."
4. **End-of-life requires propulsion.** At 650 km, natural decay is ~22 years (moderate solar),
   failing the binding **FCC 5-year rule** [FCC 22-74]; controlled de-orbit dominates the Δv budget.
5. **Launch cost is no longer the swing variable**, and the optimistic "$200/kg by 2035" parity
   date is assumption-fragile: an independent Monte-Carlo puts median parity around **2044**
   (P5 2037), later than the vendor projection.

Honest framing: the most load-bearing source for the radiation, link-budget, and cost-parity
claims is a **non-peer-reviewed, vendor-authored preprint**; a real **TRL gap** separates what is
demonstrated (one H100 in orbit, ground TPU rad-testing, a 1.6 Tbps bench link, kW-class nodes)
from what the vision requires (MW-GW clusters, flown 10 Tbps formation links, $200/kg launch,
in-flight formation station-keeping). The demonstrators now flying should target debris autonomy
and credible disposal, because those, not heat, decide constellation-scale viability.

---

# PART I - CONTEXT AND VERIFIED STATUS

## 1. What is actually flying (verified, 2025-2026)

| Program | Status (cited) | Note |
|---|---|---|
| **Suncatcher** (Google/Planet) | 81-sat, 1 km-radius cluster, 650 km dawn-dusk SSO; 2 prototypes *by* early 2027 [arXiv:2511.19468; planet.com] | "by early 2027" is a corporate target, subject to slip |
| **Starcloud-1** | NVIDIA H100 (80 GB, ~4 PFLOPS), ~60 kg, launched 2 Nov 2025 [NVIDIA] | "100x prior space compute" is a company claim |
| **Starcloud** vision | 5 GW data center, ~4 km x 4 km arrays [NVIDIA] | aspirational early-2030s target |
| **Axiom ODC** | nodes reached LEO 11 Jan 2026; kW-to-MW goal [Axiom] | MW-scale is a future goal, not current capacity |

**Refuted for transparency** (failed 3-0 adversarial verification): Starcloud's "10x cheaper
including launch / 10x CO2 savings" claim, and "Axiom's first nodes by end of 2025" (actual: Jan
2026). Treat marketing economics with caution.

## 2. Corrections incorporated from verification

- **Disposal rule is 5 years, not 25** (FCC 22-74, adopted 29 Sep 2022, effective 29 Sep 2024,
  for anything in or transiting below 2,000 km) [fcc.gov; federalregister.gov].
- **TPU radiation margin is large**: first HBM irregularities at 2 krad(Si); no hard failures to
  15 krad(Si); requirement ~750 rad(Si)/5 yr; ~150 rad(Si)/yr behind 10 mm Al [arXiv:2511.19468].
- **TPU v6e TDP is undisclosed** by Google; treated as ~150-200 W (the single weakest input).
- **Optical links are range-bound**: a 10 Gbps 1550 nm OOK link at 1 W / 3 dB margin is reliable
  only to ~5,419 km [arXiv:2204.13177], which is why the cluster flies ~150 m apart.

---

# PART II - PHYSICS, DERIVATIONS, AND SIMULATIONS

Each section gives the finding, the governing equation derived from first principles, a worked
example matching the open model, and the figure. Constants: $\mu=3.986\times10^{14}\ \mathrm{m^3/s^2}$,
$R_E=6.371\times10^6\ \mathrm{m}$, $\sigma=5.670\times10^{-8}\ \mathrm{W/m^2K^4}$, $g_0=9.80665$,
$S_0=1361\ \mathrm{W/m^2}$.

## 3. Orbital mechanics

Gravity as centripetal force, $\mu m/a^2 = m v^2/a$, gives the circular speed and (from
$v=2\pi a/T$) Kepler's period:

$$v = \sqrt{\frac{\mu}{a}}, \qquad T = 2\pi\sqrt{\frac{a^3}{\mu}}.$$

At 650 km ($a=7.021\times10^6$ m): $v=7534.8$ m/s, $T=97.6$ min. The specific energy
$\mathcal{E}=-\mu/2a$ drives the decay derivation below. The sun-synchronous inclination follows
from matching $J_2$ nodal precession to Earth's solar rate, giving $i\approx 98.0^\circ$ at 650 km.

## 4. End-of-life: drag, decay, and the 5-year rule (Fig. 1)

Drag force $F_D=\tfrac12\rho v^2 C_D A$ removes orbital energy at $d\mathcal{E}/dt=-a_D v$, with
$a_D=\tfrac12\rho v^2 C_D(A/m)$. Using $\mathcal{E}=-\mu/2a$ so $d\mathcal{E}/dt=(\mu/2a^2)\dot a$
and $v=\sqrt{\mu/a}$:

$$\boxed{\ \frac{da}{dt} = -\,C_D\,\frac{A}{m}\,\rho(h)\,\sqrt{\mu a}\ }$$

Integrated (adaptive Euler, NRLMSIS density) to 120 km re-entry. **Worked result:** the reference
bus ($A/m=0.0084$, $C_D=2.2$) decays in **~22 yr** (moderate solar; 4 yr solar-max, 312 yr
solar-min). Since the FCC rule is 5 years, **active de-orbit is mandatory.** The ~100x
solar-cycle density swing is the dominant uncertainty (shown as a band).

![Fig. 1](figures/fig1_orbital_decay.png)

## 5. Thermal: feasibility and the two walls (Fig. 2)

Integrating Planck's law over the hemisphere and all wavelengths gives Stefan-Boltzmann,
$E_b=\sigma T^4$; a gray double-sided radiator with parasitic fraction $f_p$ needs

$$\boxed{\ A_{\mathrm{rad}} = \frac{Q}{\varepsilon\,\sigma\,T^4\,n_s\,(1-f_p)}\ }$$

**linear in $Q$**: no economy of scale. Worked: 1 MW at 20 C, $\varepsilon=0.90$, $n_s=2$,
$f_p=0.12$ gives $A_{\mathrm{rad}}=1508\ \mathrm{m^2}$ (matches the ~1,200 m²/MW industry rule;
consistent with Starcloud's ~4 km panel vision for GW-scale). The second wall is conductive:
with a passive chain $T_j=T_{\mathrm{rad}}+Q R_{th}$ and $R_{th}=0.30$ K/W, the interface rise
$P\times0.30$ is 90 C at 300 W but **210 C at 700 W and 360 C at 1200 W** - exceeding the entire
125 C budget. Above ~417 W, **chip-level liquid/loop-heat-pipe cooling is mandatory.**

![Fig. 2](figures/fig2_thermal_wall.png)

## 6. Radiation and reliability (Fig. 4)

Dose behind aluminium attenuates as $\dot D(x)=D_0 e^{-x/\lambda}+D_\infty$ atop a proton floor.
At 10 mm Al, 5-year dose is ~1.06 krad(Si) - consistent with the cited ~150 rad/yr
[arXiv:2511.19468]. **Margin is large:** first HBM irregularities at 2 krad (~1.9x), no hard
failures to 15 krad (~14x). The real cost is single-event upsets ($R_{\mathrm{SEU}}=\sigma_{\mathrm{SEU}}\,\phi\,N_{\mathrm{bits}}$):
because AI inference tolerates bit-flips, the optimal design is ECC + checkpointing (~86% usable
compute), not full triple-modular redundancy (which halves throughput) - a 10-20% throughput tax.

![Fig. 4](figures/fig4_radiation.png)

## 7. Orbital debris and the cascade (Fig. 3)

Rare independent impacts are Poisson; the probability of at least one catastrophic ($>$1 cm) hit
in the cluster is

$$\boxed{\ P = 1 - e^{-\Phi A N t}\ }$$

With ORDEM/MASTER-class flux $\Phi=3\times10^{-5}\ \mathrm{m^{-2}yr^{-1}}$, $A=15\ \mathrm{m^2}$,
$N=81$, $t=5$: $P=16.7\%$ (band 6-46%). A fragmentation spreads $N_f$ lethal fragments over a
sphere $4\pi d^2$; a neighbor at $d$ is struck with

$$\boxed{\ P_{\mathrm{hit}} = 1 - \exp\!\left(-\frac{N_f r_t^2}{4 d^2}\right)\ }$$

giving ~8.5% per neighbor at 150 m. Since $P_{\mathrm{hit}}\propto d^{-2}$, widening to 1 km cuts
it below 1% but breaks the optical-link budget: the **formation paradox.** (Note: ORDEM 3.2 /
ESA MASTER are the authoritative flux tools; LEGEND models the Kessler cascade. The 650 km
flux here is model-class, not a verified per-orbit figure - see caveats.)

![Fig. 3](figures/fig3_debris_risk.png)

## 8. Optical communications: why the formation is tight (Fig. C)

Telescope gain $G=(\pi D/\lambda)^2$ and free-space loss $L_{\mathrm{fs}}=(4\pi R/\lambda)^2$ set
the budget. With the cited realized design point - 1550 nm, 80 mm Rx telescope, 15 µrad
divergence, 1 µrad pointing, -35.5 dBm sensitivity, 10 Gbps OOK [arXiv:2204.13177] - a 1 W link
with 3 dB margin is reliable only to **~5,419 km** (margin zero at 7,654 km), and path loss rises
**+20 dB per decade** of range (34 mW at 1,000 km to 3.41 W at 10,000 km; the Mynaric terminal is
capped at 1 W). Suncatcher needs **~10 Tbps aggregate per link**, met by COTS DWDM (24 channels,
9.6 Tbps bidirectional per 10 cm aperture; bench demo 1.6 Tbps) only by flying ~150 m apart -
the inverse-square received-power scaling is the whole reason for the tight cluster.

![Fig. C](systems_figs/fig_comms.png)

## 9. Power, ADCS, propulsion, reliability, compute (Figs. 5, P, R, K)

- **Power.** $P = S_0 A\,\eta(T,\mathrm{life})\,\kappa\,\eta_{\mathrm{path}}$; triple-junction
  cells deliver ~253 W/m² at the load (EOL, 70 C). A dawn-dusk SSO is >95% sunlit, so the battery
  is tiny - a major mass lever.
- **ADCS.** A laser link needs sub-µrad pointing; a star tracker gives ~10 µrad, so a
  fine-steering mirror is mandatory (the bus cannot point the beam). Pointing loss
  $L=\exp(-2\theta_{\mathrm{err}}^2/\theta_{\mathrm{div}}^2)$.
- **Propulsion.** De-orbit by Hohmann perigee-lowering,
  $\Delta v = v_{c1}(1-\sqrt{2 r_2/(r_1+r_2)})=131.6$ m/s, dominates the ~190 m/s 5-year budget;
  propellant by Tsiolkovsky, $m_p=m_{\mathrm{dry}}(e^{\Delta v/I_{sp}g_0}-1)$ = ~5 kg (electric).
- **Reliability.** $R(t)=e^{-t/\mathrm{MTBF}}$; with no on-orbit repair, availability is bought
  by k-of-n redundancy and replenishment (~20%/yr at a 5-yr life).
- **Compute.** Delivered $= n\,P_{\mathrm{peak}}\,\mathrm{MFU}\,a_r$; inference MFU is only ~8-10%,
  so effective $/PFLOP-hr is 3-10x the peak figure, and effective PUE folds in the radiation tax.

![Fig. 5](figures/fig5_deltav.png)

*(Full derivations for every equation above, with intermediate steps and worked examples, are in
the [mathematical guide](Mathematical_Guide_Complete.html); the systems-model `docs/METHODS.md`
maps each to code.)*

---

# PART III - PREDICTIONS (2027-2035+)

## 10. Launch-cost parity is the swing variable, and it is fragile (Fig. PRED)

Suncatcher projects LEO launch reaching **≤$200/kg by ~2035** under a ~20% learning rate
(requiring ~370,000 t additional cumulative mass, ~1,800 Starship launches, ~180/yr), at which
point launched-power price (~$810/kW/yr) approaches terrestrial data-center power spend
($570-3,000/kW/yr) [arXiv:2511.19468]. This is the entire economic case.

**It is assumption-fragile.** An independent Monte-Carlo (Wright learning curve on cumulative
launched mass, sampling learning rate 15-25%, 2026 price $1,200-3,500/kg, payload 150-250 t, peak
cadence 80-220/yr) puts **median parity around 2044** (P5 2037, P95 2050), with ~0% probability of
hitting 2035. The vendor's 2035 sits at the optimistic edge and requires its specific aggressive
anchors (Falcon Heavy starting point, full Starship reusability at 200 t / ~$2M marginal,
sustained 20% learning). **Prediction: cost parity is more likely late-2030s to mid-2040s than
2035** - necessary but not sufficient, and gated by hardware/lifetime/utilization regardless.

![Fig. PRED](figures_pred/fig_cost_parity.png)

## 11. Capability and risk trajectory

| Horizon | Likely (engineering judgement, anchored to cited status) |
|---|---|
| **2027** | Suncatcher 2-prototype demo (TPUs in orbit); Starcloud-2 with Blackwell; first MW-class node attempts. TRL of components rises; constellation-scale unproven. |
| **2028-2030** | First kW-to-low-MW operational nodes; flown 10 Tbps formation links; in-flight J2 station-keeping validated - or not. Debris-avoidance autonomy becomes the gating demo. |
| **2030-2035** | If launch trends hold, niche economic cases (latency-critical, space-native data); GW-scale remains aspirational. Cost parity unlikely before ~2035 on broad assumptions. |
| **Debris/Kessler** | 650 km dawn-dusk SSO is congested; a ~1 km cluster raises cascade exposure. Trajectory depends on disposal compliance (FCC 5-yr) and avoidance autonomy; quantify with ORDEM 3.2 / LEGEND before constellation commit. |

**The binding milestones are not thermal.** They are: (1) demonstrated autonomous,
cluster-coordinated debris avoidance at sub-km spacing; (2) a credible propulsive de-orbit; (3) a
flown MW-class radiator at real chip power; (4) launch economics actually reaching the parity band.

---

# PART IV - HONEST CAVEATS

1. **Source quality.** The radiation, link-budget, and cost-parity claims rest on a
   non-peer-reviewed, vendor-authored preprint (arXiv:2511.19468); self-reported, not
   independently replicated.
2. **TRL gap.** Demonstrated today: one H100 in orbit, ground TPU rad-testing, a 1.6 Tbps bench
   link, kW-class nodes. Required: MW-GW clusters, flown 10 Tbps formation links, $200/kg launch,
   in-flight formation control - none demonstrated.
3. **Model-class numbers.** The 650 km debris flux, atmospheric density/decay, and radiative
   limits in this report are computed/first-order with stated uncertainty bands, not verified
   per-orbit measurements; for mission work use NASA DAS, ORDEM 3.2 / ESA MASTER+DRAMA,
   SPENVIS/SHIELDOSE-2, and a full thermal/orbit toolchain.
4. **Refuted marketing.** "10x cheaper including launch" and specific schedule claims failed
   verification - treat vendor economics skeptically.

---

# Conclusions

Cooling is the part that already works. Radiation is survivable. The real frontier is
**debris survivability in a tight formation, credible disposal, and economics** - and the
launch-cost parity that underwrites the business case is later and less certain than advertised.
The right near-term program is exactly what is flying: small, attritable demonstrators that retire
the survivability and autonomy risks. Build those, measure in flight, and gate constellation-scale
deployment behind a demonstrated answer to the formation/debris paradox - not behind a launch-cost
milestone.

---

## References (verified, primary where possible)

1. Agüera y Arcas et al. (2025). *Towards a future space-based, highly scalable AI infrastructure
   system design.* arXiv:2511.19468. https://arxiv.org/abs/2511.19468
2. Google. *Project Suncatcher.* https://blog.google/innovation-and-ai/technology/research/google-project-suncatcher/
3. Planet Labs. *Platform for Project Suncatcher.* https://www.planet.com/pulse/planet-to-build-and-operate-advanced-space-platform-for-project-suncatcher-moonshot/
4. NVIDIA. *Starcloud (Starcloud-1, H100 in orbit).* https://blogs.nvidia.com/blog/starcloud/
5. Axiom Space. *Orbital Data Center nodes.* https://www.axiomspace.com/release/axiom-space-to-launch-orbital-data-center-nodes-to-support-national-security-commercial-international-customers
6. Liang et al. (2022). *Link Budget Analysis for Free-Space Optical Satellite Networks.* arXiv:2204.13177.
7. FCC. *5-Year Rule (FCC 22-74).* https://www.fcc.gov/document/fcc-adopts-new-5-year-rule-deorbiting-satellites-0 ; Federal Register 2024-17093.
8. NASA ORDEM 3.2 User Guide, NTRS 20230014989. https://ntrs.nasa.gov/citations/20230014989
9. ESA. *MASTER / DRAMA debris tools.* https://www.esa.int/Space_Safety/Space_Debris/ESA_makes_space_debris_software_available_online
10. SPENVIS. *SHIELDOSE.* https://www.spenvis.oma.be/help/background/shieldose/shieldose.html
11. NRLMSIS 2.1 (Picone et al. 2002), doi:10.1029/2002JA009430.
12. NVIDIA H100 / B200 / GB200 datasheets; Google Cloud TPU v6e documentation.

## Reproduce everything

```bash
git clone https://github.com/Samarjithbiswas/space-based-ai-datacenter
cd space-based-ai-datacenter && pip install numpy matplotlib pytest
python reproduce_all.py        # all models, figures, equation images
python report/predictions.py   # the cost-parity Monte-Carlo
```

Every figure and number above is regenerated by the open code; the full derivations are in the
mathematical guide. Independent reproduction and corrections are welcome.
