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


def test_create_intermediate_lesson_plan():
    response = client.post(
        "/lesson-plan",
        json={"level": "intermediate"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Lesson plan created."
    assert data["level"] == "intermediate"