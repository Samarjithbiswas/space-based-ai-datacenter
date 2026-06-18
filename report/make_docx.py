"""Convert Report_II_Complete.md to a real Microsoft Word .docx with NATIVE, editable
Word equations (OMML), Word tables, and embedded figures, via Pandoc.

Fixes the three genuine currency '$' (which would otherwise be parsed as math), then
runs pandoc with a table of contents. Run from the report/ directory so the figure
paths (figures/, systems_figs/, figures_pred/) resolve and embed."""
import re, pathlib, pypandoc

SRC = pathlib.Path("Report_II_Complete.md")
t = SRC.read_text(encoding="utf-8")

# --- protect genuine currency '$' from the math parser ---
t = t.replace("LCOE ($/PFLOP-hr)", "LCOE (USD/PFLOP-hr)")
t = t.replace("$/kg launch", "USD/kg launch")
t = t.replace(" $ |", " USD |")          # lone NPV-units cell in the nomenclature table

tmp = pathlib.Path("_report_docx_src.md")
tmp.write_text(t, encoding="utf-8")

# parity check (single '$' minus 2x display pairs should now be even)
single = t.count("$") - 2 * t.count("$$")
print("inline '$' after fix:", single, "(even ->", single % 2 == 0, ")")

pypandoc.convert_file(
    str(tmp), "docx", outputfile="Report_II_Complete.docx",
    extra_args=["--toc", "--toc-depth=2", "--resource-path=.",
                "--metadata=title:Space-Based AI Data Centers — A Complete Engineering Treatise",
                "--metadata=author:Samarjith Biswas, PhD"],
)
tmp.unlink()
out = pathlib.Path("Report_II_Complete.docx")
print("wrote", out, f"({out.stat().st_size/1024:.0f} KB)")
