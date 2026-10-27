# Handoff for the next agent

## Starting point
- Repository: `/workspace/Shahjahan-Asha-0.13-private`
- Branch: `private/refinement-0.13`
- Starting commit: `65e04be1bf4ac6b0e673089a79849a9c42fefcc5` (private 0.13 refinement, based on the audited private 0.12 baseline).
- The public `main` remains at the approved 0.10 prototype (`d655c528a7e14634a23f2f28526b90fc793942f2`). Preserve it, all prior versions, and their sources.

## What 0.13 contains
A private refinement of the supplied handwritten font: coordinated glyph/metric adjustments; owner-derived dotted ড়/ঢ়/য় forms; dependent-mark and GDEF anchor work; OpenType `ccmp` and a small set of explicitly targeted conjunct substitutions; bounded contour cleanup; editable SFD/FEA sources, test font, provenance/coverage ledgers, validation records, and render/browser evidence. See `private/0.13/CHANGELOG-0.13.md` and `private/0.13/tests/validation/validation-summary.md`.

## Tests and evidence already recorded
- FontForge SFD-to-TTF roundtrip and OTS 8.2.1 sanitation passed; delivered and rebuilt fonts match the recorded naming/vertical-metric fields and expected tables.
- HarfBuzz: 15 nonblank corpus lines at five sizes (12, 16, 24, 36, 48 px) gave 75/75 exact comparisons for glyph order, clusters, advances and offsets, with no `.notdef` in those test lines.
- Required base/sign mapping probes passed (70); six named conjunct probes formed: ক্ষ, ক্ষ্ম, ক্র, ক্ক, ক্ত, ক্ল. Dotted-letter regression passed 12/12 direct/decomposed comparisons, and 9/9 measured below-mark gaps met the 25-unit minimum.
- FontForge physical contour-error mask `0x4007e` was zero in the editable SFD, delivered TTF and rebuilt TTF. Connected Linux Sandbox Chromium passed documented font/document checks at 12–48 px with no horizontal overflow.
- These are scoped engineering checks only—not visual review, linguistic/orthographic approval, broad shaping acceptance, or evidence of production readiness. Do not describe the corpus results as such.

## Blocking limitations / exact status
**Status: private engineering preview only—not a release candidate, not full Bengali shaping, and not approved for release.** Forty-four delivered-font glyphs still have FontForge `0x100000` missing-anchor warnings. In explicit probes, ক় and অ্ retain marks at zero offset because required anchors are absent; do not claim these sequences are supported. There is no general reph/phala, half-form or unlisted-conjunct support. Review `private/0.13/SUPPORTED-COVERAGE-0.13.md` and the raw `private/0.13/tests/validation/validation.json` before making claims.

## Environments
Tested in the connected Linux Sandbox, including Chromium at 12, 16, 24, 36 and 48 px. Android handset/browser, Windows Font Viewer and Microsoft Word were unavailable and remain untested. Browser DOM checks do not establish per-character font attribution or cross-platform behavior.

## Safe boundaries
- Keep all work private and versioned; preserve public `main`/0.10 and all earlier versions unchanged.
- Do not merge, tag, release, publish, or push any new commit without separate explicit approval. The existing 0.13 commit was previously pushed only to `private/refinement-0.13`; this handoff note is a new local-only commit unless separately authorized later.
- Use only owner-supplied source material. Never use the unidentified 3804/3805 exercise sheet or copy AdorshoLipi outlines/code.

## Suggested next steps
1. Read this note, `private/0.13/README-0.13.md`, the supported-coverage file, and validation summary/raw JSON before editing.
2. Have a Bengali type specialist review the existing proofs and identify/prioritize the missing-anchor cases; design and test any fixes without claiming broader support than the exact evidence allows.
3. After changes, rerun the documented build/validation and shaping checks, regenerate evidence, and update coverage/limitations honestly. Keep changes on this private branch and stop before any publication action pending separate approval.
