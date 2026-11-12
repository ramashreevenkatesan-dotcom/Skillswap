/**
 * SkillSwap — Teach JavaScript
 * Handles publishing skills, editing listings, and delete confirmations
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Edit Skill Modal Populate
  document.querySelectorAll('.open-edit-skill-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const skillId = btn.getAttribute('data-id');
      const title = btn.getAttribute('data-title');
      const category = btn.getAttribute('data-category');
      const description = btn.getAttribute('data-desc');
      const level = btn.getAttribute('data-level');
      const language = btn.getAttribute('data-lang');
      const mode = btn.getAttribute('data-mode');
      const duration = btn.getAttribute('data-duration');
      const days = btn.getAttribute('data-days');
      const times = btn.getAttribute('data-times');
      const resources = btn.getAttribute('data-resources');
      const outcomes = btn.getAttribute('data-outcomes');

      const editForm = document.getElementById('edit-skill-form');
      if (editForm) {
        editForm.action = `/teach/${skillId}/edit`;
        document.getElementById('edit-title').value = title || '';
        document.getElementById('edit-category').value = category || '';
        document.getElementById('edit-description').value = description || '';
        document.getElementById('edit-level').value = level || 'Intermediate';
        document.getElementById('edit-language').value = language || 'English';
        document.getElementById('edit-mode').value = mode || 'Online';
        document.getElementById('edit-duration').value = duration || '45-60 mins';
        document.getElementById('edit-days').value = days || '';
        document.getElementById('edit-times').value = times || '';
        document.getElementById('edit-resources').value = resources || '';
        document.getElementById('edit-outcomes').value = outcomes || '';
      }

      openModal('edit-skill-modal');
    });
  });

  // 2. Delete Confirmation
  document.querySelectorAll('.confirm-delete-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      const confirmed = confirm('Are you sure you want to permanently delete this teaching listing? This cannot be undone.');
      if (!confirmed) {
        e.preventDefault();
        return false;
      }
    });
  });
});
