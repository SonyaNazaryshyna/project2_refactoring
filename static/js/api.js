/* ══════════════════════════════════
   API helper — shared across pages
══════════════════════════════════ */
const API_BASE = '/api/v1';

async function apiCall(path, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw { status: res.status, message: data.message || data.detail || 'Помилка сервера' };
  return data;
}

function timeAgo(iso) {
  const diff = (Date.now() - new Date(iso)) / 1000;
  if (diff < 60)    return 'щойно';
  if (diff < 3600)  return `${Math.floor(diff/60)} хв тому`;
  if (diff < 86400) return `${Math.floor(diff/3600)} год тому`;
  return new Date(iso).toLocaleDateString('uk-UA', { day:'numeric', month:'short' });
}
