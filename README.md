diff --git a/README.md b/README.md
index ac4465c28b0c1b4f8a63e6a696f955e5b8a696d5..70a7e2c2e551f86436fda4364e0fa411fa3e1045 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,67 @@
-# ai
+# Disaster Rescue AI (Prototype)
+
+This project is a starter model pipeline for rescue missions in **closed or dangerous areas** where humans cannot quickly reach after disasters or attacks.
+
+## What this model does
+
+1. **Video processing input**
+   - Accepts victim signals derived from either:
+     - uploaded video, or
+     - live drone camera stream.
+2. **Victim priority stack**
+   - Builds a rescue-first ranking using injury severity, consciousness, mobility, nearby hazards, and estimated decline time.
+3. **Best rescue entry point suggestion**
+   - Uses a risk-aware path search on a hazard grid to recommend entry points with the lowest average rescue cost.
+
+## Current implementation
+
+- `src/rescue_ai.py`
+  - `VictimPrioritizer` computes victim urgency score.
+  - `EntryPointAnalyzer` computes safe/efficient entry points.
+  - `RescueCoordinator` orchestrates the full response pipeline.
+- `tests/test_rescue_ai.py`
+  - Smoke test for ranking and entry-point output.
+
+## Example incident JSON
+
+```json
+{
+  "source": "drone-live-stream-17",
+  "victims": [
+    {
+      "victim_id": "V-01",
+      "location": [4, 2],
+      "injury_severity": 0.9,
+      "consciousness": 0.2,
+      "mobility": 0.1,
+      "nearby_hazard": 0.7,
+      "estimated_minutes_to_decline": 18
+    }
+  ],
+  "risk_grid": [
+    [0.1, 0.2, 0.3],
+    [0.1, 0.9, 0.4],
+    [0.1, 0.2, 0.1]
+  ],
+  "candidate_entries": [[0, 0], [2, 0], [0, 2]]
+}
+```
+
+## Run
+
+```bash
+python -m src.rescue_ai incident.json
+```
+
+## Test
+
+```bash
+pytest -q
+```
+
+## Next steps for production
+
+- Replace manual victim signals with computer-vision models (pose, thermal, motion, smoke/fire cues).
+- Add uncertainty calibration for low-visibility frames.
+- Add multi-drone fusion and map stitching.
+- Integrate with real-time command dashboard.
