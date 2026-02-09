from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import os

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["log_platform"]
collection = db["logs"]

app = FastAPI(title="Log Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Health check
@app.get("/")
def health():
    return {"status": "running"}

# 🔹 Ingest logs (already used by SDK)
@app.post("/logs")
async def receive_logs(request: Request):
    payload = await request.json()
    logs = payload.get("batch", [])

    for log in logs:
        log["received_at"] = datetime.utcnow()
        collection.insert_one(log)

    return {"status": "ok", "stored": len(logs)}

# 🔹 FETCH LOGS AS JSON ✅ (THIS IS WHAT YOU WANT)
@app.get("/logs")
def get_logs(
    limit: int = Query(50, le=500),
    level: str | None = None,
    appName: str | None = None
):
    query = {}

    if level:
        query["level"] = level.upper()

    if appName:
        query["appName"] = appName

    logs = collection.find(query).sort("received_at", -1).limit(limit)

    result = []
    for log in logs:
        log["_id"] = str(log["_id"])  # ObjectId → string
        result.append(log)

    return {
        "count": len(result),
        "logs": result
    }
