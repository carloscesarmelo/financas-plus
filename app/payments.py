"""Integração com webhooks da Kiwify.

ATENÇÃO: a documentação pública e completa do payload da Kiwify (nomes exatos de
campos como Customer/Subscription/Product) não está acessível de forma confiável.
Por isso este módulo:

  1. Grava SEMPRE o payload bruto em PaymentEvent, mesmo quando não consegue
     processá-lo — isso garante que nenhum evento se perde.
  2. Tenta extrair email/evento/produto por múltiplos caminhos possíveis
     (variações de maiúsculas e nomes de campo conhecidas).

Passo a passo para calibrar em produção:
  1. Configure o webhook na Kiwify (Apps > Webhooks) apontando para
     `https://SEU_DOMINIO/webhooks/kiwify?token=KIWIFY_WEBHOOK_TOKEN`.
  2. Selecione os eventos: compra_aprovada, compra_reembolsada, chargeback,
     subscription_canceled, subscription_renewed.
  3. Clique em "Testar Webhook" no painel da Kiwify.
  4. Consulte a tabela payment_events (campo raw_payload) e confirme se
     EMAIL_PATHS / EVENT_TYPE_KEYS / PRODUCT_ID_PATHS abaixo batem com o payload
     real. Ajuste se necessário.
  5. Em KIWIFY_PLAN_MAP (variável de ambiente), mapeie cada product_id da
     Kiwify para "mensal", "anual" ou "vitalicio".
"""

import datetime
import json
import os

from sqlalchemy.orm import Session

from app.models import PaymentEvent, User

EVENTS_APPROVED = {"compra_aprovada", "subscription_renewed"}
EVENTS_REVOKED = {"compra_reembolsada", "chargeback", "subscription_canceled"}

EMAIL_PATHS = ["Customer.email", "customer.email", "email", "buyer.email"]
EVENT_TYPE_KEYS = ["webhook_event_type", "event", "order_status"]
PRODUCT_ID_PATHS = ["Product.product_id", "product.product_id", "product_id", "Subscription.plan.id"]

PLAN_DURATION_DAYS = {"mensal": 30, "anual": 365}


def _dig(payload: dict, path: str):
    value = payload
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def _first_match(payload: dict, paths: list[str]):
    for path in paths:
        value = _dig(payload, path)
        if value:
            return value
    return None


def _plan_map() -> dict:
    raw = os.environ.get("KIWIFY_PLAN_MAP", "{}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _plan_expiry(plan_key: str) -> datetime.datetime | None:
    days = PLAN_DURATION_DAYS.get(plan_key)
    if not days:
        return None
    return datetime.datetime.utcnow() + datetime.timedelta(days=days)


def user_has_active_plan(db: Session, user: User) -> bool:
    if not user.plan_active:
        return False
    if user.plan_expires_at and user.plan_expires_at < datetime.datetime.utcnow():
        user.plan_active = False
        db.commit()
        return False
    return True


def apply_kiwify_event(db: Session, payload: dict) -> PaymentEvent:
    email = _first_match(payload, EMAIL_PATHS)
    event_type = _first_match(payload, EVENT_TYPE_KEYS)
    product_id = _first_match(payload, PRODUCT_ID_PATHS)
    plan_key = _plan_map().get(product_id) if product_id else None

    user = db.query(User).filter(User.email == email).first() if email else None

    event = PaymentEvent(
        provider="kiwify",
        event_type=event_type,
        email=email,
        user_id=user.id if user else None,
        raw_payload=payload,
    )

    if user and plan_key and event_type in EVENTS_APPROVED:
        user.plan = plan_key
        user.plan_active = True
        user.plan_expires_at = _plan_expiry(plan_key)
        event.plan_applied = plan_key
        event.processed = True
    elif user and event_type in EVENTS_REVOKED:
        user.plan_active = False
        event.processed = True

    db.add(event)
    db.commit()
    db.refresh(event)
    return event
