#!/usr/bin/python3
"""Rebuild the private test TTF from its SFD and compile external layout features.
Default output is tests/validation/roundtrip.ttf; no delivered files are overwritten.
"""
import os, sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SFD = ROOT / 'ShahjahanAsha-SourceGlyphSeed-0.13-private-test.sfd'
FEA = ROOT / 'ShahjahanAsha-opentype-features-0.13.fea'
OUTDIR = ROOT / 'tests' / 'validation'
OUTDIR.mkdir(parents=True, exist_ok=True)
args = [a for a in sys.argv[1:] if a != '--fontforge-child']
OUT = Path(args[0]).resolve() if args else OUTDIR / 'roundtrip.ttf'
if not OUT.is_relative_to(OUTDIR.resolve()):
    raise SystemExit('Output must remain under tests/validation')
if '--fontforge-child' in sys.argv:
    import fontforge
    f = fontforge.open(str(SFD))
    f.generate(str(OUT))
    f.close()
    raise SystemExit(0)
# FontForge reads the editable outlines and SFD metadata; the separate FEA is
# compiled afterward, preserving source name/metrics from the SFD (see report).
subprocess.run(['/usr/bin/fontforge', '-lang=py', '-script', str(Path(__file__).resolve()), '--fontforge-child'], check=True)
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeatures
font = TTFont(str(OUT))
addOpenTypeFeatures(font, str(FEA))
font.save(str(OUT))
print(f'Built {OUT}')
