"""Export reading materials and comprehension questions to CSV."""
from __future__ import annotations

import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent


def extract_items(js: str) -> list[dict]:
    items: list[dict] = []
    pattern = r'id: "(S\d+)"[\s\S]*?title: "([^"]+)"[\s\S]*?conditions: \{([\s\S]*?)\}\s*,\s*questions:'
    for match in re.finditer(pattern, js):
        sid, title, cond_block = match.group(1), match.group(2), match.group(3)
        conditions: dict[str, list[str]] = {}
        for cond_match in re.finditer(r"(original|helper|dftgen): \[([\s\S]*?)\]", cond_block):
            parts = re.findall(r'"([^"]*)"', cond_match.group(2))
            conditions[cond_match.group(1)] = parts
        items.append({"id": sid, "title": title, "conditions": conditions})
    return items


def main() -> None:
    text = (BASE / "stimuli.js").read_text(encoding="utf-8")
    items = extract_items(text)
    qrows = list(csv.DictReader((BASE / "questions.csv").open(encoding="utf-8-sig")))

    materials_path = BASE / "materials_long.csv"
    master_path = BASE / "materials_and_questions_full.csv"

    with materials_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["stimulus_id", "title", "condition", "unit_no", "text"])
        for item in items:
            for condition, parts in item["conditions"].items():
                for index, part in enumerate(parts, start=1):
                    writer.writerow([item["id"], item["title"], condition, index, part])

    with master_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "record_type",
                "stimulus_id",
                "title",
                "condition",
                "unit_or_question_no",
                "text_or_question",
                "option_a",
                "option_b",
                "option_c",
                "option_d",
                "correct_option",
                "answer_text",
            ]
        )
        for item in items:
            for condition, parts in item["conditions"].items():
                for index, part in enumerate(parts, start=1):
                    writer.writerow(
                        ["material", item["id"], item["title"], condition, index, part, "", "", "", "", "", ""]
                    )
        for row in qrows:
            writer.writerow(
                [
                    "question",
                    row["stimulus_id"],
                    row["title"],
                    "",
                    row["question_no"],
                    row["question"],
                    row["option_a"],
                    row["option_b"],
                    row["option_c"],
                    row["option_d"],
                    row["correct_option"],
                    row["answer_text"],
                ]
            )

    print(f"items={len(items)} questions={len(qrows)}")
    print(f"wrote {materials_path}")
    print(f"wrote {master_path}")


if __name__ == "__main__":
    main()
