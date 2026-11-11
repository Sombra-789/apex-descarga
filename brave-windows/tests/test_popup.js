'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const elements = new Map();
const requests = [];
let activeURL = 'https://example.org/video';
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    value: id === 'quality' ? '1080' : id === 'mode' ? 'stable' : '',
    hidden: true, textContent: '', handlers: {}, style: {},
    classList: {toggle() {}}, setAttribute() {}, focus() {}, append() {}, replaceChildren() {},
    addEventListener(name, fn) {this.handlers[name] = fn;}
  });
  return elements.get(id);
}
const chrome = {
  tabs: {query: async () => [{url: activeURL}]},
  runtime: {sendMessage: async request => {
    requests.push(request);
    if (request.type === 'GET_DATA') return {ok:true,queue:[],history:[]};
    return {ok:true,version:'1.2.4',ytdlp:'test',ffmpeg:true};
  }},
  storage: {local: {get: async () => ({}), set: async () => {}}, onChanged:{addListener() {}}}
};
const context = vm.createContext({chrome, URL, console, Date, Math, Number,
  document:{getElementById:element,createElement:()=>element(Symbol())},window:{setTimeout}});
for (const name of ['site-policy.js','popup.js'])
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../extension',name),'utf8'),context);
(async () => {
  await new Promise(resolve=>setTimeout(resolve,20));
  for (const url of ['https://x.com/user/status/123','https://example.org/video.mp4','https://dailymotion.com/video/123']) {
    activeURL = url;
    await element('current-tab').handlers.click();
    assert.equal(element('video-url').value,url);
  }
  activeURL = 'https://www.threads.com/@a/post/123';
  await element('current-tab').handlers.click();
  assert.equal(element('error').hidden,false);
  assert.match(element('error').textContent,/Threads/);
  requests.length = 0;
  await element('analyze').handlers.click();
  await element('download').handlers.click();
  assert.equal(requests.length,0,'Threads must not be sent to the native host or queue');
  activeURL = 'brave://extensions';
  await element('current-tab').handlers.click();
  assert.match(element('error').textContent,/HTTP/);
  console.log('PASS: current tab accepts HTTP(S) sites; Threads shows a clear message before analysis/download');
})().catch(error=>{console.error(error);process.exitCode=1;});
