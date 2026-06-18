# Mathematical Foundations of Space-Based AI Data Centers
## A Complete, Derivation-by-Derivation Engineering Guide

**Author:** Samarjith Biswas, PhD
**Companion to:** *Space-Based AI Data Centers, Part II* (complete systems study)
**Edition:** June 2026

This guide derives, from first principles and in full, every governing equation used across
the thirteen subsystems of the orbital data-center model. Each section gives: the physical
setup, the derivation with intermediate steps, a worked numerical example whose result matches
the open-source model, the assumptions and their validity, and how the result is used. Symbols
are collected in the nomenclature table; numerical constants are listed once below.

---

## 0. Conventions, constants, and nomenclature

All quantities are SI unless stated. Vectors are bold in concept; here written component-wise.
The reference mission is Google Project Suncatcher: a dawn-dusk sun-synchronous orbit at
altitude $h = 650\ \mathrm{km}$, an $N = 81$ satellite cluster of radius $1\ \mathrm{km}$ with
inter-satellite spacing $d \approx 150\ \mathrm{m}$.

**Physical constants**

| Symbol | Value | Meaning |
|---|---|---|
| $\mu$ | $3.986004418\times10^{14}\ \mathrm{m^3 s^{-2}}$ | Earth gravitational parameter |
| $R_E$ | $6.371\times10^{6}\ \mathrm{m}$ | Earth mean radius |
| $J_2$ | $1.08263\times10^{-3}$ | Earth oblateness coefficient |
| $\sigma$ | $5.670374\times10^{-8}\ \mathrm{W\,m^{-2}K^{-4}}$ | Stefan-Boltzmann constant |
| $h_P$ | $6.62607\times10^{-34}\ \mathrm{J\,s}$ | Planck constant |
| $k_B$ | $1.38065\times10^{-23}\ \mathrm{J\,K^{-1}}$ | Boltzmann constant |
| $c$ | $2.99792458\times10^{8}\ \mathrm{m\,s^{-1}}$ | speed of light (vacuum) |
| $g_0$ | $9.80665\ \mathrm{m\,s^{-2}}$ | standard gravity |
| $S_0$ | $1361\ \mathrm{W\,m^{-2}}$ | solar constant at 1 AU |
| $T_\mathrm{CMB}$ | $2.725\ \mathrm{K}$ | cosmic-microwave-background sink |

---

## 1. Orbital mechanics of a circular orbit

**Setup.** A satellite of mass $m$ on a circular orbit of radius $r=a$ is held by gravity
acting as the centripetal force.

**Derivation.** Newton's second law in the radial direction:

$$\frac{\mu m}{a^2} = \frac{m v^2}{a}.$$

The mass cancels, giving the **circular orbital speed**

$$\boxed{\ v = \sqrt{\frac{\mu}{a}}\ } \tag{1.1}$$

The orbital period follows from $v = 2\pi a / T$:

$$T = \frac{2\pi a}{v} = 2\pi a \sqrt{\frac{a}{\mu}} = \boxed{\ 2\pi\sqrt{\frac{a^3}{\mu}}\ } \tag{1.2}$$

which is Kepler's third law. The **mean motion** (orbital angular rate) is

$$n = \frac{2\pi}{T} = \sqrt{\frac{\mu}{a^3}}. \tag{1.3}$$

The **specific orbital energy** (energy per unit mass) combines kinetic and potential parts.
For any orbit, the vis-viva relation $v^2 = \mu\!\left(\tfrac{2}{r} - \tfrac{1}{a}\right)$ holds;
the total specific energy is

$$\mathcal{E} = \frac{v^2}{2} - \frac{\mu}{r} = -\frac{\mu}{2a}, \tag{1.4}$$

a result we will use directly in the orbital-decay derivation (Section 4).

**Worked example ($h = 650\ \mathrm{km}$).** With $a = R_E + h = 7.021\times10^{6}\ \mathrm{m}$:

$$v = \sqrt{\frac{3.986\times10^{14}}{7.021\times10^{6}}} = 7534.8\ \mathrm{m/s},\qquad
T = 2\pi\sqrt{\frac{(7.021\times10^{6})^3}{3.986\times10^{14}}} = 5854.8\ \mathrm{s} = 97.6\ \mathrm{min}.$$

**Assumptions.** Point-mass gravity, perfectly circular orbit, no perturbations. Valid to
better than 1 percent for sizing; $J_2$ and drag are treated separately (Sections 2, 4).

---

## 2. Sun-synchronous orbit from $J_2$ nodal precession

**Setup.** Earth's oblateness ($J_2$) makes the orbital plane's right ascension of the
ascending node (RAAN, $\Omega$) precess. A sun-synchronous orbit (SSO) chooses the inclination
$i$ so this precession equals Earth's mean orbital rate about the Sun,
$\dot\Omega_\mathrm{sun} = 2\pi / (365.2422\ \mathrm{days}) = 1.991\times10^{-7}\ \mathrm{rad/s}$.

**Derivation.** The secular $J_2$ nodal precession rate for a near-circular orbit is

$$\dot\Omega = -\frac{3}{2}\, n\, J_2 \left(\frac{R_E}{a}\right)^2 \cos i. \tag{2.1}$$

Setting $\dot\Omega = \dot\Omega_\mathrm{sun}$ and solving for the inclination:

$$\boxed{\ \cos i = -\frac{2\,\dot\Omega_\mathrm{sun}\,a^2}{3\,n\,J_2\,R_E^2}\ } \tag{2.2}$$

The minus sign forces $i > 90^\circ$ (a retrograde-precessing, near-polar orbit).

**Worked example ($h = 650\ \mathrm{km}$).** With $n = 1.074\times10^{-3}\ \mathrm{rad/s}$,
$a = 7.021\times10^6$, Eq. (2.2) gives $\cos i = -0.1386$, hence

$$i = \arccos(-0.1386) = 98.0^\circ,$$

matching the reference mission's stated inclination.

**Use.** SSO keeps the orbit plane at a near-fixed angle to the Sun all year. The dawn-dusk
variant (orbit plane near the terminator) yields continuous sunlight (Section 3, 10).

---

## 3. Eclipse geometry and the dawn-dusk advantage

**Setup.** The fraction of an orbit spent in Earth's shadow depends on the beta angle $\beta$,
the angle between the orbit plane and the Sun direction.

**Derivation.** Eclipses occur only when the line of sight to the Sun is blocked by Earth.
Geometrically, the satellite avoids shadow entirely when $|\beta|$ exceeds the **critical beta
angle** at which the orbit just grazes Earth's limb:

$$\boxed{\ \beta^\* = \arcsin\!\frac{R_E}{R_E + h}\ } \tag{3.1}$$

For $|\beta| < \beta^\*$, the sunlit fraction of the orbit is

$$f_\mathrm{sun} = 1 - \frac{1}{\pi}\cos^{-1}\!\left[\frac{\sqrt{h^2 + 2R_E h}}{(R_E + h)\cos\beta}\right]. \tag{3.2}$$

**Worked example ($h = 650\ \mathrm{km}$).**

$$\beta^\* = \arcsin\frac{6371}{7021} = \arcsin(0.9074) = 65.1^\circ.$$

A dawn-dusk SSO holds $|\beta|$ near $90^\circ$ for most of the year, so $|\beta| > \beta^\*$ and
$f_\mathrm{sun} \to 1$: better than 95 percent illumination, minimal thermal cycling, and a tiny
battery (Section 10).

---

## 4. Atmospheric drag and orbital decay

**Setup.** Even at 650 km the thin atmosphere exerts drag that slowly lowers the orbit. We seek
$da/dt$ and integrate it to a re-entry lifetime.

**Drag force.** A body of cross-section $A$ moving at speed $v$ through gas of density $\rho$
feels a drag force opposing its velocity,

$$F_D = \tfrac{1}{2}\,\rho\,v^2\,C_D\,A, \tag{4.1}$$

with drag coefficient $C_D \approx 2.2$ in free-molecular flow. The **specific** (per-mass)
deceleration is

$$a_D = \frac{F_D}{m} = \tfrac{1}{2}\,\rho\,v^2\,C_D\,\frac{A}{m}. \tag{4.2}$$

**Energy-balance derivation of the decay rate.** Drag does negative work at the rate (force
times speed, per unit mass):

$$\frac{d\mathcal{E}}{dt} = -\,a_D\, v = -\tfrac{1}{2}\,\rho\,C_D\,\frac{A}{m}\,v^3. \tag{4.3}$$

For a near-circular orbit $\mathcal{E} = -\mu/(2a)$ from Eq. (1.4), so

$$\frac{d\mathcal{E}}{dt} = \frac{d}{dt}\!\left(-\frac{\mu}{2a}\right) = \frac{\mu}{2a^2}\,\frac{da}{dt}. \tag{4.4}$$

Equating (4.3) and (4.4) and substituting $v = \sqrt{\mu/a}$ so that $v^3 = (\mu/a)^{3/2}$:

$$\frac{\mu}{2a^2}\frac{da}{dt} = -\tfrac{1}{2}\,\rho\,C_D\,\frac{A}{m}\left(\frac{\mu}{a}\right)^{3/2}.$$

Cancelling and simplifying the powers of $a$ and $\mu$:

$$\boxed{\ \frac{da}{dt} = -\,C_D\,\frac{A}{m}\,\rho(h)\,\sqrt{\mu\,a}\ } \tag{4.5}$$

The decay accelerates as the orbit lowers because $\rho(h)$ rises steeply with decreasing
altitude, ending in a rapid re-entry. The per-revolution contraction is
$\Delta a_\mathrm{rev} = \dot a\, T = -2\pi C_D (A/m)\,\rho\, a^2$.

**Atmosphere model.** $\rho(h)$ is interpolated log-linearly between NRLMSIS anchors at
600/650/700/800 km for three solar-activity levels. The minimum-to-maximum density ratio is
about $100$ over the 11-year solar cycle; this is the single largest source of lifetime
uncertainty and is shown as a band, not a point.

**Solution.** Equation (4.5) is integrated by adaptive forward Euler,
$a_{k+1} = a_k - C_D (A/m)\,\rho(a_k - R_E)\sqrt{\mu a_k}\,\Delta t$, terminating at $h = 120\ \mathrm{km}$.

**Worked result.** For the reference bus ($A/m = 0.0084\ \mathrm{m^2/kg}$, $C_D = 2.2$) at 650 km,
the integral gives a natural lifetime of about **22 years** at moderate solar activity (4 years
at solar maximum, 312 years at solar minimum). Since the FCC post-mission disposal rule is now
**5 years**, only a solar-maximum launch is even marginal: active de-orbit propulsion is
mandatory (Section 15).

---

## 5. Radiative thermal balance and radiator sizing

**Setup.** In vacuum the only way to reject heat is radiation. We derive the radiated power and
the area a radiator needs.

**From Planck to Stefan-Boltzmann.** A blackbody emits spectral radiance (power per area per
solid angle per wavelength) given by Planck's law:

$$B(\lambda, T) = \frac{2 h_P c^2}{\lambda^5}\,\frac{1}{\exp\!\big(h_P c / \lambda k_B T\big) - 1}. \tag{5.1}$$

Integrating over the emitting hemisphere ($\int \cos\theta\, d\Omega = \pi$) and over all
wavelengths gives the hemispherical emissive power:

$$E_b(T) = \pi \int_0^\infty B(\lambda, T)\, d\lambda = \sigma T^4,
\qquad \sigma = \frac{2\pi^5 k_B^4}{15\, h_P^3 c^2}. \tag{5.2}$$

A real (gray) surface of emissivity $\varepsilon$ radiating to a background at $T_\infty$ rejects

$$Q_\mathrm{rad} = \varepsilon\,\sigma\,A\,(T^4 - T_\infty^4). \tag{5.3}$$

The radiative sink is the CMB, $T_\infty = 2.725\ \mathrm{K}$; since
$T_\infty^4 / T^4 \sim 10^{-8}$ for $T \sim 300\ \mathrm{K}$, the sink term is dropped.

**Double-sided radiator with parasitic loads.** A deployed panel radiates from both faces and
loses a fraction $f_p$ of its output to absorbed solar, albedo, and Earth-IR (Section 9). The
**net** rejected flux per unit one-side area is $q_\mathrm{net} = \varepsilon\sigma T^4\, n_s\, (1 - f_p)$
with $n_s = 2$. The radiator area required for a heat load $Q$ at operating temperature $T$ is

$$\boxed{\ A_\mathrm{rad} = \frac{Q}{\varepsilon\,\sigma\,T^4\,n_s\,(1 - f_p)}\ } \tag{5.4}$$

This is **linear in $Q$**: cooling has no economy of scale, the central constraint of the study.

**Worked example (1 MW at 20 C).** With $\varepsilon = 0.90$, $T = 293.15\ \mathrm{K}$, $n_s = 2$,
$f_p = 0.12$:

$$\varepsilon\sigma T^4 = 0.90 \times 5.670\times10^{-8} \times (293.15)^4 = 376.9\ \mathrm{W/m^2}\ \text{(per side)},$$
$$q_\mathrm{net} = 376.9 \times 2 \times 0.88 = 663.3\ \mathrm{W/m^2},\qquad
A_\mathrm{rad} = \frac{10^6}{663.3} = 1508\ \mathrm{m^2}.$$

This matches the industry "about 1,200 m² per MW" rule of thumb (which assumes a slightly higher
$\varepsilon$ and lower $f_p$). At 60 C the $T^4$ factor raises $q_\mathrm{net}$ and the area
falls to about 900 m², at the cost of silicon lifetime.

---

## 6. Solving for radiator temperature: Newton-Raphson

**Setup.** When the area $A$ is fixed and the temperature is the unknown (the Part I baseline),
Eq. (5.3) is a quartic in $T$ that must be solved numerically.

**Derivation.** Define the residual and its derivative:

$$f(T) = Q - \varepsilon\sigma A\, T^4, \qquad f'(T) = -4\,\varepsilon\sigma A\, T^3. \tag{6.1}$$

The Newton-Raphson iteration is

$$T_{k+1} = T_k - \frac{f(T_k)}{f'(T_k)} = T_k + \frac{Q - \varepsilon\sigma A\, T_k^4}{4\,\varepsilon\sigma A\, T_k^3}. \tag{6.2}$$

Because $f(T)$ is smooth and monotone decreasing for $T > 0$, convergence from $T_0 = 300\ \mathrm{K}$
to a tolerance $|T_{k+1} - T_k| < 0.01\ \mathrm{K}$ takes 2 to 4 iterations.

**Worked example (Part I baseline).** With $Q = 1450\ \mathrm{W}$, $A = 4.0\ \mathrm{m^2}$
(single-sided), $\varepsilon = 0.85$: iteration one gives $T_1 = 294.4\ \mathrm{K}$, iteration two
converges, yielding $T_\mathrm{rad} = 294.4\ \mathrm{K} = 21.4\ \mathrm{C}$.

---

## 7. Conductive thermal network and the interface wall

**Setup.** Heat must first travel from the chip junction to the radiator through solid layers.

**Fourier's law and the thermal-resistance analogy.** One-dimensional steady conduction through a
layer of conductivity $k$, area $A$, length $L$ carries

$$Q = k A\,\frac{\Delta T}{L} \quad\Longleftrightarrow\quad \Delta T = Q\, R_{th},\qquad R_{th} = \frac{L}{k A}. \tag{7.1}$$

This is exactly Ohm's law with $\Delta T \leftrightarrow V$, $Q \leftrightarrow I$,
$R_{th} \leftrightarrow R$. Layers in series add, parallel paths combine reciprocally:

$$R_{th}^\mathrm{series} = \sum_i R_i, \qquad \frac{1}{R_{th}^\mathrm{parallel}} = \sum_i \frac{1}{R_i}. \tag{7.2}$$

The junction temperature is then

$$\boxed{\ T_j = T_\mathrm{rad} + Q\, R_{th}^\mathrm{sys}\ } \tag{7.3}$$

**The interface wall.** With the Part I passive chain $R_{th}^\mathrm{sys} = 0.30\ \mathrm{K/W}$,
the temperature rise across the chain alone is $\Delta T = P \times 0.30$:

$$P = 300\ \mathrm{W} \Rightarrow 90\ \mathrm{C}; \quad
P = 700\ \mathrm{W} \Rightarrow 210\ \mathrm{C}; \quad
P = 1200\ \mathrm{W} \Rightarrow 360\ \mathrm{C}.$$

Since the entire junction budget is $T_{j,\max} = 125\ \mathrm{C}$, any chip with
$P\, R_{th} > 125\ \mathrm{C}$, i.e. $P > 417\ \mathrm{W}$ at $R_{th} = 0.30$, **cannot be cooled
passively at any radiator size.** This forces chip-level liquid or loop-heat-pipe cooling for
H100-class and larger parts.

---

## 8. Transient thermal response (eclipse)

**Setup.** During a brief eclipse the radiator keeps emitting while solar input drops. We need
the temperature excursion.

**Lumped-capacitance model.** If internal gradients are negligible (small Biot number), the
radiator is a single thermal node:

$$m\, c_p\, \frac{dT}{dt} = Q_\mathrm{in}(t) - Q_\mathrm{out}(T). \tag{8.1}$$

**Biot number check.** With a radiative coefficient $h_\mathrm{rad} = 4\varepsilon\sigma T^3$,
characteristic length $L_c = t_\mathrm{plate}$, and conductivity $k$:

$$\mathrm{Bi} = \frac{h_\mathrm{rad} L_c}{k} = \frac{(4.6)(0.005)}{167} \approx 1.4\times10^{-4} \ll 0.1, \tag{8.2}$$

so the lumped model is valid. **Linearizing** the radiation term about $T_0$ gives a first-order
system with time constant

$$\tau = \frac{m\, c_p}{h_\mathrm{rad}\, A}, \qquad h_\mathrm{rad} = 4\,\varepsilon\,\sigma\, T_0^3. \tag{8.3}$$

A step change $\Delta Q$ in input drives the temperature toward a new steady state
$\Delta T_\mathrm{ss} = \Delta Q / (h_\mathrm{rad} A)$ along

$$T(t) = T_0 + \Delta T_\mathrm{ss}\left(1 - e^{-t/\tau}\right). \tag{8.4}$$

**Worked example.** Radiator $m = 54\ \mathrm{kg}$, $c_p = 900\ \mathrm{J/(kg\,K)}$,
$A = 4\ \mathrm{m^2}$, $T_0 = 294.4\ \mathrm{K}$, $\varepsilon = 0.85$: $h_\mathrm{rad} = 4.6\ \mathrm{W/m^2K}$,
$\tau = (54)(900) / (4.6 \times 4) \approx 2620\ \mathrm{s} \approx 44\ \mathrm{min}$. A 5-minute eclipse
($\Delta Q = -100\ \mathrm{W}$) gives $\Delta T_\mathrm{ss} = -5.6\ \mathrm{K}$ and
$T(300) = 294.4 - 5.6\,(1 - e^{-300/2620}) = 293.8\ \mathrm{K}$, a drop of only 0.6 C: the thermal
mass buffers the eclipse almost completely.

---

## 9. External heat loads: view factor, albedo, Earth IR, solar

**Setup.** A surface in LEO absorbs sunlight, sunlight reflected by Earth (albedo), and Earth's
own infrared emission. These set the parasitic fraction $f_p$ of Section 5.

**Earth view factor.** For a flat surface facing a sphere of radius $R_E$ at orbital radius
$r = R_E + h$, the fraction of the hemisphere subtended by Earth is

$$\boxed{\ F = \tfrac{1}{2}\!\left[1 - \sqrt{1 - \left(\tfrac{R_E}{r}\right)^2}\,\right]\ } \tag{9.1}$$

At 650 km, $F = 0.290$.

**The three loads.** With solar absorptivity $\alpha_s$ and emissivity $\varepsilon$:

$$Q_\mathrm{solar} = S_0\, \alpha_s\, \cos\theta\, A, \tag{9.2}$$
$$Q_\mathrm{albedo} = S_0\, a\, F\, \alpha_s\, A, \qquad a = 0.30\ \text{(Bond albedo)}, \tag{9.3}$$
$$Q_\mathrm{IR} = q_\mathrm{IR}\, F\, \varepsilon\, A, \qquad q_\mathrm{IR} = 237\ \mathrm{W/m^2}. \tag{9.4}$$

**Worked example (edge-on radiator, $\alpha_s = 0.15$, $\varepsilon = 0.91$, $A = 4\ \mathrm{m^2}$).**
Edge-on to the Sun, $\cos\theta \approx 0$, so $Q_\mathrm{solar} \approx 0$;
$Q_\mathrm{albedo} = 1361 \times 0.30 \times 0.290 \times 0.15 \times 4 = 71\ \mathrm{W}$;
$Q_\mathrm{IR} = 237 \times 0.290 \times 0.91 \times 4 = 251\ \mathrm{W}$. An Earth-facing radiator sees
about 322 W of parasitic load; the optimized edge-on baseline lumps this to about 100 W.

---

## 10. Electrical power: solar array and battery

**Setup.** A photovoltaic array converts sunlight to electrical power; a battery covers eclipse.

**Array power.** The electrical power delivered to the load is the incident solar power times the
cell efficiency $\eta$ (which degrades with radiation and falls with temperature), the panel
packing factor, and the array-to-load path efficiency:

$$P = S_0\, A\, \eta(T, \mathrm{life})\, \kappa_\mathrm{pack}\, \eta_\mathrm{path}, \tag{10.1}$$
$$\eta(T,\mathrm{life}) = \eta_\mathrm{life}\,\big[1 + k_T (T - 28)\big], \tag{10.2}$$

with triple-junction values $\eta_\mathrm{BOL} = 0.296$, $\eta_\mathrm{EOL,5yr} = 0.275$, temperature
coefficient $k_T = -0.0023\ \mathrm{per\ C}$, $\kappa_\mathrm{pack} = 0.85$, $\eta_\mathrm{path} = 0.88$.

**Worked example (1 m², EOL, 70 C).**
$\eta = 0.275\,[1 - 0.0023(70 - 28)] = 0.248$;
$P = 1361 \times 1 \times 0.248 \times 0.85 \times 0.88 = 253\ \mathrm{W}$.

**Battery sizing.** To carry the load $P_L$ through an eclipse of duration $t_e$ at depth of
discharge DoD and specific energy $e_\mathrm{sp}$, the battery mass is

$$m_\mathrm{bat} = \frac{P_L\, t_e}{\mathrm{DoD}\, e_\mathrm{sp}}. \tag{10.3}$$

In a dawn-dusk SSO, $t_e$ is small (seasonal only), so $m_\mathrm{bat}$ is minimal, a major mass
saving over standard LEO with its 16 deep cycles per day.

---

## 11. Attitude control and optical pointing

**Setup.** A laser inter-satellite link needs sub-microradian pointing, far beyond what the bus
attitude alone provides.

**Diffraction-limited beam divergence.** A telescope of aperture $D$ at wavelength $\lambda$
produces a full-angle divergence (Airy criterion)

$$\Theta \approx \frac{2.44\,\lambda}{D}. \tag{11.1}$$

At range $R$ the beam spot radius is $w(R) \approx \tfrac{1}{2}\Theta R$.

**Pointing loss (Gaussian beam).** A pointing error $\theta_\mathrm{err}$ relative to the beam
divergence $\theta_\mathrm{div}$ costs received power

$$L_\mathrm{point} = \exp\!\left(-\frac{2\,\theta_\mathrm{err}^2}{\theta_\mathrm{div}^2}\right). \tag{11.2}$$

**Knowledge limit.** A star tracker of accuracy $\psi$ (arcseconds) gives attitude knowledge
$\psi \times 4.848\ \mathrm{\mu rad/arcsec}$. At $\psi = 2''$ this is about $10\ \mathrm{\mu rad}$, ten
times coarser than the sub-microradian link requirement, so a fine-steering mirror is mandatory.

**Disturbance torques.** The dominant LEO torques are gravity-gradient and aerodynamic:

$$\tau_\mathrm{gg} = \tfrac{3}{2}\, n^2\, |I_z - I_x|\, \sin 2\theta, \qquad
\tau_\mathrm{aero} = \tfrac{1}{2}\rho v^2 C_D A\, \ell_{cp\text{-}cg}, \tag{11.3}$$

where $\ell_{cp\text{-}cg}$ is the center-of-pressure to center-of-mass offset. Reaction wheels
absorb these and are desaturated by magnetorquers.

---

## 12. Free-space optical communications link budget

**Setup.** The received optical power sets the achievable data rate; range dominates the budget.

**Antenna (telescope) gain.** An aperture of diameter $D$ has gain

$$G = \left(\frac{\pi D}{\lambda}\right)^2. \tag{12.1}$$

**Free-space path loss.** Spreading over a sphere of radius $R$ attenuates power by

$$L_\mathrm{fs} = \left(\frac{4\pi R}{\lambda}\right)^2. \tag{12.2}$$

**Link equation (decibel form).** Combining transmit power, both telescopes, and losses:

$$P_\mathrm{rx} = P_\mathrm{tx} + G_\mathrm{tx} + G_\mathrm{rx} - L_\mathrm{fs} - L_\mathrm{point} - L_\mathrm{atm} - L_\mathrm{optics}. \tag{12.3}$$

**Worked example (why the formation is tight).** At $\lambda = 1.55\ \mathrm{\mu m}$, $D = 0.1\ \mathrm{m}$:
$G = 10\log_{10}[(\pi \cdot 0.1 / 1.55\times10^{-6})^2] = 106\ \mathrm{dB}$ per telescope. The path loss is
$L_\mathrm{fs} = 184\ \mathrm{dB}$ at 200 m but $258\ \mathrm{dB}$ at 1000 km, a 74 dB difference. Flying
satellites about 150 m apart buys back this 74 dB, which is why a sub-200 m formation makes
800 Gbps on a single transceiver realistic.

**Latency.** Light travels at $c$ in vacuum but $c/n_\mathrm{fiber}$ in fiber ($n_\mathrm{fiber} = 1.4675$);
a LEO optical mesh therefore beats terrestrial fiber for path distances beyond about 3000 km.

---

## 13. Ionizing radiation: dose, shielding, and upsets

**Setup.** Trapped electrons and protons deposit dose in the silicon; energetic particles flip
bits.

**Dose-depth.** Behind aluminium of thickness $x$, the trapped-electron dose attenuates
quasi-exponentially atop a proton/bremsstrahlung floor:

$$\dot D(x) = D_0\, e^{-x/\lambda} + D_\infty, \qquad \lambda \approx 1.7\ \mathrm{mm}, \tag{13.1}$$

calibrated so that $D_\infty \sim 100$ to $160\ \mathrm{rad/yr}$ (the proton floor measured by SIRI-1
at 600 km SSO and consistent with the reference mission's proton-beam test). Cumulative mission
dose is $D_\mathrm{tot} = \dot D(x)\, t_\mathrm{mission}$.

**Worked example (10 mm Al, 5 years).** $\dot D_\mathrm{lo} = 2.0\times10^4 e^{-10/1.7} + 100 = 156$,
$\dot D_\mathrm{hi} = 266\ \mathrm{rad/yr}$; $D_\mathrm{tot} \approx \tfrac{1}{2}(156 + 266)\times 5 \approx 1.06\ \mathrm{krad(Si)}$,
below the HBM tolerance of about 2 krad (margin about 1.9x).

**Single-event upsets.** The upset rate scales as

$$R_\mathrm{SEU} = \sigma_\mathrm{SEU}\, \phi\, N_\mathrm{bits}, \tag{13.2}$$

with per-bit cross-section $\sigma_\mathrm{SEU}$ and particle flux $\phi$ (enhanced in the South
Atlantic Anomaly and polar horns). ECC corrects single-bit errors; the uncorrectable multi-bit
tail (about $10^{-3} R_\mathrm{SEU}$) is absorbed by checkpointing, costing a 10 to 20 percent
throughput tax.

---

## 14. Orbital debris: collision probability and cascade

**Setup.** Debris impacts are rare, independent events; we want the probability of at least one
catastrophic hit, and the chance one fragmentation cascades through the formation.

**Poisson model (from the binomial limit).** Divide a mission into $n$ short slices, each with hit
probability $p = \Phi A\, \Delta t$ (flux $\times$ area $\times$ time). The number of hits is binomial;
taking $n \to \infty$ with $n p \to \Lambda$ yields a Poisson distribution,

$$P(K = k) = \frac{\Lambda^k e^{-\Lambda}}{k!}, \qquad \Lambda = \Phi\, A\, N\, t. \tag{14.1}$$

The probability of **at least one** catastrophic ($>1\ \mathrm{cm}$) impact in the cluster is

$$\boxed{\ P(K \ge 1) = 1 - e^{-\Phi A N t}\ } \tag{14.2}$$

**Worked example.** With $\Phi = 3\times10^{-5}\ \mathrm{m^{-2}yr^{-1}}$ (ORDEM/MASTER central),
$A = 15\ \mathrm{m^2}$, $N = 81$, $t = 5\ \mathrm{yr}$: $\Lambda = 0.182$,
$P = 1 - e^{-0.182} = 16.7\%$. The flux band $10^{-5}$ to $10^{-4}$ maps to 6 to 46 percent.

**Cascade coupling (expanding-shell model).** A break-up sends $N_f$ lethal fragments over a sphere
of area $4\pi d^2$ at range $d$; a neighbor of cross-section $\pi r_t^2$ intercepts an expected
$\Lambda_n = N_f r_t^2 / (4 d^2)$, so

$$\boxed{\ P_\mathrm{hit}(d) = 1 - \exp\!\left(-\frac{N_f\, r_t^2}{4\, d^2}\right)\ } \tag{14.3}$$

**Worked example.** $N_f = 2000$, $r_t = 2\ \mathrm{m}$, $d = 150\ \mathrm{m}$:
$\Lambda_n = 8000/90000 = 0.0889$, $P_\mathrm{hit} = 8.5\%$ per neighbor. Since $P_\mathrm{hit} \propto d^{-2}$,
widening to 1 km drops it below 1 percent but degrades the optical-link budget: the formation
paradox.

---

## 15. Propulsion: drag make-up, de-orbit, and propellant

**Setup.** The satellite must counter drag, hold formation, dodge debris, and de-orbit at end of
life.

**Drag make-up.** Integrating the specific drag deceleration (4.2) over the mission:

$$\Delta v_\mathrm{drag} = \int_0^t a_D\, dt = \tfrac{1}{2}\,\rho\, v^2\, C_D\,\frac{A}{m}\, t. \tag{15.1}$$

At 650 km this is about 13 m/s over 5 years.

**Controlled de-orbit (Hohmann perigee-lowering).** A single retrograde burn at the circular
radius $r_1$ lowers the perigee to $r_2$ (180 km). The transfer ellipse has semi-major axis
$a_t = (r_1 + r_2)/2$. By vis-viva, the speed at the apogee of the transfer (where the burn occurs) is

$$v_\mathrm{apo} = \sqrt{\mu\!\left(\frac{2}{r_1} - \frac{1}{a_t}\right)}
= \sqrt{\mu\!\left(\frac{2}{r_1} - \frac{2}{r_1 + r_2}\right)}
= \sqrt{\frac{\mu}{r_1}}\,\sqrt{\frac{2 r_2}{r_1 + r_2}}. \tag{15.2}$$

The required impulse is the difference from the circular speed $v_{c1} = \sqrt{\mu/r_1}$:

$$\boxed{\ \Delta v_\mathrm{deorbit} = v_{c1}\!\left(1 - \sqrt{\frac{2 r_2}{r_1 + r_2}}\right)\ } \tag{15.3}$$

**Worked example (650 to 180 km).** $r_1 = 7.021\times10^6$, $r_2 = 6.551\times10^6$,
$v_{c1} = 7534.8\ \mathrm{m/s}$:

$$\Delta v_\mathrm{deorbit} = 7534.8\left(1 - \sqrt{\tfrac{2(6.551)}{7.021 + 6.551}}\right) = 7534.8\,(1 - 0.9825) = 131.6\ \mathrm{m/s}.$$

This single term dominates the 5-year budget of about 190 m/s (drag 13, formation 8, avoidance 5,
de-orbit 132, plus 20 percent margin).

**Propellant (Tsiolkovsky).** Momentum conservation for a rocket expelling mass at exhaust speed
$v_e = I_{sp}\, g_0$ gives $m\, dv = -v_e\, dm$, which integrates to the rocket equation
$\Delta v = v_e \ln(m_0/m_f)$. Solving for the propellant $m_p = m_0 - m_f$ with $m_f = m_\mathrm{dry}$:

$$\boxed{\ m_p = m_\mathrm{dry}\!\left(e^{\Delta v / (I_{sp} g_0)} - 1\right)\ } \tag{15.4}$$

**Worked example ($\Delta v = 189.5\ \mathrm{m/s}$, $m_\mathrm{dry} = 375\ \mathrm{kg}$).** Hydrazine
($I_{sp} = 220\ \mathrm{s}$): $m_p = 375\,(e^{0.0878} - 1) = 34.4\ \mathrm{kg}$. Electric
($I_{sp} = 1500\ \mathrm{s}$): $m_p = 4.9\ \mathrm{kg}$.

---

## 16. Reliability and constellation availability

**Setup.** With no on-orbit repair, availability is bought through redundancy and replenishment.

**Exponential reliability.** In the flat "useful life" region of the bathtub curve, failures are a
constant-hazard (Poisson) process, so the probability a unit survives to time $t$ is

$$R(t) = e^{-t/\mathrm{MTBF}} = e^{-\lambda t}. \tag{16.1}$$

A unit with $\mathrm{MTBF} = 50{,}000\ \mathrm{h}$ over 5 years ($43{,}800\ \mathrm{h}$) has
$R = e^{-0.876} = 0.42$: less than half survive un-aided, so redundancy is mandatory.

**$k$-of-$n$ redundancy.** If a system works when at least $k$ of $n$ identical units (each
reliability $p$) survive:

$$R_\mathrm{sys} = \sum_{i=k}^{n} \binom{n}{i}\, p^i\, (1-p)^{\,n-i}. \tag{16.2}$$

**Constellation capacity.** The expected fraction of required capacity available (no
replenishment) is $\min\!\big(1,\ n_\mathrm{deployed}\, p / n_\mathrm{required}\big)$; operational
constellations sustain capacity by continuous replenishment at a rate
$\approx 1/\text{(design life)}$ (about 20 percent per year for a 5-year life).

---

## 17. Compute, utilization, and effective efficiency

**Setup.** The deliverable is useful compute, not peak FLOPS.

**Delivered compute.** With $n$ chips of peak $P_\mathrm{peak}$, model-FLOPs utilization (MFU), and
radiation availability $a_r$:

$$\text{delivered} = n\, P_\mathrm{peak}\, \mathrm{MFU}\, a_r. \tag{17.1}$$

MFU is 40 to 60 percent for training but only 8 to 10 percent for inference decode (memory-bound),
so an inference platform must be planned around the low regime.

**Effective PUE.** Folding the radiation throughput tax into the power-overhead ratio:

$$\mathrm{PUE}_\mathrm{eff} = \frac{P_\mathrm{total} / P_\mathrm{compute}}{a_r}. \tag{17.2}$$

**Cost of useful compute.** Cost per useful PFLOP-hour is the per-chip hourly cost divided by the
useful throughput $P_\mathrm{peak}\,\mathrm{MFU}\, a_r$; at realistic MFU this is 3 to 10 times the
peak figure.

---

## 18. Techno-economics

**Setup.** Per-satellite cost splits into launch and hardware.

**Cost model.** $C_\mathrm{sat} = p_\mathrm{launch}\, m_\mathrm{launch} + C_\mathrm{hw}$. Launch equals
hardware at the **cross-over price**

$$p^\* = \frac{C_\mathrm{hw}}{m_\mathrm{launch}}. \tag{18.1}$$

With $C_\mathrm{hw} = 1.1$ million USD and $m_\mathrm{launch} = 415\ \mathrm{kg}$,
$p^\* = 2650\ \mathrm{USD/kg}$. Below this, hardware dominates; below about 600 USD/kg, launch is a
small correction, so the economics are gated by hardware cost, lifetime, utilization, and the
radiation tax, not by the headline dollar-per-kilogram. Total cost of ownership is
$\mathrm{TCO} = \mathrm{CAPEX} + n_\mathrm{years}\,\mathrm{OPEX}$.

---

## 19. Master list of governing equations

| # | Quantity | Equation |
|---|---|---|
| 1.1 | Circular speed | $v = \sqrt{\mu/a}$ |
| 1.2 | Period | $T = 2\pi\sqrt{a^3/\mu}$ |
| 2.2 | SSO inclination | $\cos i = -2\dot\Omega_\mathrm{sun} a^2 / (3 n J_2 R_E^2)$ |
| 3.1 | Critical beta | $\beta^\* = \arcsin\!\big(R_E/(R_E+h)\big)$ |
| 4.5 | Orbital decay | $\dot a = -C_D (A/m)\,\rho\,\sqrt{\mu a}$ |
| 5.4 | Radiator area | $A_\mathrm{rad} = Q / [\varepsilon\sigma T^4 n_s (1 - f_p)]$ |
| 6.2 | Newton-Raphson | $T_{k+1} = T_k + (Q - \varepsilon\sigma A T_k^4)/(4\varepsilon\sigma A T_k^3)$ |
| 7.3 | Junction temp | $T_j = T_\mathrm{rad} + Q R_{th}$ |
| 8.4 | Eclipse transient | $T(t) = T_0 + \Delta T_\mathrm{ss}(1 - e^{-t/\tau})$ |
| 9.1 | Earth view factor | $F = \tfrac{1}{2}[1 - \sqrt{1 - (R_E/r)^2}]$ |
| 10.1 | Array power | $P = S_0 A\,\eta\,\kappa\,\eta_\mathrm{path}$ |
| 11.2 | Pointing loss | $L = \exp(-2\theta_\mathrm{err}^2/\theta_\mathrm{div}^2)$ |
| 12.2 | Free-space loss | $L_\mathrm{fs} = (4\pi R/\lambda)^2$ |
| 13.1 | Dose-depth | $\dot D = D_0 e^{-x/\lambda} + D_\infty$ |
| 14.2 | Debris risk | $P = 1 - e^{-\Phi A N t}$ |
| 14.3 | Cascade | $P_\mathrm{hit} = 1 - e^{-N_f r_t^2 / 4 d^2}$ |
| 15.3 | De-orbit Δv | $\Delta v = v_{c1}(1 - \sqrt{2 r_2/(r_1 + r_2)})$ |
| 15.4 | Propellant | $m_p = m_\mathrm{dry}(e^{\Delta v/I_{sp} g_0} - 1)$ |
| 16.1 | Reliability | $R(t) = e^{-t/\mathrm{MTBF}}$ |
| 16.2 | k-of-n | $R_\mathrm{sys} = \sum_{i=k}^{n}\binom{n}{i}p^i(1-p)^{n-i}$ |
| 17.1 | Delivered compute | $n P_\mathrm{peak}\,\mathrm{MFU}\,a_r$ |
| 18.1 | Launch cross-over | $p^\* = C_\mathrm{hw}/m_\mathrm{launch}$ |

Every equation here is implemented in the open-source model and checked against the worked
examples by its validation suite. This guide is the authoritative derivation reference for the
*Space-Based AI Data Centers, Part II* study.
