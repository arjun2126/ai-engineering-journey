# Tennis Lesson Planner API

A Python FastAPI backend that creates, validates, generates, and stores tennis
lesson plans based on a player's skill level, training goal, and lesson duration.

## What it does

- Provides built-in lesson-plan templates for beginner, intermediate, and advanced players
- Validates player name, level, goal, and lesson duration
- Generates a structured lesson plan using rule-based templates
- Saves lesson plans in SQLite
- Retrieves individual saved plans or a list of saved plans
- Includes automated API tests
- Runs locally or inside Docker

## Architecture

```text
Client / Swagger Docs
        |
        v
FastAPI API
        |
        +--> Input validation with Pydantic
        |
        +--> Rule-based lesson generator
        |
        v
SQLite database
        |
        v
JSON response
```

## Project structure

```text
app/
  main.py        API routes and request handling
  database.py    SQLite connection and database initialization
  generator.py   Rule-based lesson-plan generation
  templates.py   Built-in plans by skill level

tests/
  test_main.py   Automated API tests
```

## Requirements

- Python 3.14+
- Docker Desktop, optional
- Git

## Local setup

```bash
git clone [https://github.com/arjun2126/ai-engineering-journey.git](https://github.com/arjun2126/ai-engineering-journey.git)
cd ai-engineering-journey

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the automatic API documentation:

```text
http://127.0.0.1:8000/docs
```

## Run tests

```bash
python -m pytest -v
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks whether the API is running |
| GET | `/lesson-plan?level=beginner` | Gets a built-in lesson-plan template |
| POST | `/lesson-plans` | Generates and saves a lesson plan |
| GET | `/lesson-plans` | Lists saved lesson plans |
| GET | `/lesson-plans/{lesson_plan_id}` | Gets one saved lesson plan |

## Example request

```json
{
  "player_name": "Arjun",
  "level": "intermediate",
  "goal": "Improve serve consistency and attack the next ball",
  "duration_minutes": 60
}
```

## Example response

```json
{
  "id": 1,
  "player_name": "Arjun",
  "level": "intermediate",
  "goal": "Improve serve consistency and attack the next ball",
  "duration_minutes": 60,
  "plan_content": {
    "title": "Intermediate lesson for Arjun",
    "generator": "rules"
  }
}
```

## Docker

Build the image:

```bash
docker build -t tennis-lesson-planner-api .
```

Run it with a persistent Docker volume:

```bash
docker volume create tennis-planner-data

docker run --rm -p 8000:8000 \
  -e DATABASE_PATH=/app/data/tennis_planner.db \
  -v tennis-planner-data:/app/data \
  tennis-lesson-planner-api
```

Open:

```text
http://localhost:8000/docs
```

## Next steps

- Replace or enhance the rule-based generator with an LLM
- Add structured AI output validation
- Add evaluation test cases for generated plans
- Move from SQLite to PostgreSQL for production deployment
- Add authentication and user accounts