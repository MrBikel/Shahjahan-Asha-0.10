#!/usr/bin/env python3
"""Rebuild a candidate TTF for the 0.10 OFL release from its SFD and features."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
SFD = ROOT / "ShahjahanAsha-0.10.sfd"
FEATURES = ROOT / "ShahjahanAsha-opentype-features-0.10.fea"
SHIPPED_TTF = ROOT / "ShahjahanAsha-0.10.ttf"
DEFAULT_OUTPUT = ROOT / "dist" / "ShahjahanAsha-0.10-rebuilt.ttf"

RELEASE_NAME_RECORDS = {
    0: "Copyright (c) 2026 Md. Mehedi Hasan (https://github.com/MrBikel).",
    1: "Shahjahan Asha",
    2: "Regular",
    3: "ShahjahanAsha-0.10;Shahjahan Asha Regular",
    4: "Shahjahan Asha",
    5: "Version 0.10",
    6: "ShahjahanAsha-Regular",
    9: "Md. Mehedi Hasan",
    10: "Experimental partial handwritten Bengali typeface.",
    11: "https://github.com/MrBikel/Shahjahan-Asha-0.10",
    12: "https://github.com/MrBikel/Shahjahan-Asha-0.10",
    13: "This Font Software is licensed under the SIL Open Font License, Version 1.1. See LICENSE.txt.",
    14: "https://openfontlicense.org",
    16: "Shahjahan Asha",
    17: "Regular",
}


def set_release_name_records(font: TTFont) -> None:
    names = font["name"]
    for name_id, value in RELEASE_NAME_RECORDS.items():
        names.names = [record for record in names.names if record.nameID != name_id]
        names.setName(value, name_id, 3, 1, 0x0409)
        names.setName(value, name_id, 1, 0, 0)


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
        raise SystemExit("Refusing to overwrite the released TTF")
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
            set_release_name_records(font)
            font.save(str(featured_ttf))
            featured_ttf.replace(output)
        finally:
            featured_ttf.unlink(missing_ok=True)

    print(f"Built candidate TTF: {output}")
    print("The released TTF was not modified.")


if __name__ == "__main__":
    main()
