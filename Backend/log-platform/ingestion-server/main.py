from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = "logs.json"

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump([], f)

@app.get("/")
def health():
    return {"status": "running"}

@app.post("/logs")
async def ingest_logs(request: Request):
    payload = await request.json()
    batch = payload.get("batch", [])

    with open(LOG_FILE, "r+") as f:
        logs = json.load(f)
        for log in batch:
            log["received_at"] = datetime.utcnow().isoformat()
            logs.append(log)
        f.seek(0)
        json.dump(logs, f, indent=2)

    return {"stored": len(batch)}

@app.get("/logs")
def get_logs(limit: int = 100):
    with open(LOG_FILE) as f:
        logs = json.load(f)
    return {"count": len(logs), "logs": logs[-limit:]}
