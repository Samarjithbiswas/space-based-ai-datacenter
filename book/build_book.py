r"""Build the Overleaf-ready LaTeX book from report/Report_II_Complete.md.

The book is a BUILD TARGET, not a hand-maintained file: every time the report
grows (the loop keeps expanding it), re-running this regenerates a longer book
with all the new equations, derivations, tables, and figures.

Pipeline:
  1. Preprocess the Markdown:
       - drop the title/subtitle headings (they live on the cover page),
       - turn "# PART I, X" into "# X" so LaTeX prints "Part I" + X cleanly,
       - protect the few literal currency '$' from the math parser,
       - convert tagged display math  $$ ... \tag{n} $$  into a real
         equation environment (\tag is illegal inside pandoc's \[ ... \]).
  2. Run pandoc as a standalone BOOK, injecting the house-style preamble and
     the cover page, with a table of contents and listings for code.
  3. Copy every referenced figure directory into the bundle and zip it.

Requires: pandoc (via pypandoc). No local LaTeX engine needed; the output is
an Overleaf-ready bundle (compile with pdfLaTeX), exactly like the other books
in the series.
"""
import re, shutil, zipfile, pathlib, subprocess, sys
import pypandoc

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
SRC = REPO / "report" / "Report_II_Complete.md"
FIG_DIRS = ["figures", "figures2", "figures_pred", "systems_figs", "schematics"]
OUT_TEX = HERE / "main.tex"


def preprocess(md: str) -> str:
    lines = md.splitlines()

    # 1. Drop the leading title block: the first two level-1 headings are the
    #    document title and subtitle, shown on the cover instead.
    out, dropped = [], 0
    for ln in lines:
        if dropped < 2 and re.match(r"^# \S", ln) and "PART" not in ln:
            dropped += 1
            continue
        out.append(ln)
    md = "\n".join(out)

    # 2. "# PART I, INTRODUCTION AND CONTEXT" -> "# INTRODUCTION AND CONTEXT"
    md = re.sub(r"(?m)^# PART\s+[IVXLC]+,\s*", "# ", md)
    md = re.sub(r"(?m)^# Back matter\s*$", "# Appendices and Back Matter", md)

    # 3. Protect literal currency '$' (same fixes the .docx build uses).
    md = (md.replace("LCOE ($/PFLOP-hr)", "LCOE (USD/PFLOP-hr)")
            .replace("$/kg launch", "USD/kg launch")
            .replace(" $ |", " USD |"))

    # 4. Convert tagged display math to an equation (or align) environment so
    #    \tag is legal. Untagged $$...$$ is left for pandoc to render as \[..\].
    def conv(m):
        body = m.group(1).strip()
        if r"\tag" not in body:
            return m.group(0)               # leave untagged display math alone
        env = "align" if r"\\" in body else "equation"
        return f"\n\\begin{{{env}}}\n{body}\n\\end{{{env}}}\n"

    md = re.sub(r"\$\$(.*?)\$\$", conv, md, flags=re.S)

    # parity sanity check on remaining inline '$'
    lone = md.count("$")
    if lone % 2:
        print(f"  WARNING: odd number of inline '$' remains ({lone}); a literal "
              "currency '$' may still break math. Search the .tex if compile fails.")
    return md


def build():
    md = preprocess(SRC.read_text(encoding="utf-8"))
    tmp = HERE / "_book_src.md"
    tmp.write_text(md, encoding="utf-8")

    extra = [
        "--standalone",
        "--top-level-division=part",
        "--listings",
        "--resource-path=" + str(REPO / "report"),
        f"--include-in-header={HERE/'preamble.tex'}",
        f"--include-before-body={HERE/'cover.tex'}",
        f"--include-after-body={HERE/'about_author.tex'}",
        "-V", "documentclass=book",
        "-V", "classoption=11pt",
        "-V", "classoption=openany",
        "-V", "classoption=oneside",
        "-V", "geometry=margin=2.2cm,top=2.4cm,bottom=2.4cm",
        "-V", "linkcolor=brandTealDk",
        # No title/author metadata on purpose: the cover page is the title, and
        # supplying title metadata would make pandoc emit a second \maketitle.
        # PDF document properties are set via \hypersetup in preamble.tex.
    ]
    pypandoc.convert_file(str(tmp), "latex", outputfile=str(OUT_TEX), extra_args=extra)
    tmp.unlink()

    # Copy figure directories into the bundle so paths resolve on Overleaf.
    for d in FIG_DIRS:
        src = REPO / "report" / d
        if src.exists():
            shutil.copytree(src, HERE / d, dirs_exist_ok=True)

    # Quick report
    tex = OUT_TEX.read_text(encoding="utf-8")
    print(f"wrote {OUT_TEX.name}: {len(tex.splitlines())} lines, "
          f"{tex.count('begin{equation}')+tex.count('begin{align}')} numbered equations, "
          f"{tex.count('includegraphics')} figures, "
          f"{tex.count('chapter{')} chapters, {tex.count('part{')} parts")

    # Zip an Overleaf-ready bundle.
    zip_path = REPO / "book" / "Space_Data_Center_Book_Overleaf.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(OUT_TEX, "main.tex")
        z.write(HERE / "preamble.tex", "preamble.tex")
        z.write(HERE / "cover.tex", "cover.tex")
        z.write(HERE / "about_author.tex", "about_author.tex")
        z.write(HERE / "cover_art.png", "cover_art.png")
        for d in FIG_DIRS:
            for f in (HERE / d).rglob("*"):
                if f.is_file():
                    z.write(f, str(f.relative_to(HERE)))
    print(f"wrote bundle {zip_path.name} ({zip_path.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    build()
