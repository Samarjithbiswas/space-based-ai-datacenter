"""Build Report_II_Complete.html: book-length, self-contained (figures base64) + MathJax.
Currency '$' protected; math emitted as \\( \\) / \\[ \\]; print-friendly page breaks."""
import re, base64, pathlib, markdown

ROOT = pathlib.Path(__file__).resolve().parent
md = (ROOT / "Report_II_Complete.md").read_text(encoding="utf-8")

md = md.replace(r"\$", "@@CUR@@")
store = []
md = re.sub(r"\$\$(.+?)\$\$", lambda m: (store.append(("d", m.group(1))) or f"@@M{len(store)-1}@@"), md, flags=re.S)
md = re.sub(r"\$(.+?)\$",     lambda m: (store.append(("i", m.group(1))) or f"@@M{len(store)-1}@@"), md)

def embed(m):
    p = ROOT / m.group(2)
    if not p.exists(): return m.group(0)
    return f'![{m.group(1)}](data:image/png;base64,{base64.b64encode(p.read_bytes()).decode()})'
md = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', embed, md)

body = markdown.markdown(md, extensions=["tables", "sane_lists", "toc"])
body = re.sub(r"@@M(\d+)@@",
              lambda m: ("\\[" + store[int(m.group(1))][1] + "\\]") if store[int(m.group(1))][0] == "d"
              else ("\\(" + store[int(m.group(1))][1] + "\\)"), body)
body = body.replace("@@CUR@@", "$")

CSS = """:root{--ink:#16243a;--accent:#c75c2e;--cool:#2f6f8f;--rule:#e2e2e2;--soft:#fbf7f3;}
body{font-family:'Georgia','Times New Roman',serif;color:#1c1c1c;line-height:1.7;max-width:880px;
 margin:0 auto;padding:54px 48px 110px;background:#fff;}
h1{font-family:'Helvetica Neue',Arial,sans-serif;font-size:25px;color:var(--ink);margin:34px 0 6px;
 line-height:1.25;border-top:3px solid var(--accent);padding-top:22px;}
h1:first-of-type{border-top:none;font-size:30px;padding-top:0;}
h2{font-family:'Helvetica Neue',Arial,sans-serif;font-size:19px;color:var(--ink);margin-top:34px;
 padding-bottom:5px;border-bottom:1.5px solid var(--accent);}
h3{font-family:'Helvetica Neue',Arial,sans-serif;font-size:15px;color:var(--cool);margin-top:20px;}
p,li{font-size:14.5px;text-align:justify;} strong{color:var(--ink);}
hr{border:none;border-top:1px solid var(--rule);margin:26px 0;}
img{max-width:92%;display:block;margin:18px auto 6px;border:1px solid var(--rule);border-radius:4px;
 box-shadow:0 1px 6px rgba(0,0,0,.07);}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:12.5px;
 font-family:'Helvetica Neue',Arial,sans-serif;}
th{background:var(--ink);color:#fff;text-align:left;padding:6px 9px;}
td{padding:5px 9px;border-bottom:1px solid var(--rule);vertical-align:top;}
tr:nth-child(even) td{background:var(--soft);}
code{background:#f3f0ec;padding:1px 5px;border-radius:3px;font-size:12.5px;font-family:Consolas,monospace;}
blockquote{border-left:4px solid var(--accent);margin:18px 0;padding:6px 18px;background:var(--soft);}
mjx-container{overflow-x:auto;overflow-y:hidden;}
.masthead{font-family:'Helvetica Neue',Arial,sans-serif;font-size:11px;letter-spacing:2px;
 text-transform:uppercase;color:#999;margin-bottom:6px;}
@media print{
 body{padding:0 4px;max-width:none;font-size:11pt;line-height:1.55;}
 h1{page-break-before:always;border-top:none;} h1:first-of-type{page-break-before:avoid;}
 h2{page-break-before:always;page-break-after:avoid;}   /* each chapter starts a new page (book layout) */
 img,table,blockquote,pre{page-break-inside:avoid;}
 img{max-width:86%;}
}"""

html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Space-Based AI Data Centers - A Complete Engineering Treatise</title>
<style>{CSS}</style>
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']],displayMath:[['\\\\[','\\\\]']],tags:'none'}},svg:{{fontCache:'global'}}}};</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
</head><body>
<div class="masthead">Report II &middot; Complete Edition &middot; Book-length systems treatise &middot; June 2026</div>
{body}
</body></html>"""

out = ROOT / "Report_II_Complete.html"; out.write_text(html, encoding="utf-8")
words = len(re.sub(r"<[^>]+>", " ", body).split())
print("Wrote", out.name, f"({out.stat().st_size/1024:.0f} KB)")
print("words:", words, "| images:", html.count("data:image/png;base64,"),
      "| display eqns:", body.count('\\['), "| inline eqns:", body.count('\\('),
      "| leftover:", body.count('@@'), body.count('figures/'))
chapters = body.count('<h2')
pages = round(words/480 + html.count('data:image')*0.45 + body.count('<table')*0.45
              + body.count('<h2')*0.45 + body.count('<h1')*0.6)
print(f"chapters(h2)={chapters}, tables={body.count('<table')}")
print("est. printed pages (book layout, chapter-per-page):", pages)
