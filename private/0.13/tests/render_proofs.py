#!/usr/bin/env python3
"""Exact font evaluation artifacts, not AI-generated text or outlines."""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont

PKG = Path(__file__).resolve().parent.parent
BEFORE = PKG / "evidence/baseline-v0.12/ShahjahanAsha-SourceGlyphSeed-0.12-private-test.ttf"
AFTER = PKG / "ShahjahanAsha-SourceGlyphSeed-0.13-private-test.ttf"
OUT = PKG / "proofs/hb"
OUT.mkdir(parents=True, exist_ok=True)
corpus = [s.strip() for s in (PKG / "tests/corpus.txt").read_text().splitlines()
          if s.strip() and not s.lstrip().startswith("#")]
first = "\n".join([corpus[i] for i in (0,1,2,3,6,7,14)])

def render(font, text, size, target):
    subprocess.run(["hb-view", "--font-funcs=ot", f"--font-size={size}",
                    "--margin=12", "--line-space=5", "--output-format=png",
                    f"--output-file={target}", str(font), text], check=True)

for size in (12,16,24,36,48):
    render(AFTER, "\n".join(corpus), size, OUT / f"corpus-{size}px.png")
for size in (16,48):
    a=OUT/f"before-firstchecks-{size}px.png"
    b=OUT/f"after-firstchecks-{size}px.png"
    render(BEFORE, first, size, a)
    render(AFTER, first, size, b)
    images=[Image.open(a).convert("RGB"),Image.open(b).convert("RGB")]
    # Reproducible evaluation labels only; the Bengali pixels come directly
    # from HarfBuzz rendering each actual font at the identical requested size.
    width=max(i.width for i in images)+24
    header=36
    canvas=Image.new("RGB",(width,sum(i.height for i in images)+header*2+24),"white")
    draw=ImageDraw.Draw(canvas)
    label=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
    y=8
    for text,image in zip((f"BEFORE — unchanged private 0.12 — {size} px",f"AFTER — private 0.13 engineering preview — {size} px"),images):
        draw.text((12,y),text,font=label,fill="#222222")
        y+=header
        canvas.paste(image,(12,y));y+=image.height
    canvas.save(PKG/f"proofs/before-after-{size}px.png")
print("Rendered complete corpus at 12/16/24/36/48 px and before/after proofs at 16/48 px")
