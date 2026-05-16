function openCompose(prefill='') {
  const m = document.getElementById('compose-modal');
  const ta = document.getElementById('compose-text');
  if (!m) return;
  m.classList.remove('hidden');
  ta.value = prefill;
  document.getElementById('char-num').textContent = prefill.length;
  setTimeout(() => ta.focus(), 50);
}
function closeCompose() {
  document.getElementById('compose-modal')?.classList.add('hidden');
}
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('compose-text')?.addEventListener('input', e => {
    document.getElementById('char-num').textContent = e.target.value.length;
  });
  document.getElementById('compose-submit')?.addEventListener('click', async () => {
    const content = document.getElementById('compose-text').value.trim();
    const err = document.getElementById('compose-error');
    err.classList.add('hidden');
    if (!content) return;
    try {
      await apiCall('/api/v1/posts', {method:'POST', body:JSON.stringify({content})});
      closeCompose();
      showToast('Допис опубліковано 🎉');
      setTimeout(() => location.reload(), 600);
    } catch(e) { err.textContent = e.message; err.classList.remove('hidden'); }
  });
  document.getElementById('compose-modal')?.addEventListener('click', e => {
    if (e.target.id === 'compose-modal') closeCompose();
  });
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeCompose();
  if (e.key === 'n' && !e.target.matches('input,textarea,select')) openCompose();
});
