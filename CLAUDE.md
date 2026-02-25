# CLAUDE.md — Yelp Lead Responder

This file provides context for AI assistants working in this repository.

## Project Overview

A lightweight FastAPI webhook receiver that ingests Yelp leads forwarded by Zapier and logs them. The intended purpose is to process incoming lead data (customer name, job type, location, message, etc.) and eventually respond to or store those leads.

## Repository Structure

```
yelp-lead-responder/
├── CLAUDE.md               # This file
├── README.md               # Empty (not yet written)
├── requirements.txt        # Pinned Python dependencies
├── ngrok.yml               # Ngrok tunnel config for local webhook testing
└── app/
    ├── .env.example        # Environment variable template
    ├── Dockerfile          # Python 3.11-slim container definition
    ├── docker-compose.yml  # Single-service compose config (port 8000)
    ├── main.py             # FastAPI app — all routes live here
    ├── models.py           # Pydantic data models
    └── templates.py        # Placeholder (empty, for future response templates)
```

## Running the App

### Locally (without Docker)

```bash
cd app
cp .env.example .env       # then set API_KEY in .env
pip install -r ../requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### With Docker Compose

```bash
# from repo root
docker compose -f app/docker-compose.yml up --build
```

The app runs on **port 8000** in all environments.

### Exposing Locally via Ngrok

```bash
ngrok start --config ngrok.yml default
```

This tunnels port 8000 to a public ngrok URL for receiving webhooks from Zapier.

## Environment Variables

Defined in `app/.env.example`. Copy to `app/.env` (gitignored).

| Variable  | Required | Description                                      |
|-----------|----------|--------------------------------------------------|
| `API_KEY` | Yes      | Secret key validated against `x-api-key` header |

## API Endpoints

All routes are defined in `app/main.py`.

### `GET /`
- **Auth:** None
- **Response:** `{"status": "ok"}`
- **Purpose:** Health check / webhook connectivity verification

### `POST /`
- **Auth:** `x-api-key` header must match `API_KEY` env var; returns 401 otherwise
- **Request body:** JSON (preferred) or raw bytes
- **Response:** `{"status": "received"}`
- **Side effect:** Prints the parsed JSON (or raw body) to stdout

## Data Model

`app/models.py` defines `YelpLead` (Pydantic `BaseModel`):

| Field            | Type            | Required |
|------------------|-----------------|----------|
| `customer_name`  | `str`           | Yes      |
| `job_type`       | `Optional[str]` | No       |
| `zip_code`       | `Optional[str]` | No       |
| `message`        | `Optional[str]` | No       |
| `survey_answers` | `Optional[str]` | No       |
| `image_urls`     | `Optional[str]` | No       |
| `lead_created_at`| `Optional[str]` | No       |

The model is not currently used by the POST endpoint (it accepts raw requests), but it documents the expected Yelp lead payload shape.

## Code Conventions

- **Indentation:** 2-space indent in YAML/Docker files; standard 4-space (implicit) in Python.
- **Async:** All FastAPI route handlers use `async def`.
- **Error handling:** The POST endpoint wraps `request.json()` in a try/except and falls back to `request.body()` for non-JSON payloads.
- **Configuration:** Secrets and config come exclusively from environment variables via `python-dotenv`. Never hardcode credentials.
- **Models:** Use `app/models.py` for any new Pydantic schemas. Keep models in that file unless the file grows large.
- **Templates:** Response message templates belong in `app/templates.py`.

## Dependencies

Managed via `requirements.txt` with pinned versions. Key packages:

| Package        | Version  | Purpose                          |
|----------------|----------|----------------------------------|
| fastapi        | 0.132.0  | Web framework                    |
| uvicorn        | 0.41.0   | ASGI server                      |
| pydantic       | 2.12.5   | Data validation / serialization  |
| python-dotenv  | 1.2.1    | .env file loading                |
| starlette      | 0.52.1   | HTTP toolkit (FastAPI dependency) |

To add a dependency: install it in your venv, then pin it with `pip freeze > requirements.txt` (or add the pinned line manually).

## Testing

No tests exist yet. When adding tests:
- Use `pytest` with `httpx` (or `requests`) and FastAPI's `TestClient`.
- Place test files under a `tests/` directory at the repo root.
- Run with `pytest` from the repo root.

## Docker

- **Base image:** `python:3.11-slim`
- **Build context:** repo root (the Dockerfile copies `./app` and `.env`)
- **CMD:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- The compose file mounts `.env` via `env_file` and sets `restart: always`.

## Git Workflow

- Default branch: `master`
- Feature/task branches use the `claude/` prefix (e.g., `claude/claude-md-...`)
- Commits are signed with an SSH key (configured in global git config)
- `.env` and `venv/` are gitignored — never commit secrets

## Current State & Known Gaps

- **No data persistence:** Webhook data is only printed to stdout; nothing is stored.
- **No response logic:** The app acknowledges every valid webhook but does not reply to leads.
- **`templates.py` is empty:** Intended for building outgoing message templates.
- **No tests:** No test suite or CI/CD pipeline exists yet.
- **README.md is empty:** Has not been written.
