/* Apex Descarga 2.0 alpha.1 — pure demo state engine.
   Never uses network requests, browser extension APIs or the Windows host. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.ApexCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const KEY = 'apex-descarga-2-alpha1-demo-v1';
  const STATUSES = new Set(['pending', 'active', 'paused', 'done', 'cancelled']);
  const QUALITIES = new Set(['best', '480', '720', '1080', '2160']);
  function clamp(n, min, max) {
    return Number.isFinite(Number(n)) ? Math.max(min, Math.min(max, Number(n))) : min;
  }
  function parseDemoUrl(raw) {
    if (typeof raw !== 'string' || raw.trim().length < 8 || raw.trim().length > 2000)
      return { ok: false, error: 'Escribe un enlace HTTP o HTTPS válido.' };
    try {
      const url = new URL(raw.trim());
      if (!['http:', 'https:'].includes(url.protocol) || !url.hostname ||
          url.username || url.password || /[\u0000-\u001f\u007f]/.test(raw)) {
        return { ok: false, error: 'Solo se aceptan enlaces web HTTP(S) sin credenciales.' };
      }
      const host = url.hostname.toLowerCase();
      if (host === 'localhost' || host.endsWith('.localhost') || host.endsWith('.local') ||
          /^127\./.test(host) || /^192\.168\./.test(host) || /^10\./.test(host) ||
          /^169\.254\./.test(host)) {
        return { ok: false, error: 'No se aceptan direcciones locales.' };
      }
      return { ok: true, url: url.toString(), host: host.replace(/^www\./, '') };
    } catch (_) {
      return { ok: false, error: 'La dirección no tiene un formato válido.' };
    }
  }
  function demoName(url) {
    const parsed = parseDemoUrl(url);
    if (!parsed.ok) return 'Enlace de demostración';
    const path = new URL(parsed.url).pathname.split('/').filter(Boolean).pop() || '';
    const cleanPath = path.replace(/[-_]+/g, ' ').replace(/\.(mp4|mp3|webm)$/i, '').trim();
    return cleanPath ? cleanPath.slice(0, 70) + ' · ' + parsed.host : parsed.host;
  }
  function createJob(data) {
    const parsed = parseDemoUrl(data.url);
    if (!parsed.ok) throw new Error(parsed.error);
    const format = data.format === 'mp3' ? 'mp3' : 'mp4';
    const quality = QUALITIES.has(data.quality) ? data.quality : '1080';
    return {
      id: String(data.id || ('demo-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10))),
      url: parsed.url, title: String(data.title || demoName(parsed.url)).slice(0, 100),
      format, quality, state: 'pending', percent: 0,
      sizeMB: format === 'mp3' ? 18 : (quality === '2160' ? 108 : quality === '480' ? 30 : 57),
      createdAt: Number.isFinite(data.createdAt) ? data.createdAt : Date.now()
    };
  }
  function sanitizeJob(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const parsed = parseDemoUrl(raw.url);
    if (!parsed.ok || typeof raw.id !== 'string' || raw.id.length > 100) return null;
    const format = raw.format === 'mp3' ? 'mp3' : 'mp4';
    const state = STATUSES.has(raw.state) ? raw.state : 'paused';
    const percent = clamp(raw.percent, 0, 100);
    return {
      id: raw.id, url: parsed.url,
      title: String(raw.title || demoName(parsed.url)).slice(0, 100),
      format, quality: QUALITIES.has(raw.quality) ? raw.quality : '1080',
      state: state === 'active' ? 'paused' : state,  // Don't auto-resume on page reload.
      percent: state === 'done' ? 100 : percent,
      sizeMB: clamp(raw.sizeMB, 5, 250),
      createdAt: clamp(raw.createdAt, 0, 4102444800000)
    };
  }
  function normalizeJobs(input) {
    if (!Array.isArray(input)) return [];
    const seen = new Set();
    return input.slice(0, 80).map(sanitizeJob).filter(job => {
      if (!job || seen.has(job.id)) return false;
      seen.add(job.id);
      return true;
    });
  }
  function sanitizeSettings(raw) {
    return { parallel: Math.trunc(clamp(raw && raw.parallel, 1, 3)),
      compact: Boolean(raw && raw.compact) };
  }
  function speedFor(job) {
    const seed = [...String(job.id)].reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
    return (14 + seed % 25) / 10; // Artificial demo MB/s, never network throughput.
  }
  function tickJobs(jobs, parallel, seconds) {
    const limit = Math.trunc(clamp(parallel, 1, 3));
    const delta = clamp(seconds, 0, 3);
    const next = jobs.map(job => ({ ...job }));
    let active = next.filter(job => job.state === 'active').length;
    for (const job of next) {
      if (active >= limit) break;
      if (job.state === 'pending') { job.state = 'active'; active++; }
    }
    for (const job of next) {
      if (job.state !== 'active') continue;
      job.percent = Math.min(100, Number((job.percent + (speedFor(job) / job.sizeMB) * 100 * delta).toFixed(2)));
      if (job.percent >= 100) { job.percent = 100; job.state = 'done'; }
    }
    return next;
  }
  function summary(jobs, parallel) {
    const active = jobs.filter(job => job.state === 'active');
    return {
      pending: jobs.filter(job => job.state === 'pending' || job.state === 'paused').length,
      active: active.length,
      done: jobs.filter(job => job.state === 'done').length,
      cancelled: jobs.filter(job => job.state === 'cancelled').length,
      speed: Number(active.reduce((acc, job) => acc + speedFor(job), 0).toFixed(1)),
      parallel: Math.trunc(clamp(parallel, 1, 3))
    };
  }
  function matchesFilter(job, filter) {
    switch (filter) {
      case 'active': return job.state === 'active';
      case 'pending': return job.state === 'pending' || job.state === 'paused';
      case 'done': return job.state === 'done';
      default: return true;
    }
  }
  return { KEY, clamp, parseDemoUrl, demoName, createJob, sanitizeJob, normalizeJobs,
    sanitizeSettings, tickJobs, speedFor, summary, matchesFilter };
});
