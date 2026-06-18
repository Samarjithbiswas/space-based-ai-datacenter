# Technical review: `orbital-thermal-bounds` (Dan Lee)

Reviewer: Samarjith Biswas, PhD · Scope: independent, collegial engineering review of the
public repository, for the purpose of harmonizing it against the Part I thermal baseline.

## Summary

This is careful, honest, and genuinely useful work. It is narrower than my study by design
(a reduced-order one-node radiator model plus thermodynamic bounds), and within that scope it
is more rigorous on the thermal physics than my Part I treatment was. The two efforts are
complementary: this repo goes deep on radiator bounds and view factors; my work goes broad
across all spacecraft subsystems. I would be glad to cite it as the reference thermal-bounds
treatment.

## Strengths

1. **The edge-on view-factor correction is a real result.** Replacing McCalip's cos-tilt
   heuristic (with a 5% floor) by an exact tilted-plate-to-sphere Earth view factor, and
   showing the equilibrium temperature shifts by +6.35 K (+5.77 K geometry, +0.58 K a
   floating-point artifact), is a clean, reproducible, and practically important finding. It
   directly bears on my Part I assumption that an edge-on radiator sees ~100 W of lumped
   parasitic load (see "Harmonization" below).
2. **The thermodynamic bounds are elegant and correct in spirit.** The Carnot-at-2.7-K
   argument, the (3+q⁴)/4 optimal-area rule, the (T_h/T_c)³ heat-to-work area penalty, and
   the no-self-powering-from-waste-heat theorem are the right first-principles guardrails for
   this problem, and they are not in the popular discourse.
3. **Verification discipline is excellent.** Periodic-steady-state closure, scale-aware
   energy balance, an N/2N/4N temporal-resolution certificate (largest certified pointwise
   error 0.0046 K vs a 0.01 K tolerance), SHA-256-pinned oracle, and CI that fails closed are
   well above the norm for an independent preprint.
4. **Honest scope statements.** "Not validated against flown hardware," "not for flight
   design," and the intentional `xfail` for the unimplemented disk-integrated albedo model are
   exactly the right disclosures.

## Constructive feedback

1. **Significant figures.** Reporting equilibrium temperatures to 12 decimals
   (335.749538028260 K) is arithmetically exact but physically over-precise for a one-node
   reduced-order model whose input uncertainties (ε, α_s, sink, areal heat capacity) move the
   answer by many kelvin. I would quote the headline as +6.3 K (or +6.35 K) and keep the
   high-precision tables as a reproducibility artifact, clearly labeled as numerical, not
   physical, precision.
2. **One-node limit.** A single lumped node implicitly assumes an isothermal radiator. Worth
   stating the Biot-number regime where that holds, and noting that a real high-flux panel has
   an in-plane gradient (fin efficiency) that lowers the effective radiating temperature. A
   two-node or fin-efficiency factor would bound this.
3. **Two-face asymmetry.** Edge-on to the sun, the two radiator faces see different
   environments (one more Earth, one more deep space). An asymmetric two-face balance would
   refine the exact-VF result you already compute.
4. **Solar-cycle sink variation.** The effective sink and the small albedo term vary over the
   orbit and the solar cycle; a sensitivity band (not just a point) would strengthen the
   bounds story.
5. **Independent human check on the bounds.** The adversarial multi-AI + Wolfram audit is a
   genuinely interesting methodology, and you flag correctly that it is not human peer review.
   The five theorems would benefit from one domain expert reading the proofs; I am happy to
   sanity-check the area-optimum and heat-to-work derivations.

## Harmonization with the Part I baseline

The cleanest joint result is on exactly the quantity your repo nails. My Part I baseline used
the satellite-to-Earth view factor F = 0.5·[1 − √(1 − (R_E/r)²)] = 0.290 at 650 km, and then
lumped the edge-on radiator's external load to ~100 W. Your exact per-face value (~0.26 edge-on
at 550 km) suggests the Earth-IR and albedo loading on an edge-on radiator is materially larger
than a naive "edge-on ⇒ near-zero" assumption. Folding your exact view factor into my external-
load equations (Q_albedo = S₀·a·F·α_s·A, Q_IR = q_IR·F·ε·A) is the right harmonized treatment,
and I expect it raises the radiator temperature a few kelvin, consistent with your correction.

I have put the published Part I baseline into an open model
(`thermal.report_i_baseline()` → T_rad 21.3 °C, T_j 111.3 °C, T_j,fail 114.8 °C) so your
package can diff against it directly. Your proposed three-case plan (reproduce / harmonize with
your sink + exact VF / transient + single-pipe-failure) is exactly the right structure, and I
will cross-check results both ways.

## Verdict

Recommended. Narrow scope, executed rigorously and honestly, with one headline result of real
value to anyone modeling orbital radiators. The main asks are cosmetic (significant figures)
and incremental (two-node / two-face / sensitivity bands), not corrections.
