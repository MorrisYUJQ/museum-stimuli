"""Generate table4_compare.html — expert-spot-check UI + museum-stimuli S1 text."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Curated Focus Mode text for Table 4. This is not a raw dump of dftgen.html:
# it keeps the same facts but is edited for screenshot readability.
CURATED_DFT_FOCUS_UNITS = [
    "==洮河石雕兰亭集会图砚==。",
    "时代：==宋代==。",
    "长 22.4 厘米，宽 13.5 厘米，厚 6.8 厘米。",
    "它是一方长方形砚台。",
    "砚面和四侧用浅浮雕刻出==兰亭修褉图==。",
    "画面来自东晋永和九年的兰亭雅集。",
    "核心人物包括==王羲之==和谢安等名士。",
    "王羲之的==《兰亭序》==写的就是这次聚会。",
    "",
    "砚面主体是兰亭图。",
    "有楼台、亭阁、山峦和祥云。",
    "工匠把==曲水==设计成墨池。",
    "池上还有镂空树干、楼栏和小桥。",
    "这些细节让砚台既可使用，也可观赏。",
    "",
    "四面侧壁刻有修褉环景图。",
    "画中有四十多个人物。",
    "有人谈论、烹茶、赏画、读书、捕鱼和打拳。",
    "另有==浴鹅图==，描绘六只鹅在水边嬉戏。",
    "",
    "砚背下凹，呈斜坡状。",
    "石质细腻，包浆厚，呈豆绿色。",
    "明末时曾由==吴拭==收藏。",
    "",
    "==洮河石砚==又称洮砚。",
    "它是中国==四大名砚==之一。",
    "早在唐宋时期已经有名。",
    "至今已有一千三百多年历史。",
    "",
    "原料是洮河石。",
    "洮河石是一种==水成岩==，也称==辉绿岩==。",
    "它因产于甘肃==卓尼县==洮河之滨而得名。",
    "石色多为绿色，也有墨绿、碧绿、辉绿等变化。",
    "",
    "唐代书法家==柳公权==在==《论砚》==中提到临洮砚。",
    "这说明洮砚很早就受到文人重视。",
    "当时它已可与==端砚==、==歙砚==并列。",
    "",
    "宋代以后，洮砚逐渐成为地方贡品。",
    "它取代停采的红丝石砚，进入“四大名砚”之列。",
    "宋代鉴赏家==赵希鹄==在==《洞天清禄集•古砚辨》==中称赞洮河绿石。",
    "他认为这种石“绿如蓝，润如玉”。",
    "",
    "洮河砚最初并不只是文房珍品。",
    "洮河流域在宋代属于==西夏==政权范围。",
    "当地人也曾用这种石材磨砺战刀。",
    "后来，细腻石质和雅润色泽被文人重新发现。",
    "",
    "例如==苏东坡==曾在铭文中赞美黄庭坚收藏的洮河石砚。",
    "这说明洮河砚既有实用价值，也承载文人文化记忆。",
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


def build_dft_focus_text() -> str:
    return "\n\n".join(CURATED_DFT_FOCUS_UNITS)


def main() -> None:
    original_html = (ROOT / "original.html").read_text(encoding="utf-8")
    helper_html = (ROOT / "dyslexia_helper.html").read_text(encoding="utf-8")
    dftgen_html = (ROOT / "dftgen.html").read_text(encoding="utf-8")

    sid = "s1-洮河石雕兰亭集会图砚"
    original_inner = extract_section(original_html, sid)
    helper_inner = extract_section(helper_html, sid)
    extract_slide_data(dftgen_html)  # Validate that the source page still contains S1 data.
    dft_focus_text = build_dft_focus_text()

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
