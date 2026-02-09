from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

app = FastAPI(title="Log Ingestion Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/logs")
async def receive_logs(request: Request):
    payload = await request.json()
    logs = payload.get("batch", [])

    print("\n===== LOG BATCH RECEIVED =====")
    for log in logs:
        log["received_at"] = datetime.utcnow().isoformat()
        print(json.dumps(log, indent=2))

    return {
        "status": "ok",
        "received": len(logs)
    }
