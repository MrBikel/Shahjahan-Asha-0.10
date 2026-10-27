# 0.13 private refinement changelog

This revision derives from the best valid private baseline, 0.12. It preserves the handwritten contours and makes family-level optical/metric corrections; it does not claim a full redraw.

## Glyph and metrics

- Rebalanced mapped independent vowels and core consonants to shared optical-height and side-bearing systems, with restrained local stroke strengthening for weak vowel shapes and Bengali numerals.
- Reworked dependent-sign proportions and their placement zones; normalized the danda to a 600-unit short-punctuation height and compact bearings. Punctuation advances/side bearings and composed forms were regularized instead of hiding spacing problems with kerning.
- Reconstructed chandrabindu from the owner's crescent and dot components; made anusvara a compact spacing sign while retaining its owner-derived Bengali form; kept visarga's paired-dot form.
- Rebuilt ড়, ঢ় and য় as owner-derived ড/ঢ/য bodies with one shared, period-derived 70×70 dot. The combining nukta uses the same dot; explicit `ccmp` composition makes each direct form shape identically to its canonical decomposed sequence. Dotted bases are spaced away from ু/ূ/ৃ, with a measured minimum 25-unit vertical ink gap in the tested nine combinations. This replaces an earlier contour-rank heuristic that failed for য়.
- Retained the owner's distinct curled AU source form for U+09D7, split by `ccmp` with U+09C7; constructed colon, semicolon, curly quotes, em dash and percent from owner-derived punctuation only.
- Corrected contour direction/extrema and repaired integer-export degeneracies in bounded passes. No autotracing or global aggressive simplification was used. Physical FontForge contour-error mask is now zero.

## OpenType and coverage

- Refined dependent-mark anchors and GDEF classes; registered Bengali `bng2` and default languagesystems.
- `ccmp` handles split AU and the three dotted-letter canonical compositions. Existing targeted substitutions remain: ক্ষ/ক্ষ্ম in `akhn`, ক্র in `vatu`, and ক্ক/ক্ত/ক্ল in `cjct`.
- This is deliberately partial shaping, not general reph, phala, half-form or conjunct support. Forty-four TTF glyphs still carry FontForge's missing-anchor warning; sequences that need absent anchors remain unsupported and are documented.

## Status

Private engineering preview only. No push, merge, publication or release was performed.