"""Render EVERY Markdown table in Report_II_Complete.md as a clean PNG (white + transparent),
matching the figure styling, so all tables can be dropped into LinkedIn as images.

Per-cell: math in $...$ is typeset with mathtext; plain cells get Unicode superscripts; literal
currency '$' is escaped; each cell is wrapped if long so nothing clips. Output: report/tables/.
"""
import re, pathlib
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle
import textwrap

mpl.rcParams["mathtext.fontset"] = "cm"
SRC = pathlib.Path("Report_II_Complete.md")
OUT = pathlib.Path("tables"); OUT.mkdir(exist_ok=True)
NAVY, SOFT, INK = "#16243a", "#f1efe9", "#1c1c1c"

_SUP = {"^3": "³", "^2": "²", "^4": "⁴", "^-2": "⁻²", "^-1": "⁻¹", "^-8": "⁻⁸",
        "^14": "¹⁴", "^-3": "⁻³", "^7": "⁷", "^6": "⁶", "^-6": "⁻⁶"}

def prep(cell, wrap):
    """Prepare a cell string for matplotlib and wrap long plain cells."""
    cell = cell.strip().replace("**", "")
    if "$" in cell:                              # math cell: clean unsupported macros
        cell = (cell.replace(r"\dfrac", r"\frac").replace(r"\tfrac", r"\frac")
                    .replace(r"\,", " ").replace(r"\!", "").replace(r"\;", " "))
        cell = re.sub(r"\\boxed\{(.+?)\}", r"\1", cell)
        if cell.count("$") % 2:                  # stray currency $: make literal
            cell = cell.replace("$", r"\$")
        return cell, False
    # plain cell
    for k, v in _SUP.items():
        cell = cell.replace(k, v)
    cell = cell.replace("$", r"\$")
    if wrap and len(cell) > wrap:
        cell = "\n".join(textwrap.wrap(cell, wrap)) or cell
    return cell, True

def plain_len(cell):
    c = re.sub(r"\\[a-zA-Z]+", "x", cell)
    c = re.sub(r"[$\\{}^_*]", "", c)
    return len(c.strip())

def find_tables(md):
    lines = md.splitlines()
    tables, i = [], 0
    last_head = "table"
    while i < len(lines):
        h = re.match(r"^#{1,3}\s+(.*)", lines[i])
        if h:
            last_head = h.group(1).strip()
        if "|" in lines[i] and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$", lines[i + 1]):
            header = lines[i]; j = i + 2; rows = []
            while j < len(lines) and "|" in lines[j] and lines[j].strip():
                rows.append(lines[j]); j += 1
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            tables.append((last_head, cells(header), [cells(r) for r in rows]))
            i = j
        else:
            i += 1
    return tables

def render(title, headers, rows, idx):
    ncol = len(headers)
    # wrap budget per column: wider for the widest (meaning/notes) columns
    col_chars = [max([plain_len(headers[c])] + [plain_len(r[c]) for r in rows if c < len(r)] + [3]) for c in range(ncol)]
    wrap_at = [min(cc, 44) for cc in col_chars]
    char_w = 0.115
    col_w = [max(wrap_at[c], 6) * char_w + 0.55 for c in range(ncol)]
    # prep cells (with wrapping) and compute row heights from line counts
    H = [[prep(headers[c], wrap_at[c]) for c in range(ncol)]]
    for r in rows:
        H.append([prep(r[c] if c < len(r) else "", wrap_at[c]) for c in range(ncol)])
    row_lines = [max(1, max(s.count("\n") + 1 for s, _ in row)) for row in H]
    yheights = [0.34 * rl + 0.16 for rl in row_lines]
    total_h = sum(yheights)
    total_w = sum(col_w)
    fig, ax = plt.subplots(figsize=(min(total_w, 17), max(total_h, 0.8)))
    ax.set_xlim(0, total_w); ax.set_ylim(0, total_h); ax.axis("off"); ax.invert_yaxis()
    xs = [sum(col_w[:c]) + 0.12 for c in range(ncol)]
    y = 0.0
    for ri, row in enumerate(H):
        rh = yheights[ri]
        if ri == 0:
            ax.add_patch(Rectangle((0, y), total_w, rh, facecolor=NAVY, ec="none"))
        elif ri % 2 == 0:
            ax.add_patch(Rectangle((0, y), total_w, rh, facecolor=SOFT, ec="none"))
        for c, (txt, _plain) in enumerate(row):
            color = "white" if ri == 0 else (NAVY if c == 0 else INK)
            fw = "bold" if ri == 0 else "normal"
            fs = 12 if ri == 0 else (13 if c == 0 and "$" in txt else 11.5)
            try:
                ax.text(xs[c], y + rh / 2, txt, color=color, fontsize=fs, fontweight=fw,
                        va="center", ha="left", clip_on=False)
            except Exception:
                ax.text(xs[c], y + rh / 2, re.sub(r"[$\\]", "", txt), color=color,
                        fontsize=fs, va="center", ha="left", clip_on=False)
        y += rh
    for k in range(len(H) + 1):
        yy = sum(yheights[:k])
        ax.plot([0, total_w], [yy, yy], color="#d9dde1", lw=0.6)
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower())[:40].strip("_")
    name = f"table_{idx:02d}_{slug}"
    try:
        fig.savefig(OUT / f"{name}.png", dpi=250, bbox_inches="tight", pad_inches=0.1, facecolor="white")
        fig.savefig(OUT / f"{name}_transparent.png", dpi=250, bbox_inches="tight", pad_inches=0.1, transparent=True)
    finally:
        plt.close(fig)
    return name, title

if __name__ == "__main__":
    md = SRC.read_text(encoding="utf-8")
    tabs = find_tables(md)
    index = []
    for i, (title, headers, rows) in enumerate(tabs, 1):
        if not rows:
            continue
        name, ttl = render(title, headers, rows, i)
        index.append(f"- `{name}.png` -- from section: {ttl} ({len(rows)} rows)")
    (OUT / "INDEX.md").write_text("# Table images\n\n" + "\n".join(index) + "\n",
                                  encoding="utf-8")
    print(f"rendered {len(index)} tables to {OUT}")
    for ln in index:
        print("  ", ln)
