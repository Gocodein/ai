"""Persistence helpers for incident inputs/outputs."""
"""Persistence helpers for disaster rescue outputs.

Use this module to:
1) load an incident input from `incident.json`,
2) store incident metadata + model outputs in SQLite.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable
from typing import Any, Dict, Iterable, List


def load_incident_json(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "incident_id" not in data:
        raise ValueError("incident.json must include incident_id")
    if "environment" not in data:
        raise ValueError("incident.json must include environment")
    return data


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            source_uri TEXT,
            status TEXT DEFAULT 'active',
            environment_risk REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS victim_priorities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT NOT NULL,
            victim_id TEXT NOT NULL,
            priority_rank INTEGER NOT NULL,
            priority_score REAL NOT NULL,
            risk_factor REAL NOT NULL,
            safe_minutes REAL NOT NULL,
            rationale TEXT NOT NULL,
            x REAL,
            y REAL,
            FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
        );

        CREATE TABLE IF NOT EXISTS entry_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT NOT NULL,
            entry_name TEXT NOT NULL,
            score REAL NOT NULL,
            rationale TEXT NOT NULL,
            checkpoints_json TEXT,
            x REAL,
            y REAL,
            blockage_risk REAL,
            structural_risk REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
        );
        """
    )
    conn.commit()


def upsert_incident(conn: sqlite3.Connection, incident: Dict[str, Any], environment_risk: float) -> None:
    conn.execute(
        """
        INSERT INTO incidents (incident_id, source_type, source_uri, status, environment_risk)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(incident_id) DO UPDATE SET
            source_type=excluded.source_type,
            source_uri=excluded.source_uri,
            status=excluded.status,
            environment_risk=excluded.environment_risk
def upsert_incident(conn: sqlite3.Connection, incident: Dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO incidents (incident_id, source_type, source_uri, status)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(incident_id) DO UPDATE SET
            source_type=excluded.source_type,
            source_uri=excluded.source_uri,
            status=excluded.status
        """,
        (
            incident["incident_id"],
            incident.get("source", {}).get("type", "unknown"),
            incident.get("source", {}).get("uri"),
            incident.get("status", "active"),
            environment_risk,
        ),
    )
    conn.commit()


def replace_victim_priorities(conn: sqlite3.Connection, incident_id: str, rows: Iterable[Dict[str, Any]]) -> None:
    conn.execute("DELETE FROM victim_priorities WHERE incident_id = ?", (incident_id,))
    conn.executemany(
        """
        INSERT INTO victim_priorities
        (incident_id, victim_id, priority_rank, priority_score, risk_factor, safe_minutes, rationale, x, y)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        (incident_id, victim_id, priority_rank, priority_score, rationale, x, y)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                incident_id,
                row["victim_id"],
                row["priority_rank"],
                row["priority_score"],
                row["risk_factor"],
                row["safe_minutes"],
                row["rationale"],
                row.get("x"),
                row.get("y"),
            )
            for row in rows
        ],
    )
    conn.commit()


def save_entry_recommendation(conn: sqlite3.Connection, incident_id: str, recommendation: Dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO entry_recommendations
        (incident_id, entry_name, score, rationale, checkpoints_json, x, y, blockage_risk, structural_risk)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        (incident_id, entry_name, score, rationale, x, y, blockage_risk, structural_risk)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            incident_id,
            recommendation["entry_name"],
            recommendation["score"],
            recommendation["rationale"],
            recommendation.get("checkpoints_json"),
            recommendation.get("x"),
            recommendation.get("y"),
            recommendation.get("blockage_risk"),
            recommendation.get("structural_risk"),
        ),
    )
    conn.commit()


def open_database(path: str | Path = "rescue_ops.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    init_db(conn)
    return conn
