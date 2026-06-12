import csv
import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parent


def js_block_for_item(text: str, stimulus_id: str) -> str:
    match = re.search(r'id: "' + re.escape(stimulus_id) + r'"[\s\S]*?questions:', text)
    if not match:
        raise RuntimeError(f"Could not find {stimulus_id} in stimuli.js")
    return match.group(0)


def condition_parts(block: str, condition: str) -> list[str]:
    key = f"{condition}: ["
    start = block.index(key) + len(key)
    depth = 1
    idx = start
    while idx < len(block):
        char = block[idx]
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return re.findall(r'"([^"]*)"', block[start:idx])
        idx += 1
    return []


def word_count(parts: list[str]) -> int:
    return sum(
        len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", part))
        for part in parts
    )


def main() -> None:
    required = ["index.html", "stimuli.js", "questions.csv", "selected_items.json", "README.md"]
    print("Files:")
    for name in required:
        print(f"  {name}: {(BASE / name).exists()}")

    rows = list(csv.DictReader((BASE / "questions.csv").open(encoding="utf-8-sig")))
    items = json.loads((BASE / "selected_items.json").read_text(encoding="utf-8"))

    print(f"Selected items: {len(items)}")
    print(f"Question rows: {len(rows)}")
    print(f"CSV item IDs: {sorted({row['stimulus_id'] for row in rows})}")

    text = (BASE / "stimuli.js").read_text(encoding="utf-8")
    print("\nWord counts for manuscript Table 5 candidates:")
    for item in items[:2]:
        block = js_block_for_item(text, item["stimulus_id"])
        print(f"  {item['stimulus_id']}: {item['title']}")
        for condition in ["original", "helper", "dftgen"]:
            parts = condition_parts(block, condition)
            print(f"    {condition}: words={word_count(parts)}, units={len(parts)}")


if __name__ == "__main__":
    main()
