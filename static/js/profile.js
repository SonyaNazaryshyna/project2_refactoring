document.addEventListener('DOMContentLoaded', () => {
  const followBtn = document.getElementById('follow-btn');
  if (followBtn) {
    followBtn.addEventListener('click', async () => {
      const username = followBtn.dataset.username;
      const following = followBtn.dataset.following === 'true';
      try {
        await apiCall(`/api/v1/users/${username}/follow`, {method: following ? 'DELETE' : 'POST'});
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
      } catch(e) { showToast(e.message, 'error'); }
    });
  }
});
