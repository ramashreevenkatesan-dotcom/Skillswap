/**
 * SkillSwap — Requests JavaScript
 * Handles status updates, scheduling sessions, and peer review submissions
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Status Change Confirmation
  document.querySelectorAll('.status-action-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      const action = form.getAttribute('data-action-label') || 'update this request';
      const confirmed = confirm(`Are you sure you want to ${action}?`);
      if (!confirmed) {
        e.preventDefault();
        return false;
      }
    });
  });

  // 2. Open Schedule Session Modal
  document.querySelectorAll('.open-schedule-modal-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const requestId = btn.getAttribute('data-request-id');
      const reqInput = document.getElementById('session-request-id');
      if (reqInput) reqInput.value = requestId;

      const form = document.getElementById('schedule-session-form');
      if (form) form.action = `/request/${requestId}/schedule-session`;

      openModal('schedule-session-modal');
    });
  });

  // 3. Open Review Modal
  document.querySelectorAll('.open-review-modal-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const requestId = btn.getAttribute('data-request-id');
      const partnerName = btn.getAttribute('data-partner-name');

      const form = document.getElementById('submit-review-form');
      if (form) form.action = `/request/${requestId}/review`;

      const partnerSpan = document.getElementById('review-partner-name');
      if (partnerSpan) partnerSpan.textContent = partnerName || 'your peer';

      openModal('submit-review-modal');
    });
  });

  // 4. Interactive Star Rating Selector
  const starContainer = document.getElementById('star-rating-selector');
  const ratingInput = document.getElementById('rating-score-input');
  if (starContainer && ratingInput) {
    const stars = starContainer.querySelectorAll('.star-icon');
    stars.forEach(star => {
      star.addEventListener('click', () => {
        const val = parseInt(star.getAttribute('data-val'), 10);
        ratingInput.value = val;
        stars.forEach(s => {
          const sVal = parseInt(s.getAttribute('data-val'), 10);
          if (sVal <= val) {
            s.style.color = '#FBBF24';
          } else {
            s.style.color = '#475569';
          }
        });
      });

      star.addEventListener('mouseenter', () => {
        const val = parseInt(star.getAttribute('data-val'), 10);
        stars.forEach(s => {
          const sVal = parseInt(s.getAttribute('data-val'), 10);
          if (sVal <= val) {
            s.style.opacity = '1';
          } else {
            s.style.opacity = '0.4';
          }
        });
      });

      starContainer.addEventListener('mouseleave', () => {
        const currentVal = parseInt(ratingInput.value || 0, 10);
        stars.forEach(s => {
          const sVal = parseInt(s.getAttribute('data-val'), 10);
          s.style.opacity = '1';
          s.style.color = (sVal <= currentVal) ? '#FBBF24' : '#475569';
        });
      });
    });
  }
});
