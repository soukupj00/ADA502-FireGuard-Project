# Intelligence System

Async worker that pulls MET weather data, computes fire risk, and stores readings in Postgres.

## Layout
- `src/db/`: database models and persistence helpers
- `src/utils/`: MET API client, geohash helpers, and risk calculator
- `src/main.py`: worker loop

## Configuration
Settings are loaded from `.env` (see `.env.example`).

- `DATABASE_URL`: async SQLAlchemy connection string
- `FETCH_INTERVAL_SECONDS`: seconds between fetch cycles (default `3600`)

## Quick start
Run the worker:

```bash
python -m main
```

Run tests:

```bash
pytest
```

