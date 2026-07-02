import os
import secrets

import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password
from app.database import get_db
from app.models import User


def _is_admin_email(email: str) -> bool:
    raw = os.environ.get("ADMIN_EMAILS", "")
    admins = {e.strip().lower() for e in raw.split(",") if e.strip()}
    return email.lower() in admins

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@router.post("/register")
def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    email_normalized = email.strip().lower()
    existing = db.query(User).filter(User.email == email_normalized).first()
    if existing:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Esse e-mail já está cadastrado."},
            status_code=400,
        )

    user = User(
        name=name.strip(),
        email=email_normalized,
        password_hash=hash_password(password),
        is_admin=_is_admin_email(email_normalized),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id
    return RedirectResponse("/onboarding", status_code=303)


@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    email_normalized = email.strip().lower()
    user = db.query(User).filter(User.email == email_normalized).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "E-mail ou senha inválidos."},
            status_code=400,
        )

    if not user.is_admin and _is_admin_email(email_normalized):
        user.is_admin = True
        db.commit()

    request.session["user_id"] = user.id
    if not user.onboarding_completed:
        return RedirectResponse("/onboarding", status_code=303)
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@router.get("/forgot-password")
def forgot_password_form(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request, "user": None})


@router.post("/forgot-password")
def forgot_password_submit(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_at = datetime.datetime.utcnow()
        db.commit()
    return templates.TemplateResponse(
        "forgot_password.html", {"request": request, "user": None, "submitted": True}
    )


@router.get("/reset-password")
def reset_password_form(request: Request, token: str = ""):
    return templates.TemplateResponse(
        "reset_password.html", {"request": request, "user": None, "token": token, "error": None}
    )


@router.post("/reset-password")
def reset_password_submit(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    expiry = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    user = db.query(User).filter(
        User.reset_token == token,
        User.reset_token_at >= expiry,
    ).first()
    if not user:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "user": None, "token": token, "error": "Link inválido ou expirado."},
        )
    user.password_hash = hash_password(password)
    user.reset_token = None
    user.reset_token_at = None
    db.commit()
    return RedirectResponse("/login?msg=senha_redefinida", status_code=303)
