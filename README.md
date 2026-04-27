# TaskFlow API

A task management REST API built with FastAPI and SQLAlchemy.

## Features

- **Task CRUD** — Create, read, update, delete tasks with priorities and due dates
- **Users** — Registration and profile management
- **Comments** — Threaded comments on tasks
- **Analytics** — Task completion metrics, overdue tracking, priority breakdown
- **Priority Escalation** — Automatic escalation of overdue tasks per [business rules](docs/business-rules.md)
- **Task Cloning** — Duplicate an existing task as a starting point for similar work
- **Task Deferral** — Push due dates forward by a selected number of days
- **Task Reassignment** — Transfer a task to another owner
- **Bulk Cancel** — Cancel all open tasks for a specific owner

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload

# Run tests
pytest -v
```

## API Docs

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
taskflow-api/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # DB engine and session
│   ├── routers/
│   │   ├── users.py         # User endpoints
│   │   └── tasks.py         # Task, comment, analytics endpoints
│   └── services/
│       ├── auth.py           # Password hashing
│       ├── task_service.py   # Task business logic
│       └── analytics_service.py  # Metrics computation
├── tests/
│   ├── conftest.py           # Test fixtures
│   ├── test_users.py
│   ├── test_tasks.py
│   └── test_escalation.py
├── docs/
│   └── business-rules.md    # Business rules documentation
├── requirements.txt
└── pyproject.toml
```

## Running Tests

```bash
pytest -v
```

## Contributing

See [docs/business-rules.md](docs/business-rules.md) for expected behavior.
