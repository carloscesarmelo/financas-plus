import datetime

# Parâmetros financeiros globais (taxa fixa do produto, não atrelada a CDI).
MONTHLY_RATE = 0.01          # 1% a.m.
DAILY_RATE = 0.0003333       # 0,03333% a.d. — fator diário
# Regra de aplicação: juros incidem sempre em D+1 (o rendimento começa a contar
# no dia seguinte ao depósito realizado).


def progression_sum(n: int) -> float:
    """Soma de Progressão Aritmética: Sn = n*(a1+an)/2, com a1=1 e an=n."""
    return n * (1 + n) / 2


def day_amounts(total_days: int) -> list[float]:
    return [float(d) for d in range(1, total_days + 1)]


def calculate_compound_interest(cash_flows: list[float], total_days: int, daily_rate: float = DAILY_RATE) -> float:
    """
    Valor futuro de um fluxo de caixa diário aplicando juros compostos em D+1.

    FV = Σ_{t=1}^{n} C_t * (1 + i)^(n - t)

    `cash_flows[t-1]` é o valor depositado no dia t. O expoente (n - t) embute
    a regra D+1: o depósito do dia t só rende a partir do dia seguinte, de modo
    que o depósito do último dia (t = n) não acumula juros (expoente 0).
    """
    fv = 0.0
    for t, amount in enumerate(cash_flows, start=1):
        days_earning = total_days - t
        fv += amount * ((1 + daily_rate) ** days_earning)
    return fv


def accrued_interest_on_deposits(challenge_days, now: datetime.datetime | None = None,
                                 daily_rate: float = DAILY_RATE) -> dict:
    """
    Calcula, para os depósitos REALMENTE marcados, o principal depositado e o
    saldo já rendido até hoje, aplicando 0,03333% a.d. sobre o saldo, em D+1
    (cada depósito começa a render no dia seguinte ao da sua marcação).

    Retorna principal, saldo total (principal + juros) e juros acumulados.
    """
    now = now or datetime.datetime.utcnow()
    today = now.date()

    principal = 0.0
    balance = 0.0
    for day in challenge_days:
        if not day.marked or not day.marked_at:
            continue
        principal += day.amount
        # D+1: conta os dias inteiros decorridos a partir do dia seguinte ao depósito.
        days_elapsed = (today - day.marked_at.date()).days
        days_earning = max(0, days_elapsed)
        balance += day.amount * ((1 + daily_rate) ** days_earning)

    return {
        "principal": principal,
        "balance": balance,
        "interest": balance - principal,
    }


def strategy_scenarios(total_days: int, daily_rate: float = DAILY_RATE) -> dict:
    """
    Três cenários educativos com o MESMO principal total (PA de 1..n), mudando
    apenas a ordem dos depósitos, para evidenciar o impacto da antecipação de
    capital sobre o rendimento final.
    """
    n = total_days

    crescente = [float(t) for t in range(1, n + 1)]            # 1, 2, ..., n
    decrescente = [float(t) for t in range(n, 0, -1)]          # n, n-1, ..., 1
    media = (1 + n) / 2
    intermediario = [media for _ in range(n)]                  # constante na média

    principal = progression_sum(n)

    def build(cash_flows):
        fv = calculate_compound_interest(cash_flows, n, daily_rate)
        return {"future_value": fv, "interest": fv - principal}

    return {
        "total_days": n,
        "principal": principal,
        "crescente": build(crescente),
        "decrescente": build(decrescente),
        "intermediario": build(intermediario),
    }


def challenge_pace_status(challenge, now: datetime.datetime | None = None) -> dict:
    """
    Avalia o ritmo do desafio sem punir o usuário: apenas sinaliza se ele está
    em dia ou acumulando dias para recuperar, e se ainda não depositou hoje.
    Nenhum dia é bloqueado ou perdido — tudo pode ser marcado depois.
    """
    now = now or datetime.datetime.utcnow()
    today = now.date()

    days_since_start = (today - challenge.created_at.date()).days + 1
    expected_marked = max(0, min(days_since_start, challenge.total_days))

    marked_count = sum(1 for d in challenge.days if d.marked)
    days_behind = max(0, expected_marked - marked_count)

    marked_today = any(d.marked_at and d.marked_at.date() == today for d in challenge.days if d.marked)

    is_completed = marked_count >= challenge.total_days

    return {
        "days_behind": days_behind,
        "marked_today": marked_today,
        "is_completed": is_completed,
    }
