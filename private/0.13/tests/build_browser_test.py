#!/usr/bin/env python3
"""Generate a local Chromium specimen page from corpus.txt for 0.13 testing."""
from html import escape
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
CORPUS = HERE / "corpus.txt"
OUT = HERE / "browser-test.html"
FONT_NAME = "ShahjahanAsha-SourceGlyphSeed-0.13-private-test.ttf"
FONT = "../" + FONT_NAME + "?sha256=" + hashlib.sha256((PKG / FONT_NAME).read_bytes()).hexdigest()[:12]

lines = [line.strip() for line in CORPUS.read_text(encoding="utf-8").splitlines()
         if line.strip() and not line.lstrip().startswith("#")]
blocks = "\n".join(
    f'<div class="line" data-line="{i:02d}"><span class="num">{i:02d}</span> '
    f'<span class="specimen">{escape(text)}</span></div>'
    for i, text in enumerate(lines, 1)
)
page = f'''<!doctype html>
<html lang="bn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Shahjahan Asha 0.13 private — browser test</title>
<style>
@font-face {{
  font-family: "ShahjahanAsha013";
  src: url("{FONT}") format("truetype");
  font-weight: 400;
  font-style: normal;
  font-display: block;
}}
:root {{ --size: 16px; }}
* {{ box-sizing: border-box; }}
body {{ margin: 18px; color: #1b1b1b; background: #fff; font: 14px/1.35 system-ui, sans-serif; }}
h1 {{ margin: 0 0 4px; font-size: 19px; }}
p {{ margin: 0 0 12px; color: #444; }}
#status {{ padding: 6px 8px; margin: 8px 0 14px; border: 1px solid #bbb; font: 12px/1.35 monospace; white-space: pre-wrap; }}
#corpus {{ width: min(100%, 1500px); }}
.line {{ display: flex; gap: 10px; align-items: baseline; padding: 4px 0; border-bottom: 1px solid #eee; }}
.num {{ flex: 0 0 30px; color: #777; font: 11px/1 monospace; }}
.specimen {{ min-width: 0; max-width: 100%; white-space: normal; overflow-wrap: anywhere;
  font-family: "ShahjahanAsha013", sans-serif; font-size: var(--size); line-height: 1.55;
  font-weight: 400; font-feature-settings: "kern" 1; font-kerning: normal; }}
</style>
</head>
<body>
<h1>Shahjahan Asha 0.13 — private Chromium specimen</h1>
<p>First visual checks are lines 01–02; all requested corpus lines follow in order.</p>
<pre id="status">Waiting for the local font to load…</pre>
<div id="corpus">{blocks}</div>
<script>
(async () => {{
  const q = new URLSearchParams(location.search);
  const allowed = new Set(["12", "16", "24", "36", "48"]);
  const size = allowed.has(q.get("size")) ? q.get("size") : "16";
  document.documentElement.style.setProperty("--size", size + "px");
  const allText = [...document.querySelectorAll(".specimen")].map(e => e.textContent).join(" ");
  const faces = await document.fonts.load(size + 'px "ShahjahanAsha013"', allText);
  await document.fonts.ready;
  const lines = [...document.querySelectorAll(".line")];
  const failures = lines.filter(e => e.getBoundingClientRect().height <= 0 || e.scrollWidth > e.clientWidth);
  const result = {{
    browser: navigator.userAgent,
    sizePx: Number(size),
    corpusLines: lines.length,
    loadedFontFaces: faces.length,
    fontCheck: document.fonts.check(size + 'px "ShahjahanAsha013"', allText),
    documentFonts: document.fonts.size,
    failedOrOverflowingLines: failures.map(e => e.dataset.line),
    viewport: {{ width: innerWidth, height: innerHeight }},
    contentHeight: document.documentElement.scrollHeight,
  }};
  const ok = result.loadedFontFaces > 0 && result.fontCheck && failures.length === 0;
  document.body.dataset.testStatus = ok ? "PASS" : "FAIL";
  const status = document.getElementById("status");
  status.textContent = (ok ? "PASS" : "FAIL") + " — " + size + " px; " + lines.length + " corpus lines; " + faces.length + " loaded private font face; font check " + result.fontCheck + "; overflow failures " + failures.length;
  status.dataset.report = JSON.stringify(result);
}})().catch(err => {{
  document.body.dataset.testStatus = "FAIL";
  document.getElementById("status").textContent = "FAIL\\n" + String(err);
}});
</script>
</body>
</html>
'''
OUT.write_text(page, encoding="utf-8")
print(f"wrote {OUT} with {len(lines)} corpus lines")
