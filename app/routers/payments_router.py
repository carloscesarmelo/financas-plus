import os

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PaymentEvent
from app.payments import apply_kiwify_event

router = APIRouter()


def _check_token(token: str | None):
    expected_token = (os.environ.get("KIWIFY_WEBHOOK_TOKEN") or "").strip()
    if not expected_token or (token or "").strip() != expected_token:
        raise HTTPException(status_code=401, detail="Token inválido")


@router.post("/webhooks/kiwify")
async def kiwify_webhook(request: Request, token: str | None = None, db: Session = Depends(get_db)):
    _check_token(token)

    payload = await request.json()
    event = apply_kiwify_event(db, payload)

    return {"received": True, "processed": event.processed}
