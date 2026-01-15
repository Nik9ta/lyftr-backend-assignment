from fastapi import FastAPI, Request, HTTPException, Query
from .models import init_db
from .schemas import MessagePayload
from .utils import verify_signature
from .storage import insert_message, get_messages, get_stats
from .config import settings

app = FastAPI()

# Startup event
@app.on_event("startup")
def startup_event():
    init_db()

# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    raw_body = await request.body()

    signature = request.headers.get("X-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="missing signature")

    if not verify_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="invalid signature")

    payload = MessagePayload.model_validate_json(raw_body)

    result = insert_message(payload)
    return {"status": "ok", "result": result}


# Messages endpoint
@app.get("/messages")
def list_messages(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    from_: str = Query(None, alias="from"),
    since: str = Query(None),
    q: str = Query(None)
):
    return get_messages(limit, offset, from_, since, q)

# Stats endpoint
@app.get("/stats")
def stats():
    return get_stats()

# Health probes
@app.get("/health/live")
def live():
    return {"status": "live"}

@app.get("/health/ready")
def ready():
    try:
        init_db()
        if not settings.WEBHOOK_SECRET:
            raise Exception("WEBHOOK_SECRET not set")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="not ready")
