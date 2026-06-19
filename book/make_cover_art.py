"""Render a professional A4 portrait cover for the book: the orbital render set in a navy
field, with the series title typeset over it. Output: book/cover_art.png (2480x3508, A4@300dpi).
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "Cover 2.png"
OUT = pathlib.Path(__file__).resolve().parent / "cover_art.png"
F = "C:/Windows/Fonts/"

NAVY = (11, 19, 32)
TEAL = (45, 212, 191)
TEAL_SOFT = (94, 234, 212)
WHITE = (255, 255, 255)
SOFT = (203, 213, 225)
MUTE = (148, 163, 184)

W, H = 2480, 3508
cv = Image.new("RGB", (W, H), NAVY)

# --- orbital render as a soft-edged band in the upper-middle ---
photo = Image.open(SRC).convert("RGB")
pw = W
ph = int(photo.height * pw / photo.width)
photo = photo.resize((pw, ph), Image.LANCZOS)
y0 = 760
mask = Image.new("L", (pw, ph), 255)
md = ImageDraw.Draw(mask)
fade = 200
for i in range(fade):
    a = int(255 * i / fade)
    md.line([(0, i), (pw, i)], fill=a)
    md.line([(0, ph - 1 - i), (pw, ph - 1 - i)], fill=a)
cv.paste(photo, (0, y0), mask)

d = ImageDraw.Draw(cv)
title1_f = ImageFont.truetype(F + "segoeuib.ttf", 150)
title2_f = ImageFont.truetype(F + "segoeuib.ttf", 150)
sub_f = ImageFont.truetype(F + "seguisb.ttf", 74)
badge_f = ImageFont.truetype(F + "segoeuib.ttf", 46)
small_f = ImageFont.truetype(F + "segoeui.ttf", 46)
auth_f = ImageFont.truetype(F + "segoeuib.ttf", 58)
cx = W // 2


def tracked(y, text, font, fill, tracking, anchor_mm=True):
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    asc, desc = font.getmetrics()
    ty = y - (asc + desc) / 2
    for ch, w in zip(text, widths):
        d.text((x, ty), ch, font=font, fill=fill)
        x += w + tracking


# --- top badge ---
tracked(360, "EDITION I", badge_f, TEAL_SOFT, 18)
tracked(430, "A COMPLETE ENGINEERING STUDY", small_f, MUTE, 10)
d.line([(cx - 150, 500), (cx + 150, 500)], fill=TEAL, width=4)

# --- title (below the render) ---
ty = 2230
d.text((cx, ty), "Space-Based Data Center", font=title1_f, fill=WHITE, anchor="mm")
d.text((cx, ty + 168), "Infrastructure", font=title2_f, fill=WHITE, anchor="mm")
d.text((cx, ty + 320), "A Multi-Physics Approach", font=sub_f, fill=TEAL_SOFT, anchor="mm")

# --- description ---
desc = ["Orbital mechanics, thermal control, radiation, debris, links, power,",
        "propulsion, reliability, compute, and economics, from first principles",
        "to numbers, with an open and reproducible simulation model."]
dy = 2820
for ln in desc:
    d.text((cx, dy), ln, font=small_f, fill=SOFT, anchor="mm")
    dy += 64

# --- author / footer ---
d.line([(cx - 170, 3180), (cx + 170, 3180)], fill=TEAL, width=4)
d.text((cx, 3270), "Samarjith Biswas, PhD", font=auth_f, fill=WHITE, anchor="mm")
d.text((cx, 3340), "Edition I  ·  2026", font=small_f, fill=MUTE, anchor="mm")

cv.save(OUT, "PNG")
print(f"wrote {OUT.name}  ({W}x{H})")
