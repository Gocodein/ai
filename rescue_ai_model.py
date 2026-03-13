"""Disaster-response AI pipeline with triage + navigation planning.

Focus areas:
1) ingest detections from uploaded video/live drone feed,
2) compute per-victim risk factor and estimated safe window,
3) generate rescue priority stack,
4) recommend safest entry/navigation plan.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from math import sqrt
from typing import Iterable, List, Sequence


class InjuryLevel(IntEnum):
    """Estimated medical urgency of a detected victim."""

    CRITICAL = 4
    SEVERE = 3
    MODERATE = 2
    MINOR = 1


@dataclass(frozen=True)
class EnvironmentSnapshot:
    """Scene-level hazards inferred from camera + sensor cues."""

    smoke_density: float
    heat_level: float
    structural_instability: float
    toxic_gas_probability: float


@dataclass(frozen=True)
class VictimDetection:
    """Detection from FPV/mobile camera inference."""

    victim_id: str
    x: float
    y: float
    breathing_score: float
    movement_score: float
    bleeding_probability: float
    trapped_probability: float
    injury_level: InjuryLevel


@dataclass(frozen=True)
class RescuePriority:
    victim: VictimDetection
    score: float
    risk_factor: float
    estimated_safe_minutes: float
    rationale: str


@dataclass(frozen=True)
class EntryPoint:
    name: str
    x: float
    y: float
    blockage_risk: float
    structural_risk: float
    visibility_score: float
    navigation_clearance: float
    distance_to_victims: float


@dataclass(frozen=True)
class EntryRecommendation:
    entry_point: EntryPoint
    score: float
    checkpoints: list[tuple[float, float]]
    rationale: str


class DisasterRescueModel:
    """Decision model for triage and camera-driven navigation suggestion."""

    def process_stream(self, detections: Iterable[VictimDetection]) -> List[VictimDetection]:
        normalized: List[VictimDetection] = []
        for d in detections:
            self._validate_probability(d.breathing_score, "breathing_score")
            self._validate_probability(d.movement_score, "movement_score")
            self._validate_probability(d.bleeding_probability, "bleeding_probability")
            self._validate_probability(d.trapped_probability, "trapped_probability")
            normalized.append(d)
        return normalized

    def compute_environment_risk(self, env: EnvironmentSnapshot) -> float:
        self._validate_probability(env.smoke_density, "smoke_density")
        self._validate_probability(env.heat_level, "heat_level")
        self._validate_probability(env.structural_instability, "structural_instability")
        self._validate_probability(env.toxic_gas_probability, "toxic_gas_probability")

        return (
            0.30 * env.smoke_density
            + 0.25 * env.heat_level
            + 0.25 * env.structural_instability
            + 0.20 * env.toxic_gas_probability
        )

    def prioritize_victims(
        self,
        detections: Sequence[VictimDetection],
        environment: EnvironmentSnapshot,
    ) -> List[RescuePriority]:
        """Rank victims by urgency + survivability + environment danger."""

        env_risk = self.compute_environment_risk(environment)
        priorities: List[RescuePriority] = []

        for d in detections:
            oxygen_risk = 1.0 - d.breathing_score
            immobility_risk = 1.0 - d.movement_score
            severity_weight = float(d.injury_level) / float(InjuryLevel.CRITICAL)

            risk_factor = (
                0.32 * severity_weight
                + 0.22 * d.bleeding_probability
                + 0.18 * d.trapped_probability
                + 0.14 * oxygen_risk
                + 0.06 * immobility_risk
                + 0.08 * env_risk
            )

            # Simple interpretable safe-window estimation for demo.
            estimated_safe_minutes = max(2.0, 25.0 * (1.0 - risk_factor))

            rationale = (
                f"risk={risk_factor:.2f}, injury={d.injury_level.name}, "
                f"env={env_risk:.2f}, safe_minutes={estimated_safe_minutes:.1f}"
            )
            priorities.append(
                RescuePriority(
                    victim=d,
                    score=risk_factor,
                    risk_factor=risk_factor,
                    estimated_safe_minutes=estimated_safe_minutes,
                    rationale=rationale,
                )
            )

        priorities.sort(key=lambda p: p.score, reverse=True)
        return priorities

    def suggest_entry_point(
        self,
        candidate_points: Sequence[EntryPoint],
        high_priority_victims: Sequence[RescuePriority],
        environment: EnvironmentSnapshot,
    ) -> EntryRecommendation:
        if not candidate_points:
            raise ValueError("candidate_points cannot be empty")

        env_risk = self.compute_environment_risk(environment)
        top_victims = [p.victim for p in high_priority_victims[:3]]

        evaluated: list[EntryRecommendation] = []
        for point in candidate_points:
            self._validate_probability(point.blockage_risk, "blockage_risk")
            self._validate_probability(point.structural_risk, "structural_risk")
            self._validate_probability(point.visibility_score, "visibility_score")
            self._validate_probability(point.navigation_clearance, "navigation_clearance")

            if top_victims:
                avg_distance = sum(self._distance(point.x, point.y, v.x, v.y) for v in top_victims) / len(top_victims)
            else:
                avg_distance = point.distance_to_victims

            safety_score = 1.0 - (0.40 * point.structural_risk + 0.35 * point.blockage_risk + 0.25 * env_risk)
            camera_navigation_score = 0.55 * point.visibility_score + 0.45 * point.navigation_clearance
            access_score = 1.0 / (1.0 + avg_distance)
            total = 0.45 * safety_score + 0.30 * camera_navigation_score + 0.25 * access_score

            checkpoints = self._build_checkpoints(point, top_victims)
            rationale = (
                f"safety={safety_score:.2f}, nav={camera_navigation_score:.2f}, "
                f"access={access_score:.2f}, env={env_risk:.2f}"
            )
            evaluated.append(
                EntryRecommendation(
                    entry_point=point,
                    score=total,
                    checkpoints=checkpoints,
                    rationale=rationale,
                )
            )

        evaluated.sort(key=lambda e: e.score, reverse=True)
        return evaluated[0]

    @staticmethod
    def _build_checkpoints(point: EntryPoint, victims: Sequence[VictimDetection]) -> list[tuple[float, float]]:
        if not victims:
            return [(point.x, point.y)]
        target = victims[0]
        mid_x = (point.x + target.x) / 2
        mid_y = (point.y + target.y) / 2
        return [(point.x, point.y), (mid_x, mid_y), (target.x, target.y)]

    @staticmethod
    def _distance(x1: float, y1: float, x2: float, y2: float) -> float:
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    @staticmethod
    def _validate_probability(value: float, name: str) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in [0, 1], got {value}")


def demo() -> None:
    model = DisasterRescueModel()
    environment = EnvironmentSnapshot(0.6, 0.5, 0.45, 0.3)

    detections = model.process_stream(
        [
            VictimDetection("V-1", 20, 80, 0.30, 0.20, 0.85, 0.70, InjuryLevel.CRITICAL),
            VictimDetection("V-2", 60, 65, 0.70, 0.40, 0.40, 0.65, InjuryLevel.SEVERE),
            VictimDetection("V-3", 15, 30, 0.90, 0.75, 0.10, 0.20, InjuryLevel.MODERATE),
        ]
    )

    priorities = model.prioritize_victims(detections, environment)
    points = [
        EntryPoint("North Gate", 10, 95, 0.25, 0.30, 0.75, 0.70, 20.0),
        EntryPoint("East Breach", 90, 70, 0.10, 0.65, 0.60, 0.55, 25.0),
        EntryPoint("Service Tunnel", 5, 40, 0.45, 0.20, 0.80, 0.65, 35.0),
    ]

    best_entry = model.suggest_entry_point(points, priorities, environment)

    print("Rescue priority stack:")
    for rank, item in enumerate(priorities, start=1):
        print(
            f"{rank}. {item.victim.victim_id} -> risk={item.risk_factor:.3f}, "
            f"safe_minutes={item.estimated_safe_minutes:.1f} ({item.rationale})"
        )

    print("\nRecommended entry point:")
    print(f"{best_entry.entry_point.name} -> score={best_entry.score:.3f} ({best_entry.rationale})")
    print(f"Checkpoints: {best_entry.checkpoints}")


if __name__ == "__main__":
    demo()
