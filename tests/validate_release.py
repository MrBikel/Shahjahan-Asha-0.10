#!/usr/bin/env python3
"""Validate the 0.10 release font and its documented source artifacts."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FONT = ROOT / "ShahjahanAsha-SourceGlyphSeed-0.10-private-test.ttf"
SOURCE_MAP = ROOT / "SOURCE-MAP-MERGED-PROVISIONAL.csv"
OWNER_MAP = ROOT / "OWNER-CONFIRMED-CELLS-0.10.csv"
PROOF = ROOT / "proofs" / "owner-confirmed-ligature-source-vs-font.png"
SVG_DIR = ROOT / "sources" / "svg"
MASK_DIR = ROOT / "sources" / "masks"
CROP_DIR = ROOT / "sources" / "confirmed-crops"
NEW = [
    ("ক্ক", "lig_kka", "U+0995 U+09CD U+0995", "R1C1"),
    ("ক্ত", "lig_kta", "U+0995 U+09CD U+09A4", "R1C4"),
    ("ক্র", "lig_kra", "U+0995 U+09CD U+09B0", "R1C6"),
    ("ক্ল", "lig_kla", "U+0995 U+09CD U+09B2", "R1C7"),
]
OLD = [("ক্ষ", "lig_ksha"), ("ক্ষ্ম", "lig_kshma")]
errors: list[str] = []


def shape(font_path: Path, text: str, feature_settings: list[str] | None = None) -> list[dict]:
    command = [
        "hb-shape", f"--font-file={font_path}", f"--text={text}",
        "--script=Beng", "--direction=ltr", "--shapers=ot", "--output-format=json",
    ]
    if feature_settings:
        command.append("--features=" + ",".join(feature_settings))
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        errors.append(f"hb-shape failed for {text!r}: {(result.stderr or result.stdout).strip()}")
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        errors.append(f"Could not parse hb-shape output for {text!r}")
        return []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT,
                        help="TTF to validate (defaults to the published 0.10 TTF)")
    args = parser.parse_args()
    font_path = args.font.expanduser().resolve()
    if not font_path.is_file():
        raise SystemExit(f"Missing TTF: {font_path}")
    missing_tools = [tool for tool in ("hb-shape", "ots-sanitize") if shutil.which(tool) is None]
    if missing_tools:
        raise SystemExit(
            "Missing required validation tool(s): " + ", ".join(missing_tools)
            + ". Install HarfBuzz (hb-shape) and OpenType Sanitizer (ots-sanitize), then retry."
        )
    for required in [SOURCE_MAP, OWNER_MAP, PROOF,
                     ROOT / "ShahjahanAsha-SourceGlyphSeed-0.10-private-test.sfd",
                     ROOT / "ShahjahanAsha-opentype-features-0.10.fea"]:
        if not required.is_file():
            errors.append(f"Missing release artifact: {required.relative_to(ROOT)}")
    inventories = [
        ("SVG outlines", list(SVG_DIR.glob("*.svg")), 105),
        ("PGM masks", list(MASK_DIR.glob("*.pgm")), 105),
        ("PNG masks", list(MASK_DIR.glob("*.png")), 105),
        ("confirmed source crops", list(CROP_DIR.glob("*.png")), 4),
    ]
    for label, files, expected_count in inventories:
        if len(files) != expected_count:
            errors.append(f"Expected {expected_count} {label}, found {len(files)}")
        empty = [path.relative_to(ROOT) for path in files if path.stat().st_size == 0]
        if empty:
            errors.append(f"Empty {label} files: {empty}")

    try:
        with SOURCE_MAP.open(encoding="utf-8-sig", newline="") as stream:
            source_rows = list(csv.DictReader(stream))
        with OWNER_MAP.open(encoding="utf-8-sig", newline="") as stream:
            owner_rows = list(csv.DictReader(stream))
    except OSError as exc:
        raise SystemExit(f"Could not read source maps: {exc}")

    if len(source_rows) != 99:
        errors.append(f"Expected 99 inherited provisional source rows, found {len(source_rows)}")
    if len(owner_rows) != 4 or {row.get("cell_id") for row in owner_rows} != {cell for _, _, _, cell in NEW}:
        errors.append("Owner-confirmed map must contain exactly the four 0.10 cells")

    font = TTFont(font_path)
    cmap = font.getBestCmap()
    glyph_order = font.getGlyphOrder()
    glyf = font["glyf"]
    expected_cmap = {int(row["codepoint"][2:], 16) for row in source_rows} | {0x20}
    if len(cmap) != 100 or set(cmap) != expected_cmap:
        errors.append(f"cmap mismatch: expected 100 entries, found {len(cmap)}")
    custom = {"lig_ksha", "lig_kshma"} | {name for _, name, _, _ in NEW}
    meaningful_glyphs = set(cmap.values()) | custom | {".notdef"}
    extra_glyphs = set(glyph_order) - meaningful_glyphs
    missing_glyphs = meaningful_glyphs - set(glyph_order)
    fontforge_placeholders = False
    if len(meaningful_glyphs) != 107 or missing_glyphs:
        errors.append(f"Expected the 107 meaningful glyphs; missing {sorted(missing_glyphs)}")
    if len(glyph_order) == 107 and not extra_glyphs:
        pass
    elif len(glyph_order) == 109 and extra_glyphs == {".null", "nonmarkingreturn"}:
        fontforge_placeholders = True
    else:
        errors.append(f"Unexpected glyph-order entries: {len(glyph_order)} total, extras={sorted(extra_glyphs)}")
    if not custom.issubset(glyph_order):
        errors.append(f"Missing ligature glyphs: {sorted(custom - set(glyph_order))}")

    if "GSUB" not in font or "GPOS" not in font:
        errors.append("Missing GSUB or GPOS table")
        gsub_tags: set[str] = set()
        gpos_tags: set[str] = set()
    else:
        gsub_tags = {record.FeatureTag for record in font["GSUB"].table.FeatureList.FeatureRecord}
        gpos_tags = {record.FeatureTag for record in font["GPOS"].table.FeatureList.FeatureRecord}
        if not {"akhn", "cjct", "vatu"}.issubset(gsub_tags):
            errors.append(f"Missing GSUB tags: {sorted({"akhn", "cjct", "vatu"} - gsub_tags)}")
        if not {"blwm", "dist"}.issubset(gpos_tags):
            errors.append(f"Missing inherited GPOS tags: {sorted({"blwm", "dist"} - gpos_tags)}")

    default_checks = []
    for text, name in OLD + [(text, name) for text, name, _, _ in NEW]:
        items = shape(font_path, text)
        ok = len(items) == 1 and items[0].get("g") == name and items[0].get("ax") == 1000
        ok = ok and not any(item.get("g") == ".notdef" for item in items)
        default_checks.append(ok)
    if len(default_checks) != 6 or not all(default_checks):
        errors.append(f"Default Bengali shaping substitutions passed {sum(default_checks)}/6")

    feature_checks = []
    for text, name in OLD:
        items = shape(font_path, text, ["akhn=1", "cjct=0", "vatu=0"])
        feature_checks.append(len(items) == 1 and items[0].get("g") == name)
    for text, name, _, _ in NEW:
        tag = "vatu" if name == "lig_kra" else "cjct"
        other = "cjct" if tag == "vatu" else "vatu"
        items = shape(font_path, text, ["akhn=0", f"{tag}=1", f"{other}=0"])
        feature_checks.append(len(items) == 1 and items[0].get("g") == name)
    if len(feature_checks) != 6 or not all(feature_checks):
        errors.append(f"Explicit feature-isolated checks passed {sum(feature_checks)}/6")

    exclusion_checks = []
    for text, name, _, _ in NEW:
        correct = "vatu" if name == "lig_kra" else "cjct"
        wrong = "cjct" if correct == "vatu" else "vatu"
        items = shape(font_path, text, ["akhn=1", f"{correct}=0", f"{wrong}=1"])
        exclusion_checks.append(not any(item.get("g") == name for item in items)
                                and not any(item.get("g") == ".notdef" for item in items))
    if not all(exclusion_checks):
        errors.append(f"Wrong-feature exclusions passed {sum(exclusion_checks)}/4")

    controls = []
    for text in ["জ্ঞ", "ত্র", "র্ক", "ঙ্ক"]:
        items = shape(font_path, text)
        controls.append(bool(items) and not any(item.get("g") in custom or item.get("g") == ".notdef" for item in items))
    if not all(controls):
        errors.append(f"Unrelated conjunct controls passed {sum(controls)}/4")

    bounds = []
    for name in custom:
        glyph = glyf[name]
        if getattr(glyph, "numberOfContours", 0) <= 0:
            bounds.append((name, "empty"))
        elif glyph.xMin < -5 or glyph.xMax > 1005:
            bounds.append((name, glyph.xMin, glyph.xMax))
    if bounds:
        errors.append(f"Outline bound violations: {bounds}")

    virama_checks = []
    consonants = [row for row in source_rows if row["category"] == "consonant"]
    for row in consonants:
        cp = int(row["codepoint"][2:], 16)
        items = shape(font_path, chr(cp) + "\u09CD")
        ok = (len(items) == 2 and items[0].get("g") == cmap[cp]
              and items[1].get("g") == "uni09CD" and items[1].get("ax") == 0
              and items[1].get("dx") == -1000
              and not any(item.get("g") == ".notdef" for item in items))
        virama_checks.append(ok)
    if sum(virama_checks) != 35:
        errors.append(f"Virama placement checks passed {sum(virama_checks)}/35")

    post_below_checks = []
    for row in consonants:
        cp = int(row["codepoint"][2:], 16)
        base = cmap[cp]
        base_glyph = glyf[base]
        advance = font["hmtx"].metrics[base][0]
        for mark_cp, kind in {0x09BE: "right", 0x09C0: "right", 0x09C1: "below",
                              0x09C2: "below", 0x09C3: "below"}.items():
            mark = cmap[mark_cp]
            mark_glyph = glyf[mark]
            items = shape(font_path, chr(cp) + chr(mark_cp))
            if kind == "right":
                base_anchor = min(base_glyph.xMax - 20, 800)
                mark_anchor = mark_glyph.xMin
                dy = 0
            else:
                base_anchor = round((base_glyph.xMin + base_glyph.xMax) / 2)
                mark_anchor = round((mark_glyph.xMin + mark_glyph.xMax) / 2)
                dy = -mark_glyph.yMax
            dx = base_anchor - mark_anchor - advance
            ok = (len(items) == 2 and items[0].get("g") == base and items[1].get("g") == mark
                  and items[1].get("ax") == 0 and abs(items[1].get("dx", 99999) - dx) <= 2
                  and abs(items[1].get("dy", 99999) - dy) <= 2
                  and not any(item.get("g") == ".notdef" for item in items))
            post_below_checks.append(ok)
    if sum(post_below_checks) != 175:
        errors.append(f"Post-/below-base placement checks passed {sum(post_below_checks)}/175")

    prebase_checks = []
    for row in consonants:
        cp = int(row["codepoint"][2:], 16)
        base = cmap[cp]
        base_glyph = glyf[base]
        for mark_cp in (0x09BF, 0x09C7, 0x09C8):
            mark = cmap[mark_cp]
            mark_glyph = glyf[mark]
            items = shape(font_path, chr(cp) + chr(mark_cp))
            advance, gap = 340, 24
            dx = advance + base_glyph.xMin - gap - mark_glyph.xMax
            ok = (len(items) == 2 and items[0].get("g") == mark and items[0].get("ax") == advance
                  and abs(items[0].get("dx", 99999) - dx) <= 2 and items[1].get("g") == base
                  and items[1].get("ax") == font["hmtx"].metrics[base][0]
                  and not any(item.get("g") == ".notdef" for item in items))
            prebase_checks.append(ok)
    if sum(prebase_checks) != 105:
        errors.append(f"Pre-base placement checks passed {sum(prebase_checks)}/105")

    try:
        with tempfile.TemporaryDirectory(prefix="asha-ots-") as temp_dir:
            sanitized = Path(temp_dir) / "sanitized.ttf"
            result = subprocess.run(["ots-sanitize", str(font_path), str(sanitized)],
                                    capture_output=True, text=True)
            if result.returncode:
                errors.append("ots-sanitize failed: " + (result.stderr or result.stdout).strip())
    except FileNotFoundError:
        errors.append("ots-sanitize executable not found")

    if errors:
        for message in errors:
            print(f"FAIL: {message}")
        raise SystemExit(1)

    if fontforge_placeholders:
        print("PASS: 100 cmap entries; 107 meaningful glyphs plus two unencoded FontForge placeholders; GSUB/GPOS tags present")
    else:
        print("PASS: cmap 100 entries; glyph order 107; GSUB/GPOS tags present")
    print("PASS: six default substitutions; six isolated feature tests; four wrong-feature exclusions")
    print("PASS: four unrelated conjunct controls; six ligature outline bounds")
    print("PASS: inherited attachment checks — virama 35/35, post/below 175/175, pre-base 105/105")
    print("PASS: source maps, editable SFD, 105 SVGs, 210 masks, 4 confirmed crops, visual proof, and OpenType Sanitizer")
    print(f"Validated: {font_path}")


if __name__ == "__main__":
    main()
