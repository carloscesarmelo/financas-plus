from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_active_plan, require_admin
from app.database import get_db
from app.gamification import award_xp
from app.models import LearningContent, User, UserLearningProgress

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

LEVELS = ["basico", "intermediario", "avancado"]
LEVEL_LABELS = {"basico": "Básico", "intermediario": "Intermediário", "avancado": "Avançado"}


@router.get("/learn")
def learn_home(request: Request, user: User = Depends(require_active_plan), db: Session = Depends(get_db)):
    contents = db.query(LearningContent).order_by(LearningContent.level, LearningContent.created_at).all()
    completed_ids = {
        p.content_id
        for p in db.query(UserLearningProgress).filter(UserLearningProgress.user_id == user.id).all()
    }

    by_level = {level: [] for level in LEVELS}
    for content in contents:
        by_level.setdefault(content.level, []).append(content)

    return templates.TemplateResponse(
        "learning.html",
        {
            "request": request,
            "user": user,
            "by_level": by_level,
            "level_labels": LEVEL_LABELS,
            "completed_ids": completed_ids,
        },
    )


@router.post("/learn/{content_id}/complete")
def complete_content(
    content_id: int,
    user: User = Depends(require_active_plan),
    db: Session = Depends(get_db),
):
    already = (
        db.query(UserLearningProgress)
        .filter(UserLearningProgress.user_id == user.id, UserLearningProgress.content_id == content_id)
        .first()
    )
    if not already:
        db.add(UserLearningProgress(user_id=user.id, content_id=content_id))
        db.commit()
        award_xp(db, user, "learning_completed", f"Conteúdo {content_id} concluído")

    return RedirectResponse("/learn", status_code=303)


@router.get("/admin/learn")
def admin_learn_form(request: Request, user: User = Depends(require_admin)):
    return templates.TemplateResponse(
        "admin_learning.html", {"request": request, "user": user, "level_labels": LEVEL_LABELS}
    )


@router.post("/admin/learn")
def admin_learn_create(
    title: str = Form(...),
    url: str = Form(...),
    content_type: str = Form(...),
    level: str = Form(...),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db.add(LearningContent(title=title.strip(), url=url.strip(), content_type=content_type, level=level))
    db.commit()
    return RedirectResponse("/learn", status_code=303)
