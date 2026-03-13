import unittest

from rescue_ai.model import EntryPointPlanner, RescueAssessmentModel, VictimDetection, VictimPrioritizer


class VictimPrioritizerTests(unittest.TestCase):
    def test_build_priority_stack_orders_descending(self) -> None:
        victims = [
            VictimDetection("v1", (1, 1), 0.3, 0.9, 0.2, 0.1),
            VictimDetection("v2", (2, 3), 0.9, 0.1, 0.9, 0.8),
            VictimDetection("v3", (4, 2), 0.7, 0.4, 0.4, 0.2),
        ]

        ranked = VictimPrioritizer().build_priority_stack(victims)

        self.assertEqual([victim.victim_id for victim in ranked], ["v2", "v3", "v1"])


class EntryPointPlannerTests(unittest.TestCase):
    def test_choose_entry_point_prefers_closer_to_high_priority_victim(self) -> None:
        planner = EntryPointPlanner()
        grid = [
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        victims = [
            VictimDetection("critical", (0, 4), 0.95, 0.0, 0.9, 0.6),
            VictimDetection("stable", (4, 0), 0.2, 0.7, 0.2, 0.1),
        ]

        entry = planner.choose_entry_point(grid, victims)

        self.assertEqual(entry, (0, 4))


class RescueAssessmentModelTests(unittest.TestCase):
    def test_assess_runs_end_to_end(self) -> None:
        def detector(frame: dict):
            return frame["detections"]

        frames = [
            {
                "detections": [
                    VictimDetection("v1", (1, 1), 0.5, 0.5, 0.5, 0.2),
                    VictimDetection("v2", (3, 3), 0.9, 0.0, 0.8, 0.7),
                ]
            }
        ]
        grid = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]

        stack, entry = RescueAssessmentModel(detector).assess(frames, grid)

        self.assertEqual(stack[0].victim_id, "v2")
        self.assertIn(entry, {(0, 3), (3, 3)})


if __name__ == "__main__":
    unittest.main()
