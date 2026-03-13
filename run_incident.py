"""Run rescue model from incident JSON and persist results."""

from __future__ import annotations

import json
"""Run the rescue model from incident.json and persist outputs to SQLite."""

from __future__ import annotations

from pathlib import Path

from incident_store import (
    load_incident_json,
    open_database,
    replace_victim_priorities,
    save_entry_recommendation,
    upsert_incident,
)
from rescue_ai_model import (
    DisasterRescueModel,
    EntryPoint,
    EnvironmentSnapshot,
    InjuryLevel,
    VictimDetection,
)


def main(incident_path: str = "incident.example.json", db_path: str = "rescue_ops.db") -> None:
    incident = load_incident_json(incident_path)
    model = DisasterRescueModel()

    env = incident["environment"]
    environment = EnvironmentSnapshot(
        smoke_density=float(env["smoke_density"]),
        heat_level=float(env["heat_level"]),
        structural_instability=float(env["structural_instability"]),
        toxic_gas_probability=float(env["toxic_gas_probability"]),
    )

    detections = [
        VictimDetection(
            victim_id=v["victim_id"],
            x=float(v["x"]),
            y=float(v["y"]),
            breathing_score=float(v["breathing_score"]),
            movement_score=float(v["movement_score"]),
            bleeding_probability=float(v["bleeding_probability"]),
            trapped_probability=float(v["trapped_probability"]),
            injury_level=InjuryLevel[v["injury_level"]],
        )
        for v in incident.get("victim_detections", [])
    ]

    entry_points = [
        EntryPoint(
            name=e["name"],
            x=float(e["x"]),
            y=float(e["y"]),
            blockage_risk=float(e["blockage_risk"]),
            structural_risk=float(e["structural_risk"]),
            visibility_score=float(e["visibility_score"]),
            navigation_clearance=float(e["navigation_clearance"]),
            distance_to_victims=float(e.get("distance_to_victims", 0.0)),
        )
        for e in incident.get("entry_points", [])
    ]

    normalized = model.process_stream(detections)
    priorities = model.prioritize_victims(normalized, environment)
    best_entry = model.suggest_entry_point(entry_points, priorities, environment)
    environment_risk = model.compute_environment_risk(environment)

    conn = open_database(db_path)
    try:
        upsert_incident(conn, incident, environment_risk)
    priorities = model.prioritize_victims(normalized)
    best_entry = model.suggest_entry_point(entry_points, priorities)

    conn = open_database(db_path)
    try:
        upsert_incident(conn, incident)
        replace_victim_priorities(
            conn,
            incident_id=incident["incident_id"],
            rows=[
                {
                    "victim_id": p.victim.victim_id,
                    "priority_rank": rank,
                    "priority_score": p.score,
                    "risk_factor": p.risk_factor,
                    "safe_minutes": p.estimated_safe_minutes,
                    "rationale": p.rationale,
                    "x": p.victim.x,
                    "y": p.victim.y,
                }
                for rank, p in enumerate(priorities, start=1)
            ],
        )
        save_entry_recommendation(
            conn,
            incident_id=incident["incident_id"],
            recommendation={
                "entry_name": best_entry.entry_point.name,
                "score": best_entry.score,
                "rationale": best_entry.rationale,
                "checkpoints_json": json.dumps(best_entry.checkpoints),
                "x": best_entry.entry_point.x,
                "y": best_entry.entry_point.y,
                "blockage_risk": best_entry.entry_point.blockage_risk,
                "structural_risk": best_entry.entry_point.structural_risk,
            },
        )
    finally:
        conn.close()

    print(f"Saved incident {incident['incident_id']} to {Path(db_path).resolve()}")


if __name__ == "__main__":
    main()
