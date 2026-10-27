# Shahjahan Asha 0.13 — final private validation summary

**Status:** build generated; listed technical checks passed; Sandbox Chromium runtime-tested. This is a private engineering preview, not a release candidate or publication. Validation is scoped and does not establish general Bengali shaping correctness.

## Final results

- **Source roundtrip:** FontForge rebuilt a separate TTF from the versioned editable SFD, then the 0.13 FEA was compiled. Delivered and rebuilt fonts match all tested naming and vertical-metric fields; both contain 118 glyphs, 109 Unicode cmap entries and the expected TrueType/OpenType tables.
- **HarfBuzz:** 15 nonblank corpus lines × five sizes (12, 16, 24, 36 and 48 px) = **75/75 exact shaping comparisons**, matching glyph names/order, clusters, advances and offsets; no `.notdef` in either font.
- **Coverage probes:** all 70 required base×dependent-sign mappings are present; the seven priority bases and required punctuation map; the six explicitly named conjuncts (ক্ষ, ক্ষ্ম, ক্র, ক্ক, ক্ত, ক্ল) form. Mapping and `.notdef` checks are reported separately from visual or linguistic shaping acceptance.
- **Dotted letters:** dedicated regression test passed **12/12** direct-versus-decomposed shaping comparisons for ড়/ঢ়/য় with empty, ু, ূ and ৃ forms; **9/9** measured below-mark separations passed, minimum **25 font units**. The earlier contour-rank heuristic was replaced by owner-derived ড/ঢ/য bodies plus a shared period-derived dot.
- **Contours:** FontForge reports **zero physical-error flags** under `0x4007e` for the editable SFD, delivered TTF and rebuilt TTF after two bounded cleanup passes. No autotracing/global contour simplification was used.
- **OpenType Sanitizer:** OTS 8.2.1 passed for delivered and rebuilt TTF (exit code 0 for both).
- **Chromium runtime:** the connected Linux Sandbox Chromium loaded one custom font face and passed font/document checks at 12, 16, 24, 36 and 48 px. All 15 lines had positive layout boxes; zero horizontal overflow. Nine screenshots cover full short pages and the scrollable longer pages. The custom font URL is bound to the final TTF hash `40f3df7b695c`.

## Remaining warnings and limits

The delivered and roundtrip TTF each have 74 glyphs with mask `0x0` and **44 glyphs with `0x100000` (missing anchor)**. These denote incomplete mark-anchor coverage, not harmless noise. Explicit probes show ক় and অ্ retain marks at zero offset because the needed anchors are missing. Direct ড় is canonicalized by `ccmp` to ড় and passes the separate dotted-letter equivalence test; that is not generic mark-to-base attachment. The editable SFD also reports six `0x80000` nonintegral-coordinate flags, specific to SFD coordinates. The raw per-glyph data and decoded flags remain in [`validation.json`](validation.json).

The work does not claim full Bengali orthographic/shaping support, general reph/phala, half forms or unlisted conjuncts. The 70 base×sign probes test mapping, not universal visual correctness. No Android device/browser, Windows Font Viewer or Word was available; the Chromium DOM checks are not per-character fallback attribution.

## Integrity and provenance

The public 0.10 checkout is still clean at base commit `d655c528a7e14634a23f2f28526b90fc793942f2`. Earlier protected sources/previews from the checksum audit remain unchanged; six carried 0.12 baseline artifacts match their originals byte-for-byte. The work uses owner-provided source material only: no AdorshoLipi outlines and no unidentified 3804/3805 exercise sheet. No push, merge or release was performed.

## Artifact hashes

- Delivered TTF SHA-256: `40f3df7b695c74e562ee62bd42a9b63e628c2920e80deb59d5a123953aa75c3e`
- Editable SFD SHA-256: `b3b687ed17c09af55e27f8f21b57973cb9ba1c8133b52bfa48581f034d4b2c0e`
- FEA source SHA-256: `f50e278eddc1c48e59a0253f142e8cc3cef765ec1042116b04214f1cdd2f9fe6`
- SFD→TTF roundtrip SHA-256: `d5f747377cb0c646ad090901859fab68097e4e5d2e076c6866605d0ab7bd0295`

See [`chromium-runtime-summary.json`](../chromium-runtime-summary.json), [`below-dot-combinations.json`](../below-dot-combinations.json) and the [`proofs`](../../proofs/) folder for machine and visual evidence. See [`SUPPORTED-COVERAGE-0.13.md`](../../SUPPORTED-COVERAGE-0.13.md) for the exact coverage statement.