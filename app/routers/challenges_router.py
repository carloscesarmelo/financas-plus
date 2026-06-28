import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_active_plan
from app.database import get_db
from app.finance_logic import (
    accrued_interest_on_deposits,
    challenge_pace_status,
    day_amounts,
    progression_sum,
    strategy_scenarios,
)
from app.gamification import award_xp
from app.models import PLAN_DAYS, PLAN_LABELS, Challenge, ChallengeDay, User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/challenges")
def list_challenges(request: Request, user: User = Depends(require_active_plan), db: Session = Depends(get_db)):
    challenges = (
        db.query(Challenge).filter(Challenge.user_id == user.id).order_by(Challenge.created_at.desc()).all()
    )
    pace_by_challenge = {c.id: challenge_pace_status(c) for c in challenges}
    return templates.TemplateResponse(
        "challenges_list.html",
        {
            "request": request,
            "user": user,
            "challenges": challenges,
            "plan_labels": PLAN_LABELS,
            "plan_days": PLAN_DAYS,
            "pace_by_challenge": pace_by_challenge,
        },
    )


@router.post("/challenges")
def create_challenge(
    request: Request,
    plan_key: str = Form(...),
    custom_days: int = Form(0),
    user: User = Depends(require_active_plan),
    db: Session = Depends(get_db),
):
    if plan_key == "custom":
        total_days = custom_days
    else:
        total_days = PLAN_DAYS.get(plan_key)

    if not total_days or total_days <= 0:
        raise HTTPException(status_code=400, detail="Número de dias inválido para o desafio.")

    challenge = Challenge(
        user_id=user.id,
        plan_key=plan_key,
        total_days=total_days,
        objetivo_maior=user.objetivo_maior,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    amounts = day_amounts(total_days)
    for day_number, amount in enumerate(amounts, start=1):
        db.add(ChallengeDay(challenge_id=challenge.id, day_number=day_number, amount=amount))
    db.commit()

    return RedirectResponse(f"/challenges/{challenge.id}", status_code=303)


@router.get("/challenges/{challenge_id}")
def view_challenge(
    request: Request,
    challenge_id: int,
    user: User = Depends(require_active_plan),
    db: Session = Depends(get_db),
):
    challenge = (
        db.query(Challenge).filter(Challenge.id == challenge_id, Challenge.user_id == user.id).first()
    )
    if not challenge:
        raise HTTPException(status_code=404, detail="Desafio não encontrado")

    total_saved = sum(d.amount for d in challenge.days if d.marked)
    total_goal = progression_sum(challenge.total_days)
    remaining = total_goal - total_saved
    accrued = accrued_interest_on_deposits(challenge.days)
    scenarios = strategy_scenarios(challenge.total_days)
    pace = challenge_pace_status(challenge)

    return templates.TemplateResponse(
        "challenge_board.html",
        {
            "request": request,
            "user": user,
            "challenge": challenge,
            "plan_label": PLAN_LABELS.get(challenge.plan_key, "Desafio"),
            "total_saved": total_saved,
            "total_goal": total_goal,
            "remaining": remaining,
            "accrued": accrued,
            "scenarios": scenarios,
            "pace": pace,
        },
    )


@router.post("/challenges/{challenge_id}/days/{day_number}/toggle")
def toggle_day(
    challenge_id: int,
    day_number: int,
    user: User = Depends(require_active_plan),
    db: Session = Depends(get_db),
):
    challenge = (
        db.query(Challenge).filter(Challenge.id == challenge_id, Challenge.user_id == user.id).first()
    )
    if not challenge:
        raise HTTPException(status_code=404, detail="Desafio não encontrado")

    day = (
        db.query(ChallengeDay)
        .filter(ChallengeDay.challenge_id == challenge.id, ChallengeDay.day_number == day_number)
        .first()
    )
    if not day:
        raise HTTPException(status_code=404, detail="Dia não encontrado")

    day.marked = not day.marked
    day.marked_at = datetime.datetime.utcnow() if day.marked else None
    db.commit()

    if day.marked:
        award_xp(db, user, "challenge_day_marked", f"Dia {day_number} do desafio {challenge.id}")

    total_saved = sum(d.amount for d in challenge.days if d.marked)
    total_goal = progression_sum(challenge.total_days)
    accrued = accrued_interest_on_deposits(challenge.days)

    return JSONResponse(
        {
            "marked": day.marked,
            "total_saved": total_saved,
            "remaining": total_goal - total_saved,
            "principal": accrued["principal"],
            "interest": accrued["interest"],
            "balance": accrued["balance"],
            "xp": user.xp,
            "level": user.level,
        }
    )
