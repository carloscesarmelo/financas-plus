document.addEventListener("DOMContentLoaded", () => {
  const selector = document.getElementById("goal-selector");
  if (!selector) return;

  const headlineEl = document.getElementById("hero-headline");
  const subheadlineEl = document.getElementById("hero-subheadline");
  const ctaEl = document.getElementById("hero-cta");
  const customWrapper = document.getElementById("custom-desejo-wrapper");
  const customInput = document.getElementById("custom-desejo-input");

  function updateCta(label) {
    const hiddenInput = document.getElementById("desejo-selecionado");
    if (hiddenInput) hiddenInput.value = label;
    if (ctaEl) ctaEl.href = "/register?desejo=" + encodeURIComponent(label);
  }

  selector.addEventListener("click", (event) => {
    const card = event.target.closest(".desejo-card");
    if (!card) return;

    selector.querySelectorAll(".desejo-card").forEach((el) => el.classList.remove("active"));
    card.classList.add("active");

    headlineEl.textContent = card.dataset.headline;
    subheadlineEl.textContent = card.dataset.subheadline;

    const isCustom = card.dataset.goal === "custom";
    customWrapper.classList.toggle("hidden", !isCustom);

    if (!isCustom) {
      const label = card.querySelector(".desejo-label").textContent.trim();
      updateCta(label);
    } else {
      customInput.focus();
      updateCta(customInput.value || "Meu objetivo");
    }

    card.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
  });

  if (customInput) {
    customInput.addEventListener("input", () => {
      updateCta(customInput.value || "Meu objetivo");
    });
  }
});
