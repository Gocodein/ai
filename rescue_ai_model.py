"""Prototype disaster-response AI pipeline.

This module provides a practical baseline for three capabilities:
1) ingesting victim detections from uploaded video or a live drone stream,
2) producing a rescue-priority stack,
3) suggesting the safest and shortest entry point for rescue teams.

The implementation is intentionally dependency-light so you can adapt it into
any project stack.
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
class VictimDetection:
    """Represents a model detection from video/live stream frames."""

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
    """Priority output that can be pushed to field responders."""

    victim: VictimDetection
    score: float
    rationale: str


@dataclass(frozen=True)
class EntryPoint:
    """Candidate entry coordinates around impacted structure."""

    name: str
    x: float
    y: float
    blockage_risk: float
    structural_risk: float
    distance_to_victims: float


@dataclass(frozen=True)
class EntryRecommendation:
    entry_point: EntryPoint
    score: float
    rationale: str


class DisasterRescueModel:
    """Baseline decision model for disaster victim triage and entry planning."""

    def process_stream(self, detections: Iterable[VictimDetection]) -> List[VictimDetection]:
        """Validate and normalize detections from upload/live stream.

        In production, this method would perform: frame sampling, tracking,
        deduplication, confidence filtering, and temporal smoothing.
        """

        normalized: List[VictimDetection] = []
        for d in detections:
            self._validate_probability(d.breathing_score, "breathing_score")
            self._validate_probability(d.movement_score, "movement_score")
            self._validate_probability(d.bleeding_probability, "bleeding_probability")
            self._validate_probability(d.trapped_probability, "trapped_probability")
            normalized.append(d)
        return normalized

    def prioritize_victims(self, detections: Sequence[VictimDetection]) -> List[RescuePriority]:
        """Create a high-to-low rescue stack based on survivability + urgency."""

        priorities: List[RescuePriority] = []
        for d in detections:
            oxygen_risk = 1.0 - d.breathing_score
            immobility_risk = 1.0 - d.movement_score
            severity_weight = float(d.injury_level) / float(InjuryLevel.CRITICAL)

            score = (
                0.35 * severity_weight
                + 0.25 * d.bleeding_probability
                + 0.20 * d.trapped_probability
                + 0.10 * oxygen_risk
                + 0.10 * immobility_risk
            )
            rationale = (
                f"injury={d.injury_level.name}, bleeding={d.bleeding_probability:.2f}, "
                f"trapped={d.trapped_probability:.2f}, breathing_risk={oxygen_risk:.2f}"
            )
            priorities.append(RescuePriority(victim=d, score=score, rationale=rationale))

        priorities.sort(key=lambda p: p.score, reverse=True)
        return priorities

    def suggest_entry_point(
        self,
        candidate_points: Sequence[EntryPoint],
        high_priority_victims: Sequence[RescuePriority],
    ) -> EntryRecommendation:
        """Choose the best access point for rescue teams.

        Score balances safety and access speed.
        """

        if not candidate_points:
            raise ValueError("candidate_points cannot be empty")

        top_victims = [p.victim for p in high_priority_victims[:3]]
        evaluated: List[EntryRecommendation] = []
        for point in candidate_points:
            self._validate_probability(point.blockage_risk, "blockage_risk")
            self._validate_probability(point.structural_risk, "structural_risk")

            if top_victims:
                avg_distance = sum(self._distance(point.x, point.y, v.x, v.y) for v in top_victims) / len(top_victims)
            else:
                avg_distance = point.distance_to_victims

            access_score = 1.0 / (1.0 + avg_distance)
            safety_score = 1.0 - (0.55 * point.structural_risk + 0.45 * point.blockage_risk)
            score = 0.60 * safety_score + 0.40 * access_score

            rationale = (
                f"safety={safety_score:.2f}, access={access_score:.2f}, "
                f"avg_distance={avg_distance:.1f}"
            )
            evaluated.append(EntryRecommendation(entry_point=point, score=score, rationale=rationale))

        evaluated.sort(key=lambda e: e.score, reverse=True)
        return evaluated[0]

    @staticmethod
    def _distance(x1: float, y1: float, x2: float, y2: float) -> float:
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    @staticmethod
    def _validate_probability(value: float, name: str) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in [0, 1], got {value}")


def demo() -> None:
    """Run a tiny end-to-end scenario."""

    model = DisasterRescueModel()
    detections = model.process_stream(
        [
            VictimDetection("V-1", 20, 80, 0.30, 0.20, 0.85, 0.70, InjuryLevel.CRITICAL),
            VictimDetection("V-2", 60, 65, 0.70, 0.40, 0.40, 0.65, InjuryLevel.SEVERE),
            VictimDetection("V-3", 15, 30, 0.90, 0.75, 0.10, 0.20, InjuryLevel.MODERATE),
        ]
    )

    priorities = model.prioritize_victims(detections)
    points = [
        EntryPoint("North Gate", 10, 95, 0.25, 0.30, 20.0),
        EntryPoint("East Breach", 90, 70, 0.10, 0.65, 25.0),
        EntryPoint("Service Tunnel", 5, 40, 0.45, 0.20, 35.0),
    ]

    best_entry = model.suggest_entry_point(points, priorities)

    print("Rescue priority stack:")
    for rank, item in enumerate(priorities, start=1):
        print(f"{rank}. {item.victim.victim_id} -> score={item.score:.3f} ({item.rationale})")

    print("\nRecommended entry point:")
    print(f"{best_entry.entry_point.name} -> score={best_entry.score:.3f} ({best_entry.rationale})")


if __name__ == "__main__":
    demo()
