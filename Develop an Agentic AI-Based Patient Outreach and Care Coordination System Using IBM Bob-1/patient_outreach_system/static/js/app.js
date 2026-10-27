/**
 * app.js – Global JavaScript for the
 * Patient Outreach & Care Coordination System
 */

'use strict';

// ── Highlight active nav item ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(link => {
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });

  // Auto-dismiss flash messages after 4 seconds
  document.querySelectorAll('.alert[data-autohide]').forEach(el => {
    setTimeout(() => el.style.display = 'none', 4000);
  });
});

// ── Toast notification utility ─────────────────────────────────────────────────
function showToast(message, type = 'info') {
  const colours = {
    info:    { bg: '#eff6ff', color: '#1e40af', border: '#bfdbfe' },
    success: { bg: '#d1fae5', color: '#065f46', border: '#6ee7b7' },
    error:   { bg: '#fde8e8', color: '#c81e1e', border: '#fca5a5' },
    warning: { bg: '#fdf6b2', color: '#7c6b00', border: '#fcd34d' },
  };
  const c = colours[type] || colours.info;
  const toast = document.createElement('div');
  toast.style.cssText = `
    position:fixed; bottom:24px; right:24px; z-index:9999;
    background:${c.bg}; color:${c.color}; border:1px solid ${c.border};
    padding:12px 18px; border-radius:10px; font-size:13px; font-weight:600;
    box-shadow:0 4px 16px rgba(0,0,0,.15); max-width:320px;
    animation: slideIn .25s ease;
  `;
  toast.innerText = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// ── Format date helper ────────────────────────────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

// ── Simple confirm dialog ─────────────────────────────────────────────────────
function confirmAction(message) {
  return window.confirm(message);
}
