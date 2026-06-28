from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password
from app.database import get_db
from app.models import User

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

    user = User(name=name.strip(), email=email_normalized, password_hash=hash_password(password))
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

    request.session["user_id"] = user.id
    if not user.onboarding_completed:
        return RedirectResponse("/onboarding", status_code=303)
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
