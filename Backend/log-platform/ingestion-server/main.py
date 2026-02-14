# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from datetime import datetime
# import json
# import os
# import uuid
# from typing import List

# app = FastAPI(title="HackForGreen Log Ingestion Server (Pathway Compatible)")

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# LOG_FILE = "logs.ndjson"   # Using NDJSON format


# # -------------------------------
# # Ensure log file exists
# # -------------------------------
# if not os.path.exists(LOG_FILE):
#     open(LOG_FILE, "w").close()


# # -------------------------------
# # Utility Functions
# # -------------------------------

# def append_log(log: dict):
#     """Append single JSON object as one line (NDJSON format)"""
#     with open(LOG_FILE, "a") as f:
#         f.write(json.dumps(log) + "\n")


# def read_logs(limit: int = 100) -> List[dict]:
#     """Read last N logs"""
#     with open(LOG_FILE, "r") as f:
#         lines = f.readlines()

#     logs = [json.loads(line.strip()) for line in lines if line.strip()]
#     return logs[-limit:]


# # -------------------------------
# # Health Check
# # -------------------------------

# @app.get("/")
# def health():
#     return {"status": "running"}


# # -------------------------------
# # Ingest SINGLE Log (Pathway Style)
# # -------------------------------

# @app.post("/logs")
# async def ingest_log(payload: dict):

#     if "batch" not in payload or not isinstance(payload["batch"], list):
#         raise HTTPException(status_code=400, detail="Invalid format")

#     for log in payload["batch"]:
#         log["id"] = str(uuid.uuid4())
#         log["received_at"] = datetime.utcnow().isoformat()
#         append_log(log)

#     return {"status": "stored", "count": len(payload["batch"])}


# # -------------------------------
# # Get Logs
# # -------------------------------

# from fastapi.responses import PlainTextResponse

# @app.get("/logs")
# def get_logs(limit: int = 100):
#     logs = read_logs(limit)
#     ndjson = "\n".join(json.dumps(log) for log in logs)
#     return PlainTextResponse(ndjson, media_type="application/x-ndjson")


# # -------------------------------
# # Delete ALL Logs
# # -------------------------------

# @app.delete("/logs")
# def delete_all_logs():
#     open(LOG_FILE, "w").close()
#     return {"message": "All logs deleted"}


# # -------------------------------
# # Delete Log by ID
# # -------------------------------

# @app.delete("/logs/{log_id}")
# def delete_log_by_id(log_id: str):

#     with open(LOG_FILE, "r") as f:
#         lines = f.readlines()

#     new_lines = []
#     deleted = False

#     for line in lines:
#         log = json.loads(line.strip())
#         if log.get("id") != log_id:
#             new_lines.append(line)
#         else:
#             deleted = True

#     if not deleted:
#         raise HTTPException(status_code=404, detail="Log not found")

#     with open(LOG_FILE, "w") as f:
#         f.writelines(new_lines)

#     return {"message": f"Log {log_id} deleted"}

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
import uuid
import os
import json

from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.responses import PlainTextResponse


app = FastAPI(title="HackForGreen Log Ingestion Server (MongoDB Version)")

# -------------------------------
# Enable CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# MongoDB Setup
# -------------------------------

MONGO_URI = "mongodb+srv://nikzone112_db_user:zRg0pGouhD2GS3Gf@logstore.cd1jafc.mongodb.net/?appName=LogStore"
client = AsyncIOMotorClient(MONGO_URI)

db = client["hackforgreen"]
logs_collection = db["logs"]
# -------------------------------
# Health Check
# -------------------------------

@app.get("/")
def health():
    return {"status": "running"}

# -------------------------------
# Ingest Logs
# -------------------------------

@app.post("/logs")
async def ingest_log(payload: dict):

    if "batch" not in payload or not isinstance(payload["batch"], list):
        raise HTTPException(status_code=400, detail="Invalid format")

    logs_to_insert = []

    for log in payload["batch"]:
        log["id"] = str(uuid.uuid4())
        log["received_at"] = datetime.utcnow().isoformat()
        logs_to_insert.append(log)

    if logs_to_insert:
        await logs_collection.insert_many(logs_to_insert)

    return {"status": "stored", "count": len(logs_to_insert)}

# -------------------------------
# Get Logs (NDJSON Format)
# -------------------------------

@app.get("/logs")
async def get_logs(limit: int = 100):

    cursor = logs_collection.find().sort("received_at", -1).limit(limit)

    logs = []
    async for document in cursor:
        document.pop("_id", None)  # Remove Mongo internal ID
        logs.append(document)

    ndjson = "\n".join(json.dumps(log) for log in reversed(logs))
    return PlainTextResponse(ndjson, media_type="application/x-ndjson")

# -------------------------------
# Delete All Logs
# -------------------------------

@app.delete("/logs")
async def delete_all_logs():
    await logs_collection.delete_many({})
    return {"message": "All logs deleted"}

# -------------------------------
# Delete Log by ID
# -------------------------------

@app.delete("/logs/{log_id}")
async def delete_log_by_id(log_id: str):

    result = await logs_collection.delete_one({"id": log_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Log not found")

    return {"message": f"Log {log_id} deleted"}
