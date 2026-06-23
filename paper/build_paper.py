"""Build the condensed manuscript and front-matter docs to Word and HTML via pandoc.
Outputs: Space_DataCenter_Paper.docx/.html, cover_letter.docx, DISCLOSURE.html (for submission)."""
import pathlib, pypandoc

HERE = pathlib.Path(__file__).resolve().parent
jobs = [
    ("Space_DataCenter_Paper.md", "Space_DataCenter_Paper.docx", "docx", ["--toc", "--toc-depth=1"]),
    ("Space_DataCenter_Paper.md", "Space_DataCenter_Paper.html", "html", ["--standalone", "--mathjax"]),
    ("cover_letter.md", "cover_letter.docx", "docx", []),
    ("DISCLOSURE.md", "DISCLOSURE.html", "html", ["--standalone"]),
]
for src, out, fmt, extra in jobs:
    pypandoc.convert_file(str(HERE / src), fmt, outputfile=str(HERE / out), extra_args=extra)
    print("wrote", out)

words = len(" ".join((HERE / "Space_DataCenter_Paper.md").read_text(encoding="utf-8").split()).split())
print(f"paper body ~{words} words")
