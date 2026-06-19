"""Render the cover photo for the article: the 'Cover 2' render with the Part II title overlaid.

Continues the first report's title ("Space-Based Data Center Infrastructure: A Multi-Physics
Approach") as Part II. A dark bottom gradient scrim gives the title contrast over the bright
Earth. Output: summary/Cover_Part_II.png
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "Cover 2.png"
OUT = pathlib.Path(__file__).resolve().parent / "Cover_Part_II.png"
F = "C:/Windows/Fonts/"

TEAL = (94, 234, 212, 255)
WHITE = (255, 255, 255, 255)
SOFT = (222, 230, 238, 255)

im = Image.open(SRC).convert("RGBA")
W, H = im.size

# --- dark gradient scrim rising from the bottom ---
scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(scrim)
top = int(H * 0.48)
for y in range(top, H):
    t = (y - top) / (H - top)
    a = int(225 * (t ** 1.45))
    sd.line([(0, y), (W, y)], fill=(7, 12, 22, a))
im = Image.alpha_composite(im, scrim)

draw = ImageDraw.Draw(im)
title_f = ImageFont.truetype(F + "segoeuib.ttf", 112)
sub_f = ImageFont.truetype(F + "seguisb.ttf", 58)
part_f = ImageFont.truetype(F + "segoeuib.ttf", 50)
kick_f = ImageFont.truetype(F + "segoeui.ttf", 34)
auth_f = ImageFont.truetype(F + "segoeui.ttf", 34)
cx = W // 2


def tracked(y, text, font, fill, tracking):
    """Draw letter-spaced text centred on cx at vertical centre y."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    asc, desc = font.getmetrics()
    ty = y - (asc + desc) / 2
    for ch, w in zip(text, widths):
        draw.text((x, ty), ch, font=font, fill=fill)
        x += w + tracking


# kicker
tracked(int(H * 0.610), "PART II", part_f, TEAL, 16)
tracked(int(H * 0.672), "ENGINEERING STUDY  ·  2026", kick_f, (165, 205, 215, 255), 6)
# title (soft shadow then white)
draw.text((cx + 2, int(H * 0.755) + 3), "Space-Based Data Center Infrastructure",
          font=title_f, fill=(0, 0, 0, 150), anchor="mm")
draw.text((cx, int(H * 0.755)), "Space-Based Data Center Infrastructure",
          font=title_f, fill=WHITE, anchor="mm")
# subtitle
draw.text((cx, int(H * 0.845)), "A Multi-Physics Approach", font=sub_f, fill=SOFT, anchor="mm")
# divider + author
draw.line([(cx - 150, int(H * 0.900)), (cx + 150, int(H * 0.900))], fill=TEAL, width=3)
draw.text((cx, int(H * 0.945)), "Samarjith Biswas, PhD", font=auth_f, fill=SOFT, anchor="mm")

im.convert("RGB").save(OUT, "PNG")
print(f"wrote {OUT.name}  ({im.size[0]}x{im.size[1]})")
