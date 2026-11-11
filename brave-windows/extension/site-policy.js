'use strict';
globalThis.ApexSitePolicy = Object.freeze({
  errorFor(value) {
    try {
      const host = new URL(value).hostname.toLowerCase().replace(/\.+$/, '');
      if (['threads.net', 'threads.com'].some(domain => host === domain || host.endsWith('.' + domain)))
        return 'Las descargas de Threads todavía no están disponibles en Apex Descarga.';
    } catch { /* URL validation is handled by the caller. */ }
    return '';
  }
});
