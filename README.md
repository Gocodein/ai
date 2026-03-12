# Disaster Rescue AI Model (Prototype)

This repository contains a baseline AI decision pipeline for rescue missions where victims are trapped in inaccessible disaster zones.

## What this model does

1. Process victim detections from uploaded video or live drone feeds.
2. Generate a rescue priority stack (highest urgency first).
3. Recommend the best entry point for rescue teams.

## Project files

- `rescue_ai_model.py` — core triage + entry recommendation logic.
- `incident_store.py` — SQLite schema + persistence helpers.
- `run_incident.py` — CLI runner that loads JSON and saves outputs.
- `incident.example.json` — sample incident payload.
- `app.py` — FastAPI service for API/demo use.
- `tests/test_pipeline.py` — basic regression tests.

## Quick run (CLI)

```bash
python3 rescue_ai_model.py
python3 run_incident.py
```

## API run (for judge demo)

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open:
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## Run in VS Code

1. Install the Python extension by Microsoft.
2. Select interpreter (`Python: Select Interpreter`, Python 3.10+).
3. Run `rescue_ai_model.py` directly or start API with:
   ```bash
   uvicorn app:app --reload
   ```

## What to do with `incident.json` and database

Use `incident.example.json` as input contract for each rescue event:

- `incident_id`, `status`, `source`
- `victim_detections` from CV model
- `entry_points` from map/SLAM/engineer assessment

Then run:

```bash
python3 run_incident.py
```

This stores outputs in `rescue_ops.db` tables:
- `incidents`
- `victim_priorities`
- `entry_recommendations`

## Deployment-ready / hackathon-ready checklist

To make this project ready for judges and near-deployment:

### Must-have (implemented in this repo)

- API layer (`app.py`) for live demo integration.
- Input validation via Pydantic/FastAPI.
- Persistence schema for incident traceability.
- Containerization (`Dockerfile`).
- Basic automated tests.
- `.gitignore` to avoid committing local DB/cache files.

### Should add next (recommended)

1. **Auth & security**
   - Add API key/JWT auth.
   - Add request rate limiting and audit logs.
2. **Model quality**
   - Replace static weights with calibrated weights from historical data.
   - Add confidence thresholds and uncertainty output.
3. **Observability**
   - Add structured logs, metrics, and error dashboards.
4. **Reliability**
   - Add retries/queue (Celery/RQ/Kafka) for stream ingestion.
   - Add migrations (Alembic) and move from SQLite to Postgres for production.
5. **Responsible AI**
   - Add human-in-the-loop override in dashboard.
   - Save model version + explanation for each recommendation.

## Docker

```bash
docker build -t rescue-ai .
docker run --rm -p 8000:8000 rescue-ai
```

## Testing

```bash
python3 -m py_compile rescue_ai_model.py incident_store.py run_incident.py app.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Important note

This is decision-support software, not a certified medical/rescue system. Validate with emergency experts and field trials before real deployment.
This repository now contains a **baseline AI decision pipeline** for rescue missions where victims are trapped in closed or inaccessible disaster zones.

## What this model does

1. **Video / live stream processing**
   - Accepts detections from uploaded videos or live drone feeds.
   - Validates and normalizes victim signals (breathing, movement, bleeding, trapped likelihood).

2. **Victim priority stack**
   - Generates a ranked rescue list from highest to lowest urgency.
   - Uses a weighted triage score combining injury level, bleeding risk, trapped risk, and survivability indicators.

3. **Best rescue entry-point recommendation**
   - Scores candidate entry points using safety + speed-of-access.
   - Chooses the best entry route for rescuers to reach top-priority victims quickly and safely.

## Files

- `rescue_ai_model.py`: complete prototype implementation (data models, scoring logic, and demo run).

## Quick run

```bash
python3 rescue_ai_model.py
```

Example output includes:
- ranked victims (`1, 2, 3...`) with reasons,
- the recommended entry point with safety/access rationale.

## How to integrate in your project

- Replace the `process_stream()` placeholder input with your real CV pipeline (YOLO/pose/thermal/audio models).
- Feed `VictimDetection` objects from your inference engine.
- Feed candidate `EntryPoint` objects from site maps, SLAM, and structure assessment tools.
- Push `RescuePriority` + `EntryRecommendation` outputs to your rescue command dashboard.

## Important note

This is a **decision-support prototype**, not a certified medical/rescue system. Validate with emergency experts, real incident datasets, and safety regulations before deployment.
# Disaster Rescue AI Model

This repository now contains a starter AI-assisted rescue assessment pipeline for disasters and attacks where responders cannot immediately reach trapped victims.

## What it does

1. **Processes uploaded video or drone live-stream frames** using a detection function.
2. **Builds a rescue priority stack** so the most critical victims are handled first.
3. **Chooses the best entry point** for responders based on hazard map layout and victim urgency.

## Project structure

- `rescue_ai/model.py`: Core pipeline classes.
- `tests/test_model.py`: Unit tests for prioritization, entry-point selection, and end-to-end flow.

## Core idea

Each victim receives a composite urgency score based on:

- Injury severity
- Mobility (lower mobility => higher urgency)
- Vital risk
- Obstruction level (difficulty of extraction)

Victims are sorted by this score to produce a rescue stack.

For entry-point recommendation, perimeter points are evaluated by:

- Running shortest-path distances through free cells in a hazard grid
- Penalizing unreachable victims heavily
- Weighting victim distance by urgency score

The point with the lowest total weighted cost is selected.

## Quick start

```python
from rescue_ai.model import RescueAssessmentModel, VictimDetection


def detector(frame):
    # Replace with your real CV/thermal model output
    return frame["detections"]


frames = [
    {
        "detections": [
            VictimDetection("victim-a", (2, 5), 0.9, 0.1, 0.8, 0.7),
            VictimDetection("victim-b", (6, 1), 0.4, 0.7, 0.3, 0.2),
        ]
    }
]

hazard_grid = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0],
]

model = RescueAssessmentModel(detector)
priority_stack, best_entry = model.assess(frames, hazard_grid)

print([v.victim_id for v in priority_stack])
print(best_entry)
```

## Next steps for a real deployment

- Replace the mock `detector` with your trained vision + thermal model.
- Add victim tracking across frames (ReID / SORT / DeepSORT).
- Add 3D scene mapping (SLAM/LiDAR) for safer path planning.
- Integrate incident command dashboard + GIS layers.
- Add uncertainty/confidence outputs for rescue teams.

## Running tests

```bash
python -m unittest discover -s tests -q
```
# Disaster Rescue AI (Prototype)

This project is a starter model pipeline for rescue missions in **closed or dangerous areas** where humans cannot quickly reach after disasters or attacks.

## What this model does

1. **Video processing input**
   - Accepts victim signals derived from either:
     - uploaded video, or
     - live drone camera stream.
2. **Victim priority stack**
   - Builds a rescue-first ranking using injury severity, consciousness, mobility, nearby hazards, and estimated decline time.
3. **Best rescue entry point suggestion**
   - Uses a risk-aware path search on a hazard grid to recommend entry points with the lowest average rescue cost.

## Current implementation

- `src/rescue_ai.py`
  - `VictimPrioritizer` computes victim urgency score.
  - `EntryPointAnalyzer` computes safe/efficient entry points.
  - `RescueCoordinator` orchestrates the full response pipeline.
- `tests/test_rescue_ai.py`
  - Smoke test for ranking and entry-point output.

## Example incident JSON

```json
{
  "source": "drone-live-stream-17",
  "victims": [
    {
      "victim_id": "V-01",
      "location": [4, 2],
      "injury_severity": 0.9,
      "consciousness": 0.2,
      "mobility": 0.1,
      "nearby_hazard": 0.7,
      "estimated_minutes_to_decline": 18
    }
  ],
  "risk_grid": [
    [0.1, 0.2, 0.3],
    [0.1, 0.9, 0.4],
    [0.1, 0.2, 0.1]
  ],
  "candidate_entries": [[0, 0], [2, 0], [0, 2]]
}
```

## Run

```bash
python -m src.rescue_ai incident.json
```

## Test

```bash
pytest -q
```

## Next steps for production

- Replace manual victim signals with computer-vision models (pose, thermal, motion, smoke/fire cues).
- Add uncertainty calibration for low-visibility frames.
- Add multi-drone fusion and map stitching.
- Integrate with real-time command dashboard.
# AI Rescue Prioritization Model

This repository now contains a practical blueprint for an AI system that helps rescue teams locate and prioritize victims in closed or hard-to-reach disaster zones.

## Goal
Build an AI model that can:
1. Process uploaded videos or live drone camera feeds.
2. Create a victim priority stack based on urgency.
3. Recommend the safest and fastest entry point for rescue teams.

## Proposed System Name
**SAR-Vision (Search And Rescue Vision Intelligence)**

## Core Workflow

### 1) Input Processing Layer
- Accepts:
  - User-uploaded videos.
  - Live drone streams (RTSP/WebRTC).
- Splits video into frames and synchronizes timestamps.
- Runs low-light enhancement and smoke/debris denoising to improve detection reliability.

### 2) Victim Detection & Tracking
- Uses a vision model (e.g., YOLOv8/DETR backbone) to detect people.
- Uses pose estimation and motion analysis to infer victim condition:
  - Moving and responsive.
  - Injured but moving.
  - Immobile/unconscious risk.
- Tracks each person over time with multi-object tracking (ByteTrack/DeepSORT) to avoid duplicate counting.

### 3) Priority Scoring Engine
Each victim receives a dynamic priority score:

`PriorityScore = (MedicalRisk × 0.45) + (AccessibilityRisk × 0.25) + (EnvironmentThreat × 0.20) + (SurvivalTimePenalty × 0.10)`

Where:
- **MedicalRisk**: Estimated injury severity, blood loss cues, unconscious posture, no motion over long interval.
- **AccessibilityRisk**: How hard it is to reach safely.
- **EnvironmentThreat**: Nearby fire/smoke/toxic hazards/unstable structure.
- **SurvivalTimePenalty**: Time elapsed since first detection without aid.

Output:
- Ranked victim stack: **Rescue First → Last**.
- Confidence per victim and explanation fields for each score component.

### 4) Entry Point Recommendation Module
- Builds a scene map from drone images (2D occupancy or 3D mesh if depth is available).
- Detects blocked routes, fire pockets, structural collapse zones, and narrow corridors.
- Runs graph-based path planning (A*/Dijkstra with risk-aware costs) to compute:
  - Best entry point.
  - Secondary backup entry point.
  - Expected time-to-victim for top-priority cases.

### 5) Command Dashboard Output
- Live video with overlays:
  - Victim IDs and urgency color code.
  - Hazard zones.
  - Recommended ingress path.
- Incident summary JSON for rescue control systems.

## Suggested Model Stack
- **Vision backbone**: YOLOv8 or RT-DETR.
- **Pose model**: MoveNet / OpenPose / ViTPose.
- **Tracking**: ByteTrack.
- **Segmentation/hazard detection**: SegFormer or Mask2Former.
- **Route planning**: NetworkX + custom risk-weighted graph.
- **Deployment**: Edge GPU (Jetson) + cloud sync for command center.

## Minimal Data Schema
```json
{
  "frame_id": 412,
  "timestamp": "2026-03-12T10:15:30Z",
  "victims": [
    {
      "victim_id": "V-07",
      "bbox": [122, 88, 74, 168],
      "condition": "immobile",
      "priority_score": 0.91,
      "priority_rank": 1,
      "confidence": 0.86,
      "hazards_nearby": ["smoke", "falling_debris"]
    }
  ],
  "entry_points": [
    {
      "id": "E-2",
      "score": 0.84,
      "eta_seconds": 95,
      "route_risk": "moderate"
    }
  ]
}
```

## Phased Build Plan
1. **Phase 1 (MVP)**
   - Detect victims from uploaded videos.
   - Create basic priority ranking from motion + hazard proximity.
2. **Phase 2**
   - Add live drone feed support and tracking continuity.
   - Add route recommendation with map constraints.
3. **Phase 3**
   - Add multimodal signals (thermal camera, audio distress clues).
   - Validate with synthetic disaster simulations and field drills.

## Safety & Ethical Constraints
- Treat predictions as **decision support**, not autonomous final decisions.
- Keep human override mandatory.
- Log model confidence and uncertainty for every recommendation.
- Protect identity and sensitive incident footage with strict access control.

## Next Step
If you want, the next iteration can include:
- A production-ready folder structure.
- Training + inference scripts.
- A sample API (`/analyze`, `/priority`, `/entry-point`) for integration with a drone control dashboard.
