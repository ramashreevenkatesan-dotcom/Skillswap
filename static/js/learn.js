/**
 * SkillSwap — Learn JavaScript
 * Handles filters, search, and the "Request to Learn" workflow modal
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Auto-submit filter changes
  const filterSelects = document.querySelectorAll('.auto-filter-select');
  filterSelects.forEach(sel => {
    sel.addEventListener('change', () => {
      const form = sel.closest('form');
      if (form) form.submit();
    });
  });

  // 2. Open "Request to Learn" Modal from Skill Cards
  document.querySelectorAll('.open-learn-request-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const skillId = btn.getAttribute('data-skill-id');
      const skillTitle = btn.getAttribute('data-skill-title');
      const teacherName = btn.getAttribute('data-teacher-name');

      // Populate modal form elements
      const idInput = document.getElementById('modal-request-skill-id');
      const titleSpan = document.getElementById('modal-request-skill-title');
      const teacherSpan = document.getElementById('modal-request-teacher-name');

      if (idInput) idInput.value = skillId;
      if (titleSpan) titleSpan.textContent = skillTitle;
      if (teacherSpan) teacherSpan.textContent = teacherName;

      openModal('request-to-learn-modal');
    });
  });
});
