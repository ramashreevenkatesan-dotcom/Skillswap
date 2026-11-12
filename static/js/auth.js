/**
 * SkillSwap — Auth JavaScript
 * Client-side validation and password strength indicators for Login and Signup
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Signup Form Real-time Password Strength Meter
  const passwordInput = document.getElementById('signup-password');
  const confirmInput = document.getElementById('signup-confirm-password');
  const strengthMeter = document.getElementById('password-strength-indicator');
  const strengthText = document.getElementById('password-strength-text');

  if (passwordInput && strengthMeter) {
    passwordInput.addEventListener('input', () => {
      const val = passwordInput.value;
      let score = 0;

      if (val.length >= 8) score++;
      if (/[A-Z]/.test(val)) score++;
      if (/[a-z]/.test(val)) score++;
      if (/\d/.test(val)) score++;
      if (/[@$!%*?&#^_\-]/.test(val)) score++;

      strengthMeter.style.height = '4px';
      strengthMeter.style.borderRadius = '2px';
      strengthMeter.style.transition = 'all 0.3s ease';

      if (val.length === 0) {
        strengthMeter.style.width = '0%';
        if (strengthText) strengthText.textContent = '';
      } else if (score <= 2) {
        strengthMeter.style.width = '30%';
        strengthMeter.style.backgroundColor = '#EF4444';
        if (strengthText) {
          strengthText.textContent = 'Weak: Add uppercase, number & symbol';
          strengthText.style.color = '#EF4444';
        }
      } else if (score <= 4) {
        strengthMeter.style.width = '70%';
        strengthMeter.style.backgroundColor = '#F59E0B';
        if (strengthText) {
          strengthText.textContent = 'Moderate: Add special characters';
          strengthText.style.color = '#F59E0B';
        }
      } else {
        strengthMeter.style.width = '100%';
        strengthMeter.style.backgroundColor = '#10B981';
        if (strengthText) {
          strengthText.textContent = 'Strong: Secure password';
          strengthText.style.color = '#10B981';
        }
      }
    });
  }

  // Confirm password match feedback
  if (confirmInput && passwordInput) {
    confirmInput.addEventListener('input', () => {
      if (confirmInput.value !== passwordInput.value) {
        confirmInput.style.borderColor = '#EF4444';
      } else {
        confirmInput.style.borderColor = '#10B981';
      }
    });
  }

  // 2. Client-side Form Submit Validation
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', (e) => {
      const pass = passwordInput ? passwordInput.value : '';
      const confirm = confirmInput ? confirmInput.value : '';

      if (pass !== confirm) {
        e.preventDefault();
        alert('Passwords do not match. Please ensure both passwords match.');
        confirmInput.focus();
        return false;
      }

      if (pass.length < 8) {
        e.preventDefault();
        alert('Password must be at least 8 characters long.');
        passwordInput.focus();
        return false;
      }
    });
  }

  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      const emailField = document.getElementById('login-email');
      const passField = document.getElementById('login-password');
      if (emailField && !emailField.value.trim()) {
        e.preventDefault();
        alert('Please enter your email address or username.');
        emailField.focus();
        return false;
      }
      if (passField && !passField.value) {
        e.preventDefault();
        alert('Please enter your password.');
        passField.focus();
        return false;
      }
    });
  }
});
