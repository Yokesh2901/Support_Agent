# SmartSupport Agent

A full-stack multi-agent customer-support automation system that ingests tickets, classifies intent, resolves common issues, detects duplicates, escalates complex cases, stores successful resolutions, and exposes an admin dashboard.

## Architecture

Ticket → IngestAgent → TriageAgent → ResolverAgent → Resolution / Escalation

Supporting components include SQLite persistence, memory storage, structured observability, and a Flask web interface.

## Key capabilities

- Multi-agent ticket triage
- Primary and secondary intent handling
- Domain-specific resolution agents
- Duplicate-ticket protection
- Human escalation summaries
- SQLite ticket history
- Resolution memory
- Request/event logging
- Admin dashboard
- Health endpoint

## Tech stack

Python · Flask · SQLite · pytest · Tailwind CSS

## Run locally

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Configure `FLASK_SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `FLASK_DEBUG` from `.env.example`.
5. Start with `python src/api_server.py`.

## Endpoints

- `/` — customer ticket submission
- `/health` — health check
- `/tickets` — ticket JSON endpoint
- `/admin-login` — admin authentication
- `/dashboard` — protected ticket dashboard

## Security

Credentials and Flask secrets are supplied through environment variables and are intentionally not stored in source control.

## Validation status

**Portfolio-ready functional project.** Before production deployment, add comprehensive automated tests for agents, persistence, authentication, and API error paths.

## Author

Built by Yokesh using Python, Flask, and a custom multi-agent architecture.
