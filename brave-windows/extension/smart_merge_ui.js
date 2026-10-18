'use strict';
// Dedicated Smart Merge controls. Existing popup.js and its MP4/MP3 handlers stay intact.
(() => {
  const e = id => document.getElementById(id);
  let analyzed = '';
  let analysis = null;
  let running = false;
  const split = () => e('sm-urls').value.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
  function err(message) {
    e('sm-error').hidden = !message;
    e('sm-error').textContent = message || '';
  }
  async function ask(type, values = {}) {
    const response = await chrome.runtime.sendMessage({ type, ...values });
    if (!response?.ok) throw new Error(response?.error || 'No se obtuvo respuesta de Windows.');
    return response;
  }
  function enable() {
    const urls = split();
    e('sm-count').textContent = urls.length + ' enlace' + (urls.length === 1 ? '' : 's');
    e('sm-start').disabled = running || !e('sm-rights').checked ||
      !analysis || analyzed !== urls.join('\n');
  }
  e('sm-urls').addEventListener('input', () => { analysis = null; analyzed = ''; e('sm-analysis').hidden = true; enable(); });
  e('sm-rights').addEventListener('change', enable);
  e('sm-analyze').addEventListener('click', async () => {
    err('');
    const urls = split();
    if (urls.length < 2 || urls.length > 100) { err('Debes pegar de 2 a 100 enlaces, uno por línea.'); return; }
    e('sm-analyze').disabled = true;
    e('sm-analyze').textContent = 'Analizando…';
    try {
      const response = await ask('SMART_ANALYZE', { urls });
      analysis = response; analyzed = urls.join('\n');
      e('sm-analysis').hidden = false;
      const preview = response.parts.slice(0, 5).map(p => p.number + ' · ' + p.name).join('\n');
      e('sm-analysis').textContent = '✓ ' + response.count + ' partes válidas · ' +
        response.provider + '\nConjunto: ' + response.base + '\n' + preview +
        (response.count > 5 ? '\n...y ' + (response.count - 5) + ' partes más' : '') +
        '\nEl análisis inicial lee las URL; la verificación de integridad se realiza después de descargar.';
    } catch (error) { analysis = null; err(String(error.message || error)); }
    finally { e('sm-analyze').disabled = false; e('sm-analyze').textContent = '◈ Analizar partes'; enable(); }
  });
  e('sm-start').addEventListener('click', async () => {
    if (!analysis || analyzed !== split().join('\n')) return;
    err('');
    const terms = await chrome.storage.local.get('apexTermsAcceptedVersion');
    if (terms.apexTermsAcceptedVersion !== '1.2.2') {
      err('Acepta primero las condiciones de Apex Descarga en la sección de descargas MP4/MP3.');
      return;
    }
    try {
      const result = await ask('SMART_START', {
        urls: split(), parallel: Number(e('sm-parallel').value),
        output: e('sm-output').value, cleanup: e('sm-cleanup').checked
      });
      running = true;
      e('sm-progress-block').hidden = false;
      e('sm-result').hidden = true;
      e('sm-state').textContent = 'Unificando ' + result.count + ' partes…';
      enable();
      await refresh();
    } catch (error) { err(String(error.message || error)); }
  });
  e('sm-cancel').addEventListener('click', async () => {
    try {
      await ask('SMART_CANCEL');
      e('sm-cancel').disabled = true;
      e('sm-state').textContent = 'Cancelando…';
    } catch (error) { err(String(error.message || error)); }
  });
  function speedLabel(n) {
    if (!Number.isFinite(n) || n <= 0) return '—';
    return (n / 1048576).toFixed(2) + ' MiB/s promedio';
  }
  function update(job) {
    if (!job) return;
    e('sm-progress-block').hidden = false;
    running = ['running', 'cancelling'].includes(job.state);
    const labels = { running: 'Procesando', cancelling: 'Cancelando', done: 'Completado', error: 'Error', cancelled: 'Cancelado' };
    e('sm-state').textContent = labels[job.state] || 'Preparando';
    const validPercent = typeof job.percent === 'number' && Number.isFinite(job.percent);
    e('sm-percent').textContent = validPercent ? Math.round(job.percent) + '%' : '—';
    e('sm-bar').style.width = validPercent ? Math.max(0, Math.min(100, job.percent)) + '%' : '0%';
    if (validPercent) e('sm-progress').setAttribute('aria-valuenow', String(Math.round(job.percent)));
    else e('sm-progress').removeAttribute('aria-valuenow');
    e('sm-stage').textContent = (job.stage || 'analyze') + ' · ' + (job.message || 'Preparando…');
    e('sm-parts').textContent = 'Partes: ' + (job.partsDone ?? 0) + '/' + (job.partsTotal ?? '—');
    e('sm-speed').textContent = 'Velocidad: ' + speedLabel(job.speed);
    e('sm-eta').textContent = 'Tiempo restante: ' +
      (Number.isFinite(job.eta) ? Math.max(0, Math.round(job.eta)) + ' s (estimado)' : '—');
    e('sm-cancel').hidden = !running;
    e('sm-cancel').disabled = job.state === 'cancelling';
    e('sm-result').hidden = job.state !== 'done';
    if (job.state === 'done') e('sm-result').textContent =
      '✓ ARCHIVO ÚNICO LOCAL\n' + (job.file || 'Verificado') +
      '\nDestino: ' + (job.path || '') + '\nSHA-256: ' + (job.sha256 || '—');
    if (job.state === 'error') err(job.error || 'Falló el proceso de unificación.');
    else if (job.state === 'cancelled') err('Operación cancelada. Las partes completas se conservarán para reanudar.');
    enable();
  }
  async function refresh() {
    try { const state = await ask('SMART_GET_DATA'); update(state.job); }
    catch (error) { err(String(error.message || error)); }
  }
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === 'local' && changes.apexSmartState) update(changes.apexSmartState.newValue);
  });
  enable();
  refresh();
})();
