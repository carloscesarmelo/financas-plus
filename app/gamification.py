from sqlalchemy.orm import Session

from app.models import (
    ChallengeDay,
    GamificationEvent,
    Tip,
    User,
    UserLearningProgress,
    UserTipProgress,
)

XP_PER_LEVEL = 100

XP_REWARDS = {
    "challenge_day_marked": 10,
    "learning_completed": 20,
    "tip_completed": 15,
    "tip_suggestion_approved": 50,
    "tip_success_marked": 5,
}


def award_xp(db: Session, user: User, event_type: str, description: str = "") -> int:
    xp_amount = XP_REWARDS.get(event_type, 0)
    if xp_amount <= 0:
        return user.xp

    user.xp += xp_amount
    user.level = (user.xp // XP_PER_LEVEL) + 1

    db.add(
        GamificationEvent(
            user_id=user.id,
            event_type=event_type,
            xp_awarded=xp_amount,
            description=description,
        )
    )
    db.commit()
    return user.xp


def current_streak(db: Session, user: User) -> int:
    """Maior sequência de dias consecutivos marcados em qualquer desafio do usuário."""
    marked_days = (
        db.query(ChallengeDay)
        .join(ChallengeDay.challenge)
        .filter(ChallengeDay.marked.is_(True))
        .filter(ChallengeDay.challenge.has(user_id=user.id))
        .all()
    )
    by_challenge: dict[int, list[int]] = {}
    for cd in marked_days:
        by_challenge.setdefault(cd.challenge_id, []).append(cd.day_number)

    best = 0
    for days in by_challenge.values():
        days.sort()
        streak = 1
        local_best = 1 if days else 0
        for prev, cur in zip(days, days[1:]):
            if cur == prev + 1:
                streak += 1
            else:
                streak = 1
            local_best = max(local_best, streak)
        best = max(best, local_best)
    return best


def compute_badges(db: Session, user: User) -> list[dict]:
    total_marked = (
        db.query(ChallengeDay)
        .join(ChallengeDay.challenge)
        .filter(ChallengeDay.marked.is_(True))
        .filter(ChallengeDay.challenge.has(user_id=user.id))
        .count()
    )
    learning_completed = db.query(UserLearningProgress).filter(UserLearningProgress.user_id == user.id).count()
    tips_completed = db.query(UserTipProgress).filter(UserTipProgress.user_id == user.id).count()
    total_tips = db.query(Tip).count()
    streak = current_streak(db, user)

    badges = [
        {
            "name": "Primeiro Passo",
            "description": "Marcou o primeiro dia no tabuleiro de poupança",
            "unlocked": total_marked >= 1,
        },
        {
            "name": "Sequência de 7 dias",
            "description": "Marcou 7 dias consecutivos no tabuleiro",
            "unlocked": streak >= 7,
        },
        {
            "name": "Centena",
            "description": "Marcou 100 dias no total entre os desafios",
            "unlocked": total_marked >= 100,
        },
        {
            "name": "Estudante Dedicado",
            "description": "Concluiu 5 conteúdos na aba Aprender",
            "unlocked": learning_completed >= 5,
        },
        {
            "name": "Empreendedor",
            "description": "Concluiu todas as dicas de renda extra disponíveis",
            "unlocked": total_tips > 0 and tips_completed >= total_tips,
        },
    ]
    return badges
