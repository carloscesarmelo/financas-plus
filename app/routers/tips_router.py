from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_active_plan, require_admin
from app.database import get_db
from app.gamification import award_xp
from app.models import Tip, User, UserTipProgress

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/tips")
def tips_home(request: Request, user: User = Depends(require_active_plan), db: Session = Depends(get_db)):
    tips = db.query(Tip).order_by(Tip.created_at).all()
    completed_ids = {
        p.tip_id for p in db.query(UserTipProgress).filter(UserTipProgress.user_id == user.id).all()
    }

    return templates.TemplateResponse(
        "tips.html",
        {"request": request, "user": user, "tips": tips, "completed_ids": completed_ids},
    )


@router.post("/tips/{tip_id}/complete")
def complete_tip(
    tip_id: int,
    user: User = Depends(require_active_plan),
    db: Session = Depends(get_db),
):
    already = (
        db.query(UserTipProgress)
        .filter(UserTipProgress.user_id == user.id, UserTipProgress.tip_id == tip_id)
        .first()
    )
    if not already:
        db.add(UserTipProgress(user_id=user.id, tip_id=tip_id))
        db.commit()
        award_xp(db, user, "tip_completed", f"Dica {tip_id} concluída")

    return RedirectResponse("/tips", status_code=303)


@router.get("/admin/tips")
def admin_tips_form(request: Request, user: User = Depends(require_admin)):
    return templates.TemplateResponse("admin_tips.html", {"request": request, "user": user})


@router.post("/admin/tips")
def admin_tips_create(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db.add(Tip(title=title.strip(), description=description.strip(), category=category.strip()))
    db.commit()
    return RedirectResponse("/tips", status_code=303)
