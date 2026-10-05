from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_beginner_lesson_plan():
    response = client.get("/lesson-plan?level=beginner")

    assert response.status_code == 200

    data = response.json()
    assert data["level"] == "beginner"
    assert data["plan"]["duration_minutes"] == 60
    assert len(data["plan"]["drills"]) > 0


def test_invalid_lesson_level():
    response = client.get("/lesson-plan?level=expert")

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Level must be beginner, intermediate, or advanced."
    )


def test_create_and_get_saved_lesson_plan():
    create_response = client.post(
        "/lesson-plans",
        json={
            "player_name": "Arjun",
            "level": "intermediate",
            "goal": "Improve serve consistency",
            "duration_minutes": 60,
        },
    )

    assert create_response.status_code == 201

    created_plan = create_response.json()

    assert created_plan["player_name"] == "Arjun"
    assert created_plan["level"] == "intermediate"
    assert created_plan["goal"] == "Improve serve consistency"
    assert created_plan["plan_content"]["generator"] == "rules"
    assert created_plan["plan_content"]["title"] == (
        "Intermediate lesson for Arjun"
    )

    lesson_plan_id = created_plan["id"]

    get_response = client.get(f"/lesson-plans/{lesson_plan_id}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == lesson_plan_id


def test_list_saved_lesson_plans():
    client.post(
        "/lesson-plans",
        json={
            "player_name": "Arjun",
            "level": "beginner",
            "goal": "Improve forehand consistency",
            "duration_minutes": 60,
        },
    )

    response = client.get("/lesson-plans?limit=10")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_invalid_lesson_duration():
    response = client.post(
        "/lesson-plans",
        json={
            "player_name": "Arjun",
            "level": "beginner",
            "goal": "Improve forehand consistency",
            "duration_minutes": 10,
        },
    )

    assert response.status_code == 422