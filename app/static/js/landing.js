document.addEventListener("DOMContentLoaded", () => {
  const selector = document.getElementById("goal-selector");
  if (!selector) return;

  const headlineEl = document.getElementById("hero-headline");
  const subheadlineEl = document.getElementById("hero-subheadline");

  selector.addEventListener("click", (event) => {
    const card = event.target.closest(".desejo-card");
    if (!card) return;

    selector.querySelectorAll(".desejo-card").forEach((el) => el.classList.remove("active"));
    card.classList.add("active");

    headlineEl.textContent = card.dataset.headline;
    subheadlineEl.textContent = card.dataset.subheadline;

    card.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
  });
});
