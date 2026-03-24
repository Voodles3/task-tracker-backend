# Task Tracker Backend

Small FastAPI backend for a task tracker app. It exposes a simple JSON API for creating, reading, updating, and deleting tasks, and persists data to a local JSON file so tasks survive app restarts.

## What It Does

- Provides a lightweight REST API for task management
- Stores tasks in memory while the app is running
- Persists tasks and the next task ID to disk in JSON
- Returns clear `404` responses for missing tasks
- Returns a `500` response if storage operations fail

Each task has:

- `id`
- `title`
- `description` (optional)

## Tech Stack

- Python 3.12+
- FastAPI
- Uvicorn
- Pytest
- HTTPX for async endpoint tests

## Project Structure

```text
app/
  main.py           FastAPI app factory and routes
  store.py          In-memory task store and business logic
  persistence.py    JSON file persistence adapter
  schemas.py        Pydantic models and storage interfaces
tests/
  ...               API and persistence tests
```

## Requirements

- Python 3.12 or newer
- Poetry

## Install

```bash
poetry install
```

## Run the API

Start the development server with:

```bash
poetry run uvicorn app.main:create_app --factory --reload
```

The API will be available at:

- `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

By default, tasks are persisted to:

```text
app/save_data/save_data.json
```

## API Endpoints

### `GET /`

Basic root endpoint.

Response:

```json
{
  "You are at root": true
}
```

### `GET /health`

Health check endpoint.

Response:

```json
{
  "status": "ok"
}
```

### `GET /tasks`

Returns all tasks.

Response:

```json
[
  {
    "id": 1,
    "title": "Write tests",
    "description": "Cover current endpoints"
  }
]
```

### `GET /tasks/{task_id}`

Returns a single task by ID.

If the task does not exist:

```json
{
  "detail": "Task with id 999 not found"
}
```

### `POST /tasks`

Creates a new task.

Request body:

```json
{
  "title": "Write README",
  "description": "Add setup and API examples"
}
```

Response:

```json
{
  "id": 1,
  "title": "Write README",
  "description": "Add setup and API examples"
}
```

### `PATCH /tasks/{task_id}`

Updates one or more task fields.

Request body:

```json
{
  "description": "Updated description"
}
```

Response:

```json
{
  "id": 1,
  "title": "Write README",
  "description": "Updated description"
}
```

### `DELETE /tasks/{task_id}`

Deletes a task.

Response:

- `204 No Content` on success

If the task does not exist:

```json
{
  "detail": "Cannot delete task with id 999: task not found"
}
```

## Example Requests

Create a task:

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Write README","description":"Document the API"}'
```

List tasks:

```bash
curl http://127.0.0.1:8000/tasks
```

Get one task:

```bash
curl http://127.0.0.1:8000/tasks/1
```

Update a task:

```bash
curl -X PATCH http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Write better README"}'
```

Delete a task:

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/1
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Run Tests

```bash
poetry run pytest -q
```

Current test coverage includes:

- root and health endpoints
- task CRUD behavior
- missing-task error handling
- JSON persistence across app restarts
- saved file contents and next-ID behavior

## Notes

- This project uses an app factory: `create_app()`
- Task data is persisted through a JSON storage adapter
- Persistence writes use a temporary file and atomic replace to reduce corruption risk
