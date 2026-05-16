/* compose.js — new post modal */
function openCompose(prefill = '') {
  const modal = document.getElementById('compose-modal');
  const ta = document.getElementById('compose-text');
  if (!modal) return;
  modal.classList.remove('hidden');
  ta.value = prefill;
  document.getElementById('char-num').textContent = prefill.length;
  ta.focus();
}

function closeCompose() {
  document.getElementById('compose-modal')?.classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
  const ta = document.getElementById('compose-text');
  if (ta) {
    ta.addEventListener('input', e => {
      document.getElementById('char-num').textContent = e.target.value.length;
    });
  }

  document.getElementById('compose-submit')?.addEventListener('click', async () => {
    const content = document.getElementById('compose-text').value.trim();
    const errEl = document.getElementById('compose-error');
    errEl.classList.add('hidden');
    if (!content) return;
    try {
      await apiCall('/posts', { method: 'POST', body: JSON.stringify({ content }) });
      closeCompose();
      showToast('Допис опубліковано 🎉');
      setTimeout(() => location.reload(), 700);
    } catch (e) {
      errEl.textContent = e.message;
      errEl.classList.remove('hidden');
    }
  });

  document.getElementById('compose-modal')?.addEventListener('click', e => {
    if (e.target.id === 'compose-modal') closeCompose();
  });
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeCompose();
  if (e.key === 'n' && !e.target.matches('input,textarea')) openCompose();
});
