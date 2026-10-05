from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Tennis Lesson Planner API",
    description="Creates simple tennis practice plans by player skill level.",
    version="0.1.0",
)

LESSON_PLANS = {
    "beginner": {
        "duration_minutes": 60,
        "warmup": "5 minutes of light jogging and dynamic movement.",
        "drills": [
            "10 minutes: self-drop forehand and backhand rallies.",
            "15 minutes: mini-tennis from the service boxes.",
            "15 minutes: cross-court consistency drill.",
            "10 minutes: basic serve toss and service-motion practice.",
        ],
        "coaching_cues": [
            "Recover to a balanced ready position after every shot.",
            "Focus on clean contact in front of your body.",
        ],
    },
    "intermediate": {
        "duration_minutes": 60,
        "warmup": "5 minutes of dynamic movement and split-step footwork.",
        "drills": [
            "10 minutes: cooperative baseline rally with depth targets.",
            "15 minutes: cross-court then down-the-line pattern drill.",
            "15 minutes: serve plus first-ball attack pattern.",
            "10 minutes: point play starting with a serve.",
        ],
        "coaching_cues": [
            "Use your legs to create balance and controlled power.",
            "Recover toward the center after each shot.",
        ],
    },
    "advanced": {
        "duration_minutes": 75,
        "warmup": "10 minutes of dynamic movement, mobility, and reaction work.",
        "drills": [
            "15 minutes: high-tempo directional baseline patterns.",
            "20 minutes: serve-plus-one and return-plus-one situations.",
            "20 minutes: transition and net-play decision drills.",
            "10 minutes: pressure tiebreak scenarios.",
        ],
        "coaching_cues": [
            "Build points with a clear tactical intention.",
            "Use recovery position based on your opponent's likely reply.",
        ],
    },
}


class LessonRequest(BaseModel):
    level: str


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/lesson-plan")
def get_lesson_plan(level: str):
    normalized_level = level.lower().strip()

    if normalized_level not in LESSON_PLANS:
        raise HTTPException(
            status_code=400,
            detail="Level must be beginner, intermediate, or advanced.",
        )

    return {
        "level": normalized_level,
        "plan": LESSON_PLANS[normalized_level],
    }


@app.post("/lesson-plan")
def create_lesson_plan(request: LessonRequest):
    normalized_level = request.level.lower().strip()

    if normalized_level not in LESSON_PLANS:
        raise HTTPException(
            status_code=400,
            detail="Level must be beginner, intermediate, or advanced.",
        )

    return {
        "message": "Lesson plan created.",
        "level": normalized_level,
        "plan": LESSON_PLANS[normalized_level],
    }