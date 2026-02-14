# import pathway as pw
# import requests
# import time


# class LogSchema(pw.Schema):
#     timestamp: str
#     level: str
#     message: str


# class HttpLogSubject(pw.io.python.ConnectorSubject):

#     def __init__(self):
#         super().__init__()
#         self.seen_ids = set()

#     def run(self):
#         url = "https://hackforgreen.onrender.com/logs?limit=100"

#         while True:
#             try:
#                 resp = requests.get(url, timeout=5)
#                 resp.raise_for_status()
#                 data = resp.json()
#                 logs = data.get("logs", [])

#                 for log in logs:
#                     log_key = (
#                         log.get("timestamp", "") +
#                         log.get("message", "") +
#                         log.get("level", "")
#                     )

#                     if log_key not in self.seen_ids:
#                         self.seen_ids.add(log_key)

#                         print("Emitting new log:", log.get("message"))

#                         self.next(
#                             timestamp=log.get("timestamp", ""),
#                             level=log.get("level", "UNKNOWN"),
#                             message=log.get("message") or ""
#                         )


#             except Exception as e:
#                 print("Poll error:", e)

#             time.sleep(2)


# # Read stream
# logs = pw.io.python.read(
#     subject=HttpLogSubject(),
#     schema=LogSchema
# )

# pw.debug.compute_and_print(logs, include_id=False)

# pw.run()


import pathway as pw
import json

# ---------------------------
# 1️⃣ Define Schema
# ---------------------------
class LogSchema(pw.Schema):
    timestamp: str
    app: str
    url: str
    userAgent: str
    level: str
    type: str
    message: str
    data: dict
    id: str
    received_at: str


# ---------------------------
# 2️⃣ Response Mapper
# Extract only "logs" array
# ---------------------------
def mapper(response_bytes: bytes) -> bytes:
    parsed = json.loads(response_bytes.decode())
    logs = parsed["logs"]   # Extract logs list
    return json.dumps(logs).encode()


# ---------------------------
# 3️⃣ Read From Your API
# ---------------------------
logs_table = pw.io.http.read(
    url="https://hackforgreen.onrender.com/logs",
    method="GET",
    schema=LogSchema,
    response_mapper=mapper,
    format="json",
    autocommit_duration_ms=5000  # fetch every 5 seconds
)


# ---------------------------
# 4️⃣ Filter Only ERROR Logs
# ---------------------------
error_logs = logs_table.filter(
    pw.this.level == "ERROR"
)


# ---------------------------
# 5️⃣ Print Output to Console
# ---------------------------
pw.debug.compute_and_print(error_logs)


# ---------------------------
# 6️⃣ Run Pathway
# ---------------------------
pw.run()
