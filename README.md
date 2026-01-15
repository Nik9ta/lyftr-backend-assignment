# Lyftr Backend Assignment

This project implements a minimal backend service for receiving,
validating, storing, and querying WhatsApp-style message events.

## Tech Stack
- Python 3.12
- FastAPI
- SQLite
- Pydantic v2

## Features
- Webhook ingestion with HMAC-SHA256 verification
- Idempotent message handling using message_id as primary key
- Message querying with pagination and filters
- Aggregated message statistics
- Health check endpoints

## API Endpoints

### POST /webhook
Receives a message payload and validates it using an HMAC-SHA256 signature.

Headers:
- Content-Type: application/json
- X-Signature: HMAC-SHA256 hex digest of raw request body

### GET /messages
Query stored messages.

Query parameters:
- limit (default 50, max 100)
- offset
- from
- since
- q

### GET /stats
Returns aggregated message statistics.

### GET /health/live
Liveness probe.

### GET /health/ready
Readiness probe (checks DB and WEBHOOK_SECRET).

## Running Locally

```bash
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload


