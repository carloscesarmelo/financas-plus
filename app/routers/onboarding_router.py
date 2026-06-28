from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_user
from app.database import get_db
from app.models import OnboardingProfile, User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def suggest_profile(renda_atual: float, possui_dividas: bool, comportamento: str) -> str:
    if possui_dividas:
        return "Em Recuperação — foco em organizar e quitar dívidas antes de acelerar investimentos"
    if comportamento == "impulsivo":
        return "Construindo Disciplina — foco em criar o hábito de poupar de forma consistente"
    if renda_atual and renda_atual >= 5000:
        return "Acelerador — foco em otimizar investimentos e diversificar renda"
    return "Poupador Iniciante — foco em criar reserva e consistência financeira"


@router.get("/onboarding")
def onboarding_form(request: Request, user: User = Depends(require_user)):
    return templates.TemplateResponse("onboarding.html", {"request": request, "user": user})


@router.post("/onboarding")
def onboarding_submit(
    request: Request,
    renda_atual: float = Form(...),
    possui_dividas: str = Form(...),
    valor_dividas: float = Form(0),
    comportamento: str = Form(...),
    habilidades: str = Form(""),
    objetivo_maior: str = Form(...),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    tem_dividas = possui_dividas == "sim"
    perfil = suggest_profile(renda_atual, tem_dividas, comportamento)

    profile = db.query(OnboardingProfile).filter(OnboardingProfile.user_id == user.id).first()
    if not profile:
        profile = OnboardingProfile(user_id=user.id)
        db.add(profile)

    profile.renda_atual = renda_atual
    profile.possui_dividas = tem_dividas
    profile.valor_dividas = valor_dividas if tem_dividas else 0
    profile.comportamento = comportamento
    profile.habilidades = habilidades
    profile.perfil_sugerido = perfil

    user.objetivo_maior = objetivo_maior.strip()
    user.onboarding_completed = True

    db.commit()

    return RedirectResponse("/dashboard", status_code=303)
