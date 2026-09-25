"""Privacy-minimized persistence for anonymous product analytics."""

from __future__ import annotations

import datetime
import hashlib
import os
import secrets
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv

PACKAGE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PACKAGE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")


def _timestamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _env_is_configured(*names: str) -> bool:
    return all(os.getenv(name) for name in names)


def _placeholder_sql(sql: str, dialect: str) -> str:
    return sql.replace("%s", "?") if dialect == "sqlite" else sql


def hash_admin_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )
    return f"{salt.hex()}${digest.hex()}"


def verify_admin_password(password: str, encoded_hash: str) -> bool:
    try:
        salt_hex, expected_hex = encoded_hash.split("$", 1)
        actual = hash_admin_password(password, bytes.fromhex(salt_hex)).split("$", 1)[1]
        return secrets.compare_digest(actual, expected_hex)
    except (ValueError, TypeError):
        return False


def parse_admin_credentials() -> dict[str, str]:
    username = os.getenv("ADMIN_USERNAME", "").strip()
    password_hash = os.getenv("ADMIN_PASSWORD_HASH", "").strip()
    return {username: password_hash} if username and password_hash else {}


@dataclass
class FrontendDatabase:
    connection: object
    dialect: str
    status_message: str | None = None
    analytics_enabled: bool = True

    def execute(self, sql: str, params=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(_placeholder_sql(sql, self.dialect), params)
            return cursor
        except Exception:
            cursor.close()
            raise

    def fetch_all(self, sql: str, params=()):
        cursor = self.execute(sql, params)
        try:
            return cursor.fetchall()
        finally:
            cursor.close()

    def read_dataframe(self, sql: str) -> pd.DataFrame:
        cursor = self.execute(sql)
        try:
            columns = [column[0] for column in cursor.description]
            return pd.DataFrame(cursor.fetchall(), columns=columns)
        finally:
            cursor.close()

    def initialize(self):
        id_type = "SERIAL PRIMARY KEY" if self.dialect == "postgres" else "INTEGER PRIMARY KEY AUTOINCREMENT"
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS analysis_events (
                    id {id_type},
                    event_token TEXT NOT NULL,
                    resume_score INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    page_count INTEGER NOT NULL,
                    career_track TEXT NOT NULL,
                    candidate_level TEXT NOT NULL,
                    detected_skills TEXT NOT NULL,
                    recommended_skills TEXT NOT NULL,
                    recommended_courses TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS feedback (
                    id {id_type},
                    score INTEGER NOT NULL,
                    comments TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            self.connection.commit()
        finally:
            cursor.close()

    def save_analysis(self, event: dict) -> bool:
        if not self.analytics_enabled:
            return False
        cursor = self.execute(
            """
            INSERT INTO analysis_events
            (event_token, resume_score, timestamp, page_count, career_track,
             candidate_level, detected_skills, recommended_skills, recommended_courses)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                event["event_token"],
                event["resume_score"],
                event["timestamp"],
                event["page_count"],
                event["career_track"],
                event["candidate_level"],
                event["detected_skills"],
                event["recommended_skills"],
                event["recommended_courses"],
            ),
        )
        cursor.close()
        self.connection.commit()
        return True

    def save_feedback(self, *, score: int, comments: str):
        cursor = self.execute(
            "INSERT INTO feedback (score, comments, timestamp) VALUES (%s,%s,%s)",
            (score, comments.strip(), _timestamp()),
        )
        cursor.close()
        self.connection.commit()

    def load_feedback(self) -> pd.DataFrame:
        rows = self.fetch_all("SELECT id, score, comments, timestamp FROM feedback")
        return pd.DataFrame(rows, columns=["ID", "Feedback Score", "Comments", "Timestamp"])

    def load_admin_frames(self):
        rows = self.fetch_all(
            """
            SELECT id, resume_score, career_track, candidate_level, timestamp,
                   page_count, detected_skills, recommended_skills, recommended_courses
            FROM analysis_events
            """
        )
        events = pd.DataFrame(
            rows,
            columns=[
                "ID",
                "Resume Score",
                "Career Track",
                "Candidate Level",
                "Timestamp",
                "Page Count",
                "Detected Skills",
                "Recommended Skills",
                "Recommended Courses",
            ],
        )
        plot_data = events.rename(
            columns={
                "Resume Score": "resume_score",
                "Career Track": "Predicted_Field",
                "Candidate Level": "User_Level",
            }
        )
        return plot_data, events, self.load_feedback()

    def clear_analytics(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM analysis_events")
            cursor.execute("DELETE FROM feedback")
            cursor.execute("DROP TABLE IF EXISTS user_data")
            cursor.execute("DROP TABLE IF EXISTS user_feedback")
            self.connection.commit()
        finally:
            cursor.close()


def _connect_sqlite(analytics_enabled: bool):
    db_path = os.getenv("SQLITE_DB_PATH") or str(PROJECT_ROOT / "data" / "resume_analyzer.db")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, check_same_thread=False)
    message = (
        "Anonymous analytics are enabled."
        if analytics_enabled
        else "Analytics storage is disabled by default; resume content is not retained."
    )
    return FrontendDatabase(connection, "sqlite", message, analytics_enabled)


@st.cache_resource
def get_database() -> FrontendDatabase:
    analytics_enabled = os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"
    postgres_env = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    if analytics_enabled and _env_is_configured(*postgres_env):
        try:
            database = FrontendDatabase(
                psycopg2.connect(
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT"),
                    database=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                ),
                "postgres",
                "Anonymous analytics are enabled with PostgreSQL.",
                True,
            )
        except Exception:
            database = _connect_sqlite(analytics_enabled)
            database.status_message = "PostgreSQL was unavailable; anonymous analytics use local SQLite."
    else:
        database = _connect_sqlite(analytics_enabled)
    database.initialize()
    return database


def build_analysis_event(*, analysis: dict, recommended_courses: list[str]) -> dict:
    candidate = analysis["candidate"]
    summary = analysis["summary"]
    return {
        "event_token": secrets.token_urlsafe(12),
        "resume_score": int(summary["resume_score"]),
        "timestamp": _timestamp(),
        "page_count": int(candidate.get("page_count", 0)),
        "career_track": str(summary["career_track"]),
        "candidate_level": str(candidate["candidate_level"]),
        "detected_skills": ", ".join(candidate.get("skills", [])),
        "recommended_skills": ", ".join(summary.get("recommended_skills", [])),
        "recommended_courses": ", ".join(recommended_courses),
    }
