/**
 * SkillSwap — Profile JavaScript
 * Interactive tag management and profile avatar selection
 */

document.addEventListener('DOMContentLoaded', () => {
  // Interest tag input helper
  const interestInput = document.getElementById('interest-tag-input');
  const addTagBtn = document.getElementById('add-interest-tag-btn');
  const interestsHidden = document.getElementById('learning_interests');
  const tagsContainer = document.getElementById('interests-tags-container');

  if (addTagBtn && interestInput && interestsHidden && tagsContainer) {
    const updateHiddenField = () => {
      const tags = [];
      tagsContainer.querySelectorAll('.interest-badge').forEach(badge => {
        tags.push(badge.getAttribute('data-value'));
      });
      interestsHidden.value = tags.join(', ');
    };

    const addTag = (val) => {
      const clean = val.trim();
      if (!clean) return;

      const badge = document.createElement('span');
      badge.className = 'badge badge-category interest-badge';
      badge.setAttribute('data-value', clean);
      badge.style.display = 'inline-flex';
      badge.style.alignItems = 'center';
      badge.style.gap = '6px';
      badge.style.margin = '4px';
      badge.innerHTML = `${clean} <button type="button" class="remove-tag-btn" style="background:none;border:none;color:#fff;cursor:pointer;font-weight:bold;">&times;</button>`;

      badge.querySelector('.remove-tag-btn').addEventListener('click', () => {
        badge.remove();
        updateHiddenField();
      });

      tagsContainer.appendChild(badge);
      updateHiddenField();
      interestInput.value = '';
    };

    addTagBtn.addEventListener('click', () => {
      addTag(interestInput.value);
    });

    interestInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        addTag(interestInput.value);
      }
    });

    // Attach listener to existing tag remove buttons
    tagsContainer.querySelectorAll('.remove-tag-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        btn.closest('.interest-badge').remove();
        updateHiddenField();
      });
    });
  }
});
