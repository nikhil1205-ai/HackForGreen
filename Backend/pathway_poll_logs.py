import pathway as pw
import requests
import time


# -------------------------------
# Schema
# -------------------------------

class LogSchema(pw.Schema):
    timestamp: str
    level: str
    message: str


# -------------------------------
# Streaming Connector
# -------------------------------

class HttpLogSubject(pw.io.python.ConnectorSubject):

    def __init__(self):
        super().__init__()
        self.seen_ids = set()

    def run(self):
        url = "https://hackforgreen.onrender.com/logs?limit=100"

        while True:
            try:
                print("Polling API...")
                resp = requests.get(url, timeout=5)
                print("Status:", resp.status_code)

                data = resp.json()
                logs = data.get("logs", [])
                print("Logs received:", len(logs))

                for log in logs:
                    print("Log ID:", log.get("id"))

                    log_id = log.get("id")

                    if log_id and log_id not in self.seen_ids:
                        print("New log found:", log_id)

                        self.seen_ids.add(log_id)

                        self.next(
                            timestamp=log.get("timestamp", ""),
                            level=log.get("level", "UNKNOWN"),
                            message=log.get("message", "")
                        )

            except Exception as e:
                print("Poll error:", e)

            time.sleep(2)



# -------------------------------
# Pathway Pipeline
# -------------------------------

logs = pw.io.python.read(
    subject=HttpLogSubject(),
    schema=LogSchema
)

error_logs = logs.filter(pw.this.level == "ERROR")

pw.debug.compute_and_print(error_logs)
