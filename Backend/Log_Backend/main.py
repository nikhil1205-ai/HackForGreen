from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/logs")
async def receive_logs(request: Request):
    data = await request.json()

    logs = data.get("batch", [])

    for log in logs:
        log["received_at"] = datetime.utcnow().isoformat()
        print(json.dumps(log, indent=2))

    return {
        "status": "ok",
        "logs_received": len(logs)
    }
