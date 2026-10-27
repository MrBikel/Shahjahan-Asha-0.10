#!/usr/bin/python3
"""Conservative repair checked after integer TTF export; no autotracing."""
import json
import sys
from pathlib import Path
import fontforge

src, sfd, ttf, report = map(Path, sys.argv[1:5])
physical = 0x2 | 0x4 | 0x8 | 0x10 | 0x20 | 0x40 | 0x40000
f = fontforge.open(str(src))
records=[]
passes=[]
for g in f.glyphs():
    if len(g.foreground)==0 and not g.references:
        continue
    before=g.validate(True)
    old=g.boundingBox()
    if before & 4:
        g.removeOverlap()
    g.correctDirection()
    g.round()
    g.addExtrema('all')
    g.correctDirection()
    records.append({'glyph':g.glyphname,'beforeMask':before,
                    'beforeBounds':old,'afterInitialBounds':g.boundingBox()})
# Integer quantization can expose tiny crossings which are absent in the
# editable floating-point source. Check actual generated output each pass.
for iteration in range(1,7):
    f.save(str(sfd))
    f.generate(str(ttf))
    f.close()
    f=fontforge.open(str(ttf))
    failures=[]
    for g in f.glyphs():
        mask=g.validate(True)
        if mask & physical:
            failures.append({'glyph':g.glyphname,'mask':mask,'bounds':g.boundingBox()})
    passes.append({'pass':iteration,'physicalFindings':failures})
    print('TTF contour pass',iteration,'physical findings',len(failures),flush=True)
    if not failures:
        break
    if iteration==6:
        break
    for finding in failures:
        g=f[finding['glyph']]
        mask=finding['mask']
        if mask & (4|8):
            g.removeOverlap()
            # Targeted degeneracy cleanup, maximum requested curve error
            # 0.1/1000 em (0.0048 px at the largest 48 px proof), not a visual
            # simplification pass across the family.
            g.simplify(0.1)
        g.correctDirection()
        g.round()
        g.addExtrema('all')
        g.correctDirection()
final=[]
for g in f.glyphs():
    mask=g.validate(True)
    final.append({'glyph':g.glyphname,'mask':mask,'bounds':g.boundingBox()})
f.close()
report.write_text(json.dumps({
    'policy':'No autotrace or global visual simplification. Directions/extrema repaired globally. Boolean union limited to detected self-intersections/direction failures; persistent integer-export degeneracies receive a targeted 0.1-unit simplification tolerance. Six-pass maximum; unresolved findings remain explicit. Separate FEA is authoritative for layout.',
    'physicalMaskHex':hex(physical),'initial':records,'passes':passes,'finalTtf':final,
    'physicalErrorsRemaining':sum(bool(x['mask']&physical) for x in final),
},ensure_ascii=False,indent=2)+'\n')
