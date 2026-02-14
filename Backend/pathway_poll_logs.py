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
# 3️⃣ Read From Your API
# ---------------------------
logs_table = pw.io.http.read(
    url="https://hackforgreen.onrender.com/logs",
    method="GET",
    schema=LogSchema,
    format="json",   # because NDJSON = one JSON per line
    autocommit_duration_ms=5000
)



# ---------------------------
# 4️⃣ Filter Only ERROR Logs
# ---------------------------
error_logs = logs_table.filter(
    pw.this.level == "error"
)


# ---------------------------
# 5️⃣ Print Output to Console
# ---------------------------
pw.debug.compute_and_print(error_logs)


# ---------------------------
# 6️⃣ Run Pathway
# ---------------------------
pw.run()

