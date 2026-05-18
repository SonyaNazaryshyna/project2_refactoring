document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      const liked = btn.dataset.liked === 'true';
      const cnt = btn.querySelector('.like-count');
      btn.classList.toggle('liked', !liked);
      btn.dataset.liked = String(!liked);
      cnt.textContent = parseInt(cnt.textContent) + (liked ? -1 : 1);
      try {
        const url = liked ? `/api/v1/posts/${id}/unlike/` : `/api/v1/posts/${id}/like/`;
        await apiCall(url, {method: liked ? 'DELETE' : 'POST'});
      } catch {
        btn.classList.toggle('liked', liked);
        btn.dataset.liked = String(liked);
        cnt.textContent = parseInt(cnt.textContent) + (liked ? 1 : -1);
      }
    });
  });
  document.querySelectorAll('.del-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!confirm('Видалити допис?')) return;
      const id = btn.dataset.id;
      const card = document.querySelector(`.post-card[data-id="${id}"]`);
      try {
        await apiCall(`/api/v1/posts/${id}/delete/`, {method:'DELETE'});
        card.style.cssText = 'opacity:0;transform:translateX(-14px);transition:.25s';
        setTimeout(() => card.remove(), 260);
        showToast('Допис видалено');
      } catch(e) { showToast(e.message,'error'); }
    });
  });
});