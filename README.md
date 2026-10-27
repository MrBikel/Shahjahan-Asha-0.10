# Shahjahan Asha 0.10 — Experimental Partial Prototype

This repository publishes the owner-approved 0.10 test build of Shahjahan Asha, a handwritten Bengali typeface experiment. It is a narrow prototype, not a finished font release.

## What is included

The TTF and editable FontForge SFD are accompanied by the OpenType feature source, 105 SVG outlines, 210 mask files, four cropped confirmed source cells, source-cell maps, feature-assignment notes, the exact test report, and shaping/visual proofs. No complete original photographs are included. The inherited source map is provisional; the four 0.10 conjunct readings were confirmed by the owner.

## Scope and limitations

The build has 100 cmap entries (99 inherited provisional source characters plus space) and 107 glyphs. It tests six conjunct substitutions: the inherited experimental ক্ষ and ক্ষ্ম, plus owner-confirmed ক্ক, ক্ত, ক্র and ক্ল. The report records Linux-side HarfBuzz and OpenType Sanitizer checks.

This is **not full Bengali shaping**. Several basic and presentation-form features are unimplemented. There has been no Windows, Microsoft Word, or mobile QA, and this release carries no OFL claim or broader release certification. No general font-use license is included.

`TEST-REPORT-0.10.txt` is preserved verbatim from the earlier private test run. Its original statements that no public release was authorized describe the status at test time; the owner subsequently confirmed redistribution rights and explicitly approved this public 0.10 prototype. Those historical statements do not alter the recorded test results.

## Rebuild and validate

With FontForge, Python, `fonttools`, HarfBuzz's `hb-shape`, and `ots-sanitize` installed:

```sh
python3 scripts/build_from_sfd.py
python3 tests/validate_release.py
```

The builder writes a rebuilt candidate under `dist/` and refuses to overwrite files elsewhere in the repository. A custom `--output` must be under `dist/` or outside the repository; the shipped TTF is never overwritten. To validate a rebuilt candidate, pass it with `--font dist/ShahjahanAsha-SourceGlyphSeed-0.10-rebuilt.ttf`.

FontForge adds two unencoded utility glyphs (`.null` and `nonmarkingreturn`) when exporting that candidate from the SFD. The validator permits only those two extras while checking the same 107 meaningful glyphs and shaping/positioning behavior. The shipped TTF remains the exact tested 107-glyph build.

## Key files

- `ShahjahanAsha-SourceGlyphSeed-0.10-private-test.ttf` — tested font
- `ShahjahanAsha-SourceGlyphSeed-0.10-private-test.sfd` — editable FontForge source
- `ShahjahanAsha-opentype-features-0.10.fea` — OpenType layout source
- `OWNER-CONFIRMED-CELLS-0.10.csv` and `TRACE-DETAILS-0.10.csv` — confirmed source-cell assignments and trace details
- `SOURCE-MAP-MERGED-PROVISIONAL.csv` — inherited provisional source map
- `FEATURE-ASSIGNMENT-NOTES-0.10.txt` and `TEST-REPORT-0.10.txt` — shaping rationale and exact test record
- `sources/` — SVGs, masks, and four cropped source cells
- `proofs/` — source-versus-render image and HarfBuzz shaping output

The 0.8 and 0.9 packages are not included or modified by this repository.
