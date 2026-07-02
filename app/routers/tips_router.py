import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_active_plan, require_admin, require_user
from app.database import get_db
from app.gamification import award_xp
from app.models import Tip, TipSuggestion, User, UserTipProgress, UserTipSuccess

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

CATEGORIES = ["Renda imediata", "Habilidades atuais", "Ativos e renda recorrente", "Inteligência Artificial", "Compra e venda", "Outro"]


def _tip_context(tips, completed_ids, success_ids, db):
    result = []
    for tip in tips:
        success_count = len(tip.successes)
        result.append({
            "tip": tip,
            "completed": tip.id in completed_ids,
            "user_succeeded": tip.id in success_ids,
            "success_count": success_count,
        })
    result.sort(key=lambda x: x["success_count"], reverse=True)
    return result


@router.get("/tips")
def tips_home(request: Request, user: User = Depends(require_active_plan), db: Session = Depends(get_db)):
    tips = db.query(Tip).order_by(Tip.created_at.desc()).all()
    completed_ids = {p.tip_id for p in db.query(UserTipProgress).filter(UserTipProgress.user_id == user.id).all()}
    success_ids = {s.tip_id for s in db.query(UserTipSuccess).filter(UserTipSuccess.user_id == user.id).all()}
    pending_count = db.query(TipSuggestion).filter(TipSuggestion.status == "pending").count() if user.is_admin else 0

    return templates.TemplateResponse(
        "tips.html",
        {
            "request": request,
            "user": user,
            "tips_data": _tip_context(tips, completed_ids, success_ids, db),
            "pending_count": pending_count,
        },
    )


@router.post("/tips/{tip_id}/complete")
def complete_tip(tip_id: int, user: User = Depends(require_active_plan), db: Session = Depends(get_db)):
    already = db.query(UserTipProgress).filter(
        UserTipProgress.user_id == user.id, UserTipProgress.tip_id == tip_id
    ).first()
    if not already:
        db.add(UserTipProgress(user_id=user.id, tip_id=tip_id))
        db.commit()
        award_xp(db, user, "tip_completed", f"Dica {tip_id} concluída")
    return RedirectResponse("/tips", status_code=303)


@router.post("/tips/{tip_id}/success")
def mark_tip_success(tip_id: int, user: User = Depends(require_active_plan), db: Session = Depends(get_db)):
    already = db.query(UserTipSuccess).filter(
        UserTipSuccess.user_id == user.id, UserTipSuccess.tip_id == tip_id
    ).first()
    if not already:
        db.add(UserTipSuccess(user_id=user.id, tip_id=tip_id))
        db.commit()
        award_xp(db, user, "tip_success_marked", f"Sucesso com dica {tip_id}")
    return RedirectResponse("/tips", status_code=303)


@router.get("/tips/suggest")
def suggest_tip_form(request: Request, user: User = Depends(require_active_plan)):
    return templates.TemplateResponse("suggest_tip.html", {"request": request, "user": user, "categories": CATEGORIES})


@router.post("/tips/suggest")
def suggest_tip_submit(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    author_display_name: str = Form(...),
    consent_public: str = Form("off"),
    user: User = Depends(require_active_plan),
    db: Session = Depends(get_db),
):
    db.add(TipSuggestion(
        user_id=user.id,
        title=title.strip(),
        description=description.strip(),
        category=category.strip(),
        author_display_name=author_display_name.strip(),
        consent_public=(consent_public == "on"),
        status="pending",
    ))
    db.commit()
    return templates.TemplateResponse(
        "suggest_tip.html",
        {"request": request, "user": user, "categories": CATEGORIES, "success": True},
    )


@router.get("/admin/tips")
def admin_tips_form(request: Request, user: User = Depends(require_admin)):
    return templates.TemplateResponse(
        "admin_tips.html", {"request": request, "user": user, "categories": CATEGORIES}
    )


@router.post("/admin/tips")
def admin_tips_create(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db.add(Tip(title=title.strip(), description=description.strip(), category=category.strip(), source="admin"))
    db.commit()
    return RedirectResponse("/tips", status_code=303)


@router.get("/admin/tips/suggestions")
def admin_suggestions(request: Request, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    pending = db.query(TipSuggestion).filter(TipSuggestion.status == "pending").order_by(TipSuggestion.created_at).all()
    return templates.TemplateResponse(
        "admin_tip_suggestions.html", {"request": request, "user": user, "suggestions": pending}
    )


@router.post("/admin/tips/suggestions/{suggestion_id}/approve")
def approve_suggestion(suggestion_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    suggestion = db.query(TipSuggestion).filter(TipSuggestion.id == suggestion_id).first()
    if suggestion and suggestion.status == "pending":
        author = suggestion.author_display_name if suggestion.consent_public else None
        db.add(Tip(
            title=suggestion.title,
            description=suggestion.description,
            category=suggestion.category,
            source="community",
            author_name=author,
        ))
        suggestion.status = "approved"
        db.commit()
        submitter = db.query(User).filter(User.id == suggestion.user_id).first()
        if submitter:
            award_xp(db, submitter, "tip_suggestion_approved", f"Sugestão '{suggestion.title}' aprovada")
    return RedirectResponse("/admin/tips/suggestions", status_code=303)


@router.post("/admin/tips/suggestions/{suggestion_id}/reject")
def reject_suggestion(suggestion_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    suggestion = db.query(TipSuggestion).filter(TipSuggestion.id == suggestion_id).first()
    if suggestion and suggestion.status == "pending":
        suggestion.status = "rejected"
        db.commit()
    return RedirectResponse("/admin/tips/suggestions", status_code=303)
