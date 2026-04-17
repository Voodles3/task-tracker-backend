# Task Tracker Backend

This is a small FastAPI backend for a task tracker app.

It exposes a simple JSON API for creating, reading, updating, and deleting tasks,
then persists that data to a local JSON file.

Current structure is split into:

- `app/api`: FastAPI route definitions
- `app/db`: repository and storage layers
- `app/models`: Pydantic request/response models
- `app/core`: app configuration and logging

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
OR
```bash
fastapi dev
```

Then open:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

By default, task data is stored at `data/tasks.json`.
You can override this with an environment variable:

```bash
DATA_FILE_PATH=/absolute/path/tasks.json
```

## API Structure

Routes:

- `GET /api/v1/tasks/health`
- `GET /api/v1/tasks/`
- `GET /api/v1/tasks/{task_id}`
- `POST /api/v1/tasks/`
- `PATCH /api/v1/tasks/{task_id}`
- `DELETE /api/v1/tasks/`
- `DELETE /api/v1/tasks/{task_id}`

Each task looks like this:

```json
{
  "id": 1,
  "title": "Write README",
  "description": "Explain full app behavior",
  "priority": "UNSET",
  "completed": false,
  "due_date": null,
  "completed_at": null,
  "created_at": "2026-03-31T12:00:00Z",
  "updated_at": "2026-03-31T12:00:00Z"
}
```

`GET /api/v1/tasks/` returns a paginated list:

```json
{
  "total": 0,
  "count": 0,
  "limit": 50,
  "offset": 0,
  "tasks": []
}
```

List query params:

- `completed`: filter by completion status
- `priority`: `URGENT`, `HIGH`, `MEDIUM`, `LOW`, or `UNSET`
- `due_before` / `due_after`: filter by due date
- `q`: case-insensitive title and description search
- `sort_by`: `created_at`, `updated_at`, `due_date`, `priority`, or `title`
- `order`: `asc` or `desc`
- `limit`: page size, from `1` to `100`, default `50`
- `offset`: starting index, default `0`

Notes:

- `description` is optional
- `priority` defaults to `UNSET`
- `completed` defaults to `false`
- `GET /tasks` defaults to newest-created tasks first
- missing tasks return `404`
- storage failures return `500`

## Examples

Create a task:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Write README","description":"Trim the docs down"}'
```

List tasks:

```bash
curl http://127.0.0.1:8000/api/v1/tasks/
```

Filter, sort, and paginate tasks:

```bash
curl 'http://127.0.0.1:8000/api/v1/tasks/?completed=false&sort_by=priority&limit=10&offset=0'
```

Update a task:

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Write a shorter README"}'
```

Delete a task:

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/tasks/1
```

Delete all tasks:

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/tasks/
```

## Tests

```bash
poetry run pytest -q
```

The test suite covers CRUD flows, list filtering/search/sorting/pagination,
error handling, and JSON persistence behavior.
