from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _no_live_ollama():
    with patch("app.generator.chat", side_effect=Exception("ollama disabled")):
        yield


def test_home_returns_frontend():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="planner-form"' in response.text
    assert "/static/app.js" in response.text


def test_frontend_assets_are_served():
    css_response = client.get("/static/styles.css")
    js_response = client.get("/static/app.js")

    assert css_response.status_code == 200
    assert js_response.status_code == 200
    assert "tennis" in js_response.text.lower() or "lesson" in js_response.text.lower()


def test_frontend_code_has_no_external_calls():
    js_response = client.get("/static/app.js")
    html_response = client.get("/")

    assert "ollama" not in js_response.text.lower()
    assert "ollama" not in html_response.text.lower()
    assert "https://" not in js_response.text
    assert "http://" not in js_response.text
    assert "https://" not in html_response.text


def test_page_request_shape_creates_plan():
    response = client.post(
        "/lesson-plans",
        json={
            "player_name": "Arjun",
            "level": "beginner",
            "goal": "Improve forehand consistency",
            "duration_minutes": 60,
        },
    )

    assert response.status_code == 201

    created = response.json()

    assert created["plan_content"]["generator"] == "rules"
    assert created["plan_content"]["title"] == "Beginner lesson for Arjun"
    assert created["plan_content"]["warmup"]
    assert len(created["plan_content"]["drills"]) >= 3
    assert len(created["plan_content"]["coaching_cues"]) >= 2
