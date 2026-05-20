"""Generate table4_compare.html — expert-spot-check UI + museum-stimuli S1 text."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

HIGHLIGHT_TERMS = [
    "柳公权",
    "《论砚》",
    "赵希鹄",
    "《洞天清禄集",
    "西夏",
    "辉绿岩",
    "端砚",
    "歙砚",
    "临洮",
    "苏东坡",
    "黄庭坚",
    "兰亭",
    "修褉",
    "洮河",
    "四大名砚",
]


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
    m = re.search(r"const slideData = (\{.*?\});\s*const fullData", dftgen_html, re.DOTALL)
    if not m:
        raise ValueError("slideData not found")
    data = json.loads(m.group(1))
    return data["1"]


def char_count(html_or_text: str) -> int:
    text = re.sub(r"<[^>]+>", "", html_or_text)
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"\s+", "", text)
    return len(text)


def wrap_rich_terms(text: str, terms: list[str]) -> str:
    """Mark key terms with **bold** (expert spot-check convention)."""
    out = text.replace("\n", " ").strip()
    for t in sorted(terms, key=len, reverse=True):
        if t and t in out and f"**{t}**" not in out:
            out = out.replace(t, f"**{t}**")
    out = re.sub(r"(《[^》]{1,24}》)", r"**\1**", out)
    out = re.sub(r"(\d+(?:\.\d+)?\s*(?:厘米|年|块|首|人|只|卷|字))", r"**\1**", out)
    return out


def build_dft_focus_text(units: list[str]) -> str:
    return "\n\n".join(wrap_rich_terms(u, HIGHLIGHT_TERMS) for u in units)


def main() -> None:
    original_html = (ROOT / "original.html").read_text(encoding="utf-8")
    helper_html = (ROOT / "dyslexia_helper.html").read_text(encoding="utf-8")
    dftgen_html = (ROOT / "dftgen.html").read_text(encoding="utf-8")

    sid = "s1-洮河石雕兰亭集会图砚"
    original_inner = extract_section(original_html, sid)
    helper_inner = extract_section(helper_html, sid)
    dft_units = extract_slide_data(dftgen_html)
    dft_focus_text = build_dft_focus_text(dft_units)

    counts = {
        "stimulus_id": "S1",
        "title": "洮河石雕兰亭集会图砚",
        "original_chars": char_count(original_inner),
        "helper_chars": char_count(helper_inner),
        "dft_focus_chars": char_count(dft_focus_text),
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
        "dft_focus_text": dft_focus_text,
        "word_counts": counts,
    }

    data_json = json.dumps(payload, ensure_ascii=False)
    template = (ROOT / "table4_template.html").read_text(encoding="utf-8")
    html = template.replace("/*__DATA__*/", data_json)
    out = ROOT / "table4_compare.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
