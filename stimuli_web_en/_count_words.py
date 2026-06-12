import re
from pathlib import Path

BASE = Path(__file__).resolve().parent


def word_count(parts: list[str]) -> int:
    return sum(
        len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", part))
        for part in parts
    )


def condition_parts(text: str, stimulus_id: str, condition: str) -> list[str]:
    marker = f'id: "{stimulus_id}"'
    start = text.index(marker)
    key = f"{condition}: ["
    key_start = text.index(key, start)
    array_start = key_start + len(key)
    depth = 1
    idx = array_start
    while idx < len(text):
        char = text[idx]
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                block = text[array_start:idx]
                return re.findall(r'"([^"]*)"', block)
        idx += 1
    return []


text = (BASE / "stimuli.js").read_text(encoding="utf-8")
for sid in ["S1", "S2"]:
    print(sid)
    for cond in ["original", "helper", "dftgen"]:
        parts = condition_parts(text, sid, cond)
        print(f"  {cond}: words={word_count(parts)}, units={len(parts)}")
