## Claude Lab Student Lab

Student Lab is a React/Vite interface over the existing FastMCP learning
server. The Python modules remain the source of truth for retrieval, progress,
and recommendations.

### Run locally

Install backend dependencies and start the MCP server from the repository root:

```powershell
python -m pip install -r requirements.txt
python server/server.py
```

In a second terminal, install and start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal. During development, Vite proxies
`/api` requests to `http://127.0.0.1:8000`. The MCP endpoint remains available
at `/mcp`, and the browser transport routes are `/api/progress`,
`/api/recommendation`, `/api/topic/{topic}`, and `/api/practice`.