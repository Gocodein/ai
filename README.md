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
