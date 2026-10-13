'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const dir = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
const js = fs.readFileSync(path.join(dir, 'app.js'), 'utf8');
const core = fs.readFileSync(path.join(dir, 'core.js'), 'utf8');

test('the local preview references only its own scripts and styles', () => {
  for (const file of ['styles.css', 'core.js', 'app.js'])
    assert.ok(html.includes('"' + file + '"'), file);
  assert.ok(!/<script[^>]+src=["']https?:/i.test(html));
  assert.ok(!/<link[^>]+href=["']https?:/i.test(html));
});
test('all JS-targeted elements exist in the standalone HTML', () => {
  const used = new Set([...js.matchAll(/\$\('([a-z0-9-]+)'\)/g)].map(match => match[1]));
  const defined = new Set([...html.matchAll(/\bid="([a-z0-9-]+)"/g)].map(match => match[1]));
  for (const id of used) assert.ok(defined.has(id), 'Missing DOM node: ' + id);
  assert.ok(used.size > 15);
});
test('alpha does not connect to Native Messaging, fetch or install dependencies', () => {
  const combined = js + '\n' + core;
  assert.ok(!/\bchrome\.runtime\b/.test(combined));
  assert.ok(!/\bfetch\s*\(/.test(combined));
  assert.ok(!/\bXMLHttpRequest\b/.test(combined));
  assert.ok(!/\bWebSocket\b/.test(combined));
});
test('demo and imaginary metrics are labeled visibly', () => {
  assert.match(html, /MODO DEMO/);
  assert.match(html, /simulados/);
  assert.match(html, /SIN DESCARGAS REALES/);
});
