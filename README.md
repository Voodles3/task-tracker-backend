# Task Tracker Backend

A small FastAPI backend for a task tracker app.

Exposes a simple JSON API for creating, reading, updating, and deleting tasks, then persists that data to a local JSON file.

## Stack

- Python 3.12+
- FastAPI
- Uvicorn
- Pytest

## Requirements

- Python 3.12+
- Poetry

## Install

```bash
poetry install
```

## Run

```bash
poetry run uvicorn app.main:create_app --factory --reload
```

Then open:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

By default, task data is stored at `app/save_data/save_data.json`.

## API

Routes:

- `GET /`
- `GET /health`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks`
- `DELETE /tasks/{task_id}`

Each task looks like this:

```json
{
  "id": 1,
  "title": "Write README",
  "description": "Trim the docs down"
}
```

Notes:

- `description` is optional
- missing tasks return `404`
- storage failures return `500`

## Quick Examples

Create a task:

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Write README","description":"Trim the docs down"}'
```

List tasks:

```bash
curl http://127.0.0.1:8000/tasks
```

Update a task:

```bash
curl -X PATCH http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Write a shorter README"}'
```

Delete a task:

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/1
```

Delete all tasks:

```bash
curl -X DELETE http://127.0.0.1:8000/tasks
```

## Tests

```bash
poetry run pytest -q
```

The test suite covers the main CRUD flows, error handling, and JSON persistence behavior.
