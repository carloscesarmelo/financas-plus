import datetime

from fastapi import APIRouter, Depends, Request
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
        },
    )
