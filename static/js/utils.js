function getCookie(name) {
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return v ? decodeURIComponent(v.pop()) : null;
}
async function apiCall(path, opts={}) {
  const token = getCookie('access_token') || localStorage.getItem('access_token');
  const headers = {'Content-Type':'application/json'};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const r = await fetch(path, {...opts, headers});
  const data = await r.json().catch(()=>({}));
  if (!r.ok) throw {status:r.status, message:data.message||data.detail||'Помилка'};
  return data;
}
let _tt;
function showToast(msg, type='success') {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.className = `toast ${type}`;
  clearTimeout(_tt);
  _tt = setTimeout(() => el.classList.add('hidden'), 2800);
}
