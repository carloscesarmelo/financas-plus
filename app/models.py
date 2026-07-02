import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


def now():
    return datetime.datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)

    onboarding_completed = Column(Boolean, default=False)
    objetivo_maior = Column(String, nullable=True)

    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)

    plan = Column(String, default="free")  # free, mensal, anual, vitalicio
    plan_active = Column(Boolean, default=False)
    plan_expires_at = Column(DateTime, nullable=True)  # null = sem expiração (vitalicio)
    reset_token = Column(String, nullable=True)
    reset_token_at = Column(DateTime, nullable=True)

    onboarding = relationship("OnboardingProfile", uselist=False, back_populates="user")
    challenges = relationship("Challenge", back_populates="user")


class OnboardingProfile(Base):
    __tablename__ = "onboarding_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    renda_atual = Column(Float, nullable=True)
    possui_dividas = Column(Boolean, default=False)
    valor_dividas = Column(Float, nullable=True)
    comportamento = Column(String, nullable=True)
    habilidades = Column(Text, nullable=True)
    perfil_sugerido = Column(String, nullable=True)

    created_at = Column(DateTime, default=now)

    user = relationship("User", back_populates="onboarding")


PLAN_DAYS = {
    "financas30": 30,
    "financas50": 50,
    "financas75": 75,
    "financas100": 100,
    "financas365": 365,
    "financas500": 500,
}

PLAN_LABELS = {
    "financas30": "Finanças30+",
    "financas50": "Finanças50+",
    "financas75": "Finanças75+",
    "financas100": "Finanças100+",
    "financas365": "Finanças365+",
    "financas500": "Finanças500+",
    "custom": "Dias Personalizados",
}


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_key = Column(String, nullable=False)
    total_days = Column(Integer, nullable=False)
    objetivo_maior = Column(String, nullable=True)
    created_at = Column(DateTime, default=now)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="challenges")
    days = relationship(
        "ChallengeDay", back_populates="challenge", order_by="ChallengeDay.day_number", cascade="all, delete-orphan"
    )


class ChallengeDay(Base):
    __tablename__ = "challenge_days"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    marked = Column(Boolean, default=False)
    marked_at = Column(DateTime, nullable=True)

    challenge = relationship("Challenge", back_populates="days")

    __table_args__ = (UniqueConstraint("challenge_id", "day_number", name="uq_challenge_day"),)


class LearningContent(Base):
    __tablename__ = "learning_contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # video, artigo, podcast
    level = Column(String, nullable=False)  # basico, intermediario, avancado
    created_at = Column(DateTime, default=now)

    completions = relationship("UserLearningProgress", back_populates="content", cascade="all, delete-orphan")


class UserLearningProgress(Base):
    __tablename__ = "user_learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("learning_contents.id"), nullable=False)
    completed_at = Column(DateTime, default=now)

    content = relationship("LearningContent", back_populates="completions")

    __table_args__ = (UniqueConstraint("user_id", "content_id", name="uq_user_content"),)


class Tip(Base):
    __tablename__ = "tips"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    source = Column(String, default="admin")  # admin | community
    author_name = Column(String, nullable=True)  # null = equipe FINANÇAS+
    created_at = Column(DateTime, default=now)

    completions = relationship("UserTipProgress", back_populates="tip", cascade="all, delete-orphan")
    successes = relationship("UserTipSuccess", back_populates="tip", cascade="all, delete-orphan")


class UserTipProgress(Base):
    __tablename__ = "user_tip_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tip_id = Column(Integer, ForeignKey("tips.id"), nullable=False)
    completed_at = Column(DateTime, default=now)

    tip = relationship("Tip", back_populates="completions")

    __table_args__ = (UniqueConstraint("user_id", "tip_id", name="uq_user_tip"),)


class Desejo(Base):
    __tablename__ = "desejos"

    id = Column(Integer, primary_key=True, index=True)
    emoji = Column(String, nullable=False)
    label = Column(String, nullable=False)
    headline = Column(String, nullable=False)
    subheadline = Column(Text, nullable=False)
    plan_key = Column(String, default="financas365")
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)


class Diagnostico(Base):
    __tablename__ = "diagnosticos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_diagnostico = Column(DateTime, default=now)
    pontuacao_total = Column(Integer, nullable=False)
    percentual_geral = Column(Float, nullable=False)
    pontuacao_areas = Column(JSON, nullable=False)

    user = relationship("User")


class PaymentEvent(Base):
    """Auditoria de todo webhook de pagamento recebido (payload bruto incluído)."""

    __tablename__ = "payment_events"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False, default="kiwify")
    event_type = Column(String, nullable=True)
    email = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    plan_applied = Column(String, nullable=True)
    processed = Column(Boolean, default=False)
    raw_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=now)

    user = relationship("User")


class UserTipSuccess(Base):
    __tablename__ = "user_tip_success"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tip_id = Column(Integer, ForeignKey("tips.id"), nullable=False)
    marked_at = Column(DateTime, default=now)

    tip = relationship("Tip", back_populates="successes")

    __table_args__ = (UniqueConstraint("user_id", "tip_id", name="uq_user_tip_success"),)


class TipSuggestion(Base):
    __tablename__ = "tip_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    author_display_name = Column(String, nullable=False)
    consent_public = Column(Boolean, default=False)
    status = Column(String, default="pending")  # pending | approved | rejected
    created_at = Column(DateTime, default=now)

    user = relationship("User")


class GamificationEvent(Base):
    __tablename__ = "gamification_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)
    xp_awarded = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=now)
