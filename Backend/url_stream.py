import pathway as pw
import requests
import time
import csv
import io


# -----------------------
# Schema
# -----------------------
class LogSchema(pw.Schema):
    timestamp: str
    app: str
    url: str
    userAgent: str
    level: str
    type: str
    message: str
    data: str
    id: str
    received_at: str


# -----------------------
# HTTP Log Connector
# -----------------------
class HttpLogSubject(pw.io.python.ConnectorSubject):

    def __init__(self):
        super().__init__()
        self.seen_ids = set()

    def run(self):
        api_url = "https://hackforgreen.onrender.com/logs"

        while True:
            try:
                response = requests.get(api_url)
                if response.status_code != 200:
                    print("Failed to fetch:", response.status_code)
                    time.sleep(5)
                    continue

                csv_text = response.text.strip()

                # If backend returned JSON message (no logs case)
                if csv_text.startswith("{"):
                    print("No logs yet...")
                    time.sleep(5)
                    continue

                reader = csv.DictReader(io.StringIO(csv_text))

                new_rows = 0

                for log in reader:

                    log_id = log.get("id")
                    if not log_id:
                        continue

                    if log_id in self.seen_ids:
                        continue

                    self.seen_ids.add(log_id)
                    new_rows += 1

                    self.next(
                        {
                            "timestamp": log.get("timestamp", ""),
                            "app": log.get("app", ""),
                            "url": log.get("url", ""),
                            "userAgent": log.get("userAgent", ""),
                            "level": log.get("level", ""),
                            "type": log.get("type", ""),
                            "message": log.get("message", ""),
                            "data": log.get("data", ""),
                            "id": log_id,
                            "received_at": log.get("received_at", "")
                        }
                    )

                if new_rows > 0:
                    print(f"Sent {new_rows} new logs to Pathway")

                self.commit()  # 🔥 REQUIRED

            except Exception as e:
                print("Error fetching logs:", e)

            time.sleep(5)


# -----------------------
# Create Table From API
# -----------------------
table = pw.io.python.read(
    HttpLogSubject(),
    schema=LogSchema
)


# -----------------------
# Filter ERROR Logs
# -----------------------
error_logs = table.filter(
    pw.this.level.str.strip().str.upper() == "ERROR"
)


# # -----------------------
# # Write Output
# # -----------------------
# pw.io.csv.write(error_logs, "./analysis_output.csv")
pw.io.print(error_logs)

pw.run()
