from sqlalchemy.orm import Session

from app.models import (
    ChallengeDay,
    GamificationEvent,
    Tip,
    User,
    UserLearningProgress,
    UserTipProgress,
)

XP_PER_LEVEL = 100  # mantido para compatibilidade de campo; cálculo real usa LEVELS abaixo

XP_REWARDS = {
    "challenge_day_marked": 10,
    "learning_completed": 20,
    "tip_completed": 15,
    "tip_suggestion_approved": 50,
    "tip_success_marked": 5,
}

LEVELS = [
    {"level": 1,  "name": "Desperto",              "emoji": "🌱", "xp_min": 0,      "description": "Você deu o primeiro passo rumo à sua liberdade financeira."},
    {"level": 2,  "name": "Curioso",               "emoji": "🔍", "xp_min": 100,    "description": "Está explorando o universo das finanças com interesse real."},
    {"level": 3,  "name": "Consciente",             "emoji": "💡", "xp_min": 250,    "description": "Sabe onde está e para onde quer chegar."},
    {"level": 4,  "name": "Organizado",             "emoji": "📋", "xp_min": 450,    "description": "Tem controle sobre suas entradas e saídas."},
    {"level": 5,  "name": "Disciplinado",           "emoji": "🎯", "xp_min": 700,    "description": "Segue seu plano com consistência dia a dia."},
    {"level": 6,  "name": "Poupador",               "emoji": "🏦", "xp_min": 1000,   "description": "Constrói reservas com regularidade e propósito."},
    {"level": 7,  "name": "Planejador",             "emoji": "📊", "xp_min": 1400,   "description": "Pensa o futuro com estratégia e visão."},
    {"level": 8,  "name": "Controlador",            "emoji": "⚙️", "xp_min": 1900,   "description": "Domina completamente seu fluxo de caixa."},
    {"level": 9,  "name": "Estrategista",           "emoji": "🧠", "xp_min": 2500,   "description": "Toma decisões financeiras calculadas e conscientes."},
    {"level": 10, "name": "Investidor",             "emoji": "📈", "xp_min": 3200,   "description": "Seu dinheiro já começa a trabalhar por você."},
    {"level": 11, "name": "Multiplicador",          "emoji": "🔥", "xp_min": 4100,   "description": "Escala seus resultados e multiplica oportunidades."},
    {"level": 12, "name": "Construtor",             "emoji": "🏗️", "xp_min": 5200,   "description": "Edifica patrimônio sólido e duradouro."},
    {"level": 13, "name": "Blindado",               "emoji": "🛡️", "xp_min": 6500,   "description": "Protege e expande o que conquistou com inteligência."},
    {"level": 14, "name": "Empreendedor",           "emoji": "💼", "xp_min": 8000,   "description": "Cria e gerencia múltiplas fontes de renda."},
    {"level": 15, "name": "Livre",                  "emoji": "🗝️", "xp_min": 9800,   "description": "Suas escolhas de vida não são mais limitadas pelo dinheiro."},
    {"level": 16, "name": "Independente",           "emoji": "🌟", "xp_min": 12000,  "description": "Alcançou a independência financeira. Você é a prova de que é possível."},
]


def get_level_info(xp: int) -> dict:
    """Retorna os dados completos do nível atual e do próximo para um dado XP."""
    current = LEVELS[0]
    for lvl in LEVELS:
        if xp >= lvl["xp_min"]:
            current = lvl
        else:
            break

    current_idx = current["level"] - 1
    next_lvl = LEVELS[current_idx + 1] if current_idx + 1 < len(LEVELS) else None

    if next_lvl:
        xp_in_level = xp - current["xp_min"]
        xp_needed = next_lvl["xp_min"] - current["xp_min"]
        pct = int(xp_in_level / xp_needed * 100)
        xp_to_next = next_lvl["xp_min"] - xp
    else:
        xp_in_level = xp - current["xp_min"]
        xp_needed = xp_in_level if xp_in_level > 0 else 1
        pct = 100
        xp_to_next = 0

    return {
        "level": current["level"],
        "name": current["name"],
        "emoji": current["emoji"],
        "description": current["description"],
        "next": next_lvl,
        "pct": pct,
        "xp_to_next": xp_to_next,
    }


def award_xp(db: Session, user: User, event_type: str, description: str = "") -> int:
    xp_amount = XP_REWARDS.get(event_type, 0)
    if xp_amount <= 0:
        return user.xp

    user.xp += xp_amount
    info = get_level_info(user.xp)
    user.level = info["level"]

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
