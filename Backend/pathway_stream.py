

import pathway as pw
from RAGLLM import analyze_log

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


table = pw.io.csv.read(
    "./data.csv",
    schema=LogSchema,
    mode="streaming"
)



error_logs = table.filter(
    pw.this.level.str.strip().str.upper() == "ERROR"
)


def analyze_wrapper(message: str):
    return analyze_log(message)


llm_table = error_logs.select(
    log_id=pw.this.id,
    message=pw.this.message,
    analysis=pw.apply(
        analyze_wrapper,
        pw.this.message
    )
)

pw.io.csv.write(llm_table, "./analysis_output.txt")

pw.run()

