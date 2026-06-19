"""Rasterize the inline-SVG diagrams to PNG using the headless browser's canvas.

Serves a page that holds every diagram SVG plus a script that draws each onto a 2x canvas
and POSTs the PNG back here; this handler writes them to summary/post_figures/. Run in the
background, then load http://localhost:8775/ in the preview browser.
"""
import sys, pathlib, http.server, socketserver

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diagrams

OUT = HERE / "post_figures"
OUT.mkdir(exist_ok=True)
PORT = 8775

svgs = ""
for name, (svg, cap) in diagrams.DIAGRAMS.items():
    tagged = svg.replace("<svg ", f'<svg data-name="{name}" ', 1)
    svgs += f'<div style="margin:8px">{tagged}</div>\n'

PAGE = f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>
<p id="status">working...</p>
{svgs}
<script>
async function run(){{
  const figs = [...document.querySelectorAll('svg[data-name]')];
  for (const svg of figs) {{
    const name = svg.getAttribute('data-name');
    const vb = svg.viewBox.baseVal, s = 2;
    const clone = svg.cloneNode(true);
    clone.setAttribute('width', vb.width*s); clone.setAttribute('height', vb.height*s);
    const xml = new XMLSerializer().serializeToString(clone);
    const url = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(xml);
    const img = new Image();
    await new Promise((res, rej) => {{ img.onload = res; img.onerror = rej; img.src = url; }});
    const c = document.createElement('canvas'); c.width = vb.width*s; c.height = vb.height*s;
    const ctx = c.getContext('2d'); ctx.fillStyle = '#ffffff'; ctx.fillRect(0,0,c.width,c.height);
    ctx.drawImage(img, 0, 0, c.width, c.height);
    const blob = await new Promise(r => c.toBlob(r, 'image/png'));
    await fetch('/save/' + name, {{ method: 'POST', body: blob }});
    document.getElementById('status').textContent = 'saved ' + name;
  }}
  document.getElementById('status').textContent = 'DONE';
}}
run();
</script></body></html>"""


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(PAGE.encode("utf-8"))

    def do_POST(self):
        name = self.path.rsplit("/", 1)[-1]
        n = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(n)
        (OUT / f"diagram_{name}.png").write_bytes(data)
        print("saved", name, len(data), "bytes", flush=True)
        self.send_response(200)
        self.end_headers()


with socketserver.TCPServer(("127.0.0.1", PORT), H) as srv:
    print(f"export server on {PORT}", flush=True)
    srv.serve_forever()
