from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from datetime import datetime
from typing import List
import json
import os
import uuid
import csv
import io
import threading

app = FastAPI(title="Log Server - CSV Output")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = "logs.ndjson"
lock = threading.Lock()

# Ensure file exists
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, "w").close()


# -------------------------------
# Utility Functions
# -------------------------------

def append_log(log: dict):
    with lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log) + "\n")


def read_logs(limit: int = 100) -> List[dict]:
    with open(LOG_FILE, "r", encoding="utf-8") as f:
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
# Ingest JSON Logs
# -------------------------------

@app.post("/logs")
async def ingest_logs(payload: dict):

    if "batch" not in payload or not isinstance(payload["batch"], list):
        raise HTTPException(status_code=400, detail="Invalid format")

    count = 0
    for log in payload["batch"]:
        log["id"] = str(uuid.uuid4())
        log["received_at"] = datetime.utcnow().isoformat()
        append_log(log)
        count += 1

    return {"status": "stored", "count": count}


# -------------------------------
# Get Logs as CSV (Comma Separated)
# -------------------------------

@app.get("/logs")
def get_logs(limit: int = 100):

    logs = read_logs(limit)

    if not logs:
        return {"message": "No logs found"}

    output = io.StringIO()

    # Use keys of first log as CSV header
    writer = csv.DictWriter(output, fieldnames=logs[0].keys())
    writer.writeheader()
    writer.writerows(logs)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=logs.csv"
        }
    )

@app.delete("/logs")
def delete_all_logs():
    with lock:
        open(LOG_FILE, "w").close()
    return {"message": "All logs deleted successfully"}
