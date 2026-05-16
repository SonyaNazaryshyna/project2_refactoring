/* ═══════════════════════════════════════════
   МІКРОБЛОГ — Frontend Application
   ═══════════════════════════════════════════ */

const API = 'http://localhost:8000/api/v1';

/* ── State ─────────────────────────────────── */
const state = {
  token: localStorage.getItem('access_token') || null,
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  currentView: 'feed',
  profileUsername: null,
};

/* ── API helpers ───────────────────────────── */
async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

  const res = await fetch(`${API}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) throw { 
    status: res.status, 
    message: data.message || data.detail || 'Помилка сервера' 
  };
  return data;
}

function escapeHtml(unsafe) {
  if (unsafe == null) return '';
  return String(unsafe)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/* ── Time formatting ───────────────────────── */
function timeAgo(iso) {
  const diff = (Date.now() - new Date(iso)) / 1000;
  if (diff < 60)    return 'щойно';
  if (diff < 3600)  return `${Math.floor(diff/60)} хв тому`;
  if (diff < 86400) return `${Math.floor(diff/3600)} год тому`;
  return new Date(iso).toLocaleDateString('uk-UA', { day:'numeric', month:'short' });
}

let toastTimer;
function toast(msg, type = 'success') {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.className = `toast ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.add('hidden'), 2800);
}

function showView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById(`view-${name}`)?.classList.add('active');
  document.querySelector(`[data-view="${name}"]`)?.classList.add('active');
  state.currentView = name;

  if (name === 'feed')    loadFeed();
  if (name === 'explore') loadExplore();
  if (name === 'profile') loadMyProfile();
}

function showAuth() {
  document.getElementById('auth-screen').classList.add('active');
  document.getElementById('app-screen').classList.remove('active');
}

function showApp() {
  document.getElementById('auth-screen').classList.remove('active');
  document.getElementById('app-screen').classList.add('active');
  updateSidebar();
  loadFeed();
}

function updateSidebar() {
  if (!state.user) return;
  const u = state.user;
  document.getElementById('sidebar-username').textContent = u.username;
  document.getElementById('sidebar-email').textContent = u.email;
  document.getElementById('sidebar-avatar').textContent = u.username[0].toUpperCase();
  document.getElementById('compose-avatar').textContent = u.username[0].toUpperCase();
}

/* ══════════════════════════════════════════
   AUTH
══════════════════════════════════════════ */
function setLoading(btn, loading) {
  const span = btn.querySelector('span');
  if (span) span.style.opacity = loading ? '0' : '1';
  const loader = btn.querySelector('.btn-loader');
  if (loader) loader.classList.toggle('hidden', !loading);
  btn.disabled = loading;
}

function showError(id, msg) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = msg;
    el.classList.remove('hidden');
  }
}

function hideError(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('hidden');
}

// Tab switching
document.querySelectorAll('.auth-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(`${tab.dataset.tab}-form`).classList.add('active');
    hideError('login-error');
    hideError('register-error');
  });
});

// Login
document.getElementById('login-form').addEventListener('submit', async e => {
  e.preventDefault();
  hideError('login-error');
  const btn = e.target.querySelector('.btn-primary');
  setLoading(btn, true);
  try {
    const data = await api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email:    document.getElementById('login-email').value,
        password: document.getElementById('login-password').value,
      }),
    });
    saveTokens(data);
    await fetchAndSaveMe();
    showApp();
  } catch(err) {
    showError('login-error', err.message || 'Невірний email або пароль');
  } finally { setLoading(btn, false); }
});

// Register
document.getElementById('register-form').addEventListener('submit', async e => {
  e.preventDefault();
  hideError('register-error');
  const btn = e.target.querySelector('.btn-primary');
  setLoading(btn, true);
  try {
    const data = await api('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        username: document.getElementById('reg-username').value,
        email:    document.getElementById('reg-email').value,
        password: document.getElementById('reg-password').value,
        bio:      document.getElementById('reg-bio').value,
      }),
    });
    saveTokens(data);
    await fetchAndSaveMe();
    showApp();
    toast('Ласкаво просимо! 🎉');
  } catch(err) {
    showError('register-error', err.message || 'Помилка реєстрації');
  } finally { setLoading(btn, false); }
});

function saveTokens({ access_token, refresh_token }) {
  state.token = access_token;
  localStorage.setItem('access_token', access_token);
  if (refresh_token) localStorage.setItem('refresh_token', refresh_token);
}

async function fetchAndSaveMe() {
  try {
    const data = await api('/users/me');
    state.user = data;
    localStorage.setItem('user', JSON.stringify(data));
    updateStats(data);
  } catch (e) {}
}

function updateStats(user) {
  document.getElementById('stat-followers').textContent = user.follower_count ?? '—';
  document.getElementById('stat-following').textContent = user.following_count ?? '—';
}

// Logout
document.getElementById('logout-btn').addEventListener('click', () => {
  state.token = null; state.user = null;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  showAuth();
  toast('До зустрічі! 👋');
});

/* ══════════════════════════════════════════
   POSTS RENDERING
══════════════════════════════════════════ */
function avatarColor(username) {
  const colors = [
    'linear-gradient(135deg,#e8b86d,#d4a055)',
    'linear-gradient(135deg,#7b6ef6,#5a4fd6)',
    'linear-gradient(135deg,#5cb88a,#3a9e6d)',
    'linear-gradient(135deg,#e05c5c,#c44040)',
    'linear-gradient(135deg,#5bb8d4,#3a9eb8)',
    'linear-gradient(135deg,#d46eb8,#b84fa0)',
  ];
  let h = 0;
  for (let i = 0; i < username.length; i++) h += username.charCodeAt(i);
  return colors[h % colors.length];
}

function renderPost(post, viewerUsername) {
  const isOwn = post.author_username === viewerUsername;
  const card = document.createElement('article');
  card.className = 'post-card';
  card.dataset.postId = post.id;

  card.innerHTML = `
    <div class="post-header">
      <div class="post-avatar" style="background:${avatarColor(post.author_username)}"
           data-username="${post.author_username}">
        ${post.author_username[0].toUpperCase()}
      </div>
      <div class="post-meta">
        <div class="post-author" data-username="${post.author_username}">
          @${post.author_username}
          ${isOwn ? '<span class="post-own-badge">Мій</span>' : ''}
        </div>
        <div class="post-time">${timeAgo(post.created_at)}</div>
      </div>
    </div>
    <div class="post-body">${escapeHtml(post.content)}</div>
    <div class="post-actions">
      <button class="action-btn like-btn ${post.is_liked_by_me ? 'liked' : ''}" data-post-id="${post.id}">
        <svg viewBox="0 0 24 24"><path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>
        <span>${post.like_count}</span>
      </button>
      <button class="action-btn reply-btn" data-post-id="${post.id}" data-author="${post.author_username}">
        <svg viewBox="0 0 24 24"><path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
        Відповісти
      </button>
      ${isOwn ? `
      <button class="action-btn delete-btn" data-post-id="${post.id}">
        <svg viewBox="0 0 24 24"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
        Видалити
      </button>` : ''}
    </div>
  `;

  // Like
  card.querySelector('.like-btn')?.addEventListener('click', () => toggleLike(post, card));

  // Delete
  card.querySelector('.delete-btn')?.addEventListener('click', () => deletePost(post.id, card));

  // Go to profile
  card.querySelectorAll('[data-username]').forEach(el => {
    el.addEventListener('click', () => openUserProfile(el.dataset.username));
  });

  // Reply
  card.querySelector('.reply-btn')?.addEventListener('click', () => {
    openCompose(`@${post.author_username} `);
  });

  return card;
}

/* ── Like ─────────────────────────────────── */
async function toggleLike(post, card) {
  const btn = card.querySelector('.like-btn');
  const isLiked = btn.classList.contains('liked');
  const countEl = btn.querySelector('span');
  const method = isLiked ? 'DELETE' : 'POST';

  btn.classList.toggle('liked', !isLiked);
  countEl.textContent = parseInt(countEl.textContent) + (isLiked ? -1 : 1);

  try {
    await api(`/posts/${post.id}/like`, { method });
  } catch {
    btn.classList.toggle('liked', isLiked);
    countEl.textContent = parseInt(countEl.textContent) + (isLiked ? 1 : -1);
  }
}

/* ── Delete post ──────────────────────────── */
async function deletePost(postId, card) {
  if (!confirm('Видалити цей допис?')) return;
  try {
    await api(`/posts/${postId}`, { method: 'DELETE' });
    card.style.transition = 'opacity .3s, transform .3s';
    card.style.opacity = '0';
    card.style.transform = 'translateX(-20px)';
    setTimeout(() => card.remove(), 300);
    toast('Допис видалено');
    updatePostsCount(-1);
  } catch(err) { toast(err.message, 'error'); }
}

function updatePostsCount(delta) {
  const el = document.getElementById('stat-posts');
  const n = parseInt(el.textContent) || 0;
  el.textContent = Math.max(0, n + delta);
}

/* ══════════════════════════════════════════
   FEED
══════════════════════════════════════════ */
async function loadFeed() {
  const container = document.getElementById('feed-posts');
  const empty     = document.getElementById('feed-empty');
  container.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Завантаження стрічки…</p></div>`;
  empty.classList.add('hidden');

  try {
    const data = await api('/feed?page=1&size=30');
    container.innerHTML = '';
    const posts = data.items || [];

    if (posts.length === 0) {
      container.style.display = 'none';
      empty.classList.remove('hidden');
    } else {
      container.style.display = '';
      posts.forEach((p, i) => {
        const card = renderPost(p, state.user?.username);
        card.style.animationDelay = `${i * 40}ms`;
        container.appendChild(card);
      });
    }
    // count posts
    document.getElementById('stat-posts').textContent = posts.filter(p => p.author_username === state.user?.username).length;
  } catch(err) {
    container.innerHTML = `<div class="loading-state"><p style="color:#f08080">Не вдалось завантажити стрічку</p></div>`;
  }
}

/* ══════════════════════════════════════════
   EXPLORE (all posts)
══════════════════════════════════════════ */
async function loadExplore() {
  const container = document.getElementById('explore-posts');
  container.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Завантаження…</p></div>`;

  try {
    const data = await api(`/posts?page=1&size=40`);
    container.innerHTML = '';
    const posts = data.items || [];
    if (posts.length === 0) {
      container.innerHTML = `<div class="empty-state"><div class="empty-icon">🔍</div><h3>Поки немає дописів</h3><p>Будь першим!</p></div>`;
    } else {
      posts.forEach((p, i) => {
        const card = renderPost(p, state.user?.username);
        card.style.animationDelay = `${i * 40}ms`;
        container.appendChild(card);
      });
    }
  } catch {
    // fallback: load my posts
    try {
      const me = await api('/users/me');
      const data = await api(`/users/${me.username}/posts?page=1&size=40`).catch(() => null);
      // If no explore endpoint, just show a message
      container.innerHTML = `<div class="empty-state"><div class="empty-icon">✨</div><h3>Розділ "Огляд"</h3><p>Переглядай дописи людей на яких підписаний</p></div>`;
    } catch {}
  }
}

/* ══════════════════════════════════════════
   PROFILE
══════════════════════════════════════════ */
async function loadMyProfile() {
  if (!state.user) return;
  await openUserProfile(state.user.username, true);
}

async function openUserProfile(username, isOwn = false) {
  if (!isOwn) isOwn = (username === state.user?.username);

  showView('profile');

  const container = document.getElementById('profile-content');
  container.innerHTML = `<div class="loading-state"><div class="spinner"></div></div>`;

  try {
    const user = await api(`/users/${username}`);
    const postsData = await api(`/posts?page=1&size=30`).catch(() => ({ items: [] }));

    // Filter posts by this author from the feed
    let userPosts = (postsData.items || []).filter(p => p.author_username === username);

    // Try dedicated endpoint
    try {
      const dedicated = await api(`/users/${username}/posts?page=1&size=30`);
      if (dedicated.items?.length) userPosts = dedicated.items;
    } catch {}

    const isFollowing = !isOwn && await checkIfFollowing(username);

    container.innerHTML = '';
    container.appendChild(renderProfileHeader(user, isOwn, isFollowing));

    const postsSection = document.createElement('div');
    postsSection.className = 'posts-list';

    if (userPosts.length === 0) {
      postsSection.innerHTML = `<div class="empty-state"><div class="empty-icon">📝</div><h3>Поки немає дописів</h3></div>`;
    } else {
      userPosts.forEach((p, i) => {
        const card = renderPost(p, state.user?.username);
        card.style.animationDelay = `${i * 40}ms`;
        postsSection.appendChild(card);
      });
    }
    container.appendChild(postsSection);

    if (isOwn) {
      updateStats(user);
      document.getElementById('stat-posts').textContent = userPosts.length;
    }
  } catch(err) {
    container.innerHTML = `<div class="loading-state"><p style="color:#f08080">Не вдалось завантажити профіль</p></div>`;
  }
}

async function checkIfFollowing(username) {
  if (!state.user) return false;
  try {
    const data = await api(`/users/${state.user.username}/following?page=1&size=100`);
    return (data.items || []).some(u => u.username === username);
  } catch { return false; }
}

function renderProfileHeader(user, isOwn, isFollowing) {
  const div = document.createElement('div');
  div.className = 'profile-header';

  div.innerHTML = `
    <div class="profile-top">
      <div class="profile-avatar" style="background:${avatarColor(user.username)}">
        ${escapeHtml(user.username[0].toUpperCase())}
      </div>
      ${!isOwn ? `
        <button class="follow-btn ${isFollowing ? 'unfollow' : 'follow'}" id="follow-toggle-btn">
          ${isFollowing ? 'Відписатись' : '+ Підписатись'}
        </button>
      ` : `
        <button class="btn-secondary" id="edit-profile-btn">Редагувати</button>
      `}
    </div>
    <div class="profile-name">${escapeHtml(user.username)}</div>
    <div class="profile-handle">${escapeHtml(user.email)}</div>
    ${user.bio ? `<div class="profile-bio">${escapeHtml(user.bio)}</div>` : ''}
    <div class="profile-stats">
      <div class="profile-stat">
        <strong>${user.follower_count ?? 0}</strong>
        <span>підписників</span>
      </div>
      <div class="profile-stat">
        <strong>${user.following_count ?? 0}</strong>
        <span>підписок</span>
      </div>
    </div>
  `;

  // Follow/Unfollow
  const followBtn = div.querySelector('#follow-toggle-btn');
  if (followBtn) {
    followBtn.addEventListener('click', async () => {
      const following = followBtn.classList.contains('unfollow');
      try {
        await api(`/users/${user.username}/follow`, { method: following ? 'DELETE' : 'POST' });
        followBtn.classList.toggle('follow', following);
        followBtn.classList.toggle('unfollow', !following);
        followBtn.textContent = following ? '+ Підписатись' : 'Відписатись';
        toast(following ? `Відписались від @${user.username}` : `Підписались на @${user.username} 🎉`);
        if (!following) await fetchAndSaveMe();
      } catch(err) { toast(err.message, 'error'); }
    });
  }

  // Edit profile
  const editBtn = div.querySelector('#edit-profile-btn');
  if (editBtn) editBtn.addEventListener('click', () => openEditProfile(user));

  return div;
}

/* ── Edit Profile Modal ───────────────────── */
function openEditProfile(user) {
  const existing = document.getElementById('edit-profile-modal');
  if (existing) existing.remove();

  const modal = document.createElement('div');
  modal.id = 'edit-profile-modal';
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal">
      <div class="modal-header">
        <h3>Редагувати профіль</h3>
        <button class="modal-close" id="close-edit">✕</button>
      </div>
      <div class="modal-body">
        <div class="field">
          <label>Про себе</label>
          <textarea id="edit-bio" style="background:var(--ink-3);border:1px solid var(--ink-4);border-radius:8px;padding:12px 16px;color:var(--paper);font-family:'DM Sans',sans-serif;font-size:.95rem;width:100%;resize:vertical;outline:none;line-height:1.6" rows="3" maxlength="500" placeholder="Розкажи про себе…">${escapeHtml(user.bio || '')}</textarea>
        </div>
        <div class="field" style="margin-top:16px">
          <label>Аватар (URL)</label>
          <input type="url" id="edit-avatar" value="${user.avatar_url || ''}" placeholder="https://..." />
        </div>
        <div id="edit-error" class="form-error hidden" style="margin-top:12px"></div>
        <button class="btn-primary" id="save-profile-btn" style="margin-top:20px">
          <span>Зберегти</span>
          <div class="btn-loader hidden"></div>
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  modal.querySelector('#close-edit').addEventListener('click', () => modal.remove());
  modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });

  modal.querySelector('#save-profile-btn').addEventListener('click', async () => {
    const btn = modal.querySelector('#save-profile-btn');
    const errEl = modal.querySelector('#edit-error');
    errEl.classList.add('hidden');
    setLoading(btn, true);
    try {
      const body = { bio: modal.querySelector('#edit-bio').value };
      const av = modal.querySelector('#edit-avatar').value.trim();
      if (av) body.avatar_url = av;
      await api('/users/me/update', { method: 'PATCH', body: JSON.stringify(body) });
      await fetchAndSaveMe();
      modal.remove();
      toast('Профіль оновлено ✓');
      loadMyProfile();
    } catch(err) {
      errEl.textContent = err.message;
      errEl.classList.remove('hidden');
    } finally { setLoading(btn, false); }
  });
}

/* ══════════════════════════════════════════
   COMPOSE
══════════════════════════════════════════ */
function openCompose(prefill = '') {
  const modal = document.getElementById('compose-modal');
  const textarea = document.getElementById('compose-text');
  modal.classList.remove('hidden');
  textarea.value = prefill;
  updateCharCount(prefill.length);
  textarea.focus();
  textarea.setSelectionRange(prefill.length, prefill.length);
  document.getElementById('compose-error').classList.add('hidden');
}

document.getElementById('open-compose').addEventListener('click', () => openCompose());
document.getElementById('close-compose').addEventListener('click', () => {
  document.getElementById('compose-modal').classList.add('hidden');
});
document.getElementById('compose-modal').addEventListener('click', e => {
  if (e.target.id === 'compose-modal')
    document.getElementById('compose-modal').classList.add('hidden');
});

// Char counter
document.getElementById('compose-text').addEventListener('input', e => {
  updateCharCount(e.target.value.length);
});

function updateCharCount(len) {
  document.getElementById('char-num').textContent = len;
  const wrap = document.querySelector('.char-count');
  wrap.className = `char-count${len > 250 ? ' warn' : ''}${len >= 280 ? ' limit' : ''}`;
}

// Submit post
document.getElementById('submit-post').addEventListener('click', async () => {
  const content = document.getElementById('compose-text').value.trim();
  const errEl = document.getElementById('compose-error');
  errEl.classList.add('hidden');

  if (!content) { errEl.textContent = 'Допис не може бути порожнім'; errEl.classList.remove('hidden'); return; }

  const btn = document.getElementById('submit-post');
  setLoading(btn, true);
  try {
    const post = await api('/posts', { method: 'POST', body: JSON.stringify({ content }) });
    document.getElementById('compose-modal').classList.add('hidden');
    document.getElementById('compose-text').value = '';
    updateCharCount(0);
    toast('Допис опубліковано 🎉');
    // Prepend to current view
    prependPost(post);
    updatePostsCount(1);
  } catch(err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally { setLoading(btn, false); }
});

function prependPost(post) {
  const containers = { feed: 'feed-posts', explore: 'explore-posts' };
  const cid = containers[state.currentView];
  if (!cid) return;
  const container = document.getElementById(cid);
  if (!container) return;
  // Remove empty/loading states
  container.querySelectorAll('.loading-state,.empty-state').forEach(e => e.remove());
  document.getElementById('feed-empty')?.classList.add('hidden');
  container.style.display = '';
  const card = renderPost(post, state.user?.username);
  card.style.animation = 'none';
  card.style.background = 'var(--accent-bg)';
  container.prepend(card);
  setTimeout(() => { card.style.transition = 'background .8s'; card.style.background = ''; }, 50);
}

/* ══════════════════════════════════════════
   NAVIGATION
══════════════════════════════════════════ */
document.querySelectorAll('.nav-item, [data-view]').forEach(el => {
  el.addEventListener('click', () => {
    const v = el.dataset.view;
    if (v) showView(v);
  });
});

document.getElementById('refresh-feed').addEventListener('click', loadFeed);

// Keyboard shortcuts
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.getElementById('compose-modal').classList.add('hidden');
    document.getElementById('edit-profile-modal')?.remove();
  }
  if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
    if (!document.getElementById('compose-modal').classList.contains('hidden')) {
      document.getElementById('submit-post').click();
    }
  }
  if (e.key === 'n' && !e.target.matches('input,textarea')) {
    openCompose();
  }
});

/* ══════════════════════════════════════════
   INIT
══════════════════════════════════════════ */
(async function init() {
  if (state.token) {
    try {
      await fetchAndSaveMe();
      showApp();
    } catch {
      state.token = null;
      localStorage.removeItem('access_token');
      showAuth();
    }
  } else {
    showAuth();
  }
})();