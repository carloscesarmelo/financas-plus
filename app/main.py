import datetime
import os

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.auth import NotAuthenticated, PlanRequired, require_user
from app.database import Base, SessionLocal, engine, get_db
from app.finance_logic import challenge_pace_status
from app.gamification import compute_badges, current_streak
from app.models import Challenge, LearningContent, Tip, User
from app.routers import (
    admin_router,
    auth_router,
    challenges_router,
    diagnostico_router,
    learning_router,
    onboarding_router,
    payments_router,
    plans_router,
    tips_router,
)
from app.seed import run_seed
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI(title="FINANÇAS+")

app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "dev-secret-key"))
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(admin_router.router)
app.include_router(auth_router.router)
app.include_router(onboarding_router.router)
app.include_router(diagnostico_router.router)
app.include_router(payments_router.router)
app.include_router(plans_router.router)
app.include_router(challenges_router.router)
app.include_router(learning_router.router)
app.include_router(tips_router.router)


@app.exception_handler(NotAuthenticated)
def handle_not_authenticated(request: Request, exc: NotAuthenticated):
    return RedirectResponse("/login", status_code=303)


@app.exception_handler(PlanRequired)
def handle_plan_required(request: Request, exc: PlanRequired):
    return RedirectResponse("/planos", status_code=303)


def _run_migrations():
    migrations = [
        "ALTER TABLE tips ADD COLUMN source TEXT DEFAULT 'admin'",
        "ALTER TABLE tips ADD COLUMN author_name TEXT",
        "ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'free'",
        "ALTER TABLE users ADD COLUMN plan_active INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN plan_expires_at TIMESTAMP",
    ]
    with engine.connect() as conn:
        for sql in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception:
                pass


@app.on_event("startup")
def on_startup():
    _run_migrations()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()


@app.get("/")
def root(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return templates.TemplateResponse("landing.html", {"request": request, "user": None})
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/dashboard")
def dashboard(request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)):
    challenges = (
        db.query(Challenge).filter(Challenge.user_id == user.id).order_by(Challenge.created_at.desc()).all()
    )
    badges = compute_badges(db, user)
    streak = current_streak(db, user)

    pace_by_challenge = {c.id: challenge_pace_status(c) for c in challenges}
    pending_challenges = [
        c for c in challenges if not pace_by_challenge[c.id]["is_completed"] and pace_by_challenge[c.id]["days_behind"] > 0
    ]

    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    new_tips = db.query(Tip).filter(Tip.created_at >= cutoff).order_by(Tip.created_at.desc()).all()
    new_learn = db.query(LearningContent).filter(LearningContent.created_at >= cutoff).order_by(LearningContent.created_at.desc()).all()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "challenges": challenges,
            "badges": badges,
            "streak": streak,
            "xp_to_next_level": 100 - (user.xp % 100),
            "pace_by_challenge": pace_by_challenge,
            "pending_challenges": pending_challenges,
            "new_tips": new_tips,
            "new_learn": new_learn,
        },
    )
