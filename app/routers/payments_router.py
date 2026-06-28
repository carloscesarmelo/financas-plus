import os

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.payments import apply_kiwify_event

router = APIRouter()


@router.post("/webhooks/kiwify")
async def kiwify_webhook(request: Request, token: str | None = None, db: Session = Depends(get_db)):
    expected_token = os.environ.get("KIWIFY_WEBHOOK_TOKEN")
    if not expected_token or token != expected_token:
        raise HTTPException(status_code=401, detail="Token inválido")

    payload = await request.json()
    event = apply_kiwify_event(db, payload)

    return {"received": True, "processed": event.processed}
