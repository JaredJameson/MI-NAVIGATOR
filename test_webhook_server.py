"""
Test webhook server for Feature #319 testing.

This server can:
1. Receive webhooks successfully (return 200)
2. Simulate failures (return 500)
3. Toggle between success/failure modes
4. Log all webhook attempts
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import json

app = FastAPI(title="Test Webhook Server")

# State management
server_state = {
    "mode": "success",  # "success" or "fail"
    "received_webhooks": [],
    "failure_count": 0
}


@app.get("/")
async def root():
    """Server status."""
    return {
        "status": "running",
        "mode": server_state["mode"],
        "webhooks_received": len(server_state["received_webhooks"]),
        "failures_returned": server_state["failure_count"]
    }


@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Webhook endpoint.

    Behavior depends on server mode:
    - "success": Always return 200
    - "fail": Always return 500
    """
    # Parse request
    body = await request.json()

    # Log webhook
    webhook_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "payload": body,
        "mode_when_received": server_state["mode"]
    }
    server_state["received_webhooks"].append(webhook_data)

    print(f"\n📥 Webhook received at {webhook_data['timestamp']}")
    print(f"   Mode: {server_state['mode']}")
    print(f"   Payload: {json.dumps(body, indent=2)}")

    # Return response based on mode
    if server_state["mode"] == "fail":
        server_state["failure_count"] += 1
        print(f"   ❌ Returning 500 (failure mode)")
        return JSONResponse(
            status_code=500,
            content={"error": "Simulated server error", "mode": "fail"}
        )
    else:
        print(f"   ✅ Returning 200 (success mode)")
        return JSONResponse(
            status_code=200,
            content={"message": "Webhook received", "mode": "success"}
        )


@app.post("/mode/{new_mode}")
async def set_mode(new_mode: str):
    """
    Change server mode.

    Args:
        new_mode: "success" or "fail"
    """
    if new_mode not in ["success", "fail"]:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid mode. Use 'success' or 'fail'"}
        )

    old_mode = server_state["mode"]
    server_state["mode"] = new_mode

    print(f"\n🔄 Mode changed: {old_mode} → {new_mode}")

    return {
        "message": f"Mode changed to {new_mode}",
        "old_mode": old_mode,
        "new_mode": new_mode
    }


@app.get("/webhooks")
async def get_webhooks():
    """Get all received webhooks."""
    return {
        "total": len(server_state["received_webhooks"]),
        "webhooks": server_state["received_webhooks"]
    }


@app.post("/reset")
async def reset():
    """Reset server state."""
    server_state["received_webhooks"] = []
    server_state["failure_count"] = 0
    server_state["mode"] = "success"

    print("\n🔄 Server state reset")

    return {"message": "Server reset", "state": server_state}


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Test Webhook Server Starting")
    print("="*60)
    print("\nEndpoints:")
    print("  - GET  /           - Server status")
    print("  - POST /webhook    - Receive webhooks")
    print("  - POST /mode/{mode} - Set mode (success/fail)")
    print("  - GET  /webhooks   - List received webhooks")
    print("  - POST /reset      - Reset server state")
    print("\nServer will run on: http://localhost:8001")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
