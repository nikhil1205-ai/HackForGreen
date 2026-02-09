from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os
from typing import List

app = FastAPI(title="Log Platform API (No DB)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = "logs.json"

# Ensure log file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump([], f)

@app.get("/")
def health():
    return {"status": "running"}

# 🔹 INGEST LOGS
@app.post("/logs")
async def receive_logs(request: Request):
    payload = await request.json()
    batch = payload.get("batch", [])

    if not batch:
        return {"status": "ok", "stored": 0}

    with open(LOG_FILE, "r+") as f:
        logs = json.load(f)

        for log in batch:
            log["received_at"] = datetime.utcnow().isoformat()
            logs.append(log)

        f.seek(0)
        json.dump(logs, f, indent=2)

    return {"status": "ok", "stored": len(batch)}

# 🔹 FETCH LOGS AS JSON
@app.get("/logs")
def get_logs(
    limit: int = Query(50, le=500),
    level: str | None = None,
    appName: str | None = None
):
    with open(LOG_FILE, "r") as f:
        logs: List[dict] = json.load(f)

    # Filters
    if level:
        logs = [l for l in logs if l.get("level") == level.upper()]
    if appName:
        logs = [l for l in logs if l.get("appName") == appName]

    logs = logs[-limit:]  # last N logs

    return {
        "count": len(logs),
        "logs": logs
    }
