# Logger SDK Integration Guide

## Step 1: Add SDK
```html
<script src="https://<your-username>.github.io/logger-sdk/logger-sdk.js"></script>
<script>
  Logger.init({
    endpoint: "https://your-backend.onrender.com/logs",
    appName: "your-app-name"
  });
</script>
Logger.log("User logged in");
Logger.error("Payment failed", { orderId: 123 });

---


