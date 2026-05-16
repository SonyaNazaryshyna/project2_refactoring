(function() {
  const saved = localStorage.getItem('whispr-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
})();

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('theme-toggle');
  if (!btn) return;
  const update = () => {
    const t = document.documentElement.getAttribute('data-theme');
    btn.title = t === 'dark' ? 'Світла тема' : 'Темна тема';
  };
  update();
  btn.addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('whispr-theme', next);
    update();
  });
});
