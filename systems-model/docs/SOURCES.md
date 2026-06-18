# Data Sources and Confidence

Confidence flags: **[O]** official/agency/datasheet · **[M]** standard model or peer-reviewed ·
**[E]** estimate/derived/secondary.

## Reference architecture — Project Suncatcher (arXiv:2511.19468) [O]
650 km dawn-dusk SSO · 81-sat cluster, 1 km radius, 100–200 m spacing · TPU v6e (918 TFLOPS
BF16, 32 GB HBM), 67 MeV proton test, 5-yr req 750 rad(Si), HBM limit ~2 krad · 800 Gbps /
1.6 Tbps optical @1.55 µm · launch viability <$200/kg by ~2035 · cooling via heat pipes + radiators.

## Environment
- Atmosphere: **NRLMSIS 2.1** (Picone et al. 2002, doi:10.1029/2002JA009430) [M]. ρ(650 km)≈1.6e-13
  kg/m³ (moderate), ~100× solar-cycle swing.
- Debris flux SSO: **NASA ORDEM 3.1 / ESA MASTER-8** (Horstmann et al., NTRS 20210011563) [M]:
  >1 cm = 1e-5–1e-4 /m²/yr; >1 mm = 1e-3–1e-2. Population: **ESA SER 2025** (54k >10 cm; 1.2M
  1–10 cm; 130M 1mm–1cm) [O].
- TID: **SHIELDOSE-2 / AE8-AP8** via SPENVIS [M]; calibrated to **SIRI-1** (600 km SSO, ~90–150
  rad/yr floor) and the Suncatcher proton test. SEU: ~5e-10/bit/day SRAM quiet LEO, ~100× in SPEs.
- Solar constant 1361 W/m² (Kopp & Lean 2011) [O]; Earth albedo 0.30; OLR 237 W/m²; CMB 2.725 K.

## Power (EPS)
- Triple-junction GaInP/GaAs/Ge: BOL ~29.6%, EOL(5 yr) ~27.5%, temp coeff ~−0.23 %rel/°C
  (**Azur 3G30**, **Spectrolab XTJ** datasheets) [O].
- Array specific power ~110 W/kg wing-level (**Redwire ROSA**) [O]; areal ~300–400 W/m² BOL.
- Li-ion ~160 Wh/kg pack, LEO DoD 20–40% (**NASA Li-ion guidelines**) [M]. Dawn-dusk SSO →
  ~95–99% sunlit → minimal battery.
- Path efficiency ~0.88 (MPPT × harness × regulation) [E].

## ADCS & optical pointing
- Laser ISL fine pointing ≤1 µrad RMS; beam divergence 10–50 µrad; apertures 10–30 cm
  (**SDA OCT standard**, **GRACE-FO LRI**, **Mynaric/TESAT**) [O/M].
- Star tracker ~2 arcsec ≈ 10 µrad → bus alone cannot hold the beam; **fine-steering mirror +
  coarse gimbal mandatory** [M]. Reaction-wheel microvibration is the dominant jitter source.
- LEO disturbance torques µN·m–10⁻⁴ N·m (gravity-gradient + aero); desat via magnetorquers [M].

## Communications
- FSO link budget: G=(πD/λ)², L_fs=(4πR/λ)², Gaussian pointing loss [M] (arXiv:2204.13177,
  MathWorks). NASA **TBIRD** 200 Gbps space-to-ground; **LCRD** 1.2 Gbps GEO [O].
- Latency: vacuum c vs fiber n=1.4675; LEO mesh beats fiber beyond ~3000 km crossover [M].

## Reliability
- **MIL-HDBK-217F** part-stress (relative use only) [O]; **ANSI/VITA 51.1** correction for COTS.
- CubeSat infant mortality ~26% DOA; "two-month rule" bathtub behavior [M]. EPS dominant failure
  subsystem. Starlink ~5-yr life, continuous replenishment.
- R(t)=exp(−t/MTBF); k-of-n binomial redundancy [O].

## Compute / workload
- TPU v6e 918 TFLOPS BF16, 32 GB HBM (**Google Cloud**) [O]; **TDP undisclosed, ~150–200 W est** [E].
- H100 989 TFLOPS BF16 @700 W → ~1.41 TFLOPS/W [O]. MFU: training 40–60%, inference decode ~8–10% [M].
- PUE: Google fleet 1.09, industry avg ~1.56 (**Uptime/LBNL**) [O/M]. Cloud: H100 ~$2.5/hr median,
  TPU v6e ~$2.7/chip-hr [M].

## Launch & economics
- Falcon 9 ~$3,770/kg (list / reusable payload) [O]; Starship target band $30–600/kg [E];
  Shuttle ~$54,500/kg program-averaged [E]. Disposal: **FCC 22-74** 5-yr rule (2022/2024) [O];
  25-yr international baseline (IADC/ISO 24113).

---
### Dominant caveats
1. **TPU v6e TDP** undisclosed — weakest input (~150–200 W estimate).
2. **Solar-cycle density swing (~100×)** dominates lifetime/drag uncertainty — shown as a band.
3. **1 mm–1 cm debris flux** least model-validated (ORDEM vs MASTER differ 1–2 orders).
4. First-order **sizing** models — for flight design use NASA DAS, ORDEM/MASTER, SPENVIS, STK, and a
   full thermal toolchain.
