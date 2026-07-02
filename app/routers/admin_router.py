import datetime
import os

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import (
    Challenge,
    ChallengeDay,
    Diagnostico,
    LearningContent,
    Tip,
    TipSuggestion,
    User,
    UserLearningProgress,
    UserTipSuccess,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin")
def admin_dashboard(request: Request, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    now = datetime.datetime.utcnow()
    week_ago = now - datetime.timedelta(days=7)
    month_ago = now - datetime.timedelta(days=30)

    total_users = db.query(User).count()
    users_paid = db.query(User).filter(User.plan_active.is_(True)).count()
    users_free = total_users - users_paid
    new_this_week = db.query(User).filter(User.created_at >= week_ago).count()
    new_this_month = db.query(User).filter(User.created_at >= month_ago).count()

    plan_mensal = db.query(User).filter(User.plan == "mensal", User.plan_active.is_(True)).count()
    plan_anual = db.query(User).filter(User.plan == "anual", User.plan_active.is_(True)).count()
    plan_vitalicio = db.query(User).filter(User.plan == "vitalicio", User.plan_active.is_(True)).count()

    total_diagnosticos = db.query(Diagnostico).count()
    avg_score_row = db.query(Diagnostico).all()
    avg_score = round(sum(d.percentual_geral for d in avg_score_row) / len(avg_score_row), 1) if avg_score_row else 0

    total_challenges = db.query(Challenge).count()
    total_days_marked = db.query(ChallengeDay).filter(ChallengeDay.marked.is_(True)).count()

    total_learning_completions = db.query(UserLearningProgress).count()
    total_tip_successes = db.query(UserTipSuccess).count()

    pending_suggestions = db.query(TipSuggestion).filter(TipSuggestion.status == "pending").count()

    top_tips = (
        db.query(Tip)
        .all()
    )
    top_tips_data = sorted(
        [{"tip": t, "success_count": len(t.successes)} for t in top_tips],
        key=lambda x: x["success_count"],
        reverse=True,
    )[:5]

    recent_users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .limit(10)
        .all()
    )

    pending_resets = (
        db.query(User)
        .filter(User.reset_token.isnot(None))
        .all()
    )

    grant_message = request.query_params.get("msg")

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "user": user,
            "stats": {
                "total_users": total_users,
                "users_paid": users_paid,
                "users_free": users_free,
                "new_this_week": new_this_week,
                "new_this_month": new_this_month,
                "plan_mensal": plan_mensal,
                "plan_anual": plan_anual,
                "plan_vitalicio": plan_vitalicio,
                "total_diagnosticos": total_diagnosticos,
                "avg_score": avg_score,
                "total_challenges": total_challenges,
                "total_days_marked": total_days_marked,
                "total_learning_completions": total_learning_completions,
                "total_tip_successes": total_tip_successes,
                "pending_suggestions": pending_suggestions,
            },
            "top_tips_data": top_tips_data,
            "recent_users": recent_users,
            "grant_message": grant_message,
            "pending_resets": pending_resets,
        },
    )


@router.get("/admin/backup-db")
def backup_db(user: User = Depends(require_admin)):
    db_path = os.environ.get("DATABASE_URL", "").replace("sqlite:////", "/").replace("sqlite:///", "")
    if not db_path or not os.path.exists(db_path):
        db_path = "./data/financas.db"
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return FileResponse(
        path=db_path,
        media_type="application/octet-stream",
        filename=f"financas_backup_{timestamp}.db",
    )


PLAN_DURATIONS = {"mensal": 30, "anual": 365, "vitalicio": None}


@router.post("/admin/grant-access")
def grant_access(
    email: str = Form(...),
    plan: str = Form(...),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    target = db.query(User).filter(User.email == email.strip().lower()).first()
    if not target:
        return RedirectResponse("/admin?msg=email_nao_encontrado", status_code=303)

    days = PLAN_DURATIONS.get(plan)
    target.plan = plan
    target.plan_active = True
    target.plan_expires_at = (
        datetime.datetime.utcnow() + datetime.timedelta(days=days) if days else None
    )
    db.commit()
    return RedirectResponse("/admin?msg=acesso_liberado", status_code=303)
