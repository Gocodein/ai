# Disaster Rescue AI Model (Prototype)

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
