"""Minimal API layer for deployment/demo usage."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from incident_store import (
    open_database,
    replace_victim_priorities,
    save_entry_recommendation,
    upsert_incident,
)
from rescue_ai_model import DisasterRescueModel, EntryPoint, InjuryLevel, VictimDetection

app = FastAPI(title="Disaster Rescue AI", version="0.1.0")


class Source(BaseModel):
    type: str = "unknown"
    uri: str | None = None


class VictimDetectionIn(BaseModel):
    victim_id: str
    x: float
    y: float
    breathing_score: float = Field(ge=0, le=1)
    movement_score: float = Field(ge=0, le=1)
    bleeding_probability: float = Field(ge=0, le=1)
    trapped_probability: float = Field(ge=0, le=1)
    injury_level: str


class EntryPointIn(BaseModel):
    name: str
    x: float
    y: float
    blockage_risk: float = Field(ge=0, le=1)
    structural_risk: float = Field(ge=0, le=1)
    distance_to_victims: float = 0


class IncidentIn(BaseModel):
    incident_id: str
    status: str = "active"
    source: Source = Source()
    victim_detections: list[VictimDetectionIn]
    entry_points: list[EntryPointIn]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run-incident")
def run_incident(payload: IncidentIn) -> dict:
    model = DisasterRescueModel()

    try:
        detections = [
            VictimDetection(
                victim_id=v.victim_id,
                x=v.x,
                y=v.y,
                breathing_score=v.breathing_score,
                movement_score=v.movement_score,
                bleeding_probability=v.bleeding_probability,
                trapped_probability=v.trapped_probability,
                injury_level=InjuryLevel[v.injury_level],
            )
            for v in payload.victim_detections
        ]
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown injury_level: {exc}") from exc

    if not payload.entry_points:
        raise HTTPException(status_code=400, detail="entry_points cannot be empty")

    entry_points = [
        EntryPoint(
            name=e.name,
            x=e.x,
            y=e.y,
            blockage_risk=e.blockage_risk,
            structural_risk=e.structural_risk,
            distance_to_victims=e.distance_to_victims,
        )
        for e in payload.entry_points
    ]

    priorities = model.prioritize_victims(model.process_stream(detections))
    best_entry = model.suggest_entry_point(entry_points, priorities)

    conn = open_database("rescue_ops.db")
    try:
        upsert_incident(conn, payload.model_dump())
        replace_victim_priorities(
            conn,
            incident_id=payload.incident_id,
            rows=[
                {
                    "victim_id": p.victim.victim_id,
                    "priority_rank": rank,
                    "priority_score": p.score,
                    "rationale": p.rationale,
                    "x": p.victim.x,
                    "y": p.victim.y,
                }
                for rank, p in enumerate(priorities, start=1)
            ],
        )
        save_entry_recommendation(
            conn,
            incident_id=payload.incident_id,
            recommendation={
                "entry_name": best_entry.entry_point.name,
                "score": best_entry.score,
                "rationale": best_entry.rationale,
                "x": best_entry.entry_point.x,
                "y": best_entry.entry_point.y,
                "blockage_risk": best_entry.entry_point.blockage_risk,
                "structural_risk": best_entry.entry_point.structural_risk,
            },
        )
    finally:
        conn.close()

    return {
        "incident_id": payload.incident_id,
        "priorities": [
            {
                "rank": rank,
                "victim_id": p.victim.victim_id,
                "score": p.score,
                "rationale": p.rationale,
            }
            for rank, p in enumerate(priorities, start=1)
        ],
        "entry_recommendation": {
            "name": best_entry.entry_point.name,
            "score": best_entry.score,
            "rationale": best_entry.rationale,
        },
    }
