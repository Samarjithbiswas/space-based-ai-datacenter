"""Physical and program constants (SI). Sources in docs/SOURCES.md."""

# --- universal / planetary ---
MU = 3.986004418e14      # Earth gravitational parameter [m^3 s^-2]
R_E = 6.371e6            # Earth mean radius [m]
J2 = 1.08262668e-3       # Earth oblateness coefficient [-]
SIGMA = 5.670374419e-8   # Stefan-Boltzmann [W m^-2 K^-4]
G0 = 9.80665             # standard gravity [m s^-2]
C_LIGHT = 299_792_458.0  # speed of light [m/s]

# --- environment ---
S0 = 1361.0              # solar constant at 1 AU [W/m^2] (Kopp & Lean 2011)
ALBEDO = 0.30            # Earth Bond albedo [-]
EARTH_IR = 237.0         # Earth outgoing longwave radiation [W/m^2]
T_CMB = 2.725            # deep-space radiative sink [K]
N_FIBER = 1.4675         # refractive index of silica fiber (latency comparisons)

# --- reference mission (Project Suncatcher, arXiv:2511.19468) ---
ALT_KM = 650.0           # mean cluster altitude
N_SATS = 81              # satellites per cluster
CLUSTER_RADIUS_M = 1000.0
SPACING_M = 150.0        # representative next-nearest spacing (100-200 m)
DISPOSAL_RULE_YR = 5.0   # FCC 22-74 (2022, effective 2024)

# --- reference bus (mass budget from the Part I study) ---
DRY_MASS_KG = 375.0
LAUNCH_MASS_KG = 415.0
