import os
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(
    os.getenv("DATABASE_PATH", "tennis_planner.db")
)


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS lesson_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            level TEXT NOT NULL,
            goal TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            plan_content TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    existing_columns = {
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(lesson_plans)"
        ).fetchall()
    }

    if "plan_content" not in existing_columns:
        connection.execute(
            """
            ALTER TABLE lesson_plans
            ADD COLUMN plan_content TEXT NOT NULL DEFAULT '{}'
            """
        )

    connection.commit()
    connection.close()