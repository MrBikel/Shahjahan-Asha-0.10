#!/usr/bin/env python3
"""Rebuild a candidate TTF from the editable SFD and OpenType feature source."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
SFD = ROOT / "ShahjahanAsha-SourceGlyphSeed-0.10-private-test.sfd"
FEATURES = ROOT / "ShahjahanAsha-opentype-features-0.10.fea"
SHIPPED_TTF = ROOT / "ShahjahanAsha-SourceGlyphSeed-0.10-private-test.ttf"
DEFAULT_OUTPUT = ROOT / "dist" / "ShahjahanAsha-SourceGlyphSeed-0.10-rebuilt.ttf"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"candidate output path (default: {DEFAULT_OUTPUT.relative_to(ROOT)})")
    args = parser.parse_args()

    if shutil.which("fontforge") is None:
        raise SystemExit("FontForge is required to rebuild this font; install FontForge and retry.")
    if not SFD.is_file() or not FEATURES.is_file():
        raise SystemExit("Missing released SFD or OpenType feature source")
    output = args.output.expanduser().resolve()
    repository = ROOT.resolve()
    dist_dir = (ROOT / "dist").resolve()
    if output.is_relative_to(repository) and not output.is_relative_to(dist_dir):
        raise SystemExit("Refusing to write inside the repository outside dist/; choose dist/ or a path outside the repository.")
    if output == SHIPPED_TTF.resolve():
        raise SystemExit("Refusing to overwrite the shipped prototype TTF")
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="shahjahan-asha-010-", dir=output.parent) as temp_dir:
        temp = Path(temp_dir)
        raw_ttf = temp / "fontforge-output.ttf"
        featured_ttf = temp / "featured-font.ttf"
        fontforge_script = (
            "import fontforge; "
            f"font = fontforge.open({str(SFD)!r}); "
            f"font.generate({str(raw_ttf)!r})"
        )
        try:
            subprocess.run(["fontforge", "-lang=py", "-c", fontforge_script], check=True)
            font = TTFont(str(raw_ttf))
            addOpenTypeFeatures(font, str(FEATURES), tables=["GSUB", "GPOS"])
            font.save(str(featured_ttf))
            featured_ttf.replace(output)
        finally:
            featured_ttf.unlink(missing_ok=True)

    print(f"Built candidate TTF: {output}")
    print("The shipped prototype TTF was not modified.")


if __name__ == "__main__":
    main()
