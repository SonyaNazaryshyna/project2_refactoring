/* posts.js — like & delete */
document.addEventListener('DOMContentLoaded', () => {

  // Like / unlike
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      const liked = btn.dataset.liked === 'true';
      const cnt = btn.querySelector('.like-count');
      // Optimistic update
      btn.classList.toggle('liked', !liked);
      btn.dataset.liked = String(!liked);
      cnt.textContent = parseInt(cnt.textContent) + (liked ? -1 : 1);
      try {
        await apiCall(`/posts/${id}/like`, { method: liked ? 'DELETE' : 'POST' });
      } catch {
        // Rollback
        btn.classList.toggle('liked', liked);
        btn.dataset.liked = String(liked);
        cnt.textContent = parseInt(cnt.textContent) + (liked ? 1 : -1);
      }
    });
  });

  // Delete
  document.querySelectorAll('.del-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!confirm('Видалити цей допис?')) return;
      const id = btn.dataset.id;
      const card = document.querySelector(`.post-card[data-id="${id}"]`);
      try {
        await apiCall(`/posts/${id}`, { method: 'DELETE' });
        card.style.cssText = 'opacity:0;transform:translateX(-14px);transition:.25s';
        setTimeout(() => card.remove(), 260);
        showToast('Допис видалено');
      } catch (e) {
        showToast(e.message, 'error');
      }
    });
  });

});
