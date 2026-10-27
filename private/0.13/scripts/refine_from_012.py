#!/usr/bin/env python3
"""Create the private 0.13 candidate from the immutable 0.12 baseline.

All source-derived outlines are inherited from the owner's earlier samples. New
punctuation and the AU length mark are typographic constructions from those
owner-derived glyphs. No AdorshoLipi outlines/code or 3804/3805 exercise data is
used. The script writes only inside this versioned 0.13 package.
"""
from __future__ import annotations

import csv
import copy
import json
import re
import subprocess
import tempfile
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

PKG = Path(__file__).resolve().parents[1]
BASE = PKG / "evidence" / "baseline-v0.12" / "ShahjahanAsha-SourceGlyphSeed-0.12-private-test.ttf"
BASE_FEA = PKG / "evidence" / "baseline-v0.12" / "ShahjahanAsha-opentype-features-0.12.fea"
OUT_TTF = PKG / "ShahjahanAsha-SourceGlyphSeed-0.13-private-test.ttf"
OUT_SFD = PKG / "ShahjahanAsha-SourceGlyphSeed-0.13-private-test.sfd"
OUT_FEA = PKG / "ShahjahanAsha-opentype-features-0.13.fea"
ADJUSTMENTS = PKG / "GLYPH-ADJUSTMENTS-0.13.csv"

UPM = 1000
CORE_LSB = CORE_RSB = 90
PUNCT_LSB = PUNCT_RSB = 60
DIGIT_LSB = DIGIT_RSB = 70
DANDA_TOP = 600

# Paired independent vowels share optical tops. Their tiers are informed by
# the extreme positive-y-only resizes recorded in GLYPH-ADJUSTMENTS-0.12.csv.
VOWEL_PAIRS = {
    0x0985: 620, 0x0986: 620,  # অ / আ
    0x0987: 660, 0x0988: 660,  # ই / ঈ
    0x0989: 620, 0x098A: 620,  # উ / ঊ
    0x098F: 660, 0x0990: 660,  # এ / ঐ
    0x0993: 660, 0x0994: 660,  # ও / ঔ
    0x098B: 620,               # ঋ
}
# Small-shape consonants whose inherited 0.12 source tops were far below the
# 650-unit grid use the same restrained short-body tier as the short vowels.
SHORT_CONSONANTS = {0x099E, 0x09AA, 0x09B8}  # ঞ, প, স
# Pairwise optical width correction for the identified vowel-family outliers.
VOWEL_X_SCALE = {
    0x0989: 0.90, 0x098A: 1.05, 0x098B: 0.90,
    0x098F: 0.98, 0x0990: 1.06,
    0x0993: 0.98, 0x0994: 1.04,
}
CORE_BASES = [
    0x0985,0x0986,0x0987,0x0988,0x0989,0x098A,0x098B,0x098F,0x0990,0x0993,0x0994,
    0x0995,0x0996,0x0997,0x0998,0x0999,0x099A,0x099B,0x099C,0x099D,0x099E,
    0x099F,0x09A0,0x09A1,0x09A2,0x09A3,0x09A4,0x09A5,0x09A6,0x09A7,0x09A8,
    0x09AA,0x09AB,0x09AC,0x09AD,0x09AE,0x09AF,0x09B0,0x09B2,0x09B6,0x09B7,
    0x09B8,0x09B9,0x09DC,0x09DD,0x09DF,0x09CE,
]

rows: list[dict[str, object]] = []


def cmap_name(font: TTFont, cp: int) -> str:
    name = font.getBestCmap().get(cp)
    if not name:
        raise RuntimeError(f"Baseline is missing U+{cp:04X}")
    return name


def bounds(font: TTFont, name: str) -> tuple[int, int, int, int]:
    g = font["glyf"][name]
    g.recalcBounds(font["glyf"])
    return (int(g.xMin), int(g.yMin), int(g.xMax), int(g.yMax))


def set_coords(glyph, coords) -> None:
    glyph.coordinates = coords
    glyph.recalcBounds(None)


def transform_simple(font: TTFont, name: str, sx: float = 1.0, sy: float = 1.0,
                     target_xmin: int | None = None, target_ymin: int | None = None,
                     anchor_x: float | None = None, anchor_y: float | None = None) -> None:
    g = font["glyf"][name]
    if g.isComposite() or getattr(g, "numberOfContours", 0) <= 0:
        raise RuntimeError(f"Expected a simple source outline for {name}")
    g.recalcBounds(font["glyf"])
    ox0, oy0 = int(g.xMin), int(g.yMin)
    ax = ox0 if anchor_x is None else anchor_x
    ay = oy0 if anchor_y is None else anchor_y
    coords = g.coordinates.copy()
    for i, (x, y) in enumerate(coords):
        nx = ax + (int(x) - ax) * sx
        ny = ay + (int(y) - ay) * sy
        coords[i] = (round(nx), round(ny))
    if target_xmin is not None:
        shift_x = target_xmin - min(int(x) for x, _ in coords)
        coords = coords + (shift_x, 0)
    if target_ymin is not None:
        shift_y = target_ymin - min(int(y) for _, y in coords)
        coords = coords + (0, shift_y)
    set_coords(g, coords)


def adjust_advance(font: TTFont, name: str, left: int, right: int) -> None:
    g = font["glyf"][name]
    g.recalcBounds(font["glyf"])
    width = int(g.xMax - g.xMin)
    font["hmtx"].metrics[name] = (width + left + right, left)


def refine_source_strokes(font: TTFont) -> None:
    """Controlled local weight changes; preserve all other baseline outlines."""
    weights={cmap_name(font,cp):6 for cp in (0x0987,0x0988,0x0989,0x098A,0x098F,0x0990,0x0993,0x0994)}
    weights.update({cmap_name(font,cp):12 for cp in range(0x09E6,0x09F0)})
    code=("import fontforge,sys,json; f=fontforge.open(sys.argv[1]); "
          "weights=json.loads(sys.argv[3]); "
          "[(f[n].changeWeight(w),f[n].correctDirection(),f[n].round()) for n,w in weights.items()]; "
          "f.generate(sys.argv[2]); f.close()")
    with tempfile.TemporaryDirectory(prefix="asha-owner-weight-") as tmp:
        target=Path(tmp)/"weighted.ttf"
        subprocess.run(["/usr/bin/python3","-c",code,str(BASE),str(target),json.dumps(weights)],check=True,
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        weighted=TTFont(target)
        for n,w in weights.items():
            old=bounds(font,n); adv=font["hmtx"][n][0]
            font["glyf"][n]=copy.deepcopy(weighted["glyf"][n])
            rows.append({"codepoint":"U+"+n[3:],"glyph":n,"group":"controlled stroke refinement",
                         "old_bounds":old,"new_bounds":bounds(font,n),"old_advance":adv,
                         "new_advance":adv,"rule":f"FontForge changeWeight +{w} units; owner contours only; counters retained for inspection"})
        weighted.close()


def transform_body(font: TTFont, cp: int, top: int, lsb: int,
                   xscale: float = 1.0, reason: str = "") -> None:
    name = cmap_name(font, cp)
    old = bounds(font, name)
    old_adv = font["hmtx"].metrics[name][0]
    # Scale around the source left edge, then return to the shared bearing grid.
    transform_simple(font, name, sx=xscale, sy=top / max(1, old[3]), target_xmin=lsb,
                     target_ymin=old[1], anchor_x=old[0], anchor_y=0)
    new = bounds(font, name)
    adjust_advance(font, name, lsb, CORE_RSB)
    rows.append({"codepoint":f"U+{cp:04X}","glyph":name,"group":"core optical grid",
                 "old_bounds":old,"new_bounds":new,"old_advance":old_adv,
                 "new_advance":font["hmtx"].metrics[name][0],"rule":reason or f"optical top {top}; {xscale:.3f}x optical width; {lsb}/{CORE_RSB} bearings"})


def outline_from_parts(font: TTFont, target_name: str, parts: list[tuple[str, tuple[float,float,float,float,float,float]]]):
    glyphset = font.getGlyphSet()
    pen = TTGlyphPen(glyphset)
    for source, matrix in parts:
        glyphset[source].draw(TransformPen(pen, matrix))
    return pen.glyph()


def add_glyph(font: TTFont, cp: int, name: str, parts, left: int, right: int,
              reason: str) -> None:
    if name in font.getGlyphOrder() or cp in font.getBestCmap():
        raise RuntimeError(f"Refusing to overwrite existing mapping or glyph {name}/U+{cp:04X}")
    new_outline = outline_from_parts(font, name, parts)
    order = list(font.getGlyphOrder())
    order.append(name)
    font.setGlyphOrder(order)
    glyf = font["glyf"]
    glyf[name] = new_outline
    glyf.glyphOrder = order
    g = glyf[name]
    g.recalcBounds(glyf)
    font["hmtx"].metrics[name] = (int(g.xMax - g.xMin) + left + right, left)
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap[cp] = name
    rows.append({"codepoint":f"U+{cp:04X}","glyph":name,"group":"new derived outline",
                 "old_bounds":"—","new_bounds":bounds(font,name),"old_advance":"—",
                 "new_advance":font["hmtx"].metrics[name][0],"rule":reason})


def normalize_punctuation(font: TTFont, cp: int, target_top: int | None = None) -> None:
    name = cmap_name(font, cp)
    old = bounds(font, name)
    old_adv = font["hmtx"].metrics[name][0]
    if target_top and old[3] > 0:
        transform_simple(font, name, sy=target_top / old[3], target_xmin=PUNCT_LSB,
                         target_ymin=old[1], anchor_x=old[0], anchor_y=0)
    else:
        transform_simple(font, name, target_xmin=PUNCT_LSB, target_ymin=old[1],
                         anchor_x=old[0], anchor_y=0)
    adjust_advance(font, name, PUNCT_LSB, PUNCT_RSB)
    rows.append({"codepoint":f"U+{cp:04X}","glyph":name,"group":"punctuation metrics",
                 "old_bounds":old,"new_bounds":bounds(font,name),"old_advance":old_adv,
                 "new_advance":font["hmtx"].metrics[name][0],"rule":"shared 60-unit sidebearings; preserve source form"})


def normalize_digit(font: TTFont, cp: int) -> None:
    name = cmap_name(font, cp)
    old = bounds(font, name)
    old_adv = font["hmtx"].metrics[name][0]
    transform_simple(font, name, sy=600 / max(1, old[3]), target_xmin=DIGIT_LSB,
                     target_ymin=old[1], anchor_x=old[0], anchor_y=0)
    adjust_advance(font, name, DIGIT_LSB, DIGIT_RSB)
    rows.append({"codepoint":f"U+{cp:04X}","glyph":name,"group":"numeral system",
                 "old_bounds":old,"new_bounds":bounds(font,name),"old_advance":old_adv,
                 "new_advance":font["hmtx"].metrics[name][0],"rule":"600-unit optical height, 70-unit sidebearings; baseline fixed"})


def standardize_bottom_dot(font: TTFont, cp: int) -> None:
    name = cmap_name(font, cp)
    old = bounds(font, name)
    old_adv = font["hmtx"].metrics[name][0]
    base=cmap_name(font,{0x09DC:0x09A1,0x09DD:0x09A2,0x09DF:0x09AF}[cp])
    b=bounds(font,base);cx=(b[0]+b[2])/2
    dot=cmap_name(font,0x002E);d=bounds(font,dot)
    sx=70/max(1,d[2]-d[0]);sy=70/max(1,d[3]-d[1])
    parts=[(base,(1,0,0,1,0,0)),(dot,(sx,0,0,sy,cx-35-d[0]*sx,-85-d[1]*sy))]
    font["glyf"][name]=outline_from_parts(font,name,parts)
    font["hmtx"].metrics[name]=font["hmtx"].metrics[base]
    rows.append({"codepoint":f"U+{cp:04X}","glyph":name,"group":"below-dot system",
                 "old_bounds":old,"new_bounds":bounds(font,name),"old_advance":old_adv,
                 "new_advance":font["hmtx"].metrics[name][0],"rule":f"owner {base} body plus owner period-derived 70×70 dot centered at y=-85..-15; no guessed contour selection"})


def standardize_combining_nukta(font: TTFont) -> None:
    name=cmap_name(font,0x09BC);dot=cmap_name(font,0x002E);d=bounds(font,dot)
    old=bounds(font,name)
    sx=70/max(1,d[2]-d[0]);sy=70/max(1,d[3]-d[1])
    font["glyf"][name]=outline_from_parts(font,name,[(dot,(sx,0,0,sy,465-d[0]*sx,-70-d[1]*sy))])
    font["hmtx"].metrics[name]=(0,465)
    rows.append({"codepoint":"U+09BC","glyph":name,"group":"below-dot system",
                 "old_bounds":old,"new_bounds":bounds(font,name),"old_advance":0,"new_advance":0,
                 "rule":"same owner period-derived 70×70 dot; anchor (500,0), canonical composition supported for DDA/DDHA/YA"})


def update_feature_source(font: TTFont, base_text: str, x_scales: dict[str,float]) -> str:
    # Keep mark-to-base anchors tied to their transformed base outlines.
    pat = re.compile(r"^(\s*pos base )(\w+)( <anchor )(-?\d+)( -?\d+> mark @\w+;\s*)$")
    lines=[]
    for line in base_text.splitlines():
        q=re.match(r"\s*pos base (\w+) <anchor (-?\d+) (-?\d+)> mark @(\w+);",line)
        if q:
            n,_,_,cls=q.groups()
            if n in ('uni09DC','uni09DD','uni09DF'):
                b=bounds(font,n);mid=(b[0]+b[2])//2
                if cls in ('MATRA09C1','MATRA09C2','MATRA09C3'):
                    line=f"    pos base {n} <anchor {mid} -110> mark @{cls};"
                elif cls=='VIRAMA':
                    line=f"    pos base {n} <anchor {mid} -120> mark @{cls};"
                elif cls in ('MATRA09BE','MATRA09C0'):
                    line=f"    pos base {n} <anchor {b[2]-28} 0> mark @{cls};"
            elif cls=='NUKTA' and n in ('uni09A1','uni09A2','uni09AF'):
                b=bounds(font,n)
                line=f"    pos base {n} <anchor {(b[0]+b[2])//2} -15> mark @NUKTA;"
        m=pat.match(line)
        if m and m.group(2) in x_scales:
            name=m.group(2)
            old_xmin=90
            new_x=round(90+(int(m.group(4))-old_xmin)*x_scales[name])
            line=f"{m.group(1)}{name}{m.group(3)}{new_x}{m.group(5)}"
        lines.append(line)
    text="\n".join(lines)+"\n"
    text=text.replace('markClass uni09BC <anchor 60 120> @NUKTA;','markClass uni09BC <anchor 500 0> @NUKTA;')
    text=text.replace(
        "# Shahjahan Asha 0.12 private test — inherited feature rules recalibrated to 0.12 sidebearings.",
        "# Shahjahan Asha 0.13 private test — inherited rules refined for optical metrics and added marks.",
    )

    cmap=font.getBestCmap()
    base_cps=[cp for cp in cmap if cp in CORE_BASES]
    base_names=" ".join(cmap[cp] for cp in base_cps)
    ligature_names=" ".join(n for n in font.getGlyphOrder() if n.startswith("lig_"))
    mark_names=" ".join(cmap[cp] for cp in (
        0x0981,0x09BC,0x09BE,0x09BF,0x09C0,0x09C1,0x09C2,0x09C3,
        0x09C7,0x09C8,0x09CB,0x09CC,0x09CD,0x09D7))
    gdef=(f"table GDEF {{\n"
          f"    GlyphClassDef [{base_names}], [{ligature_names}], [{mark_names}], [];\n"
          f"}} GDEF;\n")
    declarations = (
        "\n# 0.13 added owner-outline-derived mark classes.\n"
        "markClass uni0981 <anchor 120 0> @CANDRABINDU;\n"
        "markClass uni09D7 <anchor 0 0> @AULENGTH;\n" + gdef
    )
    text=text.replace("feature akhn {", declarations + "\nfeature ccmp {\n    sub uni09A1 uni09BC by uni09DC;\n    sub uni09A2 uni09BC by uni09DD;\n    sub uni09AF uni09BC by uni09DF;\n    sub uni09CC by uni09C7 uni09D7;\n} ccmp;\n\nfeature akhn {", 1)

    # Add mark-to-base rules for all mapped Bengali bases. Chandrabindu sits
    # above the body; anusvara uses a top-right optical anchor; AU length mark
    # closes the split vowel at the baseline's right edge.
    abvm_lines=["\nfeature abvm {"]
    mark_lines=["\nfeature mark {"]
    for cp in base_cps:
        name=cmap[cp]
        b=bounds(font,name)
        mid=(b[0]+b[2])//2
        top=b[3]
        right=b[2]
        abvm_lines.append(f"    pos base {name} <anchor {mid} {top+20}> mark @CANDRABINDU;")
        mark_lines.append(f"    pos base {name} <anchor {right+12} 0> mark @AULENGTH;")
    abvm_lines.append("} abvm;\n")
    mark_lines.append("} mark;\n")
    mkmk_lines=[
        "\nfeature mkmk {",
        "    pos mark uni09BE <anchor 514 670> mark @CANDRABINDU;",
        "    pos mark uni09C0 <anchor 506 760> mark @CANDRABINDU;",
        "} mkmk;\n",
    ]
    text += "\n".join(abvm_lines+mark_lines+mkmk_lines)
    return text


def add_bottom_dot_transform(font: TTFont, cp: int, sx: float, sy: float, tx: float, ty: float) -> None:
    name=cmap_name(font,cp)
    transform_simple(font,name,sx=sx,sy=sy,target_xmin=round(tx),target_ymin=round(ty),anchor_x=0,anchor_y=0)


def set_metadata(font: TTFont) -> None:
    font["head"].fontRevision=0.13
    replacements={
        "Source Glyph Seed 0.12 Private Test":"Source Glyph Seed 0.13 Private Test",
        "SourceGlyphSeed-0.12-private-test":"SourceGlyphSeed-0.13-private-test",
        "Version 0.12 private test":"Version 0.13 private test",
    }
    for record in font["name"].names:
        try: old=record.toUnicode()
        except Exception: continue
        value=old
        for a,b in replacements.items(): value=value.replace(a,b)
        if value!=old:
            record.string=value.encode(record.getEncoding(),errors="replace")


def update_font_bounds(font: TTFont) -> None:
    glyf=font["glyf"]
    all_bounds=[]
    max_advance=0
    for name in font.getGlyphOrder():
        g=glyf[name]
        if getattr(g,"numberOfContours",0)>0 or g.isComposite():
            g.recalcBounds(glyf)
            all_bounds.append((int(g.xMin),int(g.yMin),int(g.xMax),int(g.yMax)))
        max_advance=max(max_advance,int(font["hmtx"].metrics[name][0]))
    if all_bounds:
        font["head"].xMin=min(b[0] for b in all_bounds)
        font["head"].yMin=min(b[1] for b in all_bounds)
        font["head"].xMax=max(b[2] for b in all_bounds)
        font["head"].yMax=max(b[3] for b in all_bounds)
    font["hhea"].advanceWidthMax=max_advance
    # Leaves clearance for top-anchored signs without changing the 650-unit
    # body grid; this is a metric reservation, not an Android/Windows claim.
    font["hhea"].ascent=1000
    font["hhea"].descent=-400
    font["hhea"].lineGap=0
    os2=font["OS/2"]
    os2.sTypoAscender=1000
    os2.sTypoDescender=-400
    os2.sTypoLineGap=0
    os2.usWinAscent=1000
    os2.usWinDescent=400


def main() -> None:
    if not BASE.is_file() or not BASE_FEA.is_file():
        raise FileNotFoundError("Missing read-only v0.12 baseline package")
    font=TTFont(BASE)
    refine_source_strokes(font)
    cmap=font.getBestCmap()
    original_xmins={}
    actual_xscales={}

    for cp in CORE_BASES:
        name=cmap_name(font,cp)
        old=bounds(font,name)
        original_xmins[name]=old[0]
        top=VOWEL_PAIRS.get(cp,620 if cp in SHORT_CONSONANTS else 650)
        xs=VOWEL_X_SCALE.get(cp,1.0)
        actual_xscales[name]=xs
        transform_body(font,cp,top,CORE_LSB,xscale=xs,
                       reason=f"family optical top {top}; paired width correction {xs:.3f}; 90/90 bearings")

    # Source signs were only 316–407 units tall against a 650-unit body.
    # Fit full-height signs to explicit optical zones, retaining source curves.
    mark_specs={0x09BE:(1.08,650,406,0),0x09C0:(1.06,740,350,0),
                0x09BF:(1.05,740,500,0),0x09C7:(1.05,650,500,0),
                0x09C8:(1.05,740,500,0),0x09C1:(1.05,240,501,245),
                0x09C2:(1.05,260,501,231),0x09C3:(1.05,260,500,285)}
    for cp,(sx,height,ax,ay) in mark_specs.items():
        name=cmap_name(font,cp); old=bounds(font,name); old_adv=font["hmtx"].metrics[name][0]
        sy=height/max(1,old[3]-old[1])
        transform_simple(font,name,sx=sx,sy=sy,anchor_x=ax,anchor_y=ay)
        if cp in (0x09BE,0x09C0):
            b=bounds(font,name)
            font["hmtx"].metrics[name]=(b[2]-b[0]-28,font["hmtx"].metrics[name][1])
        rows.append({"codepoint":f"U+{cp:04X}","glyph":name,"group":"dependent-sign optical adjustment",
                     "old_bounds":old,"new_bounds":bounds(font,name),"old_advance":old_adv,
                     "new_advance":font["hmtx"].metrics[name][0],"rule":f"{height}-unit sign zone; {sx:.2f}× width; spacing advances reserved for aa/ii, anchor ({ax},{ay}) retained"})

    # Reconstruct the face-like source: flatten its crescent, resize its dot
    # independently and center it above, rather than uniformly scaling a face.
    name=cmap_name(font,0x0981); old=bounds(font,name); old_adv=font["hmtx"][name][0]
    g=font["glyf"][name]; coords=g.coordinates.copy(); start=0
    for j,end in enumerate(g.endPtsOfContours):
        pts=coords[start:end+1]; x0=min(x for x,y in pts);x1=max(x for x,y in pts)
        y0=min(y for x,y in pts);y1=max(y for x,y in pts)
        tx,ty,w,h=(92,130,55,55) if j==0 else (0,0,240,90)
        for k in range(start,end+1):
            x,y=coords[k];coords[k]=(round(tx+(x-x0)*w/(x1-x0)),round(ty+(y-y0)*h/(y1-y0)))
        start=end+1
    set_coords(g,coords);font["hmtx"].metrics[name]=(0,0)
    rows.append({"codepoint":"U+0981","glyph":name,"group":"special-sign reconstruction",
                 "old_bounds":old,"new_bounds":bounds(font,name),"old_advance":old_adv,"new_advance":0,
                 "rule":"owner crescent rebuilt to 240×90, separate owner dot 55×55 centered above; zero advance, GDEF/GPOS mark"})
    name=cmap_name(font,0x0982);old=bounds(font,name);old_adv=font["hmtx"][name][0]
    transform_simple(font,name,sx=0.60,sy=0.60,target_xmin=20,target_ymin=100,anchor_x=old[0],anchor_y=old[1])
    adjust_advance(font,name,20,60)
    rows.append({"codepoint":"U+0982","glyph":name,"group":"special-sign spacing form",
                 "old_bounds":old,"new_bounds":bounds(font,name),"old_advance":old_adv,
                 "new_advance":font["hmtx"][name][0],"rule":"compact owner ring/tail retained as Bengali post-base spacing sign, 20/60 bearings; not a Devanagari-like above dot"})

    # Visarga retains its owner's four-contour source drawing but is reduced and
    # placed on a compact sign width, avoiding the 0.12 full-body appearance.
    name=cmap_name(font,0x0983); old=bounds(font,name); old_adv=font["hmtx"].metrics[name][0]
    transform_simple(font,name,sx=0.50,sy=0.50,target_xmin=60,target_ymin=160,
                     anchor_x=old[0],anchor_y=old[1])
    adjust_advance(font,name,60,60)
    rows.append({"codepoint":"U+0983","glyph":name,"group":"special-sign optical adjustment",
                 "old_bounds":old,"new_bounds":bounds(font,name),"old_advance":old_adv,
                 "new_advance":font["hmtx"].metrics[name][0],"rule":"0.50× uniform outline, preserve two-dot source form, 60/60 bearings"})

    # Normalize the detached below-base dots in the retroflex/y-series family.
    standardize_combining_nukta(font)
    for cp in (0x09DC,0x09DD,0x09DF): standardize_bottom_dot(font,cp)

    # Main danda: align its ink height to the new short punctuation zone and
    # tighten symmetric spacing around Bengali letters.
    name=cmap_name(font,0x0964); old=bounds(font,name); old_adv=font["hmtx"].metrics[name][0]
    transform_simple(font,name,sy=DANDA_TOP/max(1,old[3]),target_xmin=60,target_ymin=old[1],
                     anchor_x=old[0],anchor_y=0)
    adjust_advance(font,name,60,60)
    rows.append({"codepoint":"U+0964","glyph":name,"group":"danda optical/metric correction",
                 "old_bounds":old,"new_bounds":bounds(font,name),"old_advance":old_adv,
                 "new_advance":font["hmtx"].metrics[name][0],"rule":"600-unit height, 60/60 sidebearings; source remains owner's exclamation-stem adaptation"})

    # Bengali numerals: a common readable height and even bearings, keeping
    # the handwritten contour shapes and individual widths.
    for cp in range(0x09E6,0x09F0): normalize_digit(font,cp)

    # Punctuation already in the base receives symmetric, compact metrics.
    for cp in (0x0021,0x0028,0x0029,0x002C,0x002D,0x002E,0x002F,0x003F,
               0x005B,0x005D,0x007B,0x007D,0x002B,0x002D,0x003D,0x00D7,0x00F7):
        if cp in font.getBestCmap(): normalize_punctuation(font,cp)

    # The inherited owner's U+09CC outline is the distinct curled right-side
    # AU construction. Reuse that actual owner form, not a reduced aa stem.
    au=cmap_name(font,0x09CC)
    g=font["glyf"][au];g.recalcBounds(font["glyf"])
    sy=650/max(1,int(g.yMax-g.yMin))
    part=(au,(1,0,0,sy,-int(g.xMin),-int(g.yMin)*sy))
    add_glyph(font,0x09D7,"uni09D7",[part],0,12,
              "owner-derived curled U+09CC outline used as canonical AU right component, 650-unit height")
    b=bounds(font,"uni09D7")
    font["hmtx"].metrics["uni09D7"]=(b[2]-b[0]+12,0)
    rows[-1]["new_advance"]=font["hmtx"]["uni09D7"][0]

    # Missing punctuation needed by the requested corpus is drawn only from
    # existing owner-derived period, comma and hyphen outlines.
    dot="uni002E"; comma="uni002C"; hyphen="uni002D"
    add_glyph(font,0x003A,"uni003A",[(dot,(1,0,0,1,0,0)),(dot,(1,0,0,1,0,270))],60,60,
              "two vertically aligned copies of owner-derived period dot")
    add_glyph(font,0x003B,"uni003B",[(comma,(1,0,0,1,0,0)),(dot,(1,0,0,1,20,270))],60,60,
              "owner-derived comma with a centered period dot")
    # Single curly quotes use flipped owner comma; doubles use a pair of smaller
    # copies. Left and right forms are mirrored as a family, not imported.
    add_glyph(font,0x2019,"uni2019",[(comma,(1,0,0,-1,0,550))],60,60,
              "owner-derived comma flipped vertically as a right single quote")
    add_glyph(font,0x2018,"uni2018",[(comma,(-1,0,0,-1,235,550))],60,60,
              "mirrored owner-derived comma as a left single quote")
    add_glyph(font,0x201D,"uni201D",[(comma,(0.60,0,0,-0.80,24,550)),
                                        (comma,(0.60,0,0,-0.80,104,550))],60,60,
              "two reduced owner-derived commas as a right double quote")
    add_glyph(font,0x201C,"uni201C",[(comma,(-0.60,0,0,-0.80,165,550)),
                                        (comma,(-0.60,0,0,-0.80,245,550))],60,60,
              "two mirrored reduced owner-derived commas as a left double quote")
    add_glyph(font,0x2014,"uni2014",[(hyphen,(1.75,0,0,1,-45,0))],60,60,
              "owner-derived hyphen extended to a typographic em-dash width")
    add_glyph(font,0x0025,"uni0025",[(dot,(1.20,0,0,1.20,-40,500)),
                                        (dot,(1.20,0,0,1.20,210,0)),
                                        ("uni002F",(0.80,0,0,0.95,70,0))],60,60,
              "visible owner-derived upper-left/lower-right period dots and slash composed as percent")

    # Give all mapped punctuation glyphs their compact standard metrics, then
    # preserve the glyph-specific original stem height/position.
    for cp in (0x003A,0x003B,0x2018,0x2019,0x201C,0x201D,0x2014,0x0025):
        name=cmap_name(font,cp)
        g=font["glyf"][name]; g.recalcBounds(font["glyf"])
        transform_simple(font,name,target_xmin=60)
        adjust_advance(font,name,60,60)
        for row in rows:
            if row["glyph"]==name:
                row["new_bounds"]=bounds(font,name)
                row["new_advance"]=font["hmtx"][name][0]

    # Recompile inherited GPOS anchors with the vowel width corrections and
    # add explicit split-vowel and top-mark attachment. This does not claim
    # unsupported reph/phalā/conjunct behavior.
    xmap={cmap_name(font,cp):VOWEL_X_SCALE[cp] for cp in VOWEL_X_SCALE}
    fea=update_feature_source(font,BASE_FEA.read_text(encoding="utf-8"),xmap)
    OUT_FEA.write_text(fea,encoding="utf-8")
    addOpenTypeFeatures(font,str(OUT_FEA),tables=["GSUB","GPOS","GDEF"])
    set_metadata(font)
    update_font_bounds(font)
    font.flavor=None
    font.save(OUT_TTF)
    font.close()

    # Conservative outline housekeeping fixes inherited directions/extrema and
    # unions only detected self-intersections. No simplification is performed.
    with tempfile.TemporaryDirectory(prefix="asha-clean-") as tmp:
        cleaned=Path(tmp)/"cleaned.ttf"
        subprocess.run(["/usr/bin/python3",str(PKG/"scripts/clean_contours.py"),
                        str(OUT_TTF),str(OUT_SFD),str(cleaned),str(PKG/"CONTOUR-CLEANUP-0.13.json")],
                       check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        font=TTFont(cleaned)
        addOpenTypeFeatures(font,str(OUT_FEA),tables=["GSUB","GPOS","GDEF"])
        set_metadata(font)
        update_font_bounds(font)
        font.save(OUT_TTF)

    with (PKG/"GLYPH-ADJUSTMENTS-0.13.csv").open("w",encoding="utf-8-sig",newline="") as f:
        fields=["codepoint","glyph","group","old_bounds","new_bounds","old_advance","new_advance","rule"]
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)

    print(f"TTF {OUT_TTF}")
    print(f"SFD {OUT_SFD}")
    print(f"OpenType source {OUT_FEA}")
    print(f"Glyph adjustments {len(rows)}")
    print(f"Mapped glyphs {len(font.getGlyphOrder())} / cmap {len(font.getBestCmap()) if font else 'saved'}")

if __name__ == "__main__":
    main()
