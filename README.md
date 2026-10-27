# Shahjahan Asha 0.10 — Experimental Partial Prototype
# শাহজাহান আশা ০.১০ — পরীক্ষামূলক আংশিক প্রোটোটাইপ

**Creator and copyright holder / নির্মাতা ও কপিরাইটধারী:** Md. Mehedi Hasan (মোঃ মেহেদি হাসান; pen name / কলম নাম: Mr. Bikel / মি. বিকেল)
**Font Software license / ফন্ট-সফটওয়্যারের লাইসেন্স:** SIL Open Font License 1.1 (OFL-1.1)
**Reserved Font Name / সংরক্ষিত ফন্ট-নাম:** None / নেই

## About this font / ফন্ট পরিচিতি

**বাংলা:** শাহজাহান আশা হাতে-লেখা বাংলা টাইপফেসের একটি পরীক্ষামূলক প্রকল্প। ০.১০ সংস্করণটি সীমিত আংশিক প্রোটোটাইপ—পূর্ণাঙ্গ বা চূড়ান্ত বাংলা ফন্ট নয়। নির্মাতা ও কপিরাইটধারী এই Font Software সকলের ব্যবহারের জন্য OFL 1.1-এ প্রকাশ করেছেন। লাইসেন্সের পূর্ণ সরকারি ইংরেজি পাঠ `LICENSE.txt`-এ; কোন ফাইলগুলো Font Software-এর অংশ এবং কোনগুলো নয়, তা `LICENSE-SCOPE.md`-এ নির্দিষ্ট।

**English:** Shahjahan Asha is an experimental handwritten Bengali typeface. Version 0.10 is a limited partial prototype, not a complete or final Bengali font. The creator and copyright holder releases the designated Font Software for everyone under OFL 1.1. The complete official English license is in `LICENSE.txt`; `LICENSE-SCOPE.md` identifies what is and is not part of the Font Software.

OFL 1.1 permits use, study, copying, embedding, modification, and redistribution subject to its conditions. The font software may not be sold by itself, and modified versions must remain under OFL. No Reserved Font Name is declared, so “Shahjahan Asha” is not reserved by this release. The license text is authoritative; the Bengali summary is informational only.

OFL 1.1-এ শর্তসাপেক্ষে ব্যবহার, অধ্যয়ন, কপি, embed, পরিবর্তন ও পুনর্বিতরণ করা যায়। ফন্ট-সফটওয়্যার আলাদা করে বিক্রি করা যায় না এবং পরিবর্তিত সংস্করণও OFL-এ রাখতে হয়। এই রিলিজে কোনো Reserved Font Name ঘোষণা করা হয়নি; “Shahjahan Asha” নামটি সংরক্ষিত নয়। লাইসেন্সের মূল ইংরেজি পাঠই প্রামাণ্য; বাংলা সারাংশটি কেবল তথ্যের জন্য।

## Author / লেখক

See the bilingual [author profile and portrait / লেখক-পরিচিতি ও প্রতিকৃতি](docs/author-profile.md). The portrait and profile documentation are not part of the Font Software and are not licensed under OFL; see `LICENSE-SCOPE.md`.

দ্বিভাষিক [লেখক-পরিচিতি ও প্রতিকৃতি](docs/author-profile.md) দেখুন। প্রতিকৃতি ও প্রোফাইল-নথি Font Software-এর অংশ নয় এবং OFL-এ লাইসেন্স করা হয়নি; বিস্তারিত `LICENSE-SCOPE.md`-এ।

## Contents and current limits / যা আছে ও সীমাবদ্ধতা

**বাংলা:** build-এ ১০০টি cmap entry (উত্তরাধিকারসূত্রে পাওয়া ৯৯টি provisional source character ও space) এবং ১০৭টি glyph আছে। ছয়টি conjunct substitution পরীক্ষা করা হয়েছে: provisional ক্ষ ও ক্ষ্ম, এবং মালিক-নিশ্চিত ক্ক, ক্ত, ক্র ও ক্ল। প্যাকেজে TTF, editable FontForge SFD, OpenType feature source, glyph outline ও mask, চারটি confirmed source crop, source map, build/validation scripts, এবং shaping/visual proof রয়েছে।

**English:** The build has 100 cmap entries (99 inherited provisional source characters plus space) and 107 glyphs. It tests six conjunct substitutions: provisional ক্ষ and ক্ষ্ম, plus owner-confirmed ক্ক, ক্ত, ক্র, and ক্ল. The package contains a TTF, editable FontForge SFD, OpenType feature source, glyph outlines and masks, four confirmed source crops, source maps, build/validation scripts, and shaping/visual proofs.

এটি পূর্ণ বাংলা shaping সমর্থন করে না; একাধিক basic ও presentation-form feature এখনো অসম্পূর্ণ। নথিভুক্ত পরীক্ষা Linux-এ HarfBuzz ও OpenType Sanitizer দিয়ে করা। Windows, Microsoft Word বা mobile QA করা হয়নি। / This is not full Bengali shaping; several basic and presentation-form features remain unimplemented. Recorded checks used HarfBuzz and OpenType Sanitizer on Linux. Windows, Microsoft Word, and mobile QA have not been performed.

## Historical test record / ঐতিহাসিক পরীক্ষার রেকর্ড

`TEST-REPORT-0.10.txt` earlier private test run-এর হুবহু historical record হিসেবে অপরিবর্তিত রাখা হয়েছে। সেখানে “not for public release” ও rights unresolved লেখা ছিল সেই পরীক্ষার সময়কার অবস্থা; পরে কপিরাইটধারী পুনর্বিতরণের অধিকার নিশ্চিত করে public 0.10 release অনুমোদন করেছেন। পরবর্তী অনুমোদনটি কোনো পরীক্ষার ফল বা সীমাবদ্ধতা বদলায়নি। এই রিলিজে TTF-এর নাম/লাইসেন্স metadata ও package naming আপডেট হয়েছে; glyph outline ও shaping behavior-এর পরীক্ষিত ফল বদলানোর উদ্দেশ্যে নয়।

`TEST-REPORT-0.10.txt` is preserved verbatim as the historical record of the earlier private test run. Its “not for public release” and unresolved-rights statements described the status at test time; the copyright holder later confirmed redistribution rights and approved the public 0.10 release. That later authorization changed none of the test results or limitations. This release updates TTF naming/license metadata and package naming; it does not intend to change the tested glyph outlines or shaping behavior.

## Rebuild and validate / পুনর্নির্মাণ ও যাচাই

FontForge, Python, `fonttools`, HarfBuzz (`hb-shape`), and OpenType Sanitizer (`ots-sanitize`) are required. / FontForge, Python, `fonttools`, HarfBuzz (`hb-shape`) ও OpenType Sanitizer (`ots-sanitize`) লাগবে।

```sh
python3 scripts/build_from_sfd.py
python3 tests/validate_release.py
```

The builder writes a candidate to `dist/ShahjahanAsha-0.10-rebuilt.ttf` and will not overwrite the released TTF. To validate that rebuilt candidate, run `python3 tests/validate_release.py --font dist/ShahjahanAsha-0.10-rebuilt.ttf`. FontForge may add two unencoded utility glyphs (`.null` and `nonmarkingreturn`); the validator permits only those two extras while checking the same 107 meaningful glyphs and shaping/positioning behavior.

Builderটি `dist/ShahjahanAsha-0.10-rebuilt.ttf`-এ candidate লিখবে এবং প্রকাশিত TTF overwrite করবে না। ওই rebuilt candidate যাচাই করতে `python3 tests/validate_release.py --font dist/ShahjahanAsha-0.10-rebuilt.ttf` চালান। FontForge দুটি unencoded utility glyph (`.null`, `nonmarkingreturn`) যোগ করতে পারে; validator একই ১০৭টি অর্থবহ glyph ও shaping/positioning behavior পরীক্ষা করে এবং শুধু এই দুই অতিরিক্ত glyph অনুমোদন করে।

## Key files / গুরুত্বপূর্ণ ফাইল

- `ShahjahanAsha-0.10.ttf` — release font / প্রকাশিত ফন্ট
- `ShahjahanAsha-0.10.sfd` — editable FontForge source / সম্পাদনযোগ্য FontForge source
- `ShahjahanAsha-opentype-features-0.10.fea` — OpenType layout source
- `OWNER-CONFIRMED-CELLS-0.10.csv`, `TRACE-DETAILS-0.10.csv`, `SOURCE-MAP-MERGED-PROVISIONAL.csv` — source-cell assignments and maps / source-cell বিন্যাস ও মানচিত্র
- `sources/` — SVG outlines, masks, and four source crops / SVG outline, mask ও চারটি source crop
- `scripts/`, `tests/` — build and validation tools / build ও validation tool
- `TEST-REPORT-0.10.txt`, `proofs/` — historical test record and evidence / ঐতিহাসিক test record ও প্রমাণ
- `LICENSE.txt`, `LICENSE-SCOPE.md` — OFL 1.1 text and file-scope notice / OFL 1.1 পাঠ ও ফাইল-সীমার নোট

The 0.8 and 0.9 packages are not included or modified by this repository. / ০.৮ ও ০.৯ প্যাকেজ এই repository-তে নেই এবং পরিবর্তনও করা হয়নি।
