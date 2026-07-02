import os

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PaymentEvent, User
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




@router.post("/internal/make-admin")
def make_admin(email: str, token: str | None = None, db: Session = Depends(get_db)):
    _check_token(token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.is_admin = True
    db.commit()
    return {"ok": True, "email": user.email, "is_admin": user.is_admin}


@router.get("/internal/users-debug")
def users_debug(token: str | None = None, db: Session = Depends(get_db)):
    _check_token(token)
    import os as _os
    users = db.query(User).all()
    return {
        "database_url": _os.environ.get("DATABASE_URL", "NAO DEFINIDA"),
        "users": [{"id": u.id, "email": u.email, "is_admin": u.is_admin, "plan": u.plan, "plan_active": u.plan_active} for u in users],
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
