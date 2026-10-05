import json

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.database import get_connection, initialize_database
from app.generator import generate_lesson_plan
from app.templates import LESSON_PLANS

app = FastAPI(
    title="Tennis Lesson Planner API",
    description="Creates, generates, and saves tennis practice plans.",
    version="0.4.0",
)


@app.on_event("startup")
def startup():
    initialize_database()

initialize_database()
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


def serialize_lesson_plan(row):
    result = dict(row)
    result["plan_content"] = json.loads(result["plan_content"])
    return result


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

    player_name = request.player_name.strip()
    goal = request.goal.strip()

    generated_plan = generate_lesson_plan(
        player_name=player_name,
        level=normalized_level,
        goal=goal,
        duration_minutes=request.duration_minutes,
    )

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO lesson_plans (
            player_name,
            level,
            goal,
            duration_minutes,
            plan_content
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            player_name,
            normalized_level,
            goal,
            request.duration_minutes,
            json.dumps(generated_plan),
        ),
    )

    connection.commit()

    lesson_plan_id = cursor.lastrowid

    row = connection.execute(
        "SELECT * FROM lesson_plans WHERE id = ?",
        (lesson_plan_id,),
    ).fetchone()

    connection.close()

    return serialize_lesson_plan(row)


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

    return [serialize_lesson_plan(row) for row in rows]


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

    return serialize_lesson_plan(row)