# Shahjahan Asha 0.13 — supported coverage and limitations

## Tested coverage

The font has 118 glyphs and 109 Unicode cmap entries. The supplied test corpus includes all independent Bengali vowels with deliberate double-space separation, the requested independent-consonant inventory, dependent signs, Bengali numerals, number punctuation, sentence punctuation and Bengali prose.

- HarfBuzz mapped all 15 non-comment corpus lines at 12, 16, 24, 36 and 48 px with no `.notdef`; the final delivered TTF and SFD-rebuilt TTF produced identical glyph IDs/order, clusters, advances and offsets in all 75 comparisons.
- The seven priority bases ক, গ, ট, ত, ব, র and শ each map with all ten listed dependent-sign forms (70 base–sign mapping probes). This checks mapping and shaping output, not proof that every combination is visually ideal or broadly correct.
- Six named conjunct substitutions formed in the exact probes: ক্ষ, ক্ষ্ম, ক্র, ক্ক, ক্ত and ক্ল. Only these specific paths are claimed. No general reph, ra-phala, ya-phala, ba-phala, half-form or conjunct coverage is claimed.
- The required punctuation has cmap coverage. The corpus also includes digits, ৎ, the special signs and a full listed consonant row.
- `ccmp` splits U+09CC into U+09C7 + U+09D7. For ড়, ঢ় and য়, 12 direct/decomposed HarfBuzz comparisons (each of the three forms bare and with ু/ূ/ৃ) matched exactly. Nine measured dotted-base-plus-below-mark cases have at least 25 font units between the dot and mark ink boxes.

## Important known limits

FontForge reports 44 delivered-font glyphs with `0x100000` (missing anchor). These are real incomplete attachment coverage, not contour faults. In explicit diagnostics, ক় and অ্ keep their nukta/hasanta marks at zero offset because the applicable anchors are missing. This is not accepted as supported shaping. The dotted DDA sequence ড় instead becomes the canonical precomposed ড় through `ccmp`; its direct/decomposed equality is tested separately and is not evidence of generic mark attachment.

The physical contour mask (`0x4007e`: open contours, self-intersections, wrong direction, flipped references, missing extrema, missing glyph-name substitutions and points too far apart) is zero in the editable source, delivered TTF and rebuilt TTF. The editable SFD also has six source-coordinate `0x80000` nonintegral flags; FontForge defines that flag as SFD-coordinate-specific. The full raw masks are retained in `tests/validation/validation.json`.

## Runtime and not tested

Connected Sandbox Chromium loaded the custom font face for each test size; all 15 text boxes were present, the font check passed and no horizontal line overflow was reported. Screenshots show the rendered samples. Browser DOM font checks are not per-character Chromium font attribution, though separate cmap/HarfBuzz tests found no missing glyphs in the tested strings.

No Android handset/browser, Windows Font Viewer or Microsoft Word was available. These results do not demonstrate cross-platform behavior, production readiness or general Bengali orthographic correctness. A Bengali type specialist should review the visual proofs, mark attachments, line metrics and wider text before any release decision.