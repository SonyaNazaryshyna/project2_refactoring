/* profile.js — follow / edit profile */
document.addEventListener('DOMContentLoaded', () => {
  const followBtn = document.getElementById('follow-btn');
  if (followBtn) {
    followBtn.addEventListener('click', async () => {
      const username = followBtn.dataset.username;
      const following = followBtn.dataset.following === 'true';
      try {
        await apiCall(`/users/${username}/follow`, { method: following ? 'DELETE' : 'POST' });
        followBtn.dataset.following = String(!following);
        if (!following) {
          followBtn.classList.add('is-following');
          followBtn.textContent = 'Відписатись';
          showToast(`Підписались на @${username} 🎉`);
        } else {
          followBtn.classList.remove('is-following');
          followBtn.textContent = '+ Підписатись';
          showToast(`Відписались від @${username}`);
        }
      } catch (e) {
        showToast(e.message, 'error');
      }
    });
  }

  document.getElementById('edit-modal')?.addEventListener('click', e => {
    if (e.target.id === 'edit-modal') {
      document.getElementById('edit-modal').classList.add('hidden');
    }
  });
});

async function saveProfile() {
  const bio = document.getElementById('edit-bio').value;
  const av = document.getElementById('edit-avatar').value.trim();
  const errEl = document.getElementById('edit-error');
  errEl.classList.add('hidden');
  try {
    const body = { bio };
    if (av) body.avatar_url = av;
    await apiCall('/users/me/update', { method: 'PATCH', body: JSON.stringify(body) });
    document.getElementById('edit-modal').classList.add('hidden');
    showToast('Профіль оновлено ✓');
    setTimeout(() => location.reload(), 700);
  } catch (e) {
    errEl.textContent = e.message;
    errEl.classList.remove('hidden');
  }
}
