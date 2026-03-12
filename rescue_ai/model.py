from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable, Iterable, List, Sequence, Tuple


GridPoint = Tuple[int, int]


@dataclass(frozen=True)
class VictimDetection:
    """Single victim metadata derived from a frame or thermal stream."""

    victim_id: str
    location: GridPoint
    injury_score: float
    mobility_score: float
    vital_risk_score: float
    obstruction_score: float

    def priority_score(self) -> float:
        """Compute urgency score where larger means "rescue earlier"."""

        injury_weight = 0.35
        mobility_weight = 0.20
        vital_weight = 0.30
        obstruction_weight = 0.15

        score = (
            self.injury_score * injury_weight
            + (1.0 - self.mobility_score) * mobility_weight
            + self.vital_risk_score * vital_weight
            + self.obstruction_score * obstruction_weight
        )
        return max(0.0, min(1.0, score))


class VictimPrioritizer:
    """Ranks victims into a stack/priority list for rescue sequence."""

    def build_priority_stack(self, detections: Sequence[VictimDetection]) -> List[VictimDetection]:
        return sorted(detections, key=lambda victim: victim.priority_score(), reverse=True)


class EntryPointPlanner:
    """Selects best perimeter entry point using weighted path distance."""

    def choose_entry_point(
        self,
        hazard_grid: Sequence[Sequence[int]],
        prioritized_victims: Sequence[VictimDetection],
    ) -> GridPoint:
        if not hazard_grid or not hazard_grid[0]:
            raise ValueError("hazard_grid must be a non-empty matrix")

        rows = len(hazard_grid)
        cols = len(hazard_grid[0])
        perimeter_points = self._list_perimeter_points(rows, cols, hazard_grid)
        if not perimeter_points:
            raise ValueError("No valid perimeter entry points were found")

        best_point: GridPoint | None = None
        best_cost = float("inf")

        for entry in perimeter_points:
            dist_map = self._bfs_distances(hazard_grid, entry)
            cost = 0.0
            for victim in prioritized_victims:
                victim_distance = dist_map[victim.location[0]][victim.location[1]]
                if victim_distance == -1:
                    cost += 10_000
                    continue
                cost += victim_distance * (1.0 + victim.priority_score())

            if cost < best_cost:
                best_cost = cost
                best_point = entry

        if best_point is None:
            raise ValueError("Unable to calculate a valid entry point")

        return best_point

    def _list_perimeter_points(
        self,
        rows: int,
        cols: int,
        hazard_grid: Sequence[Sequence[int]],
    ) -> List[GridPoint]:
        points: List[GridPoint] = []
        for r in range(rows):
            for c in range(cols):
                on_perimeter = r in {0, rows - 1} or c in {0, cols - 1}
                if on_perimeter and hazard_grid[r][c] == 0:
                    points.append((r, c))
        return points

    def _bfs_distances(self, hazard_grid: Sequence[Sequence[int]], start: GridPoint) -> List[List[int]]:
        rows = len(hazard_grid)
        cols = len(hazard_grid[0])
        distances = [[-1] * cols for _ in range(rows)]
        queue: deque[GridPoint] = deque([start])
        distances[start[0]][start[1]] = 0

        while queue:
            r, c = queue.popleft()
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if nr < 0 or nr >= rows or nc < 0 or nc >= cols:
                    continue
                if hazard_grid[nr][nc] == 1:
                    continue
                if distances[nr][nc] != -1:
                    continue
                distances[nr][nc] = distances[r][c] + 1
                queue.append((nr, nc))

        return distances


class VideoOrStreamProcessor:
    """Calls a detector on each frame and aggregates victim detections."""

    def __init__(self, detector: Callable[[object], Iterable[VictimDetection]]) -> None:
        self.detector = detector

    def process(self, frames: Iterable[object]) -> List[VictimDetection]:
        detections_by_id: dict[str, VictimDetection] = {}

        for frame in frames:
            for detection in self.detector(frame):
                previous = detections_by_id.get(detection.victim_id)
                if previous is None or detection.priority_score() > previous.priority_score():
                    detections_by_id[detection.victim_id] = detection

        return list(detections_by_id.values())


class RescueAssessmentModel:
    """End-to-end orchestration: frames -> priorities -> best entry point."""

    def __init__(self, detector: Callable[[object], Iterable[VictimDetection]]) -> None:
        self.processor = VideoOrStreamProcessor(detector)
        self.prioritizer = VictimPrioritizer()
        self.entry_planner = EntryPointPlanner()

    def assess(
        self,
        frames: Iterable[object],
        hazard_grid: Sequence[Sequence[int]],
    ) -> tuple[List[VictimDetection], GridPoint]:
        detections = self.processor.process(frames)
        priority_stack = self.prioritizer.build_priority_stack(detections)
        entry_point = self.entry_planner.choose_entry_point(hazard_grid, priority_stack)
        return priority_stack, entry_point
