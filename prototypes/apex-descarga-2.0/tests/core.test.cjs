'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const C = require('../core.js');

test('validate only web URLs with no credentials', () => {
  assert.equal(C.parseDemoUrl('https://example.com/video').ok, true);
  for (const value of ['javascript:alert(1)', 'file:///C:/a', 'ftp://example.com', 'http://localhost:8080',
    'http://127.0.0.1', 'http://192.168.1.4', 'https://username:password@example.org', 'not-a-url']) {
    assert.equal(C.parseDemoUrl(value).ok, false, value);
  }
});
test('createJobs use safely bounded options', () => {
  const job = C.createJob({ id:'x1', url:'https://example.org/demo/movie', format:'mp3', quality:'oversized' });
  assert.equal(job.format, 'mp3');
  assert.equal(job.quality, '1080');
  assert.equal(job.state, 'pending');
  assert.equal(job.title.includes('example.org'), true);
});
test('invalid stored jobs are removed and active job is paused after reload', () => {
  const job = C.createJob({ id:'x2', url:'https://example.org/video' });
  job.state = 'active'; job.percent = 43;
  const [loaded] = C.normalizeJobs([job, job, {url:'file:///x',id:'bad'}]);
  assert.equal(C.normalizeJobs([job, job, {url:'file:///x',id:'bad'}]).length, 1);
  assert.equal(loaded.state, 'paused');
  assert.equal(loaded.percent, 43);
});
test('simulation can complete tasks but never touches an external service', () => {
  const job = C.createJob({ id:'x3', url:'https://example.org/video', format:'mp3' });
  const first = C.tickJobs([job], 1, 1);
  assert.equal(first[0].state, 'active');
  assert.ok(first[0].percent > 0);
  assert.equal(job.state, 'pending'); // Immutable input
  let jobs = first;
  for (let i = 0; i < 100; i++) jobs = C.tickJobs(jobs, 1, 1);
  assert.equal(jobs[0].state, 'done');
  assert.equal(jobs[0].percent, 100);
});
test('concurrency is limited and filter maps to job states', () => {
  const jobs = Array.from({length: 4}, (_, i) => C.createJob({ id:'j'+i, url:'https://example.com/'+i }));
  const ticked = C.tickJobs(jobs, 2, 1);
  assert.equal(ticked.filter(j => j.state === 'active').length, 2);
  assert.equal(ticked.filter(j => j.state === 'pending').length, 2);
  const summary = C.summary(ticked, 2);
  assert.equal(summary.active, 2);
  assert.equal(summary.pending, 2);
  assert.equal(C.matchesFilter(ticked[0], 'active'), true);
});
test('settings limits are clamped to one to three', () => {
  assert.deepEqual(C.sanitizeSettings({parallel:99,compact:true}), {parallel:3,compact:true});
  assert.deepEqual(C.sanitizeSettings({parallel:-1,compact:false}), {parallel:1,compact:false});
});
