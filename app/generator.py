from ollama import chat
from pydantic import BaseModel, Field

from app.templates import LESSON_PLANS


class GeneratedLessonPlan(BaseModel):
    title: str
    goal: str
    duration_minutes: int = Field(ge=30, le=180)
    warmup: str
    drills: list[str] = Field(min_length=3, max_length=6)
    coaching_cues: list[str] = Field(min_length=2, max_length=4)
    generator: str


BANNED_TERMS = [
    "pickleball",
    "third shot drop",
    "kitchen",
    "dink",
    "paddle",
]


def _plan_text_for_guardrail(plan: GeneratedLessonPlan) -> str:
    parts = [
        plan.title,
        plan.goal,
        plan.warmup,
        *plan.drills,
        *plan.coaching_cues,
    ]
    return "\n".join(parts).lower()


def contains_banned_term(plan: GeneratedLessonPlan) -> bool:
    text = _plan_text_for_guardrail(plan)
    return any(term in text for term in BANNED_TERMS)


def generate_rule_based_lesson_plan(
    player_name: str,
    level: str,
    goal: str,
    duration_minutes: int,
):
    template = LESSON_PLANS[level]

    return {
        "title": f"{level.title()} lesson for {player_name}",
        "goal": goal,
        "duration_minutes": duration_minutes,
        "warmup": template["warmup"],
        "drills": template["drills"],
        "coaching_cues": template["coaching_cues"],
        "generator": "rules",
    }


def generate_lesson_plan(
    player_name: str,
    level: str,
    goal: str,
    duration_minutes: int,
):
    fallback_plan = generate_rule_based_lesson_plan(
        player_name=player_name,
        level=level,
        goal=goal,
        duration_minutes=duration_minutes,
    )

    try:
        response = chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a certified tennis coach. Create safe, "
                        "age-neutral, practical tennis lesson plans. Do not "
                        "give medical advice or training that could be unsafe. "
                        "Return only valid JSON that follows the provided schema."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Create a {duration_minutes}-minute {level} tennis lesson "
                        f"for {player_name}. The player's goal is: {goal}. "
                        "Include one warmup, 3 to 6 drills, and 2 to 4 coaching cues. "
                        'Set the generator field to "ollama".'
                    ),
                },
            ],
            format=GeneratedLessonPlan.model_json_schema(),
            options={
                "temperature": 0.4,
            },
        )

        generated_plan = GeneratedLessonPlan.model_validate_json(
            response.message.content
        )

        if contains_banned_term(generated_plan):
            return fallback_plan

        return generated_plan.model_dump()

    except Exception:
        return fallback_plan