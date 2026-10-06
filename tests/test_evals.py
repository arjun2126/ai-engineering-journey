from unittest.mock import patch

import pytest

from evals.run_evals import evaluate_case, evaluate_plan, load_cases


@pytest.fixture(autouse=True)
def _ollama_must_not_be_called():
    with patch(
        "app.generator.chat",
        side_effect=AssertionError("eval path must not call Ollama"),
    ):
        yield


def _clean_plan(**overrides):
    plan = {
        "title": "Beginner lesson for Ava",
        "goal": "Improve serve toss",
        "duration_minutes": 30,
        "warmup": "5 minutes of light jogging and dynamic movement.",
        "drills": [
            "10 minutes: self-drop forehand and backhand rallies.",
            "15 minutes: mini-tennis from the service boxes.",
            "15 minutes: cross-court consistency drill.",
        ],
        "coaching_cues": [
            "Recover to a balanced ready position after every shot.",
        ],
        "generator": "rules",
    }
    plan.update(overrides)
    return plan


def _expected(**overrides):
    expected = {
        "required_terms": ["serve"],
        "forbidden_terms": ["pickleball", "dink"],
        "min_drills": 3,
        "expected_duration_minutes": 30,
    }
    expected.update(overrides)
    return expected


def test_all_eval_cases_pass_offline():
    cases = load_cases()

    assert len(cases) == 10

    for case in cases:
        result = evaluate_case(case)

        assert result["passed"], "%s: %s" % (result["id"], result["failures"])


def test_forbidden_term_in_drills_is_detected():
    plan = _clean_plan(
        drills=["Practice your dink at the net.", "Cross-court rally drill."]
    )

    failures = evaluate_plan(plan, _expected())

    assert any("forbidden term present: 'dink'" in f for f in failures)


def test_forbidden_term_match_is_case_insensitive():
    plan = _clean_plan(drills=["Welcome to PICKLEBALL night."])

    failures = evaluate_plan(
        plan, _expected(forbidden_terms=["pickleball"])
    )

    assert any("forbidden term present" in f for f in failures)


def test_missing_required_term_is_detected():
    failures = evaluate_plan(_clean_plan(), _expected(required_terms=["volley"]))

    assert any("required term missing: 'volley'" in f for f in failures)


def test_wrong_duration_is_detected():
    failures = evaluate_plan(
        _clean_plan(duration_minutes=45), _expected()
    )

    assert any("duration 45 != expected 30" in f for f in failures)


def test_too_few_drills_is_detected():
    plan = _clean_plan(drills=["Only one drill."])

    failures = evaluate_plan(plan, _expected())

    assert any("need at least 3" in f for f in failures)


def test_adversarial_goal_outside_instructional_content_is_not_flagged():
    plan = _clean_plan(goal="Stop popping up the dink")

    failures = evaluate_plan(
        plan, _expected(required_terms=["forehand"])
    )

    assert failures == []
