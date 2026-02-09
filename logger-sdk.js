(function (window) {
  if (window.Logger) return; // prevent double load

  const Logger = {};
  let config = {};
  let buffer = [];
  const FLUSH_INTERVAL = 1000;

  /* =========================
     Utilities
  ========================= */
  function now() {
    return new Date().toISOString();
  }

  function pushLog(log) {
    buffer.push({
      timestamp: now(),
      appName: config.appName || "unknown-app",
      url: window.location.href,
      userAgent: navigator.userAgent,
      ...log
    });
  }

  function flushLogs() {
    if (!buffer.length) return;

    fetch(config.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        batch: buffer,
        sentAt: now()
      })
    }).catch(() => {});

    buffer = [];
  }

  /* =========================
     Public API
  ========================= */
  Logger.init = function (options) {
    if (!options || !options.endpoint) {
      throw new Error("Logger.init(): endpoint is required");
    }

    config = options;

    // periodic flush
    setInterval(flushLogs, FLUSH_INTERVAL);

    /* Console capture */
    ["log", "warn", "error"].forEach(level => {
      const original = console[level];
      console[level] = function (...args) {
        pushLog({
          level: level.toUpperCase(),
          type: "console",
          message: args.map(String).join(" ")
        });
        original.apply(console, args);
      };
    });

    /* Runtime errors */
    window.addEventListener("error", e => {
      pushLog({
        level: "ERROR",
        type: "runtime",
        message: e.message,
        source: e.filename,
        line: e.lineno,
        column: e.colno
      });
    });

    /* Promise rejections */
    window.addEventListener("unhandledrejection", e => {
      pushLog({
        level: "ERROR",
        type: "promise",
        message: "Unhandled Promise Rejection",
        reason: String(e.reason)
      });
    });

    /* Performance */
    window.addEventListener("load", () => {
      const t = performance.timing;
      pushLog({
        level: "INFO",
        type: "performance",
        loadTimeMs: t.loadEventEnd - t.navigationStart
      });
    });

    pushLog({
      level: "INFO",
      type: "sdk",
      message: "Logger SDK initialized"
    });
  };

  /* Custom logs */
  Logger.log = function (message, data = {}) {
    pushLog({ level: "INFO", type: "custom", message, data });
  };

  Logger.error = function (message, data = {}) {
    pushLog({ level: "ERROR", type: "custom", message, data });
  };

  window.Logger = Logger;
})(window);
