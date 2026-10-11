'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const data = {};
let listener;
let ports = [];
function port() {
  const messages = [], recvs = [], discons = [];
  return { messages, onMessage:{addListener:f=>recvs.push(f)},onDisconnect:{addListener:f=>discons.push(f)},
    postMessage:x=>messages.push(x),
    emit:x=>recvs.forEach(f=>f(x)),
    disconnect:()=>discons.forEach(f=>f()) };
}
const chrome = {
  runtime: { id:'test-apex-extension', lastError:null,
    onMessage:{addListener:f=>{listener=f}},
    connectNative:()=>{const p=port();ports.push(p);return p},
    sendNativeMessage:(host,message,reply)=>reply(message.type==='status'?{ok:true,version:'1.2.2'}:{ok:true,title:'Test'})
  },
  storage:{local:{get:async keys=>{
    const names = typeof keys==='string'?[keys]:keys;
    const result={}; for(const k of names) if(k in data) result[k]=data[k]; return result;
  },set:async payload=>{Object.assign(data,payload)}}}
};
const context=vm.createContext({ chrome, console, URL, Date, Math, Promise });
vm.runInContext(fs.readFileSync(path.join(__dirname,'../extension/background.js'),'utf8'),context);
function delay(ms=10){return new Promise(resolve=>setTimeout(resolve,ms))}
async function msg(request){
  return await new Promise(resolve=>listener(request,{id:chrome.runtime.id},resolve));
}
(async()=>{
  let result=await msg({type:'STATUS'});
  assert.equal(result.version,'1.2.2');
  result=await msg({type:'CHOOSE_FOLDER'});
  assert.equal(result.ok,true);
  assert.equal(result.title,'Test');
  result=await msg({type:'QUEUE_ADD',url:'file:///etc/passwd',format:'mp4',quality:'1080',mode:'stable'});
  assert.equal(result.ok,false);
  const job={format:'mp4',quality:'1080',mode:'stable'};
  result=await msg({type:'QUEUE_ADD',url:'https://youtu.be/first',...job});
  assert.equal(result.ok,true);
  await delay();
  assert.equal(ports.length,1);
  assert.equal(ports[0].messages[0].type,'download');
  result=await msg({type:'QUEUE_ADD',url:'https://vimeo.com/second',...job});
  assert.equal(result.ok,true);
  assert.equal(data.apexQueue.length,1);
  result=await msg({type:'QUEUE_ADD',url:'https://vimeo.com/third',...job});
  assert.equal(result.ok,true);
  result=await msg({type:'QUEUE_REMOVE',id:data.apexQueue[1].id});
  assert.equal(result.ok,true);
  assert.equal(data.apexQueue.length,1);
  ports[0].emit({type:'progress',percent:42,message:'42% descargado'});
  await delay();
  assert.equal(data.apexJob.percent,42);
  ports[0].emit({type:'done',ok:true,file:'one.mp4',folder:'C:/Downloads'});
  await delay(30);
  assert.equal(ports.length,2);
  assert.equal(data.apexQueue.length,0);
  assert.equal(data.apexHistory[0].file,'one.mp4');
  result=await msg({type:'CANCEL_ACTIVE'});
  assert.equal(result.ok,true);
  assert.equal(ports[1].messages.at(-1).type,'cancel');
  ports[1].emit({type:'done',ok:false,cancelled:true,error:'cancelado'});
  await delay(20);
  assert.equal(data.apexJob.state,'cancelled');
  assert.equal(data.apexHistory[0].state,'cancelled');
  result=await msg({type:'PREVIEW',url:'https://youtube.com/watch?v=123'});
  assert.equal(result.title,'Test');
  await msg({type:'CLEAR_HISTORY'});
  assert.equal(data.apexHistory.length,0);
  console.log('PASS: background queue, sequential downloads, preview, cancellation, history');
})().catch(err=>{console.error(err);process.exitCode=1});
