"""Generate table4_compare.html for TM paper Table 4 screenshots (S1 stimulus)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def extract_section(html: str, section_id: str) -> str:
    pattern = rf'<section class="item" id="{re.escape(section_id)}">(.*?)</section>'
    m = re.search(pattern, html, re.DOTALL)
    if not m:
        raise ValueError(f"section not found: {section_id}")
    block = m.group(1)
    inner = re.search(r'<div class="text">(.*?)</div>', block, re.DOTALL)
    if inner:
        return inner.group(1).strip()
    return block.strip()


def extract_slide_data(dftgen_html: str) -> list[str]:
    m = re.search(r'const slideData = (\{.*?\});\s*const fullData', dftgen_html, re.DOTALL)
    if not m:
        raise ValueError("slideData not found")
    data = json.loads(m.group(1))
    return data["1"]


def char_count(html_or_text: str) -> int:
    text = re.sub(r"<[^>]+>", "", html_or_text)
    text = re.sub(r"\s+", "", text)
    return len(text)


def main() -> None:
    original_html = (ROOT / "original.html").read_text(encoding="utf-8")
    helper_html = (ROOT / "dyslexia_helper.html").read_text(encoding="utf-8")
    dftgen_html = (ROOT / "dftgen.html").read_text(encoding="utf-8")

    sid = "s1-洮河石雕兰亭集会图砚"
    original_inner = extract_section(original_html, sid)
    helper_inner = extract_section(helper_html, sid)
    dft_units = extract_slide_data(dftgen_html)

    counts = {
        "stimulus_id": "S1",
        "title": "洮河石雕兰亭集会图砚",
        "original_chars": char_count(original_inner),
        "helper_chars": char_count(helper_inner),
        "dft_focus_chars": char_count("".join(dft_units)),
    }
    (ROOT / "table4_word_counts.json").write_text(
        json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    payload = {
        "title": "洮河石雕兰亭集会图砚",
        "title_en": "Taohé stone inkstone with Lanting gathering motif (Song dynasty)",
        "stimulus_id": "S1",
        "original_html": original_inner,
        "helper_html": helper_inner,
        "dft_units": dft_units,
        "highlight_terms": [
            "柳公权",
            "《论砚》",
            "赵希鹄",
            "《洞天清禄集",
            "西夏",
            "辉绿岩",
            "端砚",
            "歙砚",
            "临洮",
        ],
        "word_counts": counts,
    }

    data_json = json.dumps(payload, ensure_ascii=False)

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Table 4 — Museum text comparison (S1)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Lexend:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --ink: #1d2533;
      --muted: #657084;
      --paper: #f8f5ee;
      --panel: #fffdf8;
      --line: #d8d0c2;
      --blue: #235789;
      --shadow: 0 18px 45px rgba(50, 45, 35, .12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Atkinson Hyperlegible", "Lexend", "Noto Sans SC", "Microsoft YaHei UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 20% 0%, rgba(35, 87, 137, .14), transparent 32rem),
        linear-gradient(135deg, #fbf8f0, #efe8dc);
      line-height: 1.55;
    }}
    .wrap {{ max-width: 1280px; margin: 0 auto; padding: 28px 22px 48px; }}
    .hero {{
      margin-bottom: 18px;
      padding: 18px 20px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(255, 253, 248, .92);
      box-shadow: var(--shadow);
    }}
    .eyebrow {{
      display: inline-block;
      padding: 5px 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      color: var(--blue);
      font: 700 11px/1.2 "Lexend", sans-serif;
      letter-spacing: .08em;
      text-transform: uppercase;
    }}
    h1 {{ margin: 12px 0 6px; font: 800 28px/1.1 "Lexend", sans-serif; letter-spacing: -.03em; }}
    .sub {{ margin: 0; color: var(--muted); font-size: 15px; max-width: 900px; }}
    .counts {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 13px;
    }}
    .sample {{
      border: 1px solid var(--line);
      border-radius: 24px;
      background: var(--panel);
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    .sample-head {{
      padding: 16px 20px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(90deg, rgba(35,87,137,.10), rgba(49,120,95,.08));
    }}
    .sample-head h2 {{ margin: 0; font: 800 18px "Lexend", sans-serif; }}
    .sample-head p {{ margin: 6px 0 0; color: var(--muted); font-size: 13px; }}
    .texts {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 14px;
      padding: 16px;
    }}
    @media (max-width: 980px) {{ .texts {{ grid-template-columns: 1fr; }} }}
    .text-box {{
      border: 1px solid var(--line);
      border-radius: 16px;
      background: #fffaf0;
      overflow: hidden;
      min-height: 320px;
    }}
    .text-box h3 {{
      margin: 0;
      padding: 12px 14px 8px;
      font: 800 12px "Lexend", sans-serif;
      color: var(--blue);
      letter-spacing: .04em;
      text-transform: uppercase;
      border-bottom: 1px solid var(--line);
      background: rgba(35,87,137,.06);
    }}
    .reader {{
      padding: 12px 14px 16px;
      font-size: 17px;
      line-height: 1.95;
      letter-spacing: .02em;
      max-width: 44rem;
    }}
    .reader p {{ margin: 0 0 10px; }}
    .dft-card {{
      margin: 12px 14px 0;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(35,87,137,.05);
      min-height: 180px;
      font-size: 19px;
      line-height: 2.05;
    }}
    .dft-controls {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 14px 14px;
    }}
    .btn {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 12px;
      background: white;
      cursor: pointer;
      font: 600 13px "Lexend", sans-serif;
    }}
    .btn:disabled {{ opacity: .35; cursor: not-allowed; }}
    .page {{ color: var(--muted); font-size: 13px; }}
    mark.hl {{
      background: rgba(250, 204, 21, .35);
      border: 1px solid rgba(250, 204, 21, .55);
      padding: 0 3px;
      border-radius: 5px;
    }}
    .footnote {{
      margin-top: 14px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.6;
    }}
    @media print {{
      body {{ background: white; }}
      .dft-controls, .footnote a {{ display: none; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <span class="eyebrow">Table 4 · Study 3 stimulus S1</span>
      <h1 id="artifact-title"></h1>
      <p class="sub" id="artifact-subtitle"></p>
      <p class="counts" id="char-counts"></p>
    </div>

    <div class="sample" id="screenshot-area">
      <div class="sample-head">
        <h2>Palace Museum (Gugong) interpretive label — three rewriting conditions</h2>
        <p>For manuscript Table 4: screenshot this panel at ≥1280px width (100% zoom). DFT-GEN column shows Focus Mode (micro-units).</p>
      </div>
      <div class="texts">
        <div class="text-box">
          <h3>Original (museum label)</h3>
          <div class="reader" id="col-original"></div>
        </div>
        <div class="text-box">
          <h3>Dyslexia Helper (one-step LLM)</h3>
          <div class="reader" id="col-helper"></div>
        </div>
        <div class="text-box">
          <h3>DFT-GEN (Focus Mode)</h3>
          <div class="dft-card" id="dft-card"></div>
          <div class="dft-controls">
            <button class="btn" id="btn-prev" type="button">←</button>
            <span class="page" id="page">1 / 1</span>
            <button class="btn" id="btn-next" type="button">→</button>
          </div>
        </div>
      </div>
    </div>

    <p class="footnote">
      Deployment: <a href="https://github.com/MorrisYUJQ/museum-stimuli">museum-stimuli</a> ·
      Character counts exported to <code>table4_word_counts.json</code> for Study 3 length comparison.
    </p>
  </div>

  <script>
    const DATA = {data_json};

    const highlightTerms = DATA.highlight_terms || [];

    function escapeHtml(s) {{
      return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }}
    function escReg(s) {{ return s.replace(/[.*+?^{{}}()|[\\]\\\\]/g, '\\\\$&'); }}
    function applyHighlight(text) {{
      let html = escapeHtml(text);
      const terms = highlightTerms.slice().sort((a,b) => b.length - a.length);
      for (const t of terms) {{
        if (!t) continue;
        html = html.replace(new RegExp(escReg(t), 'g'), '<mark class="hl">' + escapeHtml(t) + '</mark>');
      }}
      html = html.replace(/(《[^》]{{1,24}}》)/g, '<mark class="hl">$1</mark>');
      html = html.replace(/(\\d+(?:\\.\\d+)?\\s*(?:厘米|年|块|首|人|只|卷|字))/g, '<mark class="hl">$1</mark>');
      return html.replace(/\\n/g, '<br>');
    }}

    document.getElementById('artifact-title').textContent = DATA.title;
    document.getElementById('artifact-subtitle').textContent =
      DATA.title_en + ' · ' + DATA.stimulus_id + ' · Stationery (Palace Museum corpus)';
    const wc = DATA.word_counts;
    document.getElementById('char-counts').textContent =
      'Characters (no whitespace): Original ' + wc.original_chars +
      ' · Dyslexia Helper ' + wc.helper_chars +
      ' · DFT-GEN Focus ' + wc.dft_focus_chars;

    document.getElementById('col-original').innerHTML = DATA.original_html;
    document.getElementById('col-helper').innerHTML = DATA.helper_html;

    const units = (DATA.dft_units || []).map(applyHighlight);
    let idx = 0;
    const card = document.getElementById('dft-card');
    const page = document.getElementById('page');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    function updateCard() {{
      const total = Math.max(1, units.length);
      idx = Math.max(0, Math.min(idx, total - 1));
      card.innerHTML = units.length ? units[idx] : '(empty)';
      page.textContent = (idx + 1) + ' / ' + total;
      btnPrev.disabled = idx <= 0;
      btnNext.disabled = idx >= total - 1;
    }}
    btnPrev.addEventListener('click', () => {{ idx -= 1; updateCard(); }});
    btnNext.addEventListener('click', () => {{ idx += 1; updateCard(); }});
    updateCard();
  </script>
</body>
</html>
"""
    out = ROOT / "table4_compare.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
