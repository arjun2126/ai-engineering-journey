from app.templates import LESSON_PLANS


def generate_lesson_plan(
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