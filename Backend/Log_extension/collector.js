const LOG_ENDPOINT = "http://localhost:8000/logs";
const FLUSH_INTERVAL = 1000;

let logBuffer = [];

/* Add log to buffer */
function pushLog(log) {
  logBuffer.push(log);
}

/* Flush logs every 1 second */
setInterval(() => {
  if (logBuffer.length === 0) return;

  fetch(LOG_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      batch: logBuffer,
      sent_at: new Date().toISOString()
    })
  }).catch(() => {});

  logBuffer = [];
}, FLUSH_INTERVAL);

/* Hook console logs */
["log", "warn", "error"].forEach(level => {
  const original = console[level];
  console[level] = function (...args) {
    pushLog({
      timestamp: new Date().toISOString(),
      level: level.toUpperCase(),
      type: "console",
      message: args.map(String).join(" "),
      url: window.location.href
    });
    original.apply(console, args);
  };
});

/* Capture JS runtime errors */
window.addEventListener("error", e => {
  pushLog({
    timestamp: new Date().toISOString(),
    level: "ERROR",
    type: "runtime",
    message: e.message,
    source: e.filename,
    line: e.lineno,
    column: e.colno,
    url: window.location.href
  });
});

/* Capture promise rejections */
window.addEventListener("unhandledrejection", e => {
  pushLog({
    timestamp: new Date().toISOString(),
    level: "ERROR",
    type: "promise",
    message: "Unhandled Promise Rejection",
    reason: String(e.reason),
    url: window.location.href
  });
});
