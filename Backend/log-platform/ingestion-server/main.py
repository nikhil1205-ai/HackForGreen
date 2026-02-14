# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from datetime import datetime
# import json
# import os

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# LOG_FILE = "logs.json"

# if not os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w") as f:
#         json.dump([], f)

# @app.get("/")
# def health():
#     return {"status": "running"}

# @app.post("/logs")
# async def ingest_logs(request: Request):
#     payload = await request.json()
#     batch = payload.get("batch", [])

#     with open(LOG_FILE, "r+") as f:
#         logs = json.load(f)
#         for log in batch:
#             log["received_at"] = datetime.utcnow().isoformat()
#             logs.append(log)
#         f.seek(0)
#         json.dump(logs, f, indent=2)

#     return {"stored": len(batch)}

# @app.get("/logs")
# def get_logs(limit: int = 100):
#     with open(LOG_FILE) as f:
#         logs = json.load(f)
#     return {"count": len(logs), "logs": logs[-limit:]}



from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os
import uuid
from typing import Optional, List

app = FastAPI(title="HackForGreen Log Ingestion Server (Pathway Ready)")

# -------------------------------
# CORS Configuration
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = "logs.ndjson"

# Ensure file exists
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, "w").close()


# -------------------------------
# Utility Functions
# -------------------------------

def append_log(log: dict):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")


def read_logs(limit: int = 100) -> List[dict]:
    logs = []
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()

    for line in lines[-limit:]:
        logs.append(json.loads(line.strip()))

    return logs


def overwrite_logs(logs: List[dict]):
    with open(LOG_FILE, "w") as f:
        for log in logs:
            f.write(json.dumps(log) + "\n")


# -------------------------------
# Health Check
# -------------------------------

@app.get("/")
def health():
    return {"status": "running"}


# -------------------------------
# Ingest Single Log (Pathway Style)
# -------------------------------

@app.post("/logs")
def ingest_log(log: dict):
    """
    Accepts ONE JSON log object.
    """

    # Add metadata
    log["id"] = str(uuid.uuid4())
    log["received_at"] = datetime.utcnow().isoformat()

    append_log(log)

    return {
        "message": "Log stored successfully",
        "id": log["id"]
    }


# -------------------------------
# Get Logs
# -------------------------------

@app.get("/logs")
def get_logs(limit: int = 100):
    logs = read_logs(limit)
    return {
        "count": len(logs),
        "logs": logs
    }


# -------------------------------
# Delete All Logs
# -------------------------------

@app.delete("/logs")
def delete_all_logs():
    open(LOG_FILE, "w").close()
    return {"message": "All logs deleted"}


# -------------------------------
# Delete Log by ID
# -------------------------------

@app.delete("/logs/{log_id}")
def delete_log_by_id(log_id: str):
    logs = read_logs(limit=100000)

    new_logs = [log for log in logs if log.get("id") != log_id]

    if len(new_logs) == len(logs):
        raise HTTPException(status_code=404, detail="Log not found")

    overwrite_logs(new_logs)

    return {"message": f"Log {log_id} deleted"}


# -------------------------------
# Delete Logs by Level
# -------------------------------

@app.delete("/logs/level/{level}")
def delete_by_level(level: str):
    logs = read_logs(limit=100000)

    new_logs = [
        log for log in logs
        if log.get("level", "").upper() != level.upper()
    ]

    deleted_count = len(logs) - len(new_logs)

    overwrite_logs(new_logs)

    return {
        "deleted": deleted_count,
        "message": f"Deleted all {level.upper()} logs"
    }
