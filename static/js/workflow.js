/**
 * SkillSwap — Workflow JavaScript
 * Interactive visual journey across the 7 stages of peer learning
 */

document.addEventListener('DOMContentLoaded', () => {
  const stageCards = document.querySelectorAll('.workflow-stage-card');
  const stageNavBtns = document.querySelectorAll('.workflow-nav-pill');

  if (stageNavBtns.length > 0 && stageCards.length > 0) {
    stageNavBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const stageNum = btn.getAttribute('data-stage');
        stageNavBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const targetCard = document.getElementById(`stage-${stageNum}`);
        if (targetCard) {
          targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
          targetCard.classList.add('stage-highlight');
          setTimeout(() => {
            targetCard.classList.remove('stage-highlight');
          }, 1500);
        }
      });
    });
  }
});
