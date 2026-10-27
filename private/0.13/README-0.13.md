# Shahjahan Asha 0.13 — private engineering preview

This is a new, reversible private working version derived from the audited 0.12 private test. It refines the font as a coordinated system rather than a set of isolated visual patches. It is **not a release candidate, not published, and not merged**.

## What is included

- `ShahjahanAsha-SourceGlyphSeed-0.13-private-test.sfd` — editable FontForge source.
- `ShahjahanAsha-SourceGlyphSeed-0.13-private-test.ttf` — generated test font.
- `ShahjahanAsha-opentype-features-0.13.fea` — editable OpenType layout source.
- `GLYPH-ADJUSTMENTS-0.13.csv`, `UNICODE-COVERAGE-0.13.csv` and `evidence/source-traces/SOURCE-REFERENCES-0.13.csv` — outline/metric and provenance ledgers.
- `proofs/before-after-16px.png`, `proofs/before-after-48px.png`, full HarfBuzz corpus renders and final Chromium captures.
- `CHANGELOG-0.13.md`, `SUPPORTED-COVERAGE-0.13.md` and `tests/validation/validation-summary.md` — changes, scope and test evidence.

## Build and test

From this directory, with FontForge, FontTools, HarfBuzz CLI and OTS installed:

```sh
python3 scripts/refine_from_012.py
python3 tests/test_dotted_letters.py
python3 scripts/build_from_sfd.py
python3 tests/validate_font.py
python3 tests/render_proofs.py
python3 tests/build_browser_test.py
```

`refine_from_012.py` reads only the six audited 0.12 baseline files carried in `evidence/baseline-v0.12/` and writes inside this 0.13 directory. `build_from_sfd.py` places its roundtrip only in `tests/validation/`. The Chromium page expects a local web server; the reported captures were made in the connected Sandbox browser, not on Android.

## Safety and provenance

The public 0.10 checkout and old private source/previews were not edited. The copied 0.12 baseline files match their audited originals byte-for-byte. The work uses the owner's supplied handwriting sources and derived outlines; it does not use AdorshoLipi outlines, or the unidentified 3804/3805 exercise sheet. The local git branch is `private/refinement-0.13`; it has not been pushed, merged, or used to create a release.

## Status

**Build generated. Scoped validation passed. Sandbox Chromium runtime-tested at 12, 16, 24, 36 and 48 px.** Incomplete mark-anchor coverage remains and broader Bengali shaping is not claimed. Android, Windows Font Viewer and Word were not available for testing. See the supported-coverage and validation reports before using the font.