(function(){
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  let projectId = null;

  document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    projectId = params.get('project_id');
    if (!projectId) {
      alert('المعرف project_id مفقود في العنوان');
      window.location.href = '/pages/dashboard.html';
      return;
    }

    $('#reloadBtn').addEventListener('click', loadStatus);
    loadStatus();
  });

  async function loadStatus(){
    try{
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const apiBase = (typeof API_BASE !== 'undefined' && API_BASE) ? API_BASE : 'http://127.0.0.1:8000/api';
      const serverBase = apiBase.replace(/\/?api\/?$/, '');
      const url = `${serverBase}/api/projects/${projectId}/telegram/bot-status/`;

      const res = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if(!res.ok){
        const txt = await res.text();
        throw new Error(`HTTP ${res.status}: ${txt}`);
      }
      const data = await res.json();
      renderSummary(data.summary || {});
      renderRows(data.results || []);
    }catch(err){
      console.error('Bot status error:', err);
      alert('فشل فحص حالة البوت:\n' + (err.message || err));
    }finally{
      setLoading(false);
    }
  }

  function setLoading(flag){
    const btn = $('#reloadBtn');
    if(flag){
      btn.disabled = true;
      btn.textContent = '... جارِ الفحص';
    }else{
      btn.disabled = false;
      btn.textContent = 'إعادة الفحص';
    }
  }

  function renderSummary(s){
    $('#c_total').textContent = s.total_sections ?? '-';
    $('#c_with').textContent = s.with_group ?? '-';
    $('#c_added').textContent = s.bot_added ?? '-';
    $('#c_admin').textContent = s.bot_admin ?? '-';
    $('#c_missing').textContent = s.missing_group ?? '-';
  }

  function badge(val, typeTrue='ok', typeFalse='warn'){
    const ok = Boolean(val);
    const cls = ok ? typeTrue : typeFalse;
    const txt = ok ? 'نعم' : 'لا';
    return `<span class="badge ${cls}">${txt}</span>`;
  }

  function renderRows(items){
    const tbody = $('#rows');
    tbody.innerHTML = '';
    const empty = $('#empty');

    if(!items.length){
      empty.style.display = 'block';
      return;
    }
    empty.style.display = 'none';

    for(const it of items){
      const tr = document.createElement('tr');
      const chatId = it.chat_id != null ? `<code>${it.chat_id}</code>` : '<span class="muted">-</span>';
      const invite = it.invite_link ? `<a class="link" href="${it.invite_link}" target="_blank">فتح</a>` : '<span class="muted">-</span>';
      const status = it.bot_member_status ? `<span class="badge ${it.bot_member_status==='administrator'||it.bot_member_status==='creator'?'ok':'warn'}">${it.bot_member_status}</span>` : '<span class="muted">-</span>';
      const added = badge(it.is_bot_added, 'ok', 'err');
      const admin = badge(it.is_bot_admin, 'ok', 'warn');
      const members = (it.members_count != null) ? it.members_count : '<span class="muted">-</span>';
      const err = it.error ? `<span class="badge err">${escapeHtml(asText(it.error))}</span>` : '<span class="muted">-</span>';

      tr.innerHTML = `
        <td>${escapeHtml(it.section_name || '')}</td>
        <td>${chatId}</td>
        <td>${invite}</td>
        <td>${status}</td>
        <td>${added}</td>
        <td>${admin}</td>
        <td>${members}</td>
        <td>${err}</td>
      `;
      tbody.appendChild(tr);
    }
  }

  function asText(v){
    if(typeof v === 'string') return v;
    try{ return JSON.stringify(v); }catch{ return String(v); }
  }

  function escapeHtml(s){
    return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  }
})();
