const LOG_ENDPOINT = "http://localhost:8000/logs";
let networkBuffer = [];
let lastFlush = Date.now();

chrome.webRequest.onCompleted.addListener(
  details => {
    networkBuffer.push({
      timestamp: new Date().toISOString(),
      level: "INFO",
      type: "network",
      method: details.method,
      status: details.statusCode,
      url: details.url
    });

    if (Date.now() - lastFlush >= 1000) {
      fetch(LOG_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          batch: networkBuffer,
          sent_at: new Date().toISOString()
        })
      }).catch(() => {});

      networkBuffer = [];
      lastFlush = Date.now();
    }
  },
  { urls: ["<all_urls>"] }
);
