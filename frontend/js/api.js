/* ═══════════════════════════════════════
   api.js — всі запити до бекенду
═══════════════════════════════════════ */

export const BASE = 'http://localhost:8000/api/v1';

export function getToken() {
  return localStorage.getItem('access_token');
}

export async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw { status: res.status, message: data.message || data.detail || 'Помилка сервера' };
  }
  return data;
}

// ── Auth ──────────────────────────────
export const auth = {
  register: (body) => request('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  login:    (body) => request('/auth/login',    { method: 'POST', body: JSON.stringify(body) }),
  refresh:  (body) => request('/auth/refresh',  { method: 'POST', body: JSON.stringify(body) }),
};

// ── Users ─────────────────────────────
export const users = {
  me:         ()         => request('/users/me'),
  updateMe:   (body)     => request('/users/me/update', { method: 'PATCH', body: JSON.stringify(body) }),
  profile:    (username) => request(`/users/${username}`),
  follow:     (username) => request(`/users/${username}/follow`, { method: 'POST' }),
  unfollow:   (username) => request(`/users/${username}/follow`, { method: 'DELETE' }),
  followers:  (username, page = 1) => request(`/users/${username}/followers?page=${page}&size=20`),
  following:  (username, page = 1) => request(`/users/${username}/following?page=${page}&size=20`),
  posts:      (username, page = 1) => request(`/users/${username}/posts?page=${page}&size=30`),
};

// ── Posts ─────────────────────────────
export const posts = {
  create:  (body)   => request('/posts', { method: 'POST', body: JSON.stringify(body) }),
  get:     (id)     => request(`/posts/${id}`),
  edit:    (id, body) => request(`/posts/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  delete:  (id)     => request(`/posts/${id}`, { method: 'DELETE' }),
  like:    (id)     => request(`/posts/${id}/like`, { method: 'POST' }),
  unlike:  (id)     => request(`/posts/${id}/like`, { method: 'DELETE' }),
  feed:    (page = 1, size = 30) => request(`/feed?page=${page}&size=${size}`),
  explore: (page = 1, size = 40) => request(`/posts?page=${page}&size=${size}`),
};
