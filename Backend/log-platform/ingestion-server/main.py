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
from typing import List

app = FastAPI(title="HackForGreen Log Ingestion Server (Pathway Compatible)")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = "logs.ndjson"   # Using NDJSON format


# -------------------------------
# Ensure log file exists
# -------------------------------
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, "w").close()


# -------------------------------
# Utility Functions
# -------------------------------

def append_log(log: dict):
    """Append single JSON object as one line (NDJSON format)"""
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")


def read_logs(limit: int = 100) -> List[dict]:
    """Read last N logs"""
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()

    logs = [json.loads(line.strip()) for line in lines if line.strip()]
    return logs[-limit:]


# -------------------------------
# Health Check
# -------------------------------

@app.get("/")
def health():
    return {"status": "running"}


# -------------------------------
# Ingest SINGLE Log (Pathway Style)
# -------------------------------

@app.post("/logs")
async def ingest_log(log: dict):
    """
    Accepts ONE JSON object per request.
    Compatible with Pathway streaming.
    """

    if not isinstance(log, dict):
        raise HTTPException(status_code=400, detail="Invalid JSON object")

    # Add metadata
    log["id"] = str(uuid.uuid4())
    log["received_at"] = datetime.utcnow().isoformat()

    append_log(log)

    return {
        "status": "stored",
        "log_id": log["id"]
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
# Delete ALL Logs
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

    with open(LOG_FILE, "r") as f:
        lines = f.readlines()

    new_lines = []
    deleted = False

    for line in lines:
        log = json.loads(line.strip())
        if log.get("id") != log_id:
            new_lines.append(line)
        else:
            deleted = True

    if not deleted:
        raise HTTPException(status_code=404, detail="Log not found")

    with open(LOG_FILE, "w") as f:
        f.writelines(new_lines)

    return {"message": f"Log {log_id} deleted"}
