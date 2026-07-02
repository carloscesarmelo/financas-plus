import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import require_user
from app.database import get_db
from app.diagnostico_data import AREAS, AREAS_BY_KEY, DIAS_BLOQUEIO, PONTUACAO_MAXIMA
from app.models import Diagnostico, User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def latest_diagnostico(db: Session, user: User) -> Diagnostico | None:
    return (
        db.query(Diagnostico)
        .filter(Diagnostico.user_id == user.id)
        .order_by(Diagnostico.data_diagnostico.desc())
        .first()
    )


def lock_status(diagnostico: Diagnostico | None) -> dict:
    if not diagnostico:
        return {"locked": False, "days_remaining": 0}
    elapsed = (datetime.datetime.utcnow() - diagnostico.data_diagnostico).days
    remaining = DIAS_BLOQUEIO - elapsed
    if remaining > 0:
        return {"locked": True, "days_remaining": remaining}
    return {"locked": False, "days_remaining": 0}


@router.get("/diagnostico")
def diagnostico_form(request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)):
    last = latest_diagnostico(db, user)
    lock = lock_status(last)
    if lock["locked"]:
        return RedirectResponse("/diagnostico/resultado", status_code=303)

    return templates.TemplateResponse(
        "diagnostico_quiz.html",
        {"request": request, "user": user, "areas": AREAS, "is_retake": last is not None},
    )


@router.post("/diagnostico")
def diagnostico_submit(
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
    area_1: int = Form(...),
    area_2: int = Form(...),
    area_3: int = Form(...),
    area_4: int = Form(...),
    area_5: int = Form(...),
    area_6: int = Form(...),
    area_7: int = Form(...),
    area_8: int = Form(...),
):
    last = latest_diagnostico(db, user)
    if lock_status(last)["locked"]:
        return RedirectResponse("/diagnostico/resultado", status_code=303)

    respostas = [area_1, area_2, area_3, area_4, area_5, area_6, area_7, area_8]
    pontuacao_areas = {area["key"]: valor for area, valor in zip(AREAS, respostas)}
    pontuacao_total = sum(respostas)
    percentual_geral = (pontuacao_total / PONTUACAO_MAXIMA) * 100

    db.add(
        Diagnostico(
            user_id=user.id,
            pontuacao_total=pontuacao_total,
            percentual_geral=percentual_geral,
            pontuacao_areas=pontuacao_areas,
        )
    )
    db.commit()

    return RedirectResponse("/diagnostico/resultado", status_code=303)


@router.get("/diagnostico/resultado")
def diagnostico_resultado(request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)):
    diagnosticos = (
        db.query(Diagnostico)
        .filter(Diagnostico.user_id == user.id)
        .order_by(Diagnostico.data_diagnostico.desc())
        .all()
    )

    if not diagnosticos:
        return RedirectResponse("/diagnostico", status_code=303)

    atual = diagnosticos[0]
    anterior = diagnosticos[1] if len(diagnosticos) > 1 else None
    lock = lock_status(atual)

    areas_resultado = []
    for area in AREAS:
        valor_atual = atual.pontuacao_areas.get(area["key"], 0)
        opcao = next((opt for opt in area["options"] if opt["value"] == valor_atual), None)
        valor_anterior = anterior.pontuacao_areas.get(area["key"], 0) if anterior else None
        areas_resultado.append(
            {
                "title": area["title"],
                "valor": valor_atual,
                "valor_anterior": valor_anterior,
                "feedback": opcao["feedback"] if opcao else "",
            }
        )

    ctx = {
        "request": request,
        "user": user,
        "atual": atual,
        "anterior": anterior,
        "areas_resultado": areas_resultado,
        "lock": lock,
    }

    return templates.TemplateResponse("diagnostico_resultado.html", ctx)


@router.get("/diagnostico/resultado/imprimir")
def diagnostico_imprimir(request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)):
    diagnosticos = (
        db.query(Diagnostico)
        .filter(Diagnostico.user_id == user.id)
        .order_by(Diagnostico.data_diagnostico.desc())
        .all()
    )

    if not diagnosticos:
        return RedirectResponse("/diagnostico", status_code=303)

    atual = diagnosticos[0]
    areas_resultado = []
    for area in AREAS:
        valor_atual = atual.pontuacao_areas.get(area["key"], 0)
        opcao = next((opt for opt in area["options"] if opt["value"] == valor_atual), None)
        areas_resultado.append(
            {
                "title": area["title"],
                "valor": valor_atual,
                "feedback": opcao["feedback"] if opcao else "",
                "label": opcao["label"] if opcao else "",
            }
        )

    lock = lock_status(atual)
    proximo = (atual.data_diagnostico + datetime.timedelta(days=DIAS_BLOQUEIO)).strftime("%d/%m/%Y")

    return templates.TemplateResponse(
        "diagnostico_pdf.html",
        {
            "request": request,
            "user": user,
            "atual": atual,
            "areas_resultado": areas_resultado,
            "proximo": proximo,
            "pontuacao_maxima": PONTUACAO_MAXIMA,
        },
    )
