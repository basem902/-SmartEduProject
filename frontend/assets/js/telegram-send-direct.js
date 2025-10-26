(function(){
  const $ = (sel) => document.querySelector(sel);

  let projectId = null;
  let serverBase = null;

  document.addEventListener('DOMContentLoaded', () => {
    // Read project_id
    const params = new URLSearchParams(window.location.search);
    projectId = params.get('project_id');
    if(!projectId){
      alert('معرف المشروع مفقود');
      window.location.href = '/pages/dashboard.html';
      return;
    }

    // Compute base URLs
    const apiBase = (typeof API_BASE !== 'undefined' && API_BASE) ? API_BASE : 'http://127.0.0.1:8000/api';
    serverBase = apiBase.replace(/\/?api\/?$/, '');

    // Auth check: require token
    const tokenCheck = getToken();
    if (!tokenCheck) {
      try { console.warn('No access_token in storage; redirecting to login'); } catch {}
      const redirect = encodeURIComponent(location.pathname + location.search);
      location.href = `/pages/login.html?redirect=${redirect}`;
      return;
    }

    // Wire events
    $('#sendBtn').addEventListener('click', sendNow);

    // Load project basic info
    loadProject();
  });

  async function loadProject(){
    try{
      const token = getToken();
      const res = await fetch(`${serverBase}/api/projects/${projectId}/detail/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if(!res.ok){
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      // Fill UI
      $('#pTitle').textContent = data.title || '-';
      $('#pSubject').textContent = data.subject || '-';
      const sectionsCount = (data.sections || []).length;
      $('#pSections').textContent = `${sectionsCount} شعبة`;
    }catch(err){
      console.error('Load project error:', err);
      alert('فشل تحميل بيانات المشروع');
    }
  }

  async function sendNow(){
    const pin = document.getElementById('optPin').checked;
    const files = document.getElementById('optFiles').checked;

    toggleLoading(true);
    try{
      const token = getToken();
      const url = `${serverBase}/api/projects/${projectId}/send-telegram/`;
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          send_files: files,
          pin_message: pin
        })
      });

      const text = await res.text();
      let data;
      try { data = JSON.parse(text); } catch { data = { error: text }; }

      if(!res.ok){
        throw new Error(data.error || text || 'HTTP Error');
      }

      renderResult(data.telegram || {});
    }catch(err){
      console.error('Send error:', err);
      showResultError(err.message || String(err));
    }finally{
      toggleLoading(false);
    }
  }

  function toggleLoading(flag){
    $('#loading').style.display = flag ? 'flex' : 'none';
  }

  function showResultError(message){
    $('#resultCard').style.display = 'block';
    $('#summary').innerHTML = `<span class="err">❌ ${escapeHtml(message)}</span>`;
    $('#details').innerHTML = '';
  }

  function renderResult(telegram){
    const success = Array.isArray(telegram.success) ? telegram.success : [];
    const failed = Array.isArray(telegram.failed) ? telegram.failed : [];
    const total = Number.isFinite(telegram.total) ? telegram.total : (success.length + failed.length);

    $('#resultCard').style.display = 'block';
    $('#summary').innerHTML = `
      <span class="ok">تم الإرسال:</span> ${success.length}
      <span class="muted"> | </span>
      <span class="err">فشل:</span> ${failed.length}
      <span class="muted"> | </span>
      <span>المجموع:</span> ${total}
    `;

    const details = [];
    if(success.length){
      details.push(`<div>✅ تم الإرسال إلى:</div>`);
      success.forEach(s => {
        details.push(`<div>• ${escapeHtml(s.section_name || String(s.section_id))} <span class="muted">${s.message_id ? `(message_id: ${s.message_id})` : ''}</span></div>`);
      });
    }
    if(failed.length){
      details.push(`<div style="margin-top:8px">⚠️ لم يتم الإرسال:</div>`);
      failed.forEach(f => {
        details.push(`<div>• ${escapeHtml(f.section_name || String(f.section_id))} — <span class="err">${escapeHtml(asText(f.error))}</span></div>`);
      });
    }
    $('#details').innerHTML = details.join('') || '<div class="muted">لا توجد تفاصيل</div>';
  }

  function asText(v){
    if(typeof v === 'string') return v;
    try { return JSON.stringify(v); } catch { return String(v); }
  }
  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
  }

  function getToken(){
    try{
      return localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || '';
    }catch{ return ''; }
  }
})();
