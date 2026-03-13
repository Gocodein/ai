# Disaster Rescue AI Model

This project is refined for your exact workflow:
- FPV drone/mobile camera feed,
- AI calculates victim risk factor + estimated safe minutes,
- AI builds rescue priority list,
- AI suggests safest navigation route from camera-derived scene signals.

## Core flow implemented

1. Capture real-time footage from drone FPV or mobile demo camera.
2. Run detection pipeline to produce `victim_detections` and environment hazards.
3. Compute:
   - environment risk score,
   - victim risk factor and safe-time estimate,
   - priority stack,
   - safest entry + checkpoints.
4. Save results to database for dashboard/command center.

## Files

- `rescue_ai_model.py` — triage + environment-risk + navigation logic.
- `incident_store.py` — SQLite persistence layer.
- `run_incident.py` — CLI pipeline runner.
- `app.py` — FastAPI endpoint for live/demo integration.
- `incident.example.json` — reference incident payload.
- `disaster_rescue_colab.ipynb` — Google Colab ready notebook.
- `tests/test_pipeline.py` — regression tests.

## Local run

```bash
python3 rescue_ai_model.py
python3 run_incident.py
```

## API run

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

## Database outputs

After `run_incident.py`, SQLite `rescue_ops.db` stores:
- `incidents` (incident + env risk)
- `victim_priorities` (rank, risk, safe minutes)
- `entry_recommendations` (entry score + navigation checkpoints)

## Google Colab (to avoid local library issues)

Use `disaster_rescue_colab.ipynb`:
1. Open Colab and upload notebook + repo files.
2. Run all cells.
3. It installs required libraries, runs model logic, and generates `rescue_ops.db`.

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

This is decision-support software. Final rescue decisions must remain with trained emergency responders.
