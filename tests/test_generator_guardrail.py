import json
from types import SimpleNamespace
from unittest.mock import patch

from app.generator import generate_lesson_plan


def _ollama_response(plan_dict):
    return SimpleNamespace(
        message=SimpleNamespace(content=json.dumps(plan_dict))
    )


def _valid_ollama_plan(**overrides):
    plan = {
        "title": "Intermediate lesson for Arjun",
        "goal": "Improve serve consistency",
        "duration_minutes": 60,
        "warmup": "Dynamic movement and footwork.",
        "drills": [
            "Cooperative baseline rally with depth targets.",
            "Cross-court then down-the-line pattern drill.",
            "Serve plus first-ball attack pattern.",
        ],
        "coaching_cues": [
            "Recover to a balanced ready position.",
            "Focus on clean contact in front.",
        ],
        "generator": "ollama",
    }
    plan.update(overrides)
    return plan


def _generate_with_mocked_ollama(plan_dict):
    with patch(
        "app.generator.chat",
        return_value=_ollama_response(plan_dict),
    ):
        return generate_lesson_plan(
            player_name="Arjun",
            level="intermediate",
            goal="Improve serve consistency",
            duration_minutes=60,
        )


def test_clean_ollama_plan_passes_through():
    result = _generate_with_mocked_ollama(_valid_ollama_plan())

    assert result["generator"] == "ollama"


def test_banned_term_in_drills_falls_back_to_rules():
    plan = _valid_ollama_plan(
        drills=[
            "Practice third shot drop near the kitchen.",
            "Cross-court rally drill.",
            "Serve plus one pattern.",
        ]
    )
    result = _generate_with_mocked_ollama(plan)

    assert result["generator"] == "rules"
    assert result["title"] == "Intermediate lesson for Arjun"


def test_banned_terms_detected_case_insensitively():
    for banned_text in [
        "PICKLEBALL rally",
        "Third Shot Drop practice",
        "Stay out of the KITCHEN",
        "Work on your DINK",
        "Grab your PADDLE",
    ]:
        plan = _valid_ollama_plan(
            coaching_cues=[banned_text, "Recover to ready position."]
        )
        result = _generate_with_mocked_ollama(plan)

        assert result["generator"] == "rules", banned_text


def test_banned_term_in_title_goal_warmup_and_cues_falls_back():
    cases = [
        {"title": "Pickleball basics for tennis players"},
        {"goal": "Learn to dink like a pro"},
        {"warmup": "Footwork around the kitchen line"},
        {"coaching_cues": ["Use your paddle face", "Stay balanced."]},
    ]
    for override in cases:
        result = _generate_with_mocked_ollama(_valid_ollama_plan(**override))

        assert result["generator"] == "rules", override


def test_ollama_error_still_falls_back_to_rules():
    with patch("app.generator.chat", side_effect=Exception("ollama down")):
        result = generate_lesson_plan(
            player_name="Arjun",
            level="intermediate",
            goal="Improve serve consistency",
            duration_minutes=60,
        )

    assert result["generator"] == "rules"
