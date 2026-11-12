/**
 * SkillSwap — Skill Exchange JavaScript
 * Handles transparent matching displays and reciprocal exchange proposal modal
 */

document.addEventListener('DOMContentLoaded', () => {
  // Propose Exchange modal handler
  document.querySelectorAll('.open-propose-exchange-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const recipientId = btn.getAttribute('data-recipient-id');
      const recipientName = btn.getAttribute('data-recipient-name');
      const learnSkillId = btn.getAttribute('data-learn-skill-id');
      const teachSkillId = btn.getAttribute('data-teach-skill-id');

      // Populate Modal Fields
      const recIdInput = document.getElementById('exchange-recipient-id');
      const recNameSpan = document.getElementById('exchange-recipient-name');
      const learnSelect = document.getElementById('exchange-learn-skill-select');
      const teachSelect = document.getElementById('exchange-teach-skill-select');

      if (recIdInput) recIdInput.value = recipientId;
      if (recNameSpan) recNameSpan.textContent = recipientName;

      // Set pre-selected teach skill if available
      if (teachSelect && teachSkillId) {
        teachSelect.value = teachSkillId;
      }

      // If specific learn skill id is passed, set value or ensure option exists
      if (learnSelect && learnSkillId) {
        learnSelect.value = learnSkillId;
      }

      openModal('propose-exchange-modal');
    });
  });

  // Filter Match Cards by Type (All / Reciprocal / Partial)
  const filterBtns = document.querySelectorAll('.match-filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filterType = btn.getAttribute('data-filter');
      const cards = document.querySelectorAll('.match-card-wrapper');

      cards.forEach(card => {
        const type = card.getAttribute('data-match-type');
        if (filterType === 'all' || type === filterType) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
});
