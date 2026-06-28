document.addEventListener("DOMContentLoaded", () => {
  const board = document.getElementById("board");
  if (!board) return;

  const challengeId = board.dataset.challengeId;
  const savedEl = document.getElementById("metric-saved");
  const remainingEl = document.getElementById("metric-remaining");
  const principalEl = document.getElementById("metric-principal");
  const interestEl = document.getElementById("metric-interest");
  const balanceEl = document.getElementById("metric-balance");
  const navPill = document.querySelector(".nav-pill");

  board.addEventListener("click", async (event) => {
    const cell = event.target.closest(".board-day");
    if (!cell) return;

    const dayNumber = cell.dataset.day;
    cell.style.pointerEvents = "none";

    try {
      const response = await fetch(`/challenges/${challengeId}/days/${dayNumber}/toggle`, {
        method: "POST",
      });
      if (!response.ok) throw new Error("Falha ao atualizar o dia");

      const data = await response.json();
      cell.classList.toggle("marked", data.marked);
      savedEl.textContent = `R$ ${data.total_saved.toFixed(2)}`;
      remainingEl.textContent = `R$ ${data.remaining.toFixed(2)}`;
      if (principalEl) principalEl.textContent = `R$ ${data.principal.toFixed(2)}`;
      if (interestEl) interestEl.textContent = `R$ ${data.interest.toFixed(2)}`;
      if (balanceEl) balanceEl.textContent = `R$ ${data.balance.toFixed(2)}`;
      if (navPill) {
        navPill.textContent = `Nível ${data.level} · ${data.xp} XP`;
      }
    } catch (err) {
      console.error(err);
    } finally {
      cell.style.pointerEvents = "auto";
    }
  });
});
