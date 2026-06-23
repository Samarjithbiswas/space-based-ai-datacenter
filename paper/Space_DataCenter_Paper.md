# Space-Based Data Center Infrastructure: A Multi-Physics Feasibility and Survivability Study

**Samarjith Biswas, PhD**

*Independent researcher. Correspondence and code: github.com/Samarjithbiswas/space-based-ai-datacenter*

## Abstract

The energy and thermal demands of artificial-intelligence computing have renewed interest in placing
data centers in low Earth orbit, and the first hardware has flown. This paper presents a first-order,
fully sourced, and reproducible systems-engineering analysis of an orbital artificial-intelligence
data center, using a published constellation reference architecture as the running example. Each
subsystem is derived from first principles and solved numerically with an open model that regenerates
every result. The analysis finds that radiative cooling, the function most often assumed to be the
hard problem, is the mature part of the architecture: radiator area scales linearly with power at
about fifteen hundred square meters per megawatt, and the binding thermal limit is not heat rejection
but the conduction path at the chip, which saturates above roughly four hundred watts per device and
forces liquid cooling at the die. Total ionizing dose is survivable behind a centimeter of aluminium,
at the cost of a ten to twenty percent throughput tax from single-event upsets. The binding,
unsolved constraints lie elsewhere: orbital-debris survivability in a tight formation, where the
hundred-and-fifty-meter spacing required by the optical links is the same spacing that makes a
collision cascade dangerous; mandatory active disposal, since natural decay at six hundred and fifty
kilometers runs to about two decades and fails the five-year rule; and launch economics, where a
Monte-Carlo analysis finds that most plausible cost trajectories never reach the price the business
case requires within the horizon, and where they do the median arrival is in the mid-2040s rather than
the mid-2030s. The contribution is an open, end-to-end model and an explicit separation of
demonstrated capability from projection, intended to direct demonstrator effort toward the
survivability and autonomy risks that actually gate deployment.

**Keywords:** space-based computing; orbital data center; systems engineering; spacecraft thermal
control; orbital debris; free-space optical communications; launch economics.

## 1. Introduction

Training and inference clusters for artificial intelligence are now provisioned at the scale of tens
to hundreds of megawatts, and power, water, land, and grid interconnection have become first-order
constraints on terrestrial growth. Against this pressure, operating data centers in orbit has moved
from speculation into early hardware. Within a recent fourteen-month window a data-center-class
accelerator was switched on in orbit, a second operator placed compute nodes in low Earth orbit, and
a major laboratory published a reference design for a constellation of machine-learning accelerators
flying in tight formation. The question is no longer whether the attempt will be made but whether the
physics and the economics close.

Prior treatments fall into three groups. First, vendor and laboratory concept studies set out the
architecture and the optimistic case but are non-peer-reviewed and self-reported. Second, a body of
established spacecraft-engineering literature provides the governing physics for each subsystem in
isolation: orbital mechanics and oblateness-driven nodal precession; the empirical upper-atmosphere
density models that set drag and orbital lifetime; gray-body radiative thermal control and spacecraft
thermal practice; trapped-radiation environment and dose models; orbital-debris flux models and the
collision-cascade analysis that underlies modern debris concern; and free-space optical inter-satellite
link budgets. Third, the commercial-space economics literature provides launch-cost learning-curve
analyses. What has been missing is an integrated, reproducible treatment that joins these subsystems
into one consistent design point, propagates the dominant uncertainties, and states plainly which
problems are solved and which are not.

This paper provides that treatment. The contributions are: (i) an open, validated, end-to-end systems
model that closes the mass, power, thermal, and velocity budgets and regenerates every figure and
number; (ii) a quantification of the chip-level thermal wall that distinguishes bulk heat rejection,
which scales benignly, from the conduction path, which does not; (iii) a statement of the formation
paradox, in which the link-budget spacing and the debris-survivability spacing are mutually exclusive
with present hardware; and (iv) an independent Monte-Carlo of launch-cost parity that replaces a single
optimistic date with a credibility distribution. The running example is the published reference
constellation: approximately eighty-one satellites within a one-kilometer-radius cluster in a
six-hundred-and-fifty-kilometer dawn-dusk sun-synchronous orbit.

## 2. Reference architecture and method

The analysis is first-order by design. Each subsystem is modeled with closed-form or low-order
numerical relations and implemented in an open Python package that is validated against worked examples
and carries an automated test suite. The models are sizing and risk-ranking tools, not high-fidelity
flight-design tools; the explicit limitations are stated in Section 10. Inputs are drawn, with stated
confidence, from public agency models, vendor documentation, standard texts, and the
reference-architecture preprint, with a strict line kept between demonstrated and projected quantities.
The use of generative AI as a drafting aid, and the independent verification of all equations, are
described in the accompanying disclosure.

## 3. Thermal control: solved, but it does not scale

In vacuum a body sheds heat only by radiation, and the rejected flux rises with the fourth power of
surface temperature, so for a fixed operating temperature the required radiator area is linear in the
heat load. A one-megawatt node needs on the order of fifteen hundred square meters of double-sided
panel at a warm operating point, consistent with the roughly twelve-hundred-square-meter-per-megawatt
rule used in practice. Bulk heat rejection is therefore a mature, predictable problem, and flight
hardware already does it.

The binding limit is the short conduction path between the silicon and the panel. With a passive
series resistance of about three-tenths of a kelvin per watt, the temperature rise across the chain is
proportional to per-chip power, and above roughly four hundred watts per device the rise across the
interface alone exceeds the entire junction-temperature budget. High-power accelerators therefore
require pumped-loop or loop-heat-pipe cooling at the die, which is the design choice the flying systems
have made. The practical conclusion inverts the popular framing: cooling is the low-risk part of the
architecture, and the item to watch is the chip-level thermal interface, not the radiator.

## 4. Orbital lifetime and mandatory disposal

At six hundred and fifty kilometers a tenuous atmosphere still removes orbital energy, and the orbit
decays. Integrating the drag-driven decay with an empirical density model gives a natural lifetime of
about two decades at moderate solar activity, a few years at solar maximum, and centuries at solar
minimum. This spread is itself decisive: a disposal strategy cannot rely on natural decay because the
relevant solar cycle is not known in advance. The regulatory rule now in force requires removal within
five years of end of mission, which the central case fails by a wide margin. Active disposal is
therefore mandatory. A controlled Hohmann de-orbit costs about one hundred and thirty meters per
second, dominating the velocity budget, with a propellant mass of a few kilograms using electric
propulsion. Disposal is a primary mission function with its own mass, propellant, and reliability case.

## 5. Radiation: survivable, with a throughput tax

Two distinct radiation effects matter. Accumulated dose behind a centimeter of aluminium is about one
kilorad over five years, comfortably under the mission requirement and well under the levels at which
the ground-tested processor first showed memory irregularities, with no hard failures observed to far
higher doses. Total dose is therefore survivable with margin. The cost is single-event upsets: at
orbital particle rates these are frequent enough to matter, but because machine-learning inference
tolerates occasional bit flips, the efficient design is error-correcting memory plus periodic
checkpointing rather than full triple redundancy. The penalty is a ten to twenty percent throughput
tax that should be carried explicitly in the compute budget.

## 6. Debris and the formation paradox

The orbital shell near six hundred kilometers is the most congested region of low Earth orbit. Treating
catastrophic impacts as a Poisson process, the probability that at least one member of an
eighty-one-satellite cluster suffers a catastrophic impact over five years is, on a central reading of
the tracked-fragment flux, on the order of one in six, with a wide band. The deeper hazard is coupling:
a single fragmentation sprays lethal debris into the volume the neighbors occupy, and the probability
that a neighbor is struck grows as the inverse square of the spacing. At the close spacing the
architecture adopts, this neighbor-to-neighbor hazard is high enough to raise the prospect of a
cascade. Widening the formation to a kilometer suppresses the coupling below a percent but, as Section
7 shows, breaks the optical-link budget. This mutual exclusivity, link spacing against debris spacing,
is the binding and still-unsolved constraint on the concept.

## 7. Communications and why the formation is tight

A constellation is useful only if the accelerators exchange data at very high bandwidth. In orbit the
links are optical, and an optical beam spreads as it travels, so the fraction of transmitted power
captured by the receiver falls with the square of range. With terminal parameters that exist today, a
modest single link closes reliably only to a few thousand kilometers, and the many-terabit aggregate
the architecture assumes is reachable, with present hardware, only at a spacing of about one hundred
and fifty meters. The tight cluster is therefore forced by the inverse-square behavior of the link,
and it is the same spacing that the debris analysis shows to be dangerous. Resolving this tension,
through far better optical terminals or through fast autonomous collision avoidance at sub-kilometer
spacing, is the central research problem the demonstrators should address.

## 8. Power, attitude, and delivered compute

The dawn-dusk orbit is sunlit for more than ninety-five percent of each revolution, so the battery is
small and the thermal environment is steady. Multi-junction arrays deliver a few hundred watts per
square meter at end of life. The optical links require pointing finer than the spacecraft bus can hold,
so a fast-steering mirror provides the sub-microradian correction. Delivered compute is the peak
capability reduced by real utilization and the radiation tax; because inference utilization is often
low, the honest cost per useful operation is several times the figure obtained by dividing price by
peak throughput.

## 9. Economics: parity is unlikely, not merely late

The economic case rests on launch cost falling far enough that the annualized cost of power in orbit
approaches the terrestrial cost of power, a crossover usually placed near two hundred dollars per
kilogram. We test this with a Wright learning curve on cumulative launched mass, with a logistic
cadence ramp, sampling the learning rate, the starting price, the payload, and the cadence by
Monte-Carlo. The result is sobering in a way a single date hides: across the sampled futures only a
small minority, about one in twenty, ever reach the target price within the horizon, and the large
majority never do. Conditional on the minority that reach it, the median arrival is near 2044, with a
fifth percentile of about 2037 and essentially no probability by 2035. Extending the horizon raises the
reaching fraction only into the high single digits. Parity at this price is therefore unlikely under
most assumptions rather than merely late, and it is necessary but not sufficient: hardware cost,
lifetime, and utilization gate the economics regardless.

## 10. Readiness, limitations, and the recommended program

Scored against the standard readiness scale, the components sit in the middle: an accelerator has
flown, a processor has been radiation-tested, kilowatt-class thermal hardware has flown. Everything
that depends on the constellation acting as one system, the flown multi-terabit formation link,
station-keeping through a solar cycle, and autonomous cluster-coordinated collision avoidance, sits
near the bottom. That gap is the program risk.

The analysis is first-order. It omits a multi-node thermal finite-element model, runs of the official
agency debris and dose tools, a closed-loop attitude-control simulation, micrometeoroid shielding
sizing, and a full time-domain mission simulation; a flight program would add these. The most
load-bearing single source is a non-peer-reviewed vendor preprint, and the per-chip power of the
reference accelerator is undisclosed and treated as a band.

The recommended program follows the risk. Small, attritable demonstrators should retire the
survivability and autonomy questions: fly the formation link, hold the close formation through a real
solar cycle, demonstrate a coordinated avoidance maneuver, and prove a clean disposal. Those
milestones, not another record on heat rejection, should gate any decision to build at constellation
scale.

## 11. Conclusions

Cooling already works and scales predictably; radiation is survivable with a bounded penalty; power
and attitude are in hand. The frontier that decides whether orbital artificial-intelligence compute
becomes infrastructure is the cluster of debris survivability in a tight formation, credible
propulsive disposal, a flown high-bandwidth formation link, and launch economics that are later and
far less certain than the headline. The physics of cooling is not what stands between the present and
orbital data centers; the physics of flying many expensive machines very close together, in the most
crowded shell of near-Earth space, for years, and bringing each one safely home, is.

## Data and code availability

All models, derivations, figures, and the simulations behind every number are openly available at
github.com/Samarjithbiswas/space-based-ai-datacenter (release v1.0), under the MIT License (code) and
CC-BY 4.0 (text and figures). A single command reproduces the full analysis.

## Disclosure

See the accompanying methods and AI-use disclosure. Generative AI was used as a drafting aid; all
quantitative claims are produced by the open code or cited primary sources, all equations were
independently verified, and the author is solely responsible for the content.

## References

A full, categorized bibliography of thirty-five sources, including Curtis and Vallado (astrodynamics),
the NRLMSIS atmosphere model, the AE/AP and SHIELDOSE radiation models, NASA ORDEM and ESA MASTER
debris tools, Kessler and Cour-Palais and Klinkrad (debris cascade), Hemmati and the free-space
optical link-budget literature, Gilmore and Incropera (thermal), Sutton and Biblarz (propulsion), the
SMAD systems texts, the FCC disposal rule, and the reference-architecture preprint (arXiv:2511.19468),
is provided in the accompanying monograph and repository.
