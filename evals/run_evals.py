"""Deterministic evaluations for the rule-based lesson-plan fallback.

Uses generate_rule_based_lesson_plan directly: no API calls, no Ollama,
no network. Instructional-content boundary: term checks run over the
title, warmup, drills, and coaching cues only. The fallback echoes caller
metadata verbatim (plan["goal"], and the title embeds player_name), so
those echoed fields are excluded from term checks -- otherwise an
adversarial *goal* would fail even though no instructional content
contains the term. Dataset player names are clean; only goals carry
adversarial text.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.generator import generate_rule_based_lesson_plan

CASES_PATH = Path(__file__).parent / "lesson_plan_cases.json"

INSTRUCTIONAL_FIELDS = ("title", "warmup", "drills", "coaching_cues")


def load_cases(path=CASES_PATH):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def instructional_text(plan):
    parts = [plan.get("title", ""), plan.get("warmup", "")]
    parts.extend(plan.get("drills") or [])
    parts.extend(plan.get("coaching_cues") or [])
    return "\n".join(parts).lower()


def evaluate_plan(plan, expected):
    """Return a list of failure reasons; empty means PASS."""
    failures = []

    actual_duration = plan.get("duration_minutes")
    if actual_duration != expected["expected_duration_minutes"]:
        failures.append(
            "duration %r != expected %r"
            % (actual_duration, expected["expected_duration_minutes"])
        )

    drills = plan.get("drills") or []
    if len(drills) < expected["min_drills"]:
        failures.append(
            "only %d drill(s), need at least %d"
            % (len(drills), expected["min_drills"])
        )

    text = instructional_text(plan)
    for term in expected.get("required_terms", []):
        if term.lower() not in text:
            failures.append("required term missing: %r" % term)
    for term in expected.get("forbidden_terms", []):
        if term.lower() in text:
            failures.append("forbidden term present: %r" % term)

    return failures


def evaluate_case(case):
    plan = generate_rule_based_lesson_plan(**case["input"])
    failures = evaluate_plan(plan, case["expected"])
    return {
        "id": case["id"],
        "passed": not failures,
        "failures": failures,
    }


def main():
    cases = load_cases()
    results = [evaluate_case(case) for case in cases]

    for result in results:
        if result["passed"]:
            print("PASS %s" % result["id"])
        else:
            print("FAIL %s" % result["id"])
            for failure in result["failures"]:
                print("  - %s" % failure)

    passed = sum(1 for result in results if result["passed"])
    print("%d/%d passed" % (passed, len(results)))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
