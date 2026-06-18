"""Build Master_Report.html: self-contained (figures base64-embedded) + MathJax (active math).
Currency '$' is protected; math uses \\( \\) / \\[ \\] so nothing collides or breaks."""
import re, base64, pathlib, markdown

ROOT = pathlib.Path(__file__).resolve().parent
md = (ROOT / "Master_Report.md").read_text(encoding="utf-8")

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
body{font-family:'Georgia','Times New Roman',serif;color:#1c1c1c;line-height:1.7;max-width:920px;
 margin:0 auto;padding:54px 44px 100px;background:#fff;}
h1{font-family:'Helvetica Neue',Arial,sans-serif;font-size:28px;color:var(--ink);margin:0 0 4px;line-height:1.2;}
h1+h2{margin-top:14px;border:none;color:var(--accent);font-size:17px;font-weight:600;}
h2{font-family:'Helvetica Neue',Arial,sans-serif;font-size:21px;color:var(--ink);margin-top:42px;
 padding-bottom:6px;border-bottom:2px solid var(--accent);}
h3{font-family:'Helvetica Neue',Arial,sans-serif;font-size:15px;color:var(--cool);margin-top:22px;}
p,li{font-size:15px;} strong{color:var(--ink);}
hr{border:none;border-top:1px solid var(--rule);margin:30px 0;}
img{max-width:100%;display:block;margin:18px auto 6px;border:1px solid var(--rule);border-radius:4px;
 box-shadow:0 1px 6px rgba(0,0,0,.07);}
em{color:#555;font-size:13px;}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:13px;font-family:'Helvetica Neue',Arial,sans-serif;}
th{background:var(--ink);color:#fff;text-align:left;padding:7px 10px;}
td{padding:6px 10px;border-bottom:1px solid var(--rule);vertical-align:top;}
tr:nth-child(even) td{background:var(--soft);}
code{background:#f3f0ec;padding:1px 5px;border-radius:3px;font-size:13px;font-family:Consolas,monospace;}
blockquote{border-left:4px solid var(--accent);margin:18px 0;padding:6px 18px;background:var(--soft);color:#333;}
mjx-container{overflow-x:auto;overflow-y:hidden;}
.masthead{border-top:6px solid var(--accent);padding-top:14px;margin-bottom:8px;
 font-family:'Helvetica Neue',Arial,sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#888;}
@media print{body{padding:0 8px;max-width:none;} h2{page-break-after:avoid;} img,table{page-break-inside:avoid;}}"""

html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Space-Based AI Data Centers - A Complete Engineering Study</title>
<style>{CSS}</style>
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']],displayMath:[['\\\\[','\\\\]']],tags:'none'}},svg:{{fontCache:'global'}}}};</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
</head><body>
<div class="masthead">Complete Engineering Study &middot; Physics + Simulations + Predictions &middot; June 2026</div>
{body}
</body></html>"""

out = ROOT / "Master_Report.html"; out.write_text(html, encoding="utf-8")
print("Wrote", out.name, f"({out.stat().st_size/1024:.0f} KB)")
print("embedded images:", html.count("data:image/png;base64,"),
      "| display eqns:", body.count('\\['), "| inline eqns:", body.count('\\('),
      "| leftover tokens:", body.count('@@'), "| leftover figure refs:", body.count('figures/'))
