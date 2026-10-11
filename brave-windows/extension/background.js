'use strict';
// Apex Descarga 1.2.2 - native process and queue live in the service worker.
// connectNative keeps the service worker alive while a task is active.
const HOST = 'com.apex.video_downloader';
const MAX_PENDING = 15;
let nativePort = null;
let currentJob = null;
let pending = [];
let loading = null;
let starting = false;
let cancellationRequested = false;
let jobWrite = Promise.resolve();

function validUrl(value) {
  if (typeof value !== 'string' || value.length < 8 || value.length > 2000) return false;
  try {
    const u = new URL(value);
    const h = u.hostname.toLowerCase();
    return ['http:', 'https:'].includes(u.protocol) && !!h && !u.username && !u.password &&
      !['localhost', '127.0.0.1', '::1'].includes(h) && !h.endsWith('.local');
  } catch { return false; }
}
function validOptions(req) {
  return validUrl(req.url) && ['mp4', 'mp3'].includes(req.format) &&
    ['best', '480', '720', '1080', '2160'].includes(req.quality) &&
    ['stable', 'compatible'].includes(req.mode);
}
async function load() {
  if (!loading) loading = (async () => {
    const saved = await chrome.storage.local.get(['apexJob', 'apexQueue']);
    currentJob = saved.apexJob || null;
    pending = Array.isArray(saved.apexQueue) ? saved.apexQueue.slice(0, MAX_PENDING) : [];
    // A suspended/reloaded service worker cannot still own an active connection.
    if (currentJob && ['running', 'cancelling'].includes(currentJob.state) && !nativePort) {
      currentJob = { ...currentJob, state: 'error', stage: 'done',
        error: 'La descarga se interrumpió al reiniciarse la extensión. Puedes volver a iniciarla.' };
      await chrome.storage.local.set({ apexJob: currentJob });
    }
  })();
  return loading;
}
async function saveJob(changes) {
  currentJob = { ...(currentJob || {}), ...changes, updatedAt: Date.now() };
  const snapshot = currentJob;
  // Serialize writes so a delayed progress update cannot overwrite "completed".
  jobWrite = jobWrite.catch(() => {}).then(() => chrome.storage.local.set({ apexJob: snapshot }));
  await jobWrite;
}
async function saveQueue() { await chrome.storage.local.set({ apexQueue: pending }); }
async function appendHistory(job) {
  if (!job) return;
  const saved = await chrome.storage.local.get('apexHistory');
  const history = Array.isArray(saved.apexHistory) ? saved.apexHistory : [];
  const record = { id: job.id, url: job.url, format: job.format, quality: job.quality,
    state: job.state, file: job.file || '', error: job.error || '', time: Date.now() };
  await chrome.storage.local.set({ apexHistory: [record, ...history.filter(x => x.id !== job.id)].slice(0, 30) });
}
async function finishJob(port, changes) {
  if (nativePort !== port) return;
  nativePort = null;
  cancellationRequested = false;
  await saveJob({ ...changes, stage: 'done' });
  await appendHistory(currentJob);
  try { port.disconnect(); } catch { /* already closed */ }
  await beginNext();
}
async function beginNext() {
  if (starting || nativePort || !pending.length) return;
  starting = true;
  try {
    const job = pending.shift();
    await saveQueue();
    const port = chrome.runtime.connectNative(HOST);
    nativePort = port;
    cancellationRequested = false;
    await saveJob({ ...job, state: 'running', percent: 0, stage: 'connecting',
      detail: 'Abriendo comunicación con Windows…', error: '', file: '', folder: '' });
    port.onMessage.addListener(msg => {
      if (nativePort !== port || !msg || typeof msg !== 'object') return;
      if (msg.type === 'progress') {
        const percent = typeof msg.percent === 'number' && Number.isFinite(msg.percent)
          ? Math.max(0, Math.min(99, msg.percent)) : currentJob?.percent || 0;
        saveJob({ state: cancellationRequested ? 'cancelling' : 'running', percent,
          stage: String(msg.stage || 'download'),
          detail: String(msg.message || 'Descargando…').slice(0, 230) }).catch(() => {});
      } else if (msg.type === 'done' || msg.type === 'error') {
        const cancelled = Boolean(msg.cancelled || cancellationRequested);
        const ok = msg.type === 'done' && msg.ok && !cancelled;
        finishJob(port, { state: cancelled ? 'cancelled' : ok ? 'done' : 'error',
          percent: ok ? 100 : currentJob?.percent || 0,
          detail: cancelled ? 'Descarga cancelada.' : ok ? 'Archivo guardado correctamente.' : 'No se pudo completar.',
          error: ok || cancelled ? '' : String(msg.error || 'Error del componente local.').slice(0, 500),
          technical: String(msg.technical || '').slice(0, 500),
          file: String(msg.file || '').slice(0, 260), folder: String(msg.folder || '').slice(0, 400)
        }).catch(() => {});
      }
    });
    port.onDisconnect.addListener(() => {
      const message = chrome.runtime.lastError?.message;
      if (nativePort !== port) return;
      finishJob(port, { state: cancellationRequested ? 'cancelled' : 'error',
        error: cancellationRequested ? '' : (message || 'Se perdió la comunicación con Windows.'),
        detail: cancellationRequested ? 'Descarga cancelada.' : 'Comunicación interrumpida.' }).catch(() => {});
    });
    port.postMessage({ type: 'download', url: job.url, format: job.format,
      quality: job.quality, mode: job.mode });
  } catch (error) {
    const failed = currentJob;
    nativePort = null;
    await saveJob({ ...(failed || {}), state: 'error', stage: 'done', error: String(error.message || error) });
    await appendHistory(currentJob);
  } finally { starting = false; }
  // If a synchronous startup failure happened, allow next queued item to proceed.
  if (!nativePort && pending.length) await beginNext();
}
function nativeOnce(message) {
  return new Promise(resolve => {
    chrome.runtime.sendNativeMessage(HOST, message, response => {
      const error = chrome.runtime.lastError?.message;
      resolve(error ? { ok: false, error } : response || { ok: false, error: 'El componente no respondió.' });
    });
  });
}
async function handle(request) {
  if (!request || typeof request !== 'object') return { ok: false, error: 'Mensaje inválido.' };
  await load();
  switch (request.type) {
    case 'STATUS': return nativeOnce({ type: 'status' });
    case 'PREVIEW':
      if (!validUrl(request.url)) return { ok: false, error: 'Escribe una URL HTTP(S) válida.' };
      return nativeOnce({ type: 'preview', url: request.url });
    case 'OPEN_FOLDER': return nativeOnce({ type: 'open_folder' });
    case 'CHOOSE_FOLDER': return nativeOnce({ type: 'choose_folder' });
    case 'GET_DATA': {
      const saved = await chrome.storage.local.get('apexHistory');
      return { ok: true, job: currentJob, queue: pending,
        history: Array.isArray(saved.apexHistory) ? saved.apexHistory : [] };
    }
    case 'QUEUE_ADD': {
      if (!validOptions(request)) return { ok: false, error: 'Verifica el enlace y el formato.' };
      if (pending.length >= MAX_PENDING) return { ok: false, error: 'La cola está llena (15 enlaces).' };
      const job = { id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
        url: request.url, format: request.format, quality: request.quality, mode: request.mode };
      pending.push(job);
      await saveQueue();
      await beginNext();
      return { ok: true, id: job.id };
    }
    case 'QUEUE_REMOVE': {
      pending = pending.filter(job => job.id !== request.id);
      await saveQueue();
      return { ok: true };
    }
    case 'QUEUE_CLEAR': pending = []; await saveQueue(); return { ok: true };
    case 'QUEUE_RESUME': await beginNext(); return { ok: true };
    case 'CANCEL_ACTIVE':
      if (!nativePort || !currentJob || !['running', 'cancelling'].includes(currentJob.state))
        return { ok: false, error: 'No hay descarga activa.' };
      cancellationRequested = true;
      await saveJob({ state: 'cancelling', detail: 'Cancelando descarga…' });
      try { nativePort.postMessage({ type: 'cancel' }); return { ok: true }; }
      catch (error) { return { ok: false, error: String(error.message || error) }; }
    case 'CLEAR_HISTORY': await chrome.storage.local.set({ apexHistory: [] }); return { ok: true };
    default: return { ok: false, error: 'Operación desconocida.' };
  }
}
chrome.runtime.onMessage.addListener((message, sender, reply) => {
  if (sender.id !== chrome.runtime.id) return false;
  handle(message).then(reply).catch(error => reply({ ok: false, error: String(error.message || error) }));
  return true;
});
