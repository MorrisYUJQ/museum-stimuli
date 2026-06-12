"""Shuffle MCQ option order so correct answers are spread across A-D."""
from __future__ import annotations

import csv
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent
KEYS = ["A", "B", "C", "D"]
SEED = 20260609


def balanced_targets(n: int) -> list[str]:
    pool: list[str] = []
    while len(pool) < n:
        pool.extend(KEYS)
    pool = pool[:n]
    rng = random.Random(SEED)
    rng.shuffle(pool)
    return pool


def shuffle_row(row: dict, target_key: str) -> dict:
    options = [row["option_a"], row["option_b"], row["option_c"], row["option_d"]]
    correct_text = row["answer_text"]
    if correct_text not in options:
        raise ValueError(f"{row['stimulus_id']} Q{row['question_no']}: answer_text not in options")

    distractors = [opt for opt in options if opt != correct_text]
    random.Random(f"{SEED}-{row['stimulus_id']}-{row['question_no']}").shuffle(distractors)

    target_idx = KEYS.index(target_key)
    shuffled = [""] * 4
    shuffled[target_idx] = correct_text
    distractor_iter = iter(distractors)
    for idx in range(4):
        if idx != target_idx:
            shuffled[idx] = next(distractor_iter)

    out = dict(row)
    out["option_a"], out["option_b"], out["option_c"], out["option_d"] = shuffled
    out["correct_option"] = target_key
    out["answer_text"] = correct_text
    return out


def format_js_question(row: dict) -> str:
    parts = []
    for key in KEYS:
        text = row[f"option_{key.lower()}"].replace("\\", "\\\\").replace('"', '\\"')
        parts.append(f'{{ key: "{key}", text: "{text}" }}')
    prompt = row["question"].replace("\\", "\\\\").replace('"', '\\"')
    answer = row["answer_text"].replace("\\", "\\\\").replace('"', '\\"')
    return (
        f'{{ id: "{row["stimulus_id"]}_Q{row["question_no"]}", questionNo: {row["question_no"]}, '
        f'prompt: "{prompt}", options: [{", ".join(parts)}], '
        f'correctOption: "{row["correct_option"]}", answerText: "{answer}" }}'
    )


def update_stimuli_js(rows: list[dict]) -> None:
    js_path = BASE / "stimuli.js"
    text = js_path.read_text(encoding="utf-8")

    by_stimulus: dict[str, list[dict]] = {}
    for row in rows:
        by_stimulus.setdefault(row["stimulus_id"], []).append(row)

    for stimulus_id in sorted(by_stimulus):
        stimulus_rows = sorted(by_stimulus[stimulus_id], key=lambda r: int(r["question_no"]))
        block = ",\n        ".join(format_js_question(row) for row in stimulus_rows)
        marker = f'id: "{stimulus_id}"'
        start = text.index(marker)
        q_start = text.index("questions: [", start)
        q_end = text.index("]", q_start)
        # Walk to the closing bracket of the questions array.
        depth = 0
        idx = q_start
        while idx < len(text):
            char = text[idx]
            if char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
                if depth == 0:
                    q_end = idx
                    break
            idx += 1
        replacement = f"questions: [\n        {block}\n      ]"
        text = text[:q_start] + replacement + text[q_end + 1 :]

    js_path.write_text(text, encoding="utf-8")


def main() -> None:
    csv_path = BASE / "questions.csv"
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8-sig")))
    targets = balanced_targets(len(rows))
    shuffled = [shuffle_row(row, target) for row, target in zip(rows, targets)]

    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(shuffled)

    update_stimuli_js(shuffled)

    counts = {key: sum(1 for row in shuffled if row["correct_option"] == key) for key in KEYS}
    print("correct_option counts:", counts)
    for row in shuffled:
        print(
            f"{row['stimulus_id']} Q{row['question_no']}: {row['correct_option']} = {row['answer_text']}"
        )


if __name__ == "__main__":
    main()
