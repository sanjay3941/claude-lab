# Claude Lab Student Lab

Claude Lab is a local learning assistant that combines:
- a **FastMCP Python backend** for knowledge retrieval, progress tracking, and recommendations
- a **React + Vite frontend** for dashboard, study flow, and practice flow

It helps students study from their own course material, run practice sessions, record results, and get adaptive next-topic recommendations.

## Project Structure

- `/server` — FastMCP server, API routes, learning logic, retrieval, and progress persistence
- `/frontend` — React app (TypeScript) for the Student Lab UI
- `/knowledge` — source study material (`.txt`, `.pdf`) loaded by the backend
- `/data/progress.json` — persisted practice progress data
- `/tests` — backend test and demo scripts

## Key Features

- **Knowledge retrieval** from local study documents (`knowledge/`)
- **Topic study view** using retrieved chunks
- **Practice workflow** with quiz scoring
- **Progress tracking** by topic (attempts, correct/total, accuracy)
- **Adaptive recommendation** for what to study next
- **MCP tools** exposed for agent/client use (`search_knowledge`, `get_topic_content`, `record_practice`, `get_progress`, `get_learning_recommendation`)

## Tech Stack

- Python 3 + FastMCP + Starlette/Uvicorn
- React 19 + TypeScript + Vite
- PyMuPDF for PDF ingestion

## Local Development

### 1) Backend setup and run

From repository root:

```bash
python -m pip install -r requirements.txt
python server/server.py
```

Backend defaults:
- Host: `127.0.0.1`
- Port: `8000`
- MCP endpoint: `http://127.0.0.1:8000/mcp`

You can override host/port with env vars:

```bash
HOST=0.0.0.0 PORT=8000 python server/server.py
```

### 2) Frontend setup and run

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite dev server proxies `/api` requests to `http://127.0.0.1:8000`.

### 3) Build frontend for backend static serving

The backend mounts `frontend/dist` at `/`, so create a production build before serving UI from Python server:

```bash
cd frontend
npm run build
```

## HTTP API

The backend exposes browser-friendly API routes:

- `GET /api/progress` — returns aggregated topic progress
- `GET /api/recommendation` — returns weak topics + recommended next topic
- `GET /api/topic/{topic}` — returns retrieved chunks for a topic
- `POST /api/practice` — records a completed practice result

Example practice payload:

```json
{
  "topic": "deadlock",
  "correct": 4,
  "total": 5
}
```

## MCP Tools

The FastMCP server also exposes tools for MCP clients:

- `search_knowledge(query)`
- `get_topic_content(topic)`
- `record_practice(topic, correct, total)`
- `get_progress()`
- `get_learning_recommendation()`

## Knowledge Base Notes

- Drop `.txt` and/or `.pdf` files under `knowledge/`.
- PDF content is loaded page-by-page.
- Retrieval is keyword/chunk based (lightweight lexical scoring).

## Running Tests

From repository root:

```bash
pytest
```

## Common Workflow

1. Add study material under `knowledge/`
2. Start backend (`python server/server.py`)
3. Start frontend (`npm run dev`)
4. Open the Vite URL and complete a study + practice session
5. Record results and review updated recommendation

## Notes

- Progress data is persisted to `data/progress.json`.
- CORS is enabled on API routes for local browser development.
