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
