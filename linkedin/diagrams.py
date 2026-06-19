"""Inline SVG geometry diagrams for the LinkedIn article.

Each entry is (svg, caption). The svg carries NO title text on top; the caption is
rendered in the document body, below the figure, by build_linkedin_html.py. Palette
matches the article: ink #16243a, teal #0d7d74, slate #26313f, accent #c75c2e.
"""

_FONT = "<style>text{font-family:'Inter',system-ui,sans-serif}</style>"


def _svg(body, w, h):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img">{_FONT}{body}</svg>')


# 1. Dawn-dusk sun-synchronous orbit geometry
ORBIT = (_svg("""
<defs><marker id="arO" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
<path d="M0,0 L7,3 L0,6 Z" fill="#c75c2e"/></marker></defs>
<path d="M250,65 A95,95 0 0,0 250,255 Z" fill="#1b2a3a"/>
<path d="M250,65 A95,95 0 0,1 250,255 Z" fill="#cfe0ea"/>
<circle cx="250" cy="160" r="95" fill="none" stroke="#16243a" stroke-width="1.5"/>
<line x1="250" y1="52" x2="250" y2="268" stroke="#16243a" stroke-width="1" stroke-dasharray="4 4"/>
<g stroke="#c75c2e" stroke-width="2.2" marker-end="url(#arO)">
<line x1="700" y1="110" x2="610" y2="110"/><line x1="700" y1="160" x2="610" y2="160"/>
<line x1="700" y1="210" x2="610" y2="210"/></g>
<text x="700" y="92" text-anchor="end" font-size="14" fill="#c75c2e" font-weight="600">Sunlight</text>
<ellipse cx="250" cy="160" rx="27" ry="128" fill="none" stroke="#0d7d74" stroke-width="2.6"/>
<circle cx="250" cy="32" r="6.5" fill="#0d7d74"/>
<text x="150" y="165" text-anchor="middle" font-size="13" fill="#eef2f5">Night</text>
<text x="352" y="165" text-anchor="middle" font-size="13" fill="#26313f">Day</text>
<text x="250" y="20" text-anchor="middle" font-size="12.5" fill="#0d7d74" font-weight="600">satellite</text>
<text x="430" y="300" text-anchor="middle" font-size="13" fill="#26313f">orbit plane on the day–night terminator</text>
""", 720, 320),
 "The dawn-dusk sun-synchronous orbit. The orbital plane is held on the line between day and night, so the "
 "satellite stays in sunlight for more than ninety-five percent of every orbit. That is what makes the battery "
 "almost unnecessary and the thermal environment steady.")


# 2. Passive thermal conduction path
THERMAL = (_svg("""
<defs><marker id="arT" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
<path d="M0,0 L7,3 L0,6 Z" fill="#a3303a"/></marker></defs>
<line x1="20" y1="40" x2="700" y2="40" stroke="#a3303a" stroke-width="2.2" marker-end="url(#arT)"/>
<text x="20" y="28" font-size="13" fill="#a3303a" font-weight="600">heat flow</text>
""" + "".join(
    f'<rect x="{20+i*132}" y="58" width="112" height="54" rx="6" fill="{fill}" stroke="#16243a" stroke-width="1.2"/>'
    f'<text x="{76+i*132}" y="82" text-anchor="middle" font-size="12.5" fill="#16243a" font-weight="600">{name}</text>'
    f'<text x="{76+i*132}" y="100" text-anchor="middle" font-size="11" fill="#5c6b7a">{r}</text>'
    for i, (name, r, fill) in enumerate([
        ("Junction", "0.150 K/W", "#fdece8"), ("Interface", "0.020 K/W", "#eef2f5"),
        ("Cold plate", "0.060 K/W", "#eef2f5"), ("Heat pipe", "0.050 K/W", "#eef2f5"),
        ("Radiator", "0.020 K/W", "#e3f1ef")]))
+ """
<text x="76" y="138" text-anchor="middle" font-size="12" fill="#a3303a">~111 °C</text>
<text x="664" y="138" text-anchor="middle" font-size="12" fill="#0d7d74">~21 °C</text>
<text x="700" y="92" text-anchor="end" font-size="20" fill="#0d7d74">↝↝</text>
<text x="360" y="160" text-anchor="middle" font-size="12.5" fill="#26313f">total ~0.300 K/W; the junction-to-case step dominates</text>
""", 720, 180),
 "The passive heat path from the silicon to the radiator. Each interface adds thermal resistance, and the "
 "junction-to-case step dominates. Above about four hundred watts per chip the temperature rise across this "
 "chain alone exceeds the limit, which is why high-power parts switch to a pumped liquid loop at the die.")


# 3. Hohmann de-orbit geometry
HOHMANN = (_svg("""
<defs><marker id="arH" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
<path d="M0,0 L7,3 L0,6 Z" fill="#a3303a"/></marker></defs>
<circle cx="280" cy="190" r="50" fill="#cfe0ea" stroke="#16243a" stroke-width="1.4"/>
<text x="280" y="195" text-anchor="middle" font-size="12" fill="#16243a">Earth</text>
<circle cx="280" cy="190" r="150" fill="none" stroke="#0d7d74" stroke-width="2" stroke-dasharray="5 5"/>
<text x="280" y="28" text-anchor="middle" font-size="12.5" fill="#0d7d74">operational orbit, 650 km</text>
<path d="M280,40 A120,108 0 0,0 280,242" fill="none" stroke="#a3303a" stroke-width="2.4"/>
<circle cx="280" cy="40" r="6" fill="#a3303a"/>
<line x1="280" y1="40" x2="232" y2="40" stroke="#a3303a" stroke-width="2.4" marker-end="url(#arH)"/>
<text x="225" y="36" text-anchor="end" font-size="13" fill="#a3303a" font-weight="600">retro burn Δv ≈ 132 m/s</text>
<text x="150" y="150" text-anchor="middle" font-size="12.5" fill="#a3303a">transfer ellipse</text>
<text x="280" y="262" text-anchor="middle" font-size="12" fill="#26313f">reentry perigee</text>
""", 560, 300),
 "Controlled de-orbit. A small retrograde burn lowers the far side of the orbit into the atmosphere. The "
 "maneuver costs about a hundred and thirty metres per second and is the single largest demand on the "
 "propulsion system over the mission.")


# 4. Radiation shielding and upsets
SHIELD = (_svg("""
<defs><marker id="arR" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
<path d="M0,0 L7,3 L0,6 Z" fill="#c75c2e"/></marker></defs>
<g stroke="#c75c2e" stroke-width="2" marker-end="url(#arR)">
<line x1="20" y1="60" x2="250" y2="60"/><line x1="20" y1="95" x2="250" y2="95"/>
<line x1="20" y1="130" x2="250" y2="130"/><line x1="20" y1="165" x2="250" y2="165"/></g>
<text x="20" y="44" font-size="13" fill="#c75c2e" font-weight="600">trapped protons / electrons</text>
<rect x="255" y="40" width="40" height="150" fill="#b9c6d2" stroke="#16243a" stroke-width="1.2"/>
<text x="275" y="210" text-anchor="middle" font-size="11.5" fill="#26313f">10 mm Al</text>
<g stroke="#c75c2e" stroke-width="1.4" marker-end="url(#arR)" opacity="0.55">
<line x1="295" y1="95" x2="360" y2="95"/><line x1="295" y1="135" x2="360" y2="135"/></g>
<rect x="365" y="78" width="120" height="74" rx="6" fill="#e3f1ef" stroke="#0d7d74" stroke-width="1.4"/>
<text x="425" y="112" text-anchor="middle" font-size="12.5" fill="#16243a" font-weight="600">processor</text>
<text x="425" y="131" text-anchor="middle" font-size="11" fill="#5c6b7a">ECC + checkpoint</text>
<text x="600" y="70" text-anchor="middle" font-size="12.5" fill="#16243a">~1 krad / 5 yr behind shield</text>
<text x="600" y="90" text-anchor="middle" font-size="12.5" fill="#16243a">vs ~750 rad requirement</text>
<text x="600" y="128" text-anchor="middle" font-size="12.5" fill="#a3303a">upsets &#8594; ~10–20%</text>
<text x="600" y="146" text-anchor="middle" font-size="12.5" fill="#a3303a">throughput tax</text>
""", 720, 220),
 "Shielding and upsets. A centimetre of aluminium brings the five-year dose comfortably under the requirement, "
 "so accumulated dose is not the problem. The real cost is single-event upsets, handled with error-correcting "
 "memory and checkpoints rather than full redundancy, at a ten-to-twenty-percent throughput tax.")


# 5. The formation paradox: cascade geometry
FORMATION = (_svg("""
<g>
<circle cx="120" cy="80" r="10" fill="#0d7d74"/>
<circle cx="300" cy="80" r="11" fill="#a3303a"/>
<circle cx="480" cy="80" r="10" fill="#0d7d74"/>
<circle cx="650" cy="80" r="10" fill="#0d7d74"/>
</g>
<g stroke="#a3303a" stroke-width="1.3" opacity="0.8">
<line x1="300" y1="80" x2="180" y2="40"/><line x1="300" y1="80" x2="180" y2="120"/>
<line x1="300" y1="80" x2="430" y2="40"/><line x1="300" y1="80" x2="430" y2="120"/>
<line x1="300" y1="80" x2="300" y2="20"/><line x1="300" y1="80" x2="300" y2="140"/>
<line x1="300" y1="80" x2="210" y2="80"/><line x1="300" y1="80" x2="400" y2="80"/></g>
<text x="300" y="165" text-anchor="middle" font-size="12" fill="#a3303a" font-weight="600">fragmentation sprays debris</text>
<line x1="300" y1="190" x2="480" y2="190" stroke="#16243a" stroke-width="1" marker-start="url(#arF)" marker-end="url(#arF)"/>
<defs><marker id="arF" markerWidth="8" markerHeight="8" refX="4" refY="3" orient="auto">
<path d="M6,0 L0,3 L6,6 Z" fill="#16243a"/></marker></defs>
<text x="390" y="183" text-anchor="middle" font-size="12" fill="#16243a">spacing d</text>
<text x="360" y="232" text-anchor="middle" font-size="13" fill="#26313f">neighbour-hit probability grows as 1 / d²</text>
<text x="360" y="254" text-anchor="middle" font-size="12.5" fill="#0d7d74">links want d ≈ 150 m</text>
<text x="360" y="274" text-anchor="middle" font-size="12.5" fill="#a3303a">debris safety wants d ≈ 1 km</text>
""", 720, 290),
 "The formation paradox. When one satellite fragments it sprays debris into the volume its neighbours occupy, "
 "and the chance of striking a neighbour grows as the inverse square of the spacing. The links need the "
 "satellites about a hundred and fifty metres apart; debris safety wants them a kilometre apart. Both cannot "
 "hold at once, and this is the binding, unsolved constraint.")


# 6. Optical link: beam divergence
LINK = (_svg("""
<rect x="20" y="92" width="34" height="46" rx="4" fill="#16243a"/>
<text x="37" y="160" text-anchor="middle" font-size="11.5" fill="#26313f">transmitter</text>
<path d="M54,108 L640,60 L640,170 L54,122 Z" fill="#0d7d74" opacity="0.16"/>
<line x1="54" y1="115" x2="640" y2="115" stroke="#0d7d74" stroke-width="1" stroke-dasharray="3 3"/>
<rect x="640" y="96" width="22" height="40" rx="3" fill="#16243a"/>
<text x="651" y="158" text-anchor="middle" font-size="11.5" fill="#26313f">receiver</text>
<line x1="54" y1="200" x2="640" y2="200" stroke="#16243a" stroke-width="1" marker-start="url(#arL)" marker-end="url(#arL)"/>
<defs><marker id="arL" markerWidth="8" markerHeight="8" refX="4" refY="3" orient="auto">
<path d="M6,0 L0,3 L6,6 Z" fill="#16243a"/></marker></defs>
<text x="347" y="193" text-anchor="middle" font-size="12.5" fill="#16243a">range R</text>
<text x="360" y="40" text-anchor="middle" font-size="12.5" fill="#0d7d74">beam spreads with divergence θ</text>
<text x="347" y="228" text-anchor="middle" font-size="13" fill="#26313f">captured fraction falls as 1 / R² → satellites must fly close</text>
""", 720, 250),
 "Why the cluster is tight. A laser beam spreads as it travels, so the fraction of light captured by the "
 "receiver falls as the inverse square of range. To carry the many-terabit aggregate with terminals that "
 "exist today, the satellites must fly within roughly a hundred and fifty metres of one another.")


# 7. Coarse body pointing plus fine-steering mirror
POINTING = (_svg("""
<defs><marker id="arP" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
<path d="M0,0 L7,3 L0,6 Z" fill="#0d7d74"/></marker></defs>
<rect x="40" y="70" width="120" height="90" rx="8" fill="#eef2f5" stroke="#16243a" stroke-width="1.3"/>
<text x="100" y="120" text-anchor="middle" font-size="12.5" fill="#16243a">spacecraft</text>
<text x="100" y="138" text-anchor="middle" font-size="11" fill="#5c6b7a">body: ~10 µrad</text>
<line x1="160" y1="115" x2="250" y2="115" stroke="#0d7d74" stroke-width="2"/>
<rect x="250" y="100" width="14" height="30" rx="2" fill="#0d7d74" transform="rotate(30 257 115)"/>
<text x="257" y="160" text-anchor="middle" font-size="11" fill="#0d7d74">fast-steering</text>
<text x="257" y="175" text-anchor="middle" font-size="11" fill="#0d7d74">mirror: &lt;1 µrad</text>
<line x1="262" y1="110" x2="560" y2="60" stroke="#0d7d74" stroke-width="2" marker-end="url(#arP)"/>
<circle cx="580" cy="56" r="8" fill="#16243a"/>
<text x="580" y="40" text-anchor="middle" font-size="11.5" fill="#26313f">target satellite</text>
""", 660, 210),
 "Coarse and fine pointing. The spacecraft body can be held to about ten microradians, but the link needs "
 "better than one. A small fast-steering mirror makes the fine correction independently of the bus; without "
 "it the beam cannot stay on the receiver.")


# 8. Technology-readiness ladder
def _trl():
    steps = "".join(
        f'<rect x="{60+(i)*64}" y="{300-(i+1)*28}" width="64" height="{(i+1)*28}" '
        f'fill="#f1f5f9" stroke="#cdd5dd" stroke-width="1"/>'
        f'<text x="{92+i*64}" y="294" text-anchor="middle" font-size="11" fill="#5c6b7a">{i+1}</text>'
        for i in range(9))
    pins = [
        (2, "autonomous debris\navoidance", "#a3303a"),
        (3, "close-formation\nflight", "#a3303a"),
        (4, "formation link\n(bench only)", "#c75c2e"),
        (5, "rad-tested processor /\nkW thermal", "#0d7d74"),
        (6, "accelerator\nin orbit", "#0d7d74"),
    ]
    marks = ""
    for trl, label, col in pins:
        x = 92 + (trl - 1) * 64
        y = 300 - trl * 28 - 8
        marks += f'<circle cx="{x}" cy="{y}" r="6" fill="{col}"/>'
        lines = label.split("\n")
        ly = y - 10 - (len(lines) - 1) * 13
        for ln in lines:
            marks += (f'<text x="{x}" y="{ly}" text-anchor="middle" font-size="10.5" '
                      f'fill="{col}">{ln}</text>')
            ly += 13
    legend = ('<text x="60" y="24" font-size="12.5" fill="#0d7d74">components: TRL 4–6</text>'
              '<text x="240" y="24" font-size="12.5" fill="#a3303a">system integration: TRL 2–3</text>')
    return _svg(steps + marks + legend
                + '<text x="320" y="332" text-anchor="middle" font-size="12.5" fill="#26313f">'
                  'technology-readiness level (1 = principle, 9 = flight-proven)</text>', 660, 345)


TRL = (_trl(),
 "Technology readiness. The building blocks sit in the middle of the ladder; everything that depends on the "
 "constellation operating as one coordinated system, the formation link, close-formation flight, and "
 "autonomous debris avoidance, sits near the bottom. That gap is the whole programme risk.")


DIAGRAMS = {"orbit": ORBIT, "thermal": THERMAL, "hohmann": HOHMANN, "shield": SHIELD,
            "formation": FORMATION, "link": LINK, "pointing": POINTING, "trl": TRL}
