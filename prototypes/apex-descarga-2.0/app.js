/* Apex Descarga 2.0 alpha.1 — offline interactive UI, demo only.
   This offline preview never requests network data or connects to the installed extension. */
(function () {
  'use strict';
  const C = window.ApexCore;
  if (!C) throw new Error('Falta core.js de Apex 2.0');
  const $ = id => document.getElementById(id);
  let format = 'mp4';
  let filter = 'all';
  let page = 'overview';
  let toastTimeout;
  let jobs;
  let settings;

  function seedJobs() {
    const start = Date.now();
    const one = C.createJob({ id: 'sample-a1', url: 'https://example.org/demo/video-evento', format: 'mp4', quality: '1080',
      title: 'Resumen de evento deportivo · EJEMPLO', createdAt: start - 60000 });
    one.state = 'done'; one.percent = 100;
    const two = C.createJob({ id: 'sample-a2', url: 'https://example.org/demo/horizonte', format: 'mp4', quality: '720',
      title: 'Horizonte cinematográfico · EJEMPLO', createdAt: start - 25000 });
    two.percent = 36; two.state = 'paused';
    const three = C.createJob({ id: 'sample-a3', url: 'https://example.org/demo/podcast', format: 'mp3', quality: 'best',
      title: 'Podcast de prueba · EJEMPLO', createdAt: start - 8000 });
    return [one, two, three];
  }
  function loadSaved() {
    try {
      const saved = localStorage.getItem(C.KEY);
      if (!saved) return { jobs: seedJobs(), settings: C.sanitizeSettings(null) };
      const parsed = JSON.parse(saved);
      return { jobs: C.normalizeJobs(parsed.jobs), settings: C.sanitizeSettings(parsed.settings) };
    } catch (_) {
      return { jobs: seedJobs(), settings: C.sanitizeSettings(null) };
    }
  }
  function save() {
    try { localStorage.setItem(C.KEY, JSON.stringify({ jobs, settings })); }
    catch (_) { /* Private browser modes can block localStorage; demo still works in memory. */ }
  }
  function notify(message, error) {
    const el = $('toast');
    el.textContent = message;
    el.classList.toggle('error', Boolean(error));
    el.hidden = false;
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => { el.hidden = true; }, 4200);
  }
  function element(tag, className, value) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (value !== undefined) el.textContent = String(value);
    return el;
  }
  function button(label, action, id, extraClass) {
    const btn = element('button', 'job-action' + (extraClass ? ' ' + extraClass : ''), label);
    btn.type = 'button'; btn.dataset.action = action; btn.dataset.id = id;
    return btn;
  }
  function stateLabel(state) {
    return ({ active: 'Simulando', pending: 'En espera', paused: 'Pausada', done: 'Completada', cancelled: 'Cancelada' })[state] || 'Demo';
  }
  function renderJob(job) {
    const item = element('article', 'job');
    item.dataset.jobId = job.id;
    const head = element('div', 'job-head');
    const icon = element('span', 'job-icon ' + job.format, job.format === 'mp3' ? '♫' : '▣');
    const info = element('div', 'job-desc');
    const title = element('div', 'job-title', job.title);
    title.title = job.url;
    const host = C.parseDemoUrl(job.url).host;
    const details = element('div', 'job-details', 'DEMO · ' + host + ' · ' + job.format.toUpperCase() +
      (job.format === 'mp4' ? ' · ' + (job.quality === 'best' ? 'Mejor disponible' : job.quality + 'p') : ''));
    info.append(title, details);
    const state = element('span', 'job-state ' + job.state, stateLabel(job.state));
    head.append(icon, info, state);
    item.append(head);

    if (['pending', 'paused', 'active', 'done'].includes(job.state)) {
      const progress = element('div', 'job-progress');
      const line = element('div', 'job-progress-line');
      const percent = Math.round(job.percent);
      const simulatedSize = (job.sizeMB * job.percent / 100).toFixed(1);
      line.append(element('span', '', simulatedSize + ' / ' + job.sizeMB.toFixed(1) + ' MB · FICTICIOS'),
        element('span', '', percent + '%'));
      const track = element('div', 'job-track');
      track.setAttribute('role', 'progressbar');
      track.setAttribute('aria-label', 'Progreso simulado de ' + job.title);
      track.setAttribute('aria-valuemin', '0');
      track.setAttribute('aria-valuemax', '100');
      track.setAttribute('aria-valuenow', String(percent));
      const fill = element('span');
      fill.style.width = job.percent + '%';
      track.append(fill);
      progress.append(line, track);
      if (job.state === 'active') {
        const eta = Math.ceil((job.sizeMB * (100 - job.percent) / 100) / C.speedFor(job));
        progress.append(element('div', 'job-details', 'Velocidad ficticia: ' + C.speedFor(job).toFixed(1) +
          ' MB/s · Tiempo simulado restante: ~' + eta + ' s'));
      }
      item.append(progress);
    }

    const actions = element('div', 'job-actions');
    if (job.state === 'active' || job.state === 'pending') actions.append(button('Ⅱ Pausar', 'pause', job.id));
    if (job.state === 'paused') actions.append(button('▶ Reanudar', 'resume', job.id));
    if (job.state !== 'done' && job.state !== 'cancelled') actions.append(button('✕ Cancelar', 'cancel', job.id, 'danger'));
    if (job.state === 'done' || job.state === 'cancelled') actions.append(button('✕ Quitar', 'remove', job.id, 'danger'));
    item.append(actions);
    return item;
  }
  function renderJobs() {
    const list = $('jobs');
    list.replaceChildren();
    const search = $('search').value.trim().toLowerCase();
    const visible = jobs.filter(job => C.matchesFilter(job, filter) &&
      (!search || (job.title + ' ' + job.url).toLowerCase().includes(search))).slice().reverse();
    if (visible.length) {
      const frag = document.createDocumentFragment();
      visible.forEach(job => frag.append(renderJob(job)));
      list.append(frag);
    } else {
      const empty = element('div', 'empty-state');
      empty.append(element('div', 'empty-icon', '⇣'),
        element('strong', '', 'Aquí no hay descargas demo'),
        element('p', '', 'Añade un enlace de prueba o cambia los filtros.'));
      list.append(empty);
    }
    $('jobs-counter').textContent = visible.length + (visible.length === 1 ? ' elemento' : ' elementos');
    $('clear-finished').disabled = !jobs.some(job => ['done', 'cancelled'].includes(job.state));
  }
  function renderStats() {
    const s = C.summary(jobs, settings.parallel);
    $('count-pending').textContent = String(s.pending);
    $('count-active').textContent = String(s.active);
    $('count-done').textContent = String(s.done);
    $('speed').replaceChildren(document.createTextNode(s.speed.toFixed(1) + ' '), element('small', '', 'MB/s'));
    $('side-speed').replaceChildren(document.createTextNode(s.speed.toFixed(1) + ' '), element('small', '', 'MB/s'));
    $('capacity-current').textContent = s.active + ' / ' + settings.parallel;
    $('capacity-fill').style.width = Math.round((s.active / settings.parallel) * 100) + '%';
    return s.speed;
  }
  const speedHistory = Array(21).fill(0);
  function renderBars(speed) {
    speedHistory.shift(); speedHistory.push(speed);
    const bars = $('speed-bars');
    const frag = document.createDocumentFragment();
    speedHistory.forEach(val => {
      const bar = element('div', 'bar-line');
      bar.style.height = Math.round(12 + Math.min(88, (val / 12) * 88)) + '%';
      frag.append(bar);
    });
    bars.replaceChildren(frag);
  }
  function render() {
    renderJobs();
    const speed = renderStats();
    renderBars(speed);
  }
  function setFormat(next) {
    format = next === 'mp3' ? 'mp3' : 'mp4';
    document.querySelectorAll('[data-format]').forEach(btn => {
      const selected = btn.dataset.format === format;
      btn.classList.toggle('selected', selected);
      btn.setAttribute('aria-pressed', String(selected));
    });
    $('quality').disabled = format === 'mp3';
  }
  function setFilter(next) {
    filter = next;
    document.querySelectorAll('[data-filter]').forEach(btn => {
      const selected = btn.dataset.filter === filter;
      btn.classList.toggle('active', selected);
      btn.setAttribute('aria-pressed', String(selected));
    });
    renderJobs();
  }
  function setPage(next) {
    if (!['overview', 'downloads', 'settings'].includes(next)) return;
    page = next;
    document.querySelectorAll('[data-nav]').forEach(btn => {
      const selected = btn.dataset.nav === page;
      btn.classList.toggle('active', selected);
      if (selected) btn.setAttribute('aria-current', 'page'); else btn.removeAttribute('aria-current');
    });
    document.querySelectorAll('[data-page]').forEach(section => { section.hidden = section.dataset.page !== page; });
    $('activity-layout').hidden = page === 'settings';
    $('page-name').textContent = ({ overview: 'Resumen', downloads: 'Descargas', settings: 'Preferencias' })[page];
    $('activity-title').textContent = page === 'downloads' ? 'Administrar tareas demo' : 'Actividad reciente';
    if (page === 'overview') {
      $('page-heading').innerHTML = 'Tus descargas.<br><span>Sin perder el control.</span>';
      $('page-subheading').textContent = 'Una experiencia renovada para organizar, supervisar y controlar tu flujo de archivos.';
    } else if (page === 'downloads') {
      $('page-heading').textContent = 'Cada descarga. Bajo control.';
      $('page-subheading').textContent = 'Pausa, reanuda, cancela y encuentra rápidamente tus tareas de demostración.';
    } else {
      $('page-heading').textContent = 'A tu manera.';
      $('page-subheading').textContent = 'Configura el entorno de prueba sin modificar la extensión instalada.';
    }
  }
  function addJob() {
    if (!$('consent').checked) { notify('Confirma que tienes autorización para descargar ese contenido.', true); return; }
    const parsed = C.parseDemoUrl($('url').value);
    if (!parsed.ok) { notify(parsed.error, true); $('url').focus(); return; }
    if (jobs.filter(j => ['active', 'pending', 'paused'].includes(j.state)).length >= 15) {
      notify('La cola de demostración admite hasta 15 tareas abiertas.', true); return;
    }
    const job = C.createJob({ url: parsed.url, format, quality: $('quality').value });
    jobs.push(job); save();
    $('url').value = '';
    render();
    notify('Añadido a la simulación: no se realizará ninguna descarga real.');
  }
  function manageJob(action, id) {
    const idx = jobs.findIndex(job => job.id === id);
    if (idx < 0) return;
    const job = jobs[idx];
    if (action === 'pause' && ['active', 'pending'].includes(job.state)) job.state = 'paused';
    else if (action === 'resume' && job.state === 'paused') job.state = 'pending';
    else if (action === 'cancel' && ['active', 'pending', 'paused'].includes(job.state)) job.state = 'cancelled';
    else if (action === 'remove' && ['done', 'cancelled'].includes(job.state)) jobs.splice(idx, 1);
    else return;
    save(); render();
  }
  function reset() {
    if (!window.confirm('¿Borrar todas las tareas y preferencias del prototipo? Apex Descarga 1.2.3 no se verá afectado.')) return;
    jobs = []; settings = C.sanitizeSettings(null);
    $('parallel').value = String(settings.parallel); $('compact').checked = false;
    document.body.classList.remove('compact');
    save(); render(); notify('Datos del prototipo restablecidos.');
  }
  function bind() {
    document.querySelectorAll('[data-nav]').forEach(btn => btn.addEventListener('click', () => setPage(btn.dataset.nav)));
    document.querySelectorAll('[data-format]').forEach(btn => btn.addEventListener('click', () => setFormat(btn.dataset.format)));
    document.querySelectorAll('[data-filter]').forEach(btn => btn.addEventListener('click', () => setFilter(btn.dataset.filter)));
    $('add-btn').addEventListener('click', addJob);
    $('url').addEventListener('keydown', event => { if (event.key === 'Enter') addJob(); });
    $('search').addEventListener('input', renderJobs);
    $('jobs').addEventListener('click', event => {
      const target = event.target.closest('button[data-action]');
      if (target && $('jobs').contains(target)) manageJob(target.dataset.action, target.dataset.id);
    });
    $('clear-finished').addEventListener('click', () => {
      jobs = jobs.filter(job => !['done', 'cancelled'].includes(job.state));
      save(); render(); notify('Historial demo finalizado limpiado.');
    });
    $('parallel').addEventListener('change', event => {
      settings.parallel = C.sanitizeSettings({ parallel: event.target.value }).parallel;
      save(); renderStats(); notify('Límite de simulaciones actualizado.');
    });
    $('compact').addEventListener('change', event => {
      settings.compact = event.target.checked;
      document.body.classList.toggle('compact', settings.compact);
      save();
    });
    $('reset-demo').addEventListener('click', reset);
  }
  const saved = loadSaved();
  jobs = saved.jobs;
  settings = saved.settings;
  $('parallel').value = String(settings.parallel);
  $('compact').checked = settings.compact;
  document.body.classList.toggle('compact', settings.compact);
  setFormat(format); bind(); setPage('overview'); render(); save();
  let lastTick = performance.now();
  setInterval(() => {
    const now = performance.now();
    const delta = Math.min(1.5, Math.max(0, (now - lastTick) / 1000));
    lastTick = now;
    if (jobs.some(j => j.state === 'active' || j.state === 'pending')) {
      jobs = C.tickJobs(jobs, settings.parallel, delta);
      save(); render();
    } else {
      renderStats(); renderBars(0);
    }
  }, 800);
})();
