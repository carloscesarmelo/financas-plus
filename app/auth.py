from fastapi import Depends, HTTPException, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.payments import user_has_active_plan

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class NotAuthenticated(Exception):
    """Raised when a route requires a logged-in user and none is present."""


class PlanRequired(Exception):
    """Raised when a route requires an active paid plan and the user doesn't have one."""


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user(request, db)
    if not user:
        raise NotAuthenticated()
    return user


def require_admin(request: Request, db: Session = Depends(get_db)) -> User:
    user = require_user(request, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador")
    return user


def require_active_plan(request: Request, db: Session = Depends(get_db)) -> User:
    user = require_user(request, db)
    if not user_has_active_plan(db, user):
        raise PlanRequired()
    return user
