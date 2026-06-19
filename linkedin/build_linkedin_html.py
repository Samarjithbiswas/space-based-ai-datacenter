"""Build a self-contained, equation-free, long-form LinkedIn article in HTML.

Why this exists: LinkedIn's article editor cannot render LaTeX or pasted equations, and the
earlier text version read as a series of short sections. This version removes every equation,
describes the physics in plain language, and runs each section as several full paragraphs so it
reads like a written piece rather than a list. Key figures are embedded as base64 so the file is
a single portable document that renders anywhere and can be read directly or its text copied
section by section into the LinkedIn editor.

Output: linkedin/Space_DataCenter_LinkedIn_Article.html
"""
import base64
import pathlib
from diagrams import DIAGRAMS

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(__file__).resolve().parent / "Space_DataCenter_LinkedIn_Article.html"

# (placeholder, path, caption)
FIGS = {
    "thermal": ("report/figures/fig2_thermal_wall.png",
                "The chip-level heat wall. Below roughly 400 watts a passive path holds the junction inside its budget; above it, the interface alone overruns the entire temperature allowance, which is why high-power parts need liquid cooling at the die."),
    "decay": ("report/figures/fig1_orbital_decay.png",
              "Natural orbital decay at 650 kilometers. The lifetime swings from a few years at solar maximum to centuries at solar minimum, and in the central case it is far longer than the five years regulators now allow."),
    "radiation": ("report/figures/fig4_radiation.png",
                  "Ionizing dose behind aluminium shielding over five years, set against the mission requirement and against the levels at which the tested processor first misbehaved."),
    "debris": ("report/figures/fig3_debris_risk.png",
               "Catastrophic-impact probability for the cluster, and the way a single fragmentation couples to neighbors as the spacing tightens."),
    "link": ("report/systems_figs/fig_comms.png",
             "The optical link budget. Reliable range falls quickly with distance, and the data rate the architecture needs is only reachable when the satellites fly very close together."),
    "deltav": ("report/figures/fig5_deltav.png",
               "The velocity budget for the mission. Controlled disposal at end of life is the single largest line item."),
    "cost": ("report/figures_pred/fig_cost_parity.png",
             "Launch-cost learning curve and the distribution of the year launch first reaches the price the business case needs. Most sampled futures never reach it within the horizon."),
    "risk": ("report/figures/fig7_risk_matrix.png",
             "The subsystem risk picture at a glance. Cooling and radiation sit low; debris survivability, disposal, and launch economics sit high."),
}


def b64(rel):
    p = ROOT / rel
    return base64.b64encode(p.read_bytes()).decode("ascii")


def img(placeholder):
    rel, cap = FIGS[placeholder]
    data = b64(rel)
    return (f'<figure><img alt="{cap}" src="data:image/png;base64,{data}"/>'
            f'<figcaption>{cap}</figcaption></figure>')


def svgfig(name):
    """A geometry diagram with its caption below. Embedded as a PNG <img> (rasterized in
    post_figures/) so it is copyable/saveable from the page like the chart figures; falls
    back to inline SVG if the PNG has not been exported yet."""
    svg, cap = DIAGRAMS[name]
    png = pathlib.Path(__file__).resolve().parent / "post_figures" / f"diagram_{name}.png"
    if png.exists():
        data = base64.b64encode(png.read_bytes()).decode("ascii")
        return (f'<figure class="diagram"><img alt="{cap}" src="data:image/png;base64,{data}"/>'
                f'<figcaption>{cap}</figcaption></figure>')
    return f'<figure class="diagram">{svg}<figcaption>{cap}</figcaption></figure>'


BODY = f"""
<article>

<p class="standfirst">Space-based AI data centers stopped being a conference slide in 2025. Inside fourteen months a
graphics processor of the kind that trains frontier models was switched on in orbit, a second company
placed data-center hardware in low Earth orbit, and a major laboratory published a reference design for a
constellation of machine-learning accelerators flying in tight formation. The idea has moved from the
realm of the speculative into the realm of the engineering review, and an engineering review is what it now
deserves. What follows is a subsystem-by-subsystem reading of whether this works, written from primary
sources and an open simulation model, and careful throughout to separate what has actually been
demonstrated from what is still a projection.</p>

<h2>What is actually flying</h2>

<p>Three efforts anchor the discussion, and it is worth being precise about each because the public
conversation tends to blur them together. Starcloud placed a single high-end graphics processor on a small
satellite and powered it on in orbit in November 2025. The hardware is a data-center-class part with tens
of gigabytes of memory and several petaflops of throughput, carried on a bus of around sixty kilograms.
This was a genuine first, a real accelerator running in the real environment, and it retired a number of
questions that had until then been answered only on the ground.</p>

<p>Axiom Space followed in January 2026, reaching low Earth orbit with nodes intended as the seed of an
orbital data-center capability, and stating an intent to scale from the kilowatt class toward the megawatt
class. The third effort, and the one that frames most of the numbers here, is a published reference design
for a constellation of roughly eighty satellites carrying machine-learning accelerators, flying within a
circle about a kilometer across, in a dawn-dusk sun-synchronous orbit near six hundred and fifty
kilometers, with two prototype satellites targeted for early 2027.</p>

{svgfig("orbit")}

{svgfig("constellation")}

<p>One caution belongs at the top rather than buried in a footnote. The most load-bearing single document
in this whole area is a preprint that has not been through peer review and was written by the team
proposing the system. That does not make it wrong, and much of it is careful, but it does mean the most
quoted radiation, link, and cost figures are self-reported rather than independently replicated. Two widely
repeated marketing claims, a tenfold cost advantage inclusive of launch and a deployment date that had
already slipped by the time it was quoted, did not survive checking against the public record. The right
posture toward the economics in particular is skepticism until the numbers are reproduced.</p>

<h2>Cooling already works, and that is the part everyone gets wrong</h2>

<p>The popular intuition is that space is cold, so cooling a computer there should be easy. The intuition is
backwards. A vacuum is an excellent insulator, and a body in orbit can shed heat only by radiating it as
infrared light. There is no air to carry heat away, no water, no convection of any kind. Everything the
machine dissipates has to leave as thermal radiation from a surface, and the rate at which a surface can do
that climbs only with the fourth power of its temperature. In practice that fixes a hard relationship
between how much heat you make and how much radiator you must carry.</p>

<p>Worked through for a realistic warm radiator, a one-megawatt node needs on the order of fifteen hundred
square meters of double-sided panel to stay in a sensible temperature range. That is consistent with the
rule of thumb the industry already uses, a bit over a thousand square meters for every megawatt, and it is
why serious proposals for gigawatt-scale systems show panels kilometers on a side. None of this is exotic.
The radiator scales linearly with power, the physics is well understood, and flight hardware already does
it. On the question of bulk heat rejection, the answer is that it is solved and demonstrated.</p>

<p>The real wall is not the radiator. It is the short thermal path between the silicon and that radiator.
Heat has to cross from a chip running hot into the structure that carries it to the panel, and that
interface has a fixed resistance. Push a few hundred watts through it and the temperature rise across the
interface alone is manageable. Push much past four hundred watts through a passive path and the rise across
that interface, before you even account for anything else, exceeds the entire temperature budget the chip
is allowed. The consequence is concrete and it is already visible in the hardware that has flown: any
high-power accelerator has to be cooled with a pumped liquid loop right at the die, not by a passive
conduction path. That is exactly the design choice the flying systems have made.</p>

{svgfig("thermal")}

{img("thermal")}

<p>The takeaway is almost the opposite of the popular framing. Cooling is the mature, low-risk part of this
architecture. The thing to watch is not whether heat can be rejected but the plumbing that gets it out of
the chip in the first place, and that is a solved problem at the kilowatt scale and an engineering problem,
not a research problem, at higher power.</p>

<h2>Staying up, and the harder problem of coming down</h2>

<p>At six hundred and fifty kilometers the atmosphere has not quite ended. What remains is tenuous beyond
everyday imagination, but it is still there, and over years it drains energy from the orbit and the
satellite slowly spirals down. How long that takes depends almost entirely on the Sun. When solar activity
is high the upper atmosphere puffs up and grows denser at altitude, and decay is fast. When the Sun is
quiet the same orbit can persist for a very long time.</p>

<p>For the reference orbit the central estimate for natural decay is around two decades. At the active
extreme of the solar cycle it can be as short as a handful of years, and at the quiet extreme it stretches
into centuries. That enormous spread is itself the point, because it means you cannot plan a disposal
strategy around natural decay. You do not know in advance which cycle you will get.</p>

{img("decay")}

<p>This collides directly with regulation. The rule now in force requires a satellite to be removed from
orbit within five years of finishing its mission, a sharp tightening from the much longer guideline that
came before it. The central decay estimate misses that requirement by a wide margin, and even the optimistic
case is uncomfortably close to the limit. The conclusion is unavoidable: a constellation at this altitude
must carry propulsion and actively drive itself down at end of life. Disposal is not a contingency to be
handled if convenient. It is a primary mission function that has to be designed in from the start, with its
own propellant, its own reliability case, and its own share of the mass budget.</p>

{svgfig("hohmann")}

<h2>Radiation is survivable, and the honest cost is throughput</h2>

<p>Orbit is a radiation environment. Trapped protons and electrons, cosmic rays, and the occasional solar
storm all deposit energy in electronics, and the worry has always been whether commercial accelerators,
which are not built to military radiation specifications, can take it. The accumulated dose part of this
question turns out to be reassuring. A modest aluminium enclosure attenuates the trapped radiation
substantially, and behind a centimeter of it the five-year dose is around a kilorad, comfortably under the
level the mission needs to tolerate and well under the levels at which the actual tested processor first
showed any memory irregularities. There were no hard failures in ground testing up to far higher doses than
the mission will ever see. On total dose, the margin is real.</p>

{img("radiation")}

<p>The part that genuinely costs something is not slow accumulation but sudden upset. A single energetic
particle can flip a bit in memory or logic, and at orbital particle rates these events are frequent enough
to matter. The reflexive engineering answer, triple everything and vote, is the wrong answer here because it
roughly halves the useful output of every chip. The better answer exploits a property of the workload:
machine-learning inference is statistically tolerant of the occasional flipped bit, far more so than, say,
a banking ledger. That means error-correcting memory plus periodic checkpointing, rather than full
redundancy, is the efficient design. It keeps most of the compute usable while protecting against the rare
upset that would otherwise corrupt a long-running job.</p>

<p>The right way to carry this in a plan is as an explicit tax. Radiation does not break the machine, but it
takes a slice off the top, somewhere in the range of ten to twenty percent of throughput once you account
for upsets, scrubbing, and the occasional reset. That number should appear in the cost of compute from the
beginning rather than being discovered later.</p>

{svgfig("shield")}

<h2>Debris, and the paradox built into the formation</h2>

<p>This is the subsystem that should keep designers awake, and it is the one the popular coverage almost
entirely ignores. The orbital shell around six hundred kilometers is the most crowded region of near-Earth
space, thick with spent hardware and fragments from past collisions and tests. Each satellite presents a
target, and over a five-year mission the chance that at least one member of an eighty-satellite cluster
suffers a catastrophic impact from a tracked-size fragment is, on a central reading of the flux, on the
order of one in six. The uncertainty band is wide, from a few percent to nearly half, but even the low end
is not a number a program can wave away.</p>

<p>The deeper problem is not the single impact. It is what a single impact does to a tight formation. When
one satellite is fragmented, it does not simply remove itself. It sprays a cloud of lethal debris into the
exact volume its neighbors occupy. The closer the neighbors, the higher the chance each of them is then
struck, and that coupling grows sharply as spacing shrinks. At the close spacing the architecture wants,
the probability that a fragmentation takes a neighbor with it is high enough to raise the specter of a
cascade, one failure seeding the next.</p>

{svgfig("formation")}

{img("debris")}

<p>Here is the paradox, and it is structural rather than incidental. The coupling between neighbors falls
off quickly as you spread the formation out. Widen the satellites to a kilometer apart and the
neighbor-to-neighbor hazard drops below a percent. But, as the next section explains, the optical links that
make the whole constellation function as one machine only close their budget when the satellites are very
close together. The same tight spacing that the communications design requires is precisely the spacing that
makes the debris cascade dangerous. You cannot relax one without breaking the other. This, not heat and not
radiation, is the binding and still-unsolved constraint on the whole concept.</p>

<h2>Why the formation has to be so tight</h2>

<p>A constellation of accelerators is only useful if the accelerators can talk to each other at enormous
bandwidth, because distributing a large model across many chips means moving a great deal of data between
them constantly. In orbit those links are optical, laser beams between small telescopes, and optical links
are unforgiving about distance. A laser beam spreads as it travels, so the fraction of transmitted light
that lands on the receiver falls with the square of the range. Double the distance and you lose four times
as much signal.</p>

<p>With realistic terminal hardware, a small telescope, a near-infrared laser, the kind of pointing accuracy
a spacecraft can actually hold, a modest single link closes reliably only out to a few thousand kilometers,
and the bandwidth needed for this application is far above what a single modest link provides. Reaching the
many-terabit aggregate the architecture assumes, using components that exist rather than components that are
hoped for, forces the satellites to within roughly a hundred and fifty meters of each other. The tight
cluster is not an aesthetic choice or a convenience. It is forced by the inverse-square behavior of light
over distance.</p>

{svgfig("link")}

{img("link")}

<p>This is what closes the trap described in the previous section. The communications engineer asks for the
satellites to fly close, because that is the only way to get the bandwidth. The debris engineer asks for
them to fly far apart, because that is the only way to survive a fragmentation. Both are right, and they
cannot both be satisfied with today's hardware. Resolving that tension, whether through far better optical
terminals that work at longer range, or through active collision avoidance fast and autonomous enough to
matter at these spacings, is the central research problem the demonstrators ought to be aimed at.</p>

<h2>Power, pointing, disposal, and the compute that actually comes out</h2>

<p>Several supporting subsystems deserve a paragraph each, because together they shape the design more than
any single one does in isolation. Power is the friendliest of them. The dawn-dusk orbit was chosen for a
reason: it rides the line between day and night around the planet, so the satellite sits in nearly
continuous sunlight, well over ninety-five percent of every orbit. That makes the battery almost an
afterthought, since there is barely any night to ride through, and it keeps the thermal environment steady,
which in turn justifies treating the cooling problem as a steady-state one. Modern multi-junction solar
cells deliver a few hundred watts per square meter even after accounting for degradation over the mission.</p>

{svgfig("beta")}

<p>Pointing is less friendly. A laser link between satellites a hundred and fifty meters apart has to be
aimed with extraordinary precision, far finer than the spacecraft body itself can be held by its attitude
system. The standard sensors get you within roughly ten millionths of a radian, and the link needs better
than one. The gap is closed by a small fast-steering mirror that makes fine corrections independently of the
bus. The body coarse-points, the mirror fine-points, and without that mirror the link simply does not hold.</p>

{svgfig("pointing")}

{img("deltav")}

<p>Disposal, discussed earlier as a necessity, also dominates the velocity budget. The maneuver to lower the
orbit for reentry is the single largest demand on the propulsion system, larger than station-keeping and
everything else combined over the mission. With an efficient electric thruster the propellant mass is
modest, a few kilograms, but the function is not optional and its reliability has to be high, because a
satellite that cannot deorbit becomes exactly the debris hazard the program is trying to avoid creating.</p>

<p>Finally, and this is the number most often quoted too optimistically, the compute that actually emerges is
not the headline peak figure. Useful output is the peak capability multiplied by how busy the chips really
are and by how much the radiation tax removes. Real-world utilization for inference is often quite low, so
the honest cost per unit of useful computation is several times the naive figure you would get by dividing
price by peak throughput. Any business case that quotes peak numbers is quoting a ceiling that operations
never touch.</p>

{svgfig("compute")}

<h2>The money, and why the date everyone repeats is fragile</h2>

<p>Every version of this idea rests on one economic assumption: that the cost of putting mass into orbit
falls far enough that the annual cost of power delivered in space approaches the cost of power for a data
center on the ground. The figure usually attached to that crossover is around two hundred dollars per
kilogram to low Earth orbit, and the reference work projects reaching it in the middle of the next decade.
Because the entire case hinges on this one number, it deserved its own independent test rather than being
taken on faith.</p>

<p>The test was a simulation of the launch-cost learning curve, the well-documented tendency for unit cost to
fall by a fixed fraction every time cumulative production doubles, applied to launched mass and run many
thousands of times over plausible ranges for the learning rate, the starting price, the vehicle payload, and
the flight cadence. The result is sobering in a way a single date hides. Across the sampled futures, only a
small minority, around one in twenty, ever reach the target price within the horizon studied. The large
majority never get there at all on these assumptions. Parity at two hundred dollars per kilogram is not a
near-certainty waiting for a date on the calendar. Under most defensible assumptions it does not arrive.</p>

{img("cost")}

<p>Among the minority of futures that do reach the target, the typical arrival is in the early to middle
years of the next decade rather than the middle of this one, and essentially none of them reach it as early
as the headline date. Stretching the horizon out further only lifts the fraction that ever reach parity
into the high single digits, so the conclusion is not an artifact of where the analysis was cut off. The
vendor's date sits beyond the optimistic edge of the distribution and depends on a specific stack of
aggressive assumptions all coming true together. The honest reading is twofold: this price point is unlikely
under most assumptions rather than merely late, and even if it arrives it is necessary but not sufficient,
because hardware cost, operating lifetime, and utilization gate the economics regardless of what a kilogram
costs to launch.</p>

<h2>How ready is any of this, really</h2>

<p>It helps to score the pieces honestly against the standard ladder engineers use to talk about maturity,
from a principle observed in a laboratory at the bottom to a system proven through operational use at the
top. The building blocks score respectably. A data-center accelerator has run in orbit. A processor has been
radiation-tested on the ground without hard failures. Kilowatt-class thermal hardware has flown. These sit
in the middle of the ladder, the region where a component has been demonstrated in a relevant environment.</p>

{svgfig("trl")}

{img("risk")}

<p>The system-level capabilities are where the maturity collapses, and it collapses precisely on the items
this analysis flagged as binding. A flown optical link carrying the bandwidth the design needs, between two
satellites, does not yet exist outside the laboratory bench. Holding a tight formation under the differential
drag of the solar cycle has not been demonstrated. Autonomous, cluster-coordinated collision avoidance at
sub-kilometer spacing, the very thing the debris paradox demands, sits near the bottom of the ladder. The
gap between mature components and immature system integration is the whole story of this program, and it is
why a sober roadmap looks nothing like a straight line to a gigawatt constellation.</p>

<h2>What this means for the teams flying it</h2>

<p>Put the pieces together and a clear priority ordering falls out, one that is quite different from where the
public attention goes. Cooling, the thing people worry about first, is the thing to worry about least; it
works today and scales predictably. Radiation is survivable with a known and bounded penalty. Power and
attitude are well in hand. The real frontier, the set of problems that actually decide whether orbital AI
becomes infrastructure or stays a demonstration, is the cluster of debris survivability in a tight
formation, credible propulsive disposal at end of life, a flown high-bandwidth formation link, and launch
economics that are later and far less certain than the headline suggests.</p>

<p>The encouraging part is that the program already taking shape, small and attritable demonstrators rather
than an immediate constellation, is the right program for exactly these reasons. The job of those
demonstrators should be to retire the survivability and autonomy risks: fly the formation link, hold the
close formation through a real solar cycle, demonstrate a coordinated avoidance maneuver, and prove a clean
deorbit. Those milestones, not another record on heat rejection, are what should gate any decision to build
at constellation scale. The physics of cooling is not what stands between us and orbital data centers. The
physics of flying many expensive machines very close together, in the most crowded shell of near-Earth
space, for years at a time, and bringing every one of them safely home, is.</p>

<hr/>

<p class="closing">The full study behind this article, with the complete derivations, the simulation code for
every number, and the figures above, is open and free to read and to reproduce. The link is in the first
comment. Independent checking and correction are welcome; that is the point of putting it in the open.</p>

</article>
"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Space-Based Data Center Infrastructure: A Multi-Physics Approach (Part II)</title>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600;6..72,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>
  :root {{ --ink:#16243a; --body:#26313f; --muted:#5c6b7a; --rule:#e3e7ec; --accent:#0d7d74; }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'Newsreader', Georgia, serif; color:var(--body); background:#fbfaf7;
          line-height:1.72; font-size:19px; }}
  .wrap {{ max-width:760px; margin:0 auto; padding:64px 26px 96px; }}
  .kicker {{ font-family:'Inter',sans-serif; font-size:.74rem; font-weight:700; letter-spacing:.16em;
             text-transform:uppercase; color:var(--accent); margin-bottom:18px; }}
  h1 {{ font-family:'Newsreader',serif; font-weight:700; font-size:2.6rem; line-height:1.12;
        letter-spacing:-.01em; color:var(--ink); margin-bottom:18px; }}
  .byline {{ font-family:'Inter',sans-serif; font-size:.92rem; color:var(--muted); margin-bottom:6px; }}
  .byline strong {{ color:var(--ink); font-weight:600; }}
  .standfirst {{ font-size:1.24rem; line-height:1.6; color:var(--ink); font-weight:500;
                 margin:30px 0 8px; }}
  h2 {{ font-family:'Newsreader',serif; font-weight:700; font-size:1.7rem; line-height:1.2;
        color:var(--ink); margin:48px 0 14px; letter-spacing:-.01em; }}
  p {{ margin:0 0 20px; }}
  figure {{ margin:34px 0; }}
  figure img {{ width:100%; height:auto; border:1px solid var(--rule); border-radius:8px;
                background:#fff; }}
  figure.diagram svg {{ width:100%; height:auto; border:1px solid var(--rule); border-radius:8px;
                background:#fff; padding:16px 14px; }}
  figcaption {{ font-family:'Inter',sans-serif; font-size:.84rem; line-height:1.5; color:var(--muted);
                margin-top:10px; padding-left:2px; }}
  hr {{ border:none; border-top:1px solid var(--rule); margin:46px 0; }}
  .closing {{ font-size:1.02rem; color:var(--muted); font-style:italic; }}
  .topline {{ border-bottom:1px solid var(--rule); padding-bottom:26px; }}
  @media (max-width:560px) {{ body{{font-size:18px;}} h1{{font-size:2.05rem;}} h2{{font-size:1.42rem;}}
                              .wrap{{padding:42px 20px 70px;}} }}
</style>
</head>
<body>
<div class="wrap">
  <div class="topline">
    <div class="kicker">Part II · Engineering study</div>
    <h1>Space-Based Data Center Infrastructure</h1>
    <p class="byline" style="font-size:1.15rem;color:var(--ink);font-style:italic;margin-bottom:8px;">A Multi-Physics Approach</p>
    <p class="byline"><strong>Samarjith Biswas, PhD</strong></p>
    <p class="byline">Survivability, economics, and a complete systems model, from primary sources and open simulation</p>
  </div>
  {BODY}
</div>
</body>
</html>
"""

OUT.write_text(HTML, encoding="utf-8")
size_kb = OUT.stat().st_size / 1024
words = len(" ".join(BODY.split()).split())
print(f"wrote {OUT.name}  ({size_kb:.0f} KB, ~{words} words of article text, {len(FIGS)} figures embedded)")
