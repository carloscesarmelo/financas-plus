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


@router.get("/webhooks/kiwify/diag")
def kiwify_webhook_diag(token: str | None = None):
    """Endpoint temporário só para comparar o token recebido com o configurado, sem expor nenhum dos dois por completo."""
    expected = (os.environ.get("KIWIFY_WEBHOOK_TOKEN") or "").strip()
    received = (token or "").strip()
    return {
        "expected_set": bool(expected),
        "expected_length": len(expected),
        "expected_tail": expected[-6:] if expected else None,
        "received_length": len(received),
        "received_tail": received[-6:] if received else None,
        "match": expected == received,
    }


@router.get("/webhooks/kiwify/debug")
def kiwify_webhook_debug(token: str | None = None, db: Session = Depends(get_db)):
    """Endpoint temporário para calibrar o parser com os payloads reais recebidos."""
    _check_token(token)

    events = db.query(PaymentEvent).order_by(PaymentEvent.id.desc()).limit(5).all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "email": e.email,
            "user_id": e.user_id,
            "plan_applied": e.plan_applied,
            "processed": e.processed,
            "raw_payload": e.raw_payload,
        }
        for e in events
    ]
