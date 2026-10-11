'use strict';
const $ = id => document.getElementById(id);
const urlInput = $('video-url');
const quality = $('quality');
const mode = $('mode');
let format = 'mp4';
let folderPath = '';
let isConnected = false;
let visibleJob = null;
let lastPreviewURL = '';
let acceptedTerms = false;
const TERMS_VERSION = '1.2.2';

function errorView(message) {
  $('error').hidden = false;
  $('error').textContent = String(message?.message || message || 'Error desconocido').slice(0, 700);
}
function clearError() { $('error').hidden = true; $('error').textContent = ''; }
function hostnameFor(value) {
  try { return new URL(value).hostname; } catch { return 'Enlace'; }
}
function validUrl(value) {
  try {
    const u = new URL(value);
    return ['http:', 'https:'].includes(u.protocol) && !!u.hostname && !u.username && !u.password;
  } catch { return false; }
}
function isMediaLink(value) {
  try {
    const u = new URL(value);
    const host = u.hostname.toLowerCase();
    const path = u.pathname;
    return (/(^|\.)youtube\.com$/.test(host) && (path === '/watch' && u.searchParams.has('v') || /^\/(shorts|live)\//.test(path))) ||
      host === 'youtu.be' || (/(^|\.)tiktok\.com$/.test(host) && /\/video\/|\/t\//.test(path)) ||
      (/(^|\.)instagram\.com$/.test(host) && /^\/(reel|p|tv)\//.test(path)) ||
      (/(^|\.)vimeo\.com$/.test(host) && /\d+/.test(path)) ||
      (/(^|\.)facebook\.com$/.test(host) && /\/videos\/|\/reel\//.test(path));
  } catch { return false; }
}
async function message(type, rest = {}) {
  const result = await chrome.runtime.sendMessage({ type, ...rest });
  if (!result?.ok) throw new Error(result?.error || 'No hubo respuesta de la extensión.');
  return result;
}
function setFormat(next, persist = true) {
  format = next;
  for (const item of ['mp4', 'mp3']) {
    const button = $('format-' + item);
    button.classList.toggle('selected', next === item);
    button.setAttribute('aria-pressed', String(next === item));
  }
  const audio = next === 'mp3';
  quality.disabled = audio;
  mode.disabled = audio;
  $('mode-help').textContent = audio
    ? 'Convertimos el mejor audio disponible. MP3 no puede mejorar la fuente original.'
    : mode.value === 'stable'
      ? 'Priorizamos H.264 + AAC; probamos HLS si hay HTTP 403.'
      : 'Preferimos HLS cuando el sitio lo ofrece. Puede ayudar con algunos 403.';
  if (audio) quality.value = 'best';
  else if (quality.value === 'best') quality.value = '1080';
  if (persist) savePreferences();
}

function applyTermsState() {
  const box = $('accept-terms');
  if (!box) return;
  box.checked = acceptedTerms;
}
async function ensureTermsAccepted() {
  if (acceptedTerms) return true;
  errorView('Debes aceptar las condiciones de uso antes de iniciar una descarga.');
  $('accept-terms')?.focus();
  return false;
}

function savePreferences() {
  chrome.storage.local.set({ apexPrefs: { format, quality: quality.value, mode: mode.value } }).catch(() => {});
}
$('format-mp4').addEventListener('click', () => setFormat('mp4'));
$('format-mp3').addEventListener('click', () => setFormat('mp3'));
quality.addEventListener('change', savePreferences);
mode.addEventListener('change', () => { setFormat(format); savePreferences(); });
$('accept-terms').addEventListener('change', async e => { acceptedTerms = e.target.checked; await chrome.storage.local.set({ apexTermsAcceptedVersion: acceptedTerms ? TERMS_VERSION : null }).catch(() => {}); clearError(); });

async function currentTab(silent) {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const value = tabs?.[0]?.url || '';
  if (validUrl(value) && isMediaLink(value)) {
    urlInput.value = value;
    hidePreview();
    clearError();
    return;
  }
  if (!silent) errorView('La pestaña actual no parece contener un video compatible. Abre un video concreto o pega su URL.');
}
$('current-tab').addEventListener('click', () => currentTab(false).catch(errorView));
function hidePreview() { $('preview').hidden = true; lastPreviewURL = ''; }
urlInput.addEventListener('input', () => { if (lastPreviewURL !== urlInput.value.trim()) hidePreview(); });

function durationText(seconds) {
  if (!Number.isFinite(seconds) || seconds < 0) return '';
  const s = Math.floor(seconds);
  return (s >= 3600 ? `${Math.floor(s / 3600)}:` : '') +
    `${Math.floor(s % 3600 / 60).toString().padStart(s >= 3600 ? 2 : 1, '0')}:` +
    (s % 60).toString().padStart(2, '0');
}
function renderPreview(data) {
  $('preview').hidden = false;
  $('preview-title').textContent = data.title || 'Video sin título';
  $('preview-site').textContent = String(data.site || 'VIDEO').toUpperCase();
  const parts = [data.channel, durationText(data.duration)].filter(Boolean);
  $('preview-description').textContent = parts.join(' · ') || 'Información del contenido';
  const heights = Array.isArray(data.heights) ? data.heights : [];
  $('preview-formats').textContent = heights.length
    ? 'Resoluciones: ' + heights.filter(h => h >= 360).slice(-6).map(h => `${h}p`).join(' · ')
    : 'La calidad depende de los formatos disponibles';
  const img = $('preview-image');
  if (typeof data.thumbnail === 'string' && data.thumbnail.startsWith('https://')) {
    img.src = data.thumbnail;
    img.hidden = false;
    $('preview-fallback').hidden = true;
  } else { img.removeAttribute('src'); img.hidden = true; $('preview-fallback').hidden = false; }
}
$('preview-image').addEventListener('error', () => {
  $('preview-image').hidden = true;
  $('preview-fallback').hidden = false;
});
$('analyze').addEventListener('click', async () => {
  const url = urlInput.value.trim();
  if (!validUrl(url)) { errorView('Pega primero un enlace HTTP(S) válido.'); return; }
  clearError();
  hidePreview();
  const button = $('analyze');
  button.disabled = true;
  button.textContent = 'Analizando…';
  try {
    const result = await message('PREVIEW', { url });
    if (urlInput.value.trim() === url) { renderPreview(result); lastPreviewURL = url; }
  } catch (error) { errorView('No se pudo analizar el enlace: ' + error.message); }
  finally { button.disabled = false; button.textContent = '◈ Analizar enlace'; }
});

function setFolder(value) {
  if (!value) return;
  folderPath = value;
  $('folder').textContent = value;
  $('folder').title = value;
}
function renderJob(job) {
  visibleJob = job;
  if (!job) return;
  const labels = {
    running: ['Descargando contenido…', 'EN CURSO'],
    cancelling: ['Cancelando descarga…', 'CANCELANDO'],
    done: ['Descarga completada', 'COMPLETADA'],
    error: ['No se pudo completar', 'ERROR'],
    cancelled: ['Descarga cancelada', 'CANCELADA']
  };
  const [title, pill] = labels[job.state] || ['En espera', 'EN ESPERA'];
  $('job-state').textContent = title;
  $('job-pill').textContent = pill;
  $('job-pill').className = 'pill ' + (['running', 'cancelling'].includes(job.state) ? 'running' : job.state);
  const progress = Number.isFinite(job.percent) ? Math.max(0, Math.min(100, job.percent)) : 0;
  $('bar').style.width = progress + '%';
  $('progress').setAttribute('aria-valuenow', Math.round(progress));
  $('percent').textContent = `${Math.round(progress)}%`;
  $('job-detail').textContent = job.detail || '';
  $('cancel').hidden = !['running', 'cancelling'].includes(job.state);
  $('cancel').disabled = job.state === 'cancelling';
  if (job.state === 'error' && job.error) errorView(job.error);
  else if (job.state !== 'error') clearError();
  $('file').hidden = !(job.state === 'done' && job.file);
  if (!$('file').hidden) $('file').textContent = '✓ ' + job.file;
  if (job.folder) setFolder(job.folder);
}
function renderQueue(queue, active) {
  const root = $('queue');
  root.replaceChildren();
  $('queue-count').textContent = `${queue.length} pendiente${queue.length === 1 ? '' : 's'}`;
  $('clear-queue').hidden = queue.length === 0;
  $('resume-queue').hidden = queue.length === 0 || ['running', 'cancelling'].includes(active?.state);
  if (!queue.length) {
    const p = document.createElement('p'); p.className = 'empty'; p.textContent = 'Sin archivos en espera.'; root.append(p); return;
  }
  queue.forEach((job, index) => {
    const line = document.createElement('div'); line.className = 'queue-item';
    const no = document.createElement('div'); no.className = 'queue-no'; no.textContent = index + 1;
    const main = document.createElement('div'); main.className = 'queue-name';
    const name = document.createElement('div'); name.className = 'queue-title'; name.textContent = hostnameFor(job.url); name.title = job.url;
    const sub = document.createElement('div'); sub.className = 'queue-sub'; sub.textContent = `${job.format.toUpperCase()} · ${job.quality === 'best' ? 'Mejor calidad' : job.quality + 'p'}`;
    const remove = document.createElement('button'); remove.className = 'removebtn'; remove.type = 'button'; remove.textContent = '×'; remove.title = 'Quitar de la cola'; remove.setAttribute('aria-label', 'Quitar elemento');
    remove.addEventListener('click', async () => {
      try { await message('QUEUE_REMOVE', { id: job.id }); await refreshData(); } catch (error) { errorView(error); }
    });
    main.append(name, sub); line.append(no, main, remove); root.append(line);
  });
}
function renderHistory(history) {
  const root = $('history'); root.replaceChildren();
  if (!Array.isArray(history) || !history.length) {
    const p = document.createElement('p'); p.className = 'empty'; p.textContent = 'Todavía no hay descargas recientes.'; root.append(p); return;
  }
  for (const job of history.slice(0, 30)) {
    const line = document.createElement('div'); line.className = 'history-item';
    const bullet = document.createElement('span'); bullet.className = 'history-bullet ' + (job.state === 'error' ? 'error' : job.state === 'cancelled' ? 'cancelled' : '');
    const content = document.createElement('div'); content.className = 'history-main';
    const name = document.createElement('div'); name.className = 'history-title'; name.textContent = job.file || hostnameFor(job.url); name.title = name.textContent;
    const meta = document.createElement('div'); meta.className = 'history-meta';
    const label = job.state === 'done' ? 'Completado' : job.state === 'cancelled' ? 'Cancelado' : 'Fallido';
    meta.textContent = `${(job.format || '').toUpperCase()} · ${label} · ${new Date(job.time).toLocaleDateString('es-MX')}`;
    content.append(name, meta); line.append(bullet, content); root.append(line);
  }
}
async function refreshData() {
  const state = await message('GET_DATA');
  renderJob(state.job);
  renderQueue(state.queue || [], state.job);
  renderHistory(state.history || []);
}
$('download').addEventListener('click', async () => {
  const url = urlInput.value.trim();
  if (!validUrl(url)) { errorView('Introduce un enlace HTTP(S) válido.'); return; }
  if (!(await ensureTermsAccepted())) return;
  clearError();
  $('download').disabled = true;
  $('cta-label').textContent = 'Agregando…';
  try {
    await message('QUEUE_ADD', { url, format, quality: format === 'mp3' ? 'best' : quality.value, mode: mode.value });
    await refreshData();
    $('cta-label').textContent = 'Añadido a la cola ✓';
  } catch (error) { errorView(error); }
  finally {
    $('download').disabled = false;
    window.setTimeout(() => { $('cta-label').textContent = 'Añadir a descargas'; }, 900);
  }
});
$('cancel').addEventListener('click', async () => {
  try { await message('CANCEL_ACTIVE'); await refreshData(); } catch (error) { errorView(error); }
});
$('clear-queue').addEventListener('click', async () => {
  try { await message('QUEUE_CLEAR'); await refreshData(); } catch (error) { errorView(error); }
});
$('resume-queue').addEventListener('click', async () => {
  try { await message('QUEUE_RESUME'); await refreshData(); } catch (error) { errorView(error); }
});
$('clear-history').addEventListener('click', async () => {
  try { await message('CLEAR_HISTORY'); await refreshData(); } catch (error) { errorView(error); }
});
$('open-folder').addEventListener('click', async () => {
  try { await message('OPEN_FOLDER'); } catch (error) { errorView('No se pudo abrir la carpeta: ' + error.message); }
});
$('choose-folder').addEventListener('click', async () => {
  const button = $('choose-folder');
  button.disabled = true;
  $('folder-tip').textContent = 'Abriendo el selector de carpetas de Windows…';
  clearError();
  try {
    const result = await message('CHOOSE_FOLDER');
    if (result.folder) setFolder(result.folder);
    $('folder-tip').textContent = result.cancelled
      ? 'No se realizaron cambios en la carpeta.'
      : 'Nueva carpeta guardada. Las próximas descargas utilizarán esta ubicación.';
  } catch (error) {
    $('folder-tip').textContent = 'No se pudo abrir el selector de Windows.';
    errorView('Error al seleccionar carpeta: ' + error.message);
  } finally {
    button.disabled = false;
  }
});
chrome.storage.onChanged.addListener((changes, area) => {
  if (area !== 'local') return;
  if (changes.apexJob) renderJob(changes.apexJob.newValue);
  if (changes.apexQueue) renderQueue(changes.apexQueue.newValue || [], visibleJob);
  if (changes.apexHistory) renderHistory(changes.apexHistory.newValue || []);
});
(async () => {
  try {
    const saved = await chrome.storage.local.get(['apexPrefs','apexTermsAcceptedVersion']);
    const prefs = saved.apexPrefs || {};
    acceptedTerms = saved.apexTermsAcceptedVersion === TERMS_VERSION;
    applyTermsState();
    if (['best', '480', '720', '1080', '2160'].includes(prefs.quality)) quality.value = prefs.quality;
    if (['stable', 'compatible'].includes(prefs.mode)) mode.value = prefs.mode;
    setFormat(prefs.format === 'mp3' ? 'mp3' : 'mp4', false);
    await currentTab(true).catch(() => {});
    await refreshData();
    const health = await message('STATUS');
    isConnected = true;
    $('health').className = 'connection-dot good';
    $('health').title = `Componente local ${health.version || '?'}`;
    $('connection').textContent = '● Conectado';
    $('connection').className = 'connection good';
    setFolder(health.folder);
    if (!health.ytdlp) errorView('Falta yt-dlp. Repara la instalación local.');
    else if (health.version !== '1.2.2') errorView(`Tu componente local es ${health.version || 'antiguo'}. Ejecuta ACTUALIZAR_APEX.cmd de Apex Descarga 1.2.2.`);
    else if (!health.ffmpeg) errorView('FFmpeg no está disponible. La conversión a MP3 no funcionará.');
  } catch (error) {
    isConnected = false;
    $('health').className = 'connection-dot bad';
    $('connection').textContent = '● Sin conexión';
    $('connection').className = 'connection bad';
    errorView('No se pudo conectar con Windows: ' + error.message);
  }
})();
