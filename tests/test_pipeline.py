import json
import tempfile
import unittest

from incident_store import load_incident_json, open_database
from rescue_ai_model import (
    DisasterRescueModel,
    EntryPoint,
    EnvironmentSnapshot,
    InjuryLevel,
    VictimDetection,
)


class PipelineTests(unittest.TestCase):
    def test_priorities_sorted_desc_with_environment(self):
        model = DisasterRescueModel()
        environment = EnvironmentSnapshot(0.6, 0.5, 0.5, 0.4)
from rescue_ai_model import DisasterRescueModel, EntryPoint, InjuryLevel, VictimDetection


class PipelineTests(unittest.TestCase):
    def test_priorities_sorted_desc(self):
        model = DisasterRescueModel()
        data = [
            VictimDetection("A", 0, 0, 0.2, 0.2, 0.9, 0.8, InjuryLevel.CRITICAL),
            VictimDetection("B", 0, 0, 0.9, 0.9, 0.1, 0.1, InjuryLevel.MINOR),
        ]
        out = model.prioritize_victims(data, environment)
        self.assertGreaterEqual(out[0].score, out[1].score)
        self.assertEqual(out[0].victim.victim_id, "A")
        self.assertGreater(out[0].estimated_safe_minutes, 0)

    def test_incident_json_requires_id_and_environment(self):
        out = model.prioritize_victims(data)
        self.assertGreaterEqual(out[0].score, out[1].score)
        self.assertEqual(out[0].victim.victim_id, "A")

    def test_incident_json_requires_id(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".json") as f:
            f.write(json.dumps({"status": "active"}))
            f.flush()
            with self.assertRaises(ValueError):
                load_incident_json(f.name)

    def test_db_init(self):
        conn = open_database(":memory:")
        try:
            rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            names = {r[0] for r in rows}
            self.assertIn("incidents", names)
            self.assertIn("victim_priorities", names)
            self.assertIn("entry_recommendations", names)
        finally:
            conn.close()

    def test_suggest_entry_requires_candidates(self):
        model = DisasterRescueModel()
        environment = EnvironmentSnapshot(0.2, 0.2, 0.2, 0.2)
        with self.assertRaises(ValueError):
            model.suggest_entry_point([], [], environment)

    def test_checkpoints_present(self):
        model = DisasterRescueModel()
        environment = EnvironmentSnapshot(0.2, 0.3, 0.2, 0.1)
        victims = model.prioritize_victims(
            [VictimDetection("V1", 50, 50, 0.4, 0.4, 0.6, 0.7, InjuryLevel.SEVERE)],
            environment,
        )
        rec = model.suggest_entry_point(
            [EntryPoint("Gate", 0, 0, 0.2, 0.2, 0.8, 0.8, 30.0)],
            victims,
            environment,
        )
        self.assertGreaterEqual(len(rec.checkpoints), 2)
        with self.assertRaises(ValueError):
            model.suggest_entry_point([], [])


if __name__ == "__main__":
    unittest.main()
