import os

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

PLAN_LABELS = {"mensal": "Mensal", "anual": "Anual", "vitalicio": "Vitalício"}


@router.get("/planos")
def planos(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    checkout_urls = {
        "mensal": os.environ.get("KIWIFY_CHECKOUT_URL_MENSAL", ""),
        "anual": os.environ.get("KIWIFY_CHECKOUT_URL_ANUAL", ""),
        "vitalicio": os.environ.get("KIWIFY_CHECKOUT_URL_VITALICIO", ""),
    }

    return templates.TemplateResponse(
        "planos.html",
        {
            "request": request,
            "user": user,
            "checkout_urls": checkout_urls,
            "plan_label": PLAN_LABELS.get(user.plan) if user else None,
        },
    )
