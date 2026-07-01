from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "questions.json"

PROMPT_LEAK_PATTERNS = [
    re.compile(r"\bthe correct answers?\s+(?:is|are)\b", re.IGNORECASE),
    re.compile(r"\bcorrect answers?\s+(?:is|are)\s*:", re.IGNORECASE),
    re.compile(r"\bsource PDF answer\b", re.IGNORECASE),
]


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def audit() -> list[str]:
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    issues: list[str] = []

    for question in payload.get("questions", []):
        qid = question.get("id", "<missing id>")
        prompt = question.get("prompt", "")
        choices = question.get("choices", [])
        labels = {choice.get("label") for choice in choices}
        choice_texts = [norm(choice.get("text", "")) for choice in choices]

        for pattern in PROMPT_LEAK_PATTERNS:
            if pattern.search(prompt):
                issues.append(f"{qid}: answer/explanation marker appears in prompt")
                break

        if not choices or len(choices) < 2:
            issues.append(f"{qid}: too few choices ({len(choices)})")

        if any(not text for text in choice_texts):
            issues.append(f"{qid}: empty choice text")

        if len(set(choice_texts)) < len(choice_texts):
            issues.append(f"{qid}: duplicate choice text")

        if any(re.fullmatch(r"option [a-h]", text) for text in choice_texts) and not question.get("media"):
            issues.append(f"{qid}: placeholder choice without media")

        correct_labels = set(question.get("correctLabels") or [])
        if correct_labels and not correct_labels.issubset(labels):
            issues.append(f"{qid}: correct label not present in choices")

        if norm(prompt).startswith(("select one", "select all", "a.", "b.")) or len(prompt.strip()) < 20:
            issues.append(f"{qid}: suspicious prompt")

    return issues


if __name__ == "__main__":
    found = audit()
    if found:
        print(f"Found {len(found)} issue(s):")
        for issue in found:
            print(f"- {issue}")
        raise SystemExit(1)
    print("Question audit passed.")
