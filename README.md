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
