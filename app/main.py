from app.database import get_connection, initialize_database
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="Tennis Lesson Planner API",
    description="Creates and saves tennis practice plans by player skill level.",
    version="0.3.0",
)


@app.on_event("startup")
def startup():
    initialize_database()


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
    player_name: str = Field(
        min_length=2,
        max_length=100,
        description="Name of the player.",
    )
    level: str
    goal: str = Field(
        min_length=5,
        max_length=500,
        description="The player's training goal.",
    )
    duration_minutes: int = Field(
        default=60,
        ge=30,
        le=180,
        description="Lesson duration from 30 to 180 minutes.",
    )


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


@app.post("/lesson-plans", status_code=201)
def create_lesson_plan(request: LessonRequest):
    normalized_level = request.level.lower().strip()

    if normalized_level not in LESSON_PLANS:
        raise HTTPException(
            status_code=400,
            detail="Level must be beginner, intermediate, or advanced.",
        )

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO lesson_plans (
            player_name,
            level,
            goal,
            duration_minutes
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            request.player_name.strip(),
            normalized_level,
            request.goal.strip(),
            request.duration_minutes,
        ),
    )

    connection.commit()

    lesson_plan_id = cursor.lastrowid

    row = connection.execute(
        "SELECT * FROM lesson_plans WHERE id = ?",
        (lesson_plan_id,),
    ).fetchone()

    connection.close()

    return dict(row)


@app.get("/lesson-plans")
def list_lesson_plans(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of saved lesson plans to return.",
    )
):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM lesson_plans
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


@app.get("/lesson-plans/{lesson_plan_id}")
def get_saved_lesson_plan(lesson_plan_id: int):
    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM lesson_plans WHERE id = ?",
        (lesson_plan_id,),
    ).fetchone()

    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson plan not found.",
        )

    return dict(row)