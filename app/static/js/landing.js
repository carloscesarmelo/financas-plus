document.addEventListener("DOMContentLoaded", () => {
  const selector = document.getElementById("goal-selector");
  if (!selector) return;

  const headlineEl = document.getElementById("hero-headline");
  const subheadlineEl = document.getElementById("hero-subheadline");
  const ctaEl = document.getElementById("hero-cta");

  const GOALS = {
    apartamento: {
      headline: "Seu apartamento em 500 dias. Veja como.",
      subheadline:
        "Descubra seu Score de Saúde Financeira em 5 minutos e siga o Desafio Finanças500+ — um plano gamificado, dia a dia, até a entrada do seu imóvel.",
      cta: "Fazer meu diagnóstico gratuito",
    },
    carro: {
      headline: "Seu carro novo em 365 dias. Veja como.",
      subheadline:
        "Descubra seu Score de Saúde Financeira e siga o Desafio Finanças365+ até dar a entrada — ou pagar à vista — no seu carro novo.",
      cta: "Fazer meu diagnóstico gratuito",
    },
    viagem: {
      headline: "Sua viagem dos sonhos em 100 dias. Veja como.",
      subheadline:
        "Monte sua reserva de viagem com o Desafio Finanças100+, sem abrir mão do seu orçamento mensal.",
      cta: "Fazer meu diagnóstico gratuito",
    },
    reserva: {
      headline: "Sua reserva de emergência em 50 dias. Veja como.",
      subheadline:
        "Construa sua segurança financeira com o Desafio Finanças50+ antes de planejar o próximo passo.",
      cta: "Fazer meu diagnóstico gratuito",
    },
  };

  selector.addEventListener("click", (event) => {
    const chip = event.target.closest(".goal-chip");
    if (!chip) return;

    selector.querySelectorAll(".goal-chip").forEach((el) => el.classList.remove("active"));
    chip.classList.add("active");

    const goal = GOALS[chip.dataset.goal];
    if (!goal) return;

    headlineEl.textContent = goal.headline;
    subheadlineEl.textContent = goal.subheadline;
    ctaEl.textContent = goal.cta;
  });
});
