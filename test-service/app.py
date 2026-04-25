"""
Test Service - Simulates a production service with errors.
Sends logs to Splunk AND metrics to New Relic.
"""

import uuid
import random
import logging
import time
import asyncio
import os
from datetime import datetime
import random

from fastapi import FastAPI, Request
import httpx
from dotenv import load_dotenv
import newrelic.agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# DOCKER-FRIENDLY CONFIGURATION
# ============================================

# New Relic - use environment variable for config path
NEW_RELIC_CONFIG_PATH = os.getenv("NEW_RELIC_CONFIG_PATH", "/app/newrelic.ini")
if os.path.exists(NEW_RELIC_CONFIG_PATH):
    newrelic.agent.initialize(NEW_RELIC_CONFIG_PATH)
    print(f"✅ New Relic initialized with config: {NEW_RELIC_CONFIG_PATH}")
else:
    print(f"⚠️ New Relic config not found at {NEW_RELIC_CONFIG_PATH} - continuing without NR")

# Splunk - use environment variables with fallback
SPLUNK_HEC_URL = os.getenv("SPLUNK_HEC_URL", "https://host.docker.internal:8088/services/collector")
SPLUNK_HEC_TOKEN = os.getenv("SPLUNK_API_TOKEN", "fab25b47-0f04-4797-a85e-ece5c018791a")
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.3"))

print(f"✅ Splunk HEC URL: {SPLUNK_HEC_URL}")
print(f"✅ Error rate: {ERROR_RATE}")

# Create FastAPI app
app = FastAPI(title="Test Service", description="Generates test logs for Splunk")


# ================================
# MIDDLEWARE
# ================================
@app.middleware("http")
async def newrelic_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id

    # Attach attribute to New Relic if available
    try:
        txn = newrelic.agent.current_transaction()
        if txn:
            newrelic.agent.add_custom_attribute("requestId", request_id)
    except:
        pass

    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


print("Test Service starting...")


@app.post("/simulate")
async def simulate_request(request: Request):
    start_time = time.time()
    request_id = request.state.request_id

    will_error = random.random() < ERROR_RATE

    await asyncio.sleep(0.01)

    log_data = {
        "requestId": request_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "test-service",
        "environment": "development"
    }
    error_messages = [
        "Database connection failed due to timeout",
        "API rate limit exceeded - too many requests",
        "Memory allocation failed - heap limit reached",
        "Network timeout in payment service",
        "Authentication token expired",
        "Redis connection refused",
        "Kafka producer failed to send message",
        "S3 bucket access denied",
        "Lambda function invocation timeout",
        "DynamoDB provisioned throughput exceeded"
    ]
    
    stack_traces = [
        "Traceback: Connection refused at line 42",
        "Traceback: RateLimitError at line 128",
        "Traceback: MemoryError at line 256",
        "Traceback: TimeoutError at line 89",
        "Traceback: AuthError at line 34"
    ]
    if will_error:
        log_data["level"] = "ERROR"
        log_data["message"] = random.choice(error_messages)
        log_data["stack_trace"] = random.choice(stack_traces)
        status = 500
        response_message = "Internal Server Error"
    else:
        log_data["level"] = "INFO"
        log_data["message"] = "Request processed successfully"
        status = 200
        response_message = "Success"

    await send_to_splunk(log_data)

    duration = (time.time() - start_time) * 1000

    logger.info(f"Request {request_id}: {response_message} ({duration:.2f}ms)")

    return {
        "status": status,
        "message": response_message,
        "requestId": request_id,
        "error_occurred": will_error,
        "duration_ms": duration
    }


async def send_to_splunk(log_data: dict):
    """Send log to Splunk HEC."""
    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "event": log_data,
        "index": "main",
        "sourcetype": "json"
    }

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                SPLUNK_HEC_URL,
                headers=headers,
                json=payload,
                timeout=5.0
            )
            if response.status_code != 200:
                logger.error(f"Failed to send to Splunk: {response.status_code}")
            else:
                logger.info(f"Log sent to Splunk for requestId: {log_data.get('requestId')}")
        except Exception as e:
            logger.error(f"Error sending to Splunk: {str(e)}")


@app.get("/health")
async def health(request: Request):
    return {
        "status": "ok",
        "service": "test-service",
        "requestId": request.state.request_id
    }


@app.post("/force-error")
async def force_error(request: Request):
    """Force an error for testing."""
    request_id = request.state.request_id
    error_messages = [
        "Database connection failed due to timeout in payment service",
        "API rate limit exceeded - payment service throttled",
        "Memory allocation failed in payment worker",
        "Network timeout connecting to payment gateway",
        "Authentication failed for payment service"
    ]
    
    stack_traces = [
        "Traceback: Connection refused at line 42",
        "Traceback: RateLimitError at line 128", 
        "Traceback: MemoryError at line 256",
        "Traceback: TimeoutError at line 89",
        "Traceback: AuthError at line 34"
    ]

    log_data = {
        "requestId": request_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "test-service",
        "environment": "development",
        "level": "ERROR",
        "message": random.choice(error_messages),
        "stack_trace": random.choice(stack_traces)
    }
    
    await send_to_splunk(log_data)
    
    return {
        "status": 500,
        "message": "Forced Internal Server Error",
        "requestId": request_id,
        "error_occurred": True
    }