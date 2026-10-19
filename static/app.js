(() => {
  'use strict';
  const $ = (selector, parent = document) => parent.querySelector(selector);
  const app = $('#app');
  const esc = (value = '') => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const icons = {
    grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    tickets: '<path d="M8 4h11a2 2 0 0 1 2 2v4a2 2 0 0 0 0 4v4a2 2 0 0 1-2 2H8a2 2 0 0 0-2-2 2 2 0 0 0-2-2V8a2 2 0 0 0 2-2 2 2 0 0 0 2-2Z"/><path d="M13 5v14" stroke-dasharray="2 3"/>',
    sparkle: '<path d="m12 3 1.9 6.1L20 11l-6.1 1.9L12 19l-1.9-6.1L4 11l6.1-1.9L12 3Z"/><path d="m19 17 .7 2.3L22 20l-2.3.7L19 23l-.7-2.3L16 20l2.3-.7L19 17Z"/>',
    chart: '<path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6" rx=".5"/><rect x="13" y="8" width="3" height="10" rx=".5"/><rect x="19" y="5" width="2" height="13" rx=".5"/>',
    help: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 4.2 1.8c-1.1 1-1.7 1.2-1.7 2.7M12 17h.01"/>',
    logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    arrow: '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    check: '<path d="m5 12 4 4L19 6"/>',
    menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
    download: '<path d="M12 3v13m-5-5 5 5 5-5M5 20h14"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    pin: '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2"/>',
    close: '<path d="M5 5l14 14M19 5 5 19"/>',
    activity: '<path d="M2 12h5l3-8 4 16 3-8h5"/>',
    alert: '<path d="M12 3 2 21h20L12 3Z"/><path d="M12 9v5M12 17h.01"/>',
    filter: '<path d="M4 7h16M7 12h10M10 17h4"/>',
    book: '<path d="M4 5a3 3 0 0 1 3-3h14v17H7a3 3 0 0 0-3 3V5Zm0 14a3 3 0 0 1 3-3h14"/>',
    lock: '<rect x="4" y="10" width="16" height="12" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    message: '<path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.5 9 9 0 0 1-4-.9L3 21l1.9-5.5a9 9 0 1 1 16.1-4Z"/>',
  };
  const icon = (name, size) => `<svg ${size ? `width="${size}" height="${size}"` : ''} aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${icons[name] || icons.grid}</svg>`;
  const state = { user: null, csrf: '', meta: {demo_mode: false}, view: 'overview', filters: {search:'', status:'All',category:'All',priority:'All',page:1}, roleAccounts: {student:['student@campusrelay.demo','Student@2026!'],staff:['staff@campusrelay.demo','Staff@2026!'],admin:['admin@campusrelay.demo','Admin@2026!']}, pendingAI: null, modalOpen: false, authTab:'login', currentTicket:null };
  const dateText = d => { if (!d) return '—'; const dt = new Date(d); return Number.isNaN(+dt) ? '—' : dt.toLocaleDateString(undefined, {month:'short',day:'numeric',year:'numeric'}); };
  const dateTime = d => { if (!d) return '—'; const dt = new Date(d); return Number.isNaN(+dt) ? '—' : dt.toLocaleString(undefined, {dateStyle:'medium',timeStyle:'short'}); };
  const slug = value => String(value).toLowerCase().replace(/\s+/g,'');
  const badge = status => `<span class="badge ${slug(status)}">${esc(status)}</span>`;
  const pri = level => `<span class="priority ${slug(level)}">${esc(level)}</span>`;
  const titleText = view => ({overview:'Overview',tickets:'Requests',ai:'AI triage',insights:'Analytics',help:'Guide'})[view] || 'Workspace';
  const loading = () => `<div class="panel empty"><div class="loader"></div><p>Loading your workspace…</p></div>`;
  const empty = (title, note, action = '') => `<div class="empty"><div class="empty-icon">${icon('tickets')}</div><h3>${esc(title)}</h3><p>${esc(note)}</p>${action}</div>`;
  const emailValid = x => /^\S+@\S+\.\S+$/.test(x);

  async function api(url, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const headers = {'Accept':'application/json',...(options.headers || {})};
    if (method !== 'GET') { headers['Content-Type'] = 'application/json'; headers['X-CSRF-Token'] = state.csrf; }
    let response;
    try { response = await fetch(url, { ...options, method, headers, credentials:'same-origin' }); }
    catch { throw new Error('Cannot connect to the server. Check your connection and try again.'); }
    const body = response.headers.get('content-type')?.includes('application/json') ? await response.json() : null;
    if (!response.ok) {
      if (response.status === 401 && url !== '/api/auth/login') { state.user = null; state.csrf = ''; renderLogin(); }
      const issue = body?.errors?.[0]?.message;
      throw new Error(issue || body?.detail || `Request failed (${response.status}).`);
    }
    return body;
  }

  function toast(message, error = false) {
    const region = $('#toast-region');
    const element = document.createElement('div');
    element.className = `toast${error ? ' error' : ''}`;
    element.innerHTML = icon(error ? 'alert' : 'check') + `<span>${esc(message)}</span>`;
    region.appendChild(element);
    setTimeout(() => element.remove(), 4300);
  }
  function formError(message) { const e = $('#auth-error'); if (e) { e.textContent = message; e.classList.add('show'); } else toast(message,true); }

  async function boot() {
    try { state.meta = await api('/api/meta'); } catch { state.meta = {demo_mode:false}; }
    try {
      const auth = await api('/api/auth/me');
      state.user = auth.user; state.csrf = auth.csrf_token;
      renderShell(); navigate('overview');
    } catch { renderLogin(); }
  }

  const logo = (compact = false) => `<div class="logo-wrap"><span class="logo-mark" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none"><path d="M8 8h10a6 6 0 0 1 0 12H8V8Z" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/><path d="M24 24H14a6 6 0 0 1 0-12h10v12Z" fill="currentColor" opacity=".35"/></svg></span><span class="logo-text">CampusRelay${compact ? '' : '<small>Service desk</small>'}</span></div>`;

  function renderLogin() {
    closeModal(); state.user = null;
    const login = state.authTab === 'login';
    app.innerHTML = `<div class="auth-shell">
      <section class="auth-side">
        <div class="auth-card">
          <div class="auth-brand">${logo()}</div>
          <div class="auth-content">
            <div class="auth-overline">CAMPUS SERVICE PORTAL</div>
            <h1>${login ? 'Welcome back' : 'Create your account'}</h1>
            <p class="intro">${login ? 'Sign in to track your requests and stay informed.' : 'It only takes a minute to get started.'}</p>
            <div class="tab-switch" role="tablist" aria-label="Authentication"><button type="button" class="${login ? 'active':''}" data-auth-tab="login" role="tab" aria-selected="${login}">Sign in</button><button type="button" class="${!login ? 'active':''}" data-auth-tab="register" role="tab" aria-selected="${!login}">Create account</button></div>
            <div id="auth-error" class="auth-error" role="alert"></div>
            <form id="auth-form">
              ${!login ? `<div class="field"><label for="name">Full name</label><input required id="name" name="name" minlength="2" maxlength="80" autocomplete="name" placeholder="e.g. Samira Rahman"></div>` : ''}
              <div class="field"><label for="email">Email address</label><input required id="email" name="email" type="email" maxlength="254" autocomplete="email" placeholder="you@university.edu"></div>
              <div class="field"><label for="password">Password</label><div class="password-wrap"><input required id="password" name="password" type="password" ${login ? '' : 'minlength="10"'} maxlength="128" autocomplete="${login ? 'current-password':'new-password'}" placeholder="${login ? 'Enter your password' : 'Create a strong password'}"><button type="button" class="password-toggle" data-action="toggle-password" aria-label="Show password">Show</button></div></div>
              ${!login ? `<p class="form-hint">At least 10 characters, with upper and lower case letters and a number.</p>` : ''}
              <button class="primary-btn full auth-submit" type="submit" id="submit-auth">${login ? 'Sign in' : 'Create account'} ${icon('arrow')}</button>
            </form>
            ${login && state.meta.demo_mode ? `<div class="auth-divider">Explore with a demo account</div><div class="demo-accounts">
              <button type="button" class="demo-choice" data-demo="student"><span>${icon('user')}</span><strong>Student</strong><small>Submit requests</small></button>
              <button type="button" class="demo-choice" data-demo="staff"><span>${icon('tickets')}</span><strong>Staff</strong><small>Manage requests</small></button>
              <button type="button" class="demo-choice" data-demo="admin"><span>${icon('shield')}</span><strong>Admin</strong><small>Review activity</small></button>
            </div><p class="demo-hint">Sample accounts and fictional data for demonstration only.</p>` : ''}
          </div>
          <div class="auth-bottom">Need help? <span>Contact your campus service team.</span></div>
        </div>
      </section>
      <section class="auth-story" aria-label="Product preview">
        <div class="story-header"><span class="story-brand-label">A simpler way to get things fixed.</span><span class="story-preview-label">PRODUCT PREVIEW</span></div>
        <div class="story-main"><div class="story-copy"><span class="story-kicker"><span></span> Built around the issues that matter</span><h2>Less follow-up.<br>More progress.</h2><p>From broken equipment to campus Wi-Fi, every request has a clear owner and a visible next step.</p></div>
          <div class="preview-board" aria-hidden="true"><div class="preview-toolbar"><div class="preview-toolbar-title"><span class="preview-mark">${icon('tickets')}</span><span><b>Recent requests</b><small>Your campus, all in one place</small></span></div><span class="preview-dots">•••</span></div>
          <div class="preview-row"><span class="preview-symbol purple">${icon('tickets')}</span><div><strong>Projector not connecting in Room 204</strong><small>Facilities · 3 hours ago</small></div><span class="preview-status progress">In progress</span></div>
          <div class="preview-row"><span class="preview-symbol blue">${icon('activity')}</span><div><strong>Wi-Fi outage near the library</strong><small>IT support · Yesterday</small></div><span class="preview-status solved">Resolved</span></div>
          <div class="preview-row"><span class="preview-symbol orange">${icon('pin')}</span><div><strong>Water dispenser needs repair</strong><small>Facilities · 2 days ago</small></div><span class="preview-status open-preview">Open</span></div>
          <div class="preview-footer"><div class="preview-avatars"><i>A</i><i>M</i><i>R</i></div><span>Everyone knows what happens next.</span></div></div>
        </div><div class="story-bottom">REPORT <span>→</span> TRACK <span>→</span> RESOLVE</div>
      </section>
    </div>`;
  }

  function renderShell() {
    if (!state.user) return renderLogin();
    const nav = [['overview','grid','Overview'],['tickets','tickets','Requests'],['ai','sparkle','AI triage'],['insights','chart','Analytics'],['help','help','Help & guide']];
    app.innerHTML = `<div class="shell">
      <div class="mobile-backdrop" data-action="close-menu" aria-hidden="true"></div>
      <aside id="sidebar" class="sidebar" aria-label="Main navigation">
        <div class="sidebar-brand">${logo()}</div>
        <div class="sidebar-context"><span class="context-dot"></span><span>Campus workspace</span>${icon('arrow')}</div>
        <div class="sidebar-label">WORKSPACE</div><nav aria-label="Sections">${nav.map(([key, glyph, text]) => `<button class="nav-item${state.view === key ? ' active':''}" data-nav="${key}" type="button" ${state.view===key?'aria-current="page"':''}>${icon(glyph)} <span>${text}</span></button>`).join('')}</nav>
        <div class="sidebar-spacer"></div>
        <div class="sidebar-tip"><span class="tip-symbol">${icon('help')}</span><div><strong>Need a hand?</strong><p>Find help with requests, routing and updates.</p><button type="button" data-nav="help">View quick guide ${icon('arrow')}</button></div></div>
        <div class="sidebar-footer"><div class="user-block"><span class="avatar">${esc(state.user.name.split(' ').map(x=>x[0]).slice(0,2).join(''))}</span><span class="user-meta"><strong>${esc(state.user.name)}</strong><small>${esc(state.user.role)} account</small></span><span class="user-menu-icon" aria-hidden="true">${icon('check')}</span></div>
        <button class="nav-item signout" data-action="logout" type="button">${icon('logout')} <span>Sign out</span></button></div>
      </aside>
      <main class="main"><header class="topbar"><div class="topbar-left"><button type="button" class="mobile-menu icon-btn" data-action="menu" aria-label="Open navigation" aria-expanded="false">${icon('menu')}</button><div class="topbar-title"><span class="topbar-section">CampusRelay</span><span class="crumb-chevron">/</span><span id="breadcrumb">Overview</span></div></div>
        <div class="topbar-actions"><span class="topbar-date">${new Date().toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'})}</span><span class="topbar-divider" aria-hidden="true"></span><button class="primary-btn" data-action="new" type="button">${icon('plus')} <span>New request</span></button></div></header>
      <div class="workspace" id="workspace" aria-live="polite"></div><footer class="main-footer"><span>CampusRelay <span class="footer-dot">·</span> Service desk</span><span>Designed for clearer campus operations</span></footer></main></div>`;
  }

  function heading(kicker,title,summary,buttons='') {
    return `<header class="page-header"><div><span class="page-kicker">${esc(kicker)}</span><h1>${esc(title)}</h1><p>${esc(summary)}</p></div>${buttons ? `<div class="action-group">${buttons}</div>`:''}</header>`;
  }

  async function navigate(view) {
    if (!state.user) return;
    state.view = view;
    $('#sidebar')?.classList.remove('open');
    document.body.classList.remove('menu-open');$('.mobile-menu')?.setAttribute('aria-expanded','false');
    $$('#sidebar .nav-item[data-nav]').forEach(x=>{x.classList.toggle('active', x.dataset.nav === view); if(x.dataset.nav===view)x.setAttribute('aria-current','page'); else x.removeAttribute('aria-current');});
    if ($('#breadcrumb')) $('#breadcrumb').textContent = titleText(view);
    const target = $('#workspace');
    if (!target) return;
    target.innerHTML = loading();
    window.scrollTo({top:0,behavior:'auto'});
    try {
      if (view === 'overview') await renderOverview();
      else if (view === 'tickets') await renderTickets();
      else if (view === 'ai') await renderAI();
      else if (view === 'insights') await renderInsights();
      else if (view === 'help') renderGuide();
    } catch(e) { if (state.user) target.innerHTML = empty('We could not load this view',e.message,`<button class="secondary-btn" data-nav="${esc(view)}">Retry</button>`); }
  }

  function metricsCards(data) {
    const items = [
      ['Total requests',data.total,'Requests logged to date','tickets',''],
      ['Open requests',(data.status_counts.Open || 0) + (data.status_counts.Reopened || 0),'Not yet in progress','clock','blue'],
      ['Resolved',data.resolved,'Marked complete by staff','check','violet'],
      ['High priority',data.open_high_priority,'Unresolved requests','alert','yellow'],
    ];
    return `<div class="cards">${items.map(([title,value,caption,glyph,tone]) => `<article class="metric-card"><div class="metric-top">${esc(title)} <span class="metric-icon ${tone}">${icon(glyph)}</span></div><b class="metric-num">${value.toLocaleString()}</b><div class="metric-note">${esc(caption)}</div></article>`).join('')}</div>`;
  }

  const statusColors = {'Open':'#4e79d9','In Progress':'#d6a244','Resolved':'#2d9d79','Reopened':'#d07869'};
  function statusPanel(data) {
    const total = Math.max(1,data.total);
    let sum = 0;
    const segments = Object.entries(statusColors).map(([key,color]) => { const next = sum + 100*(data.status_counts[key]||0)/total; const seg=`${color} ${sum}% ${next}%`;sum=next;return seg; });
    if (sum < 100) segments.push(`#e7eaf1 ${sum}% 100%`);
    const gradient = `conic-gradient(${segments.join(',')})`;
    return `<section class="panel"><div class="panel-heading"><div><h2>Request status</h2><p>Current distribution across stages</p></div></div>
      <div class="donut-row"><div class="donut" id="status-donut"><div class="donut-inner"><b>${data.total}</b><small>Total issues</small></div></div>
        <div class="status-legend">${Object.entries(statusColors).map(([key,color])=>`<div class="legend-row"><span class="legend-label"><span class="color-dot" data-color="${key.replace(' ','_')}"></span>${esc(key)}</span><b>${data.status_counts[key] || 0}</b></div>`).join('')}</div></div>
      <p class="panel-footnote">Categories are assigned by people. AI suggestions never change a request automatically.</p></section>`;
  }
  function categoriesPanel(data) {
    const largest = Math.max(1,...Object.values(data.category_counts));
    return `<section class="panel"><div class="panel-heading"><div><h2>By category</h2><p>Requests grouped by type</p></div></div>
      ${Object.entries(data.category_counts).map(([key,count]) => `<div class="category-row"><span>${esc(key)}</span><div class="category-track"><div class="category-fill" data-progress="${100*count/largest}"></div></div><b>${count}</b></div>`).join('')}</section>`;
  }
  function graphPanel(data) {
    const max = Math.max(1,...data.trend.map(x=>x.count));
    return `<section class="panel"><div class="panel-heading"><div><h2>Reporting activity</h2><p>New requests over the last 7 days</p></div></div>
      <div class="trend-bars" aria-label="New issues over last seven days">${data.trend.map(day=>`<div class="trend-day" title="${esc(day.date)}: ${day.count} new reports"><div class="trend-column ${day.count===0?'zero':''}" data-height="${Math.max(2,day.count/max*88)}"></div><small>${new Date(`${day.date}T12:00:00Z`).toLocaleDateString(undefined,{weekday:'short'})}</small></div>`).join('')}</div></section>`;
  }
  function paintCharts() {
    $$('.category-fill').forEach(el=>el.style.width = `${Number(el.dataset.progress)}%`);
    $$('.trend-column').forEach(el=>el.style.height = `${Number(el.dataset.height)}%`);
    const donut=$('#status-donut');
    if (donut) {
      const p=state.latestDashboard;
      const denominator=Math.max(1,p.total);let start=0;const steps=[];
      Object.entries(statusColors).forEach(([key,color])=>{const end=start+(p.status_counts[key]||0)*100/denominator; steps.push(`${color} ${start}% ${end}%`);start=end;});
      if (start<100)steps.push(`#e7eaf1 ${start}% 100%`);
      donut.style.background=`conic-gradient(${steps.join(',')})`;
    }
    $$('.color-dot').forEach(el=>{ const key=el.dataset.color.replace('_',' ');el.style.background = statusColors[key] || '#4e79d9'; });
  }
  function recentPanel(data) {
    return `<section class="panel"><div class="panel-heading"><div><h2>Recent requests</h2><p>Latest submissions in your workspace</p></div><button class="inline-link" data-nav="tickets">View all ${icon('arrow')}</button></div>
      <div class="recent-list">${data.recent.length ? data.recent.map(item=> `<button class="recent-item" data-ticket="${item.id}"><span class="recent-icon">${icon('tickets')}</span><span class="recent-info"><strong>${esc(item.title)}</strong><small>${esc(item.ref)} · ${dateText(item.created_at)}</small></span>${badge(item.status)}</button>`).join('') : empty('Nothing here yet','Your reports will appear here after submission.')}</div></section>`;
  }
  async function renderOverview() {
    const data=await api('/api/dashboard'); if (state.view!=='overview') return;
    state.latestDashboard=data;
    const staff = state.user.role !== 'student';
    const needsAction = data.open_high_priority;
    const intro = staff ? 'A clear view of what your campus team is working on.' : 'Stay on top of the reports you have submitted.';
    const note = staff
      ? (needsAction ? `${needsAction} high-priority request${needsAction === 1?'':'s'} need your team's attention.` : 'No high-priority requests are waiting right now.')
      : 'Notice a problem around campus? Submit it and track its progress here.';
    $('#workspace').innerHTML = heading('YOUR WORKSPACE', `Good ${new Date().getHours()<12?'morning':new Date().getHours()<17?'afternoon':'evening'}, ${state.user.name.split(' ')[0]}`,intro)
      + `<div class="overview-callout"><div class="callout-symbol">${icon(staff && needsAction ? 'alert' : 'check')}</div><div class="callout-text"><strong>${staff ? (needsAction ? 'Requires attention' : 'You’re all caught up on urgent requests') : 'A better campus starts with a report'}</strong><p>${esc(note)}</p></div><button class="secondary-btn" ${staff ? 'data-action="high-priority"' : 'data-action="new"'}>${staff ? 'Review requests' : 'Create request'} ${icon('arrow')}</button></div>`
      + metricsCards(data) + `<div class="two-col">${recentPanel(data)}${statusPanel(data)}</div><div class="two-col">${categoriesPanel(data)}${graphPanel(data)}</div>`;
    paintCharts();
  }

  function filterMarkup() {
    return `<div class="toolbar"><div class="search-wrap">${icon('search')}<input type="search" id="ticket-search" class="search-input" value="${esc(state.filters.search)}" placeholder="Search title, reference or location…" aria-label="Search tickets"></div>
    <select id="ticket-status" class="filter-select" aria-label="Filter by status">${['All','Open','In Progress','Resolved','Reopened'].map(x=>`<option ${state.filters.status===x?'selected':''} value="${x}">${x==='All'?'All statuses':x}</option>`).join('')}</select>
    <select id="ticket-category" class="filter-select" aria-label="Filter by category">${['All',...state.meta.categories || ['Facilities','IT','Safety','Academic','Transport']].map(x=>`<option ${state.filters.category===x?'selected':''} value="${x}">${x==='All'?'All categories':x}</option>`).join('')}</select>
    <select id="ticket-priority" class="filter-select" aria-label="Filter by priority">${['All','High','Medium','Low'].map(x=>`<option ${state.filters.priority===x?'selected':''} value="${x}">${x==='All'?'Any priority':x}</option>`).join('')}</select></div>`;
  }
  async function renderTickets() {
    const target=$('#workspace');
    target.innerHTML=heading('REQUEST MANAGEMENT','All requests',state.user.role==='student'?'Search, filter and follow the progress of requests you have submitted.':'Review and manage requests submitted across campus.')
      + filterMarkup() + `<section class="panel table-panel"><div class="table-heading"><div><h2>Request directory</h2><p>Select a request to view its details and activity.</p></div></div><div id="ticket-table">${loading()}</div></section>`;
    await loadTicketRows();
  }
  let ticketLoadSequence = 0;
  async function loadTicketRows() {
    const target=$('#ticket-table'); if (!target) return;
    const requestId=++ticketLoadSequence;
    if (target.querySelector('.table')) target.classList.add('is-updating');
    else target.innerHTML=loading();
    try {
      const f=state.filters;
      const params=new URLSearchParams({search:f.search,status:f.status,category:f.category,priority:f.priority,page:String(f.page),page_size:'8'});
      const result=await api(`/api/tickets?${params.toString()}`);
      if (requestId !== ticketLoadSequence || !$('#ticket-table') || state.view!=='tickets') return;
      target.classList.remove('is-updating');
      target.innerHTML=`<div class="table-wrap"><table class="table"><thead><tr><th>Request</th><th>Category</th><th>Priority</th><th>Status</th><th>Submitted</th><th>Assigned to</th></tr></thead><tbody>
        ${result.items.map(t=>`<tr><td><button class="ticket-link" data-ticket="${t.id}"><span class="ticket-title">${esc(t.title)}</span><span class="ref-text">${esc(t.ref)}</span></button></td>
          <td><span class="tag-category">${esc(t.category)}</span></td><td>${pri(t.priority)}</td><td>${badge(t.status)}</td><td>${dateText(t.created_at)}</td><td>${esc(t.assignee_name || 'Not assigned')}</td></tr>`).join('')}</tbody></table></div>
        ${result.items.length ? '' : empty('No matching requests','Try another search or change your filters.',`<button class="primary-btn" data-action="new">${icon('plus')} New request</button>`)}
        <div class="table-footer"><span>Showing ${result.items.length ? ((result.page-1)*8+1) : 0}–${Math.min(result.total,result.page*8)} of ${result.total} requests</span>
        <div class="pagination"><button data-page="${result.page-1}" ${result.page<=1?'disabled':''} aria-label="Previous page">‹</button><span>Page ${result.page} / ${result.pages}</span><button data-page="${result.page+1}" ${result.page>=result.pages?'disabled':''} aria-label="Next page">›</button></div></div>`;
    } catch(e) { if (requestId===ticketLoadSequence && $('#ticket-table')) {target.classList.remove('is-updating');target.innerHTML=empty('Could not load requests',e.message,`<button class="secondary-btn" data-action="reload-tickets">Retry</button>`);} }
  }

  async function renderAI() {
    const target=$('#workspace');
    target.innerHTML=heading('ASSISTED ROUTING','Triage assistant','Get a second opinion on category and urgency before filing a request.')
      + `<div class="ai-hero"><div class="ai-banner-icon">${icon('sparkle')}</div><div><span class="eyebrow">RECOMMENDATION TOOL</span><h2>The right category, without the guesswork.</h2><p>Describe a problem. The classifier offers a category and suggested priority; you always make the final choice.</p></div><span class="ai-hero-stamp">Human-reviewed</span></div>
      <div class="ai-grid"><section class="panel"><div class="panel-heading"><div><h2>Describe the issue</h2><p>Try 20 or more characters in English</p></div></div>
        <form id="ai-form"><div class="field"><label for="ai-text">What's happening?</label><textarea id="ai-text" required minlength="20" maxlength="2200" placeholder="Example: The campus Wi-Fi has stopped working in our lecture room and students cannot access assignments…" rows="7"></textarea></div><button type="submit" class="primary-btn" id="ai-submit">${icon('sparkle')} Analyze issue</button></form>
        <div class="separator"></div><div class="note">${icon('shield')} <strong>Human-in-the-loop.</strong> You can always correct the proposed category or priority when filing a report. Do not submit personal or confidential details to the demo.</div></section>
      <section class="panel"><div class="panel-heading"><div><h2>AI recommendation</h2><p>Predicted category, priority and model confidence</p></div></div><div id="ai-result">${empty('Ready when you are','Describe an issue on the left to see the classification, explanation and alternate predictions.')}</div></section></div>
      <section class="panel panel-gap" id="ai-metrics-panel"><div class="panel-heading"><div><h2>Model transparency</h2><p>Real holdout evaluation, scope and limitations</p></div></div>${loading()}</section>`;
    try {
      const m = await api('/api/ai/model-card');
      if (state.view !== 'ai' || !$('#ai-metrics-panel')) return;
      $('#ai-metrics-panel').innerHTML=`<div class="panel-heading"><div><h2>Model transparency</h2><p>Separate evaluation examples, not training accuracy</p></div></div><div class="mini-stat-grid"><div class="mini-stat"><b>${Math.round(m.accuracy*100)}%</b><span>Synthetic holdout accuracy</span></div><div class="mini-stat"><b>${Math.round(m.macro_f1*100)}%</b><span>Macro F1 score</span></div><div class="mini-stat"><b>${m.train_examples}</b><span>Training examples</span></div><div class="mini-stat"><b>${m.holdout_examples}</b><span>Separate test examples</span></div></div><p class="form-note">${esc(m.limitations)} No guarantee of performance on real-world requests.</p>`;
    } catch(e) {if ($('#ai-metrics-panel')) $('#ai-metrics-panel').innerHTML=empty('Model report unavailable',e.message);}
  }
  function aiResult(ai, lab=false) {
    return `<div class="prediction"><span class="page-kicker">Most likely category</span><div class="prediction-row"><span class="prediction-category">${esc(ai.category)}</span><span class="tag-category">${Math.round(ai.confidence*100)}% confidence</span></div>
      <div class="prob-bar"><div class="prob-fill" data-progress="${ai.confidence*100}"></div></div>
      <p class="reason">Suggested priority: ${pri(ai.priority)}</p>
      <p class="reason">${esc(ai.explanation)}</p>
      ${ai.low_confidence?`<div class="notice">Low confidence. Check the category yourself before submitting.</div>`:''}
      <div class="separator"></div><span class="detail-label">Top alternatives</span>
      ${ai.alternatives.map(x=>`<div class="legend-row alt-row"><span class="legend-label">${esc(x.category)}</span><b>${Math.round(x.probability*100)}%</b></div>`).join('')}
      ${lab ? `<button type="button" data-action="ai-to-ticket" class="secondary-btn full ai-submit-margin">${icon('arrow')} Create issue with this suggestion</button>`:''}</div>`;
  }
  async function analyzeText(text, targetId) {
    const target=$(targetId); if (!target) return null;
    target.innerHTML=`<div class="empty"><div class="loader"></div><p>Analyzing issue text…</p></div>`;
    try {
      const ai=await api('/api/ai/suggest',{method:'POST',body:JSON.stringify({text})});
      const now=$(targetId); if (now) {now.innerHTML=aiResult(ai,targetId==='#ai-result'); $$('.prob-fill',now).forEach(x=>x.style.width=`${Number(x.dataset.progress)}%`);}
      state.pendingAI=ai;
      return ai;
    } catch(e) {if ($(targetId)) $(targetId).innerHTML=`<div class="notice">${esc(e.message)}</div>`;toast(e.message,true);return null;}
  }

  async function renderInsights() {
    const data=await api('/api/dashboard'); if (state.view!=='insights') return;
    state.latestDashboard=data;
    const rate=data.total ? Math.round(data.resolved/data.total*100) : 0;
    $('#workspace').innerHTML=heading('SERVICE OVERVIEW','Analytics',data.scope==='own'?'Analytics are limited to issues you personally reported.':'Service-level patterns across every reported issue.',state.user.role==='student'?'':`<a class="secondary-btn" href="/api/export/tickets.csv">${icon('download')} Export CSV</a>`)
      + `<section class="insights-callout"><span class="insights-rate">${rate}%</span><div><strong>Requests resolved</strong><p>${data.resolved} of ${data.total} requests have been marked resolved by staff. Metrics come directly from the database.</p></div>${icon('activity')}</section>`
      + metricsCards(data) + `<div class="two-col">${categoriesPanel(data)}${statusPanel(data)}</div><div class="two-col">${graphPanel(data)}${recentPanel(data)}</div>`;
    paintCharts();
  }

  function renderGuide() {
    $('#workspace').innerHTML=heading('GETTING STARTED','How it works','A short walkthrough for students, staff, and live reviewers.')
      + `<div class="steps"><article class="step-card"><div class="step-num">01</div><h3>Report an issue</h3><p>Use “Report an issue” anywhere in your workspace. Add a descriptive title, location and details. Correct any AI suggestions as needed.</p><button class="inline-link" data-action="new">Start a report ${icon('arrow')}</button></article>
      <article class="step-card"><div class="step-num">02</div><h3>Follow progress</h3><p>Open the issue tracker to search tickets, read activity history and post an update. Students only see their own reports.</p><button class="inline-link" data-nav="tickets">View issue tracker ${icon('arrow')}</button></article>
      <article class="step-card"><div class="step-num">03</div><h3>Resolve & review</h3><p>Staff can assign tickets and move them through a controlled workflow. Resolve an issue, or reopen it when it returns.</p><button class="inline-link" data-nav="insights">See insights ${icon('arrow')}</button></article></div>
      <section class="panel panel-gap"><div class="panel-heading"><h2>The ticket lifecycle</h2></div><div class="workflow-list"><span>Open</span>${icon('arrow')}<span>In Progress</span>${icon('arrow')}<span>Resolved</span>${icon('arrow')}<span>Reopened</span>${icon('arrow')}<span>In Progress</span></div><p class="form-note">All status changes require staff privileges, are validated by the server and leave an activity record.</p></section>
      <div class="help-grid"><section class="panel"><div class="panel-heading"><h2>${icon('lock')} Security & privacy</h2></div><p class="small muted">Passwords are hashed with PBKDF2. Sessions live in HttpOnly cookies; write operations require CSRF tokens. Student report access is owner-only. Validation and authorization happen on the server.</p></section>
      <section class="panel"><div class="panel-heading"><h2>${icon('sparkle')} AI transparency</h2></div><p class="small muted">A TF-IDF and logistic regression classifier trained on fictional English examples suggests a category. A visible keyword policy recommends urgency. Accuracy refers only to synthetic test samples; decisions are always editable by people.</p><button class="inline-link" data-nav="ai">Try the AI tool ${icon('arrow')}</button></section></div>`;
  }

  function showModal(html, wide = false) {
    closeModal();state.focusBeforeModal=document.activeElement;
    const overlay = document.createElement('div'); overlay.className='overlay';overlay.id='overlay';
    overlay.innerHTML=`<div class="modal${wide?' wide':''}" role="dialog" aria-modal="true" aria-label="Issue dialog">${html}</div>`;
    document.body.appendChild(overlay);document.body.style.overflow='hidden';state.modalOpen=true;
    $('.modal input, .modal button, .modal textarea')?.focus();
  }
  function closeModal() {const hadModal=!!$('#overlay');$('#overlay')?.remove();document.body.style.overflow='';state.modalOpen=false;state.currentTicket=null;if(hadModal && state.focusBeforeModal?.isConnected)state.focusBeforeModal.focus();}
  const categoryOptions = ['Facilities','IT','Safety','Academic','Transport'].map(c=>`<option value="${c}">${c}</option>`).join('');
  const priorityOptions = ['Low','Medium','High'].map(p=>`<option value="${p}">${p}</option>`).join('');
  function newTicket(initialText='') {
    showModal(`<div class="modal-head"><div><span class="page-kicker">New service request</span><h2>Report an issue</h2><p class="small muted">Give the campus team enough detail to help.</p></div><button class="icon-btn" data-action="close" aria-label="Close">${icon('close')}</button></div>
      <form id="ticket-form"><div class="modal-body"><div class="field"><label for="new-title">Short, clear title *</label><input id="new-title" name="title" minlength="8" maxlength="120" required placeholder="e.g. Wi-Fi unavailable in Lab 3"></div>
        <div class="field"><label for="new-description">What's the problem? *</label><textarea id="new-description" name="description" minlength="20" maxlength="2000" required placeholder="Describe what happened, the impact, and when you noticed it…">${esc(initialText)}</textarea></div>
        <div class="field"><label for="new-location">Campus location *</label><input id="new-location" name="location" minlength="3" maxlength="120" required placeholder="e.g. Science Building, Level 2"></div>
        <div class="field"><button type="button" class="secondary-btn" data-action="suggest-ticket">${icon('sparkle')} Suggest category & priority</button></div>
        <div id="new-prediction"></div>
        <div class="field-grid"><div class="field"><label for="new-category">Category * <small>Editable</small></label><select id="new-category" name="category" required>${categoryOptions}</select></div>
        <div class="field"><label for="new-priority">Priority * <small>Editable</small></label><select id="new-priority" name="priority" required>${priorityOptions}</select></div></div>
        <p class="form-note">The AI is advisory. You choose the final category and urgency, and staff make all status decisions.</p>
      </div><div class="modal-foot"><button type="button" class="ghost-btn" data-action="close">Cancel</button><button type="submit" class="primary-btn" id="ticket-submit">${icon('plus')} Submit report</button></div></form>`,true);
    if (state.pendingAI && initialText) {$('#new-category').value=state.pendingAI.category;$('#new-priority').value=state.pendingAI.priority;}
  }

  async function openTicket(id) {
    showModal(`<div class="modal-head"><h2>Loading report…</h2><button class="icon-btn" data-action="close" aria-label="Close">${icon('close')}</button></div><div class="modal-body">${loading()}</div>`,true);
    try {
      const data=await api(`/api/tickets/${id}`);
      if (!state.modalOpen) return;
      state.currentTicket=data;
      const t=data.ticket, staff=state.user.role!=='student';
      $('#overlay .modal').innerHTML=`<div class="modal-head"><div><span class="page-kicker">${esc(t.ref)} · ${esc(t.category)}</span><h2>${esc(t.title)}</h2><div class="action-group">${badge(t.status)} ${pri(t.priority)}</div></div><button class="icon-btn" data-action="close" aria-label="Close">${icon('close')}</button></div>
        <div class="modal-body"><div class="detail-brief"><div><span class="detail-label">Reported by</span><span class="detail-value">${esc(t.creator_name)}</span></div><div><span class="detail-label">Submitted</span><span class="detail-value">${dateTime(t.created_at)}</span></div>
        <div><span class="detail-label">Location</span><span class="detail-value">${esc(t.location)}</span></div><div><span class="detail-label">Assigned staff</span><span class="detail-value">${esc(t.assignee_name || 'Not assigned')}</span></div></div>
        <hr class="separator"><span class="detail-label">Description</span><p class="small detail-desc">${esc(t.description)}</p>
        <div class="note">${icon('sparkle')} ML suggested <strong>${esc(t.ai_category)}</strong> (${Math.round(t.ai_confidence*100)}% confidence) and <strong>${esc(t.ai_priority)}</strong> priority when created. Reporter-selected: <strong>${esc(t.category)}</strong> / <strong>${esc(t.priority)}</strong>.</div>
        ${staff ? `<hr class="separator"><h3>Staff controls</h3><div class="field"><label for="assign-member">Assign staff member</label><select id="assign-member"><option value="">Not assigned</option></select></div><button class="secondary-btn" data-action="assign">${icon('user')} Update assignment</button>
        <div class="field field-gap"><label for="status-note">Status update note (optional)</label><input id="status-note" maxlength="500" placeholder="e.g. Maintenance team is inspecting the unit"></div>
        <div class="status-actions">${data.allowed_next.map(status=>`<button class="primary-btn" data-status="${esc(status)}">${icon('arrow')} Mark ${esc(status)}</button>`).join('') || '<span class="small muted">No allowed transition from this status.</span>'}</div>`:''}
        <hr class="separator"><div class="panel-heading"><h3>Activity timeline</h3></div><div class="activity">${data.events.map(e=>`<div class="activity-item"><strong>${esc(e.actor_name)} · ${esc(e.event_type === 'status'?`${e.from_status} → ${e.to_status}`:e.event_type === 'created'?'Submitted this report':e.event_type === 'assigned'?'Updated assignment':'Added a comment')}</strong><p>${esc(e.note)}</p><small>${dateTime(e.created_at)}</small></div>`).join('')}</div>
        <hr class="separator"><form id="comment-form" data-id="${t.id}"><div class="field"><label for="comment-text">Add an update or question</label><textarea id="comment-text" rows="3" minlength="2" maxlength="500" required placeholder="Keep updates constructive and specific."></textarea></div><button class="secondary-btn" type="submit">${icon('message')} Add comment</button></form></div>`;
      if (staff) {
        try {const people=await api('/api/users/assignees');const select=$('#assign-member'); if(select) {select.innerHTML+=people.users.map(x=>`<option value="${x.id}">${esc(x.name)} (${esc(x.role)})</option>`).join('');select.value=t.assignee_id == null ? '' : String(t.assignee_id);}} catch(e) {toast(e.message,true);}
      }
    } catch(e) {toast(e.message,true);closeModal();}
  }

  function setButtonBusy(button, busy, text='Working…') {
    if (!button) return;
    if (busy) {button.dataset.original=button.innerHTML;button.innerHTML=`<span class="loader mini-loader"></span> ${esc(text)}`;button.disabled=true;}
    else {button.innerHTML=button.dataset.original || button.innerHTML;button.disabled=false;}
  }
  async function saveTicket(event) {
    event.preventDefault();
    const f=event.target;
    const payload={title:$('#new-title').value.trim(),description:$('#new-description').value.trim(),location:$('#new-location').value.trim(),category:$('#new-category').value,priority:$('#new-priority').value};
    const button=$('#ticket-submit');setButtonBusy(button,true,'Submitting…');
    try {
      const result=await api('/api/tickets',{method:'POST',body:JSON.stringify(payload)});
      toast(`${result.ref} submitted successfully.`); closeModal();
      if (state.view==='tickets') await loadTicketRows(); else await navigate('overview');
    } catch(e) {toast(e.message,true);setButtonBusy(button,false);}
  }
  async function updateStatus(ticketId,status) {
    const note=$('#status-note')?.value || '';
    try {await api(`/api/tickets/${ticketId}/status`,{method:'PATCH',body:JSON.stringify({status,note})});toast(`Status updated to ${status}.`);closeModal();await navigate(state.view);await openTicket(ticketId);} catch(e){toast(e.message,true);}
  }
  async function updateAssignee(ticketId) {
    const raw=$('#assign-member')?.value;
    try {await api(`/api/tickets/${ticketId}/assignee`,{method:'PATCH',body:JSON.stringify({assignee_id:raw ? Number(raw):null})});toast('Assignment saved.');closeModal();await navigate(state.view);await openTicket(ticketId);} catch(e){toast(e.message,true);}
  }
  async function saveComment(event) {
    event.preventDefault();const id=event.target.dataset.id, note=$('#comment-text').value.trim();
    try {await api(`/api/tickets/${id}/comments`,{method:'POST',body:JSON.stringify({note})});toast('Comment posted.');await openTicket(id);}catch(e){toast(e.message,true);}
  }

  document.addEventListener('submit', async event => {
    if (event.target.id === 'auth-form') {
      event.preventDefault();
      const login=state.authTab==='login', button=$('#submit-auth'), email=$('#email').value.trim(), password=$('#password').value;
      if (!emailValid(email)) return formError('Please enter a valid email address.');
      const payload=login?{email,password}:{name:$('#name').value.trim(),email,password};
      setButtonBusy(button,true,login?'Signing in…':'Creating account…');
      try {
        const result=await api(login?'/api/auth/login':'/api/auth/register',{method:'POST',body:JSON.stringify(payload)});
        if (login) {state.user=result.user;state.csrf=result.csrf_token;renderShell();navigate('overview');toast(`Welcome back, ${state.user.name.split(' ')[0]}!`);}
        else {state.authTab='login';renderLogin();$('#email').value=email;toast('Account created. Sign in to continue.');}
      } catch(e){formError(e.message);setButtonBusy(button,false);}
    }
    else if (event.target.id==='ticket-form') await saveTicket(event);
    else if (event.target.id==='comment-form') await saveComment(event);
    else if (event.target.id==='ai-form') {
      event.preventDefault();const text=$('#ai-text').value.trim();state.pendingText=text;
      const button=$('#ai-submit');setButtonBusy(button,true,'Analyzing…');
      await analyzeText(text,'#ai-result');setButtonBusy(button,false);
    }
  });

  document.addEventListener('click', async event => {
    const target=event.target.closest('[data-nav], [data-action], [data-ticket], [data-demo], [data-auth-tab], [data-page], [data-status]');
    if (!target) {if (event.target.id==='overlay') closeModal();return;}
    if (target.dataset.nav) {await navigate(target.dataset.nav);return;}
    if (target.dataset.authTab) {state.authTab=target.dataset.authTab;renderLogin();return;}
    if (target.dataset.demo) {
      const [email,password]=state.roleAccounts[target.dataset.demo];
      $('#email').value=email;$('#password').value=password;$('#auth-form').requestSubmit();return;
    }
    if (target.dataset.ticket) {await openTicket(Number(target.dataset.ticket));return;}
    if (target.dataset.page) {state.filters.page=Number(target.dataset.page);await loadTicketRows();return;}
    if (target.dataset.status && state.currentTicket) {await updateStatus(state.currentTicket.ticket.id,target.dataset.status);return;}
    const action=target.dataset.action;
    if (action==='new') newTicket();
    if (action==='close') closeModal();
    if (action==='menu') {const opened=$('#sidebar')?.classList.toggle('open');document.body.classList.toggle('menu-open',!!opened);$('.mobile-menu')?.setAttribute('aria-expanded',String(!!opened));}
    if (action==='close-menu') {$('#sidebar')?.classList.remove('open');document.body.classList.remove('menu-open');$('.mobile-menu')?.setAttribute('aria-expanded','false');}
    if (action==='toggle-password') {const pw=$('#password');if(pw){const visible=pw.type==='password';pw.type=visible?'text':'password';target.textContent=visible?'Hide':'Show';target.setAttribute('aria-label',visible?'Hide password':'Show password');pw.focus();}}
    if (action==='high-priority') {state.filters={search:'',status:'All',category:'All',priority:'High',page:1};await navigate('tickets');}
    if (action==='logout') {
      try{await api('/api/auth/logout',{method:'POST',body:'{}'});}catch(e){toast(`Sign out failed: ${e.message}`,true);return;}
      state.user=null;state.csrf='';state.authTab='login';renderLogin();
    }
    if (action==='reload-tickets') await loadTicketRows();
    if (action==='assign' && state.currentTicket) await updateAssignee(state.currentTicket.ticket.id);
    if (action==='suggest-ticket') {
      const title=$('#new-title').value.trim(),desc=$('#new-description').value.trim();
      if ((title+' '+desc).trim().length<20) {toast('Add a description of at least 20 characters first.',true);return;}
      const suggestion=await analyzeText(`${title}. ${desc}`,'#new-prediction');
      if(suggestion && $('#new-category')) {$('#new-category').value=suggestion.category;$('#new-priority').value=suggestion.priority;toast('Recommendation applied. You can edit either field.');}
    }
    if (action==='ai-to-ticket') newTicket(state.pendingText || '');
  });

  let searchDelay;
  document.addEventListener('input', event => {
    if (event.target.id==='ticket-search') {
      state.filters.search=event.target.value;state.filters.page=1;
      clearTimeout(searchDelay);searchDelay=setTimeout(()=>loadTicketRows(),320);
    }
  });
  document.addEventListener('change', event => {
    const fields={'ticket-status':'status','ticket-category':'category','ticket-priority':'priority'};
    const key=fields[event.target.id];if (key) {state.filters[key]=event.target.value;state.filters.page=1;loadTicketRows();}
  });
  document.addEventListener('keydown', event => {
    if(event.key==='Escape') {if (state.modalOpen)closeModal();else if ($('#sidebar')?.classList.contains('open')) {$('#sidebar').classList.remove('open');document.body.classList.remove('menu-open');$('.mobile-menu')?.setAttribute('aria-expanded','false');}}
    if(event.key==='Tab' && state.modalOpen) {
      const controls=$$('#overlay .modal button:not(:disabled), #overlay .modal input:not(:disabled), #overlay .modal textarea:not(:disabled), #overlay .modal select:not(:disabled)');
      if (!controls.length) return;
      const first=controls[0],last=controls[controls.length-1];
      if(event.shiftKey && document.activeElement===first){event.preventDefault();last.focus();}
      else if(!event.shiftKey && document.activeElement===last){event.preventDefault();first.focus();}
    }
  });
  // Keep all JS in this file so strict Content Security Policy needs no inline scripts.
  function $$(selector,parent=document){return Array.from(parent.querySelectorAll(selector));}
  boot();
})();
