from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Dict, Iterable, List, Tuple
import json


@dataclass(frozen=True)
class VictimSignal:
    """Signals extracted from drone/live video for one victim."""

    victim_id: str
    location: Tuple[int, int]
    injury_severity: float  # 0.0 (none) to 1.0 (critical)
    consciousness: float  # 0.0 (unconscious) to 1.0 (fully conscious)
    mobility: float  # 0.0 (no movement) to 1.0 (walking)
    nearby_hazard: float  # 0.0 (safe) to 1.0 (very risky)
    estimated_minutes_to_decline: float


class VictimPrioritizer:
    """Create an ordered rescue stack from victim signals."""

    def score(self, signal: VictimSignal) -> float:
        # Higher score => rescue first.
        urgency = signal.injury_severity * 0.35
        unconscious_risk = (1 - signal.consciousness) * 0.20
        immobility = (1 - signal.mobility) * 0.15
        hazard = signal.nearby_hazard * 0.20
        time_pressure = max(0.0, 1 - (signal.estimated_minutes_to_decline / 60.0)) * 0.10
        return urgency + unconscious_risk + immobility + hazard + time_pressure

    def build_priority_stack(self, victims: Iterable[VictimSignal]) -> List[Dict]:
        ranked = sorted(victims, key=self.score, reverse=True)
        return [
            {
                "victim_id": v.victim_id,
                "location": v.location,
                "priority_score": round(self.score(v), 4),
            }
            for v in ranked
        ]


class EntryPointAnalyzer:
    """Suggest best entry points using a risk-aware shortest path search."""

    def _neighbors(self, x: int, y: int, width: int, height: int):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                yield nx, ny

    def _path_cost(
        self,
        grid: List[List[float]],
        start: Tuple[int, int],
        target: Tuple[int, int],
    ) -> float:
        width, height = len(grid[0]), len(grid)
        pq = [(0.0, start)]
        dist = {start: 0.0}

        while pq:
            cost, node = heappop(pq)
            if node == target:
                return cost
            if cost > dist[node]:
                continue

            x, y = node
            for nx, ny in self._neighbors(x, y, width, height):
                cell_risk = grid[ny][nx]
                if cell_risk >= 1.0:  # blocked cell
                    continue
                next_cost = cost + 1 + cell_risk * 5
                if next_cost < dist.get((nx, ny), float("inf")):
                    dist[(nx, ny)] = next_cost
                    heappush(pq, (next_cost, (nx, ny)))

        return float("inf")

    def best_entries(
        self,
        risk_grid: List[List[float]],
        candidate_entries: List[Tuple[int, int]],
        victim_locations: List[Tuple[int, int]],
        top_k: int = 3,
    ) -> List[Dict]:
        suggestions = []
        for entry in candidate_entries:
            travel_costs = [self._path_cost(risk_grid, entry, v) for v in victim_locations]
            reachable = [c for c in travel_costs if c != float("inf")]
            if not reachable:
                continue
            score = sum(reachable) / len(reachable)
            suggestions.append(
                {
                    "entry_point": entry,
                    "avg_rescue_cost": round(score, 3),
                    "reachable_victims": len(reachable),
                }
            )

        return sorted(suggestions, key=lambda s: (s["avg_rescue_cost"], -s["reachable_victims"]))[:top_k]


class RescueCoordinator:
    """Main orchestrator for uploaded videos or drone live streams."""

    def __init__(self):
        self.prioritizer = VictimPrioritizer()
        self.entry_analyzer = EntryPointAnalyzer()

    def process_incident(
        self,
        source: str,
        victims: Iterable[VictimSignal],
        risk_grid: List[List[float]],
        candidate_entries: List[Tuple[int, int]],
    ) -> Dict:
        victims = list(victims)
        priority_stack = self.prioritizer.build_priority_stack(victims)
        entries = self.entry_analyzer.best_entries(
            risk_grid=risk_grid,
            candidate_entries=candidate_entries,
            victim_locations=[v.location for v in victims],
        )
        return {
            "source": source,
            "victim_priority_stack": priority_stack,
            "recommended_entry_points": entries,
        }


def _load_signals(data: List[Dict]) -> List[VictimSignal]:
    return [VictimSignal(**item) for item in data]


def main() -> None:
    """Simple CLI: python -m src.rescue_ai incident.json"""
    import argparse

    parser = argparse.ArgumentParser(description="Disaster rescue triage prototype")
    parser.add_argument("incident_file", help="Path to incident JSON")
    args = parser.parse_args()

    with open(args.incident_file, "r", encoding="utf-8") as f:
        payload = json.load(f)

    coordinator = RescueCoordinator()
    result = coordinator.process_incident(
        source=payload["source"],
        victims=_load_signals(payload["victims"]),
        risk_grid=payload["risk_grid"],
        candidate_entries=[tuple(p) for p in payload["candidate_entries"]],
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
