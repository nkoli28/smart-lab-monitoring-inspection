# Project Status

This repository is an initial prototype scaffold.

## Present in the codebase
- Simulated MQTT telemetry publisher and subscriber.
- FastAPI endpoints for readings, alerts, health, and path comparison.
- SQLAlchemy models for PostgreSQL readings and alerts.
- Threshold-based temperature and vibration anomaly detection.
- A*, BFS, and Dijkstra for four-directional grid navigation.
- Browser dashboard polling API endpoints.
- Docker Compose services and initial Pytest unit tests.

## Not yet claimed as complete
- The full stack has not been executed in the author's environment yet.
- No real sensor hardware or physical robot is integrated.
- Alerts are persisted, but automatic mission dispatch and animated robot movement are future work.
- Benchmarks have not been collected under controlled, repeated conditions.
- Database/MQTT integration and dashboard behavior need local end-to-end validation.

## Validation checklist
1. Run `docker compose up --build`.
2. Confirm `/health` returns HTTP 200.
3. Check `/api/readings` for simulated telemetry.
4. Wait for an abnormal reading and inspect `/api/alerts`.
5. Check `/api/path/compare` for valid routes.
6. Run `pytest` in the app environment.
7. Capture screenshots/GIF only after successful live validation.
