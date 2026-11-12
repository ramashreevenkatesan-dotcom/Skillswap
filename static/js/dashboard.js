/**
 * SkillSwap — Dashboard JavaScript
 * Interactive controls for search, quick actions, and filter toggles
 */

document.addEventListener('DOMContentLoaded', () => {
  // Quick Search Filter on Recommended Skills Cards
  const quickSearch = document.getElementById('dashboard-quick-search');
  if (quickSearch) {
    quickSearch.addEventListener('input', (e) => {
      const term = e.target.value.toLowerCase().trim();
      const cards = document.querySelectorAll('.dashboard-skill-card');

      cards.forEach(card => {
        const title = card.getAttribute('data-title') || '';
        const cat = card.getAttribute('data-category') || '';
        const teacher = card.getAttribute('data-teacher') || '';

        if (title.toLowerCase().includes(term) || cat.toLowerCase().includes(term) || teacher.toLowerCase().includes(term)) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }
});
