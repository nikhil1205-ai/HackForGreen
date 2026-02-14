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



from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os
import uuid
from typing import Optional

app = FastAPI(title="HackForGreen Log Ingestion Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = "logs.json"

# Ensure file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump([], f)


# -------------------------------
# Utility functions
# -------------------------------

def read_logs():
    with open(LOG_FILE, "r") as f:
        return json.load(f)


def write_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


# -------------------------------
# Health
# -------------------------------

@app.get("/")
def health():
    return {"status": "running"}


# -------------------------------
# Ingest Logs
# -------------------------------



@app.post("/logs")
async def ingest_logs(request: Request):
    payload = await request.json()
    batch = payload.get("batch", [])

    logs = read_logs()

    for log in batch:
        log["id"] = str(uuid.uuid4())   
        log["received_at"] = datetime.utcnow().isoformat()
        logs.append(log)

    write_logs(logs)

    return {"stored": len(batch)}



# -------------------------------
# Get Logs
# -------------------------------

@app.get("/logs")
def get_logs(limit: int = 100):
    logs = read_logs()
    return {
        "count": len(logs),
        "logs": logs[-limit:]
    }


# -------------------------------
# Delete ALL Logs
# -------------------------------

@app.delete("/logs")
def delete_all_logs():
    write_logs([])
    return {"message": "All logs deleted"}


# -------------------------------
# Delete Log by ID
# -------------------------------

@app.delete("/logs/{log_id}")
def delete_log_by_id(log_id: str):
    logs = read_logs()

    new_logs = [log for log in logs if log.get("id") != log_id]

    if len(new_logs) == len(logs):
        raise HTTPException(status_code=404, detail="Log not found")

    write_logs(new_logs)

    return {"message": f"Log {log_id} deleted"}


# -------------------------------
# Delete Logs by Level (optional)
# -------------------------------

@app.delete("/logs/level/{level}")
def delete_by_level(level: str):
    logs = read_logs()

    new_logs = [log for log in logs if log.get("level") != level.upper()]

    deleted_count = len(logs) - len(new_logs)

    write_logs(new_logs)

    return {
        "deleted": deleted_count,
        "message": f"Deleted all {level.upper()} logs"
    }
