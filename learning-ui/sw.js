/* Cache only this site's learning assets, never external requests or records. */
const VERSION='__BUILD_VERSION__';
const CACHE='wkx-learning-'+VERSION;
const BASE=new URL('./',self.location.href);
const SHELL=['','index.html','catalog.js','app.js','records.js','style.css','learning-directions.js'];
const versioned=name=>new URL(name+(name.endsWith('.js')?'?v='+VERSION:''),BASE).href;
self.addEventListener('install',event=>event.waitUntil((async()=>{
 const cache=await caches.open(CACHE);
 for(const name of SHELL){try{const response=await fetch(versioned(name));if(await acceptable(new URL(versioned(name)),response))await cache.put(versioned(name),response);}catch{}}
})()));
self.addEventListener('message',event=>{if(event.data==='ACTIVATE_UPDATE')self.skipWaiting();});
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 for(const key of await caches.keys())if(key.startsWith('wkx-learning-')&&key!==CACHE)await caches.delete(key);
 await self.clients.claim();
})()));
async function acceptable(url,response){
 if(!response.ok)return false;
 const path=url.pathname.slice(BASE.pathname.length);
 if(path===''||path==='index.html')return (await response.clone().text()).includes('learning-directions.js');
 return true;
}
async function remember(cache,url,response){
 if(await acceptable(url,response)){
  await cache.put(url.href,response.clone());
  const keys=await cache.keys();while(keys.length>400)await cache.delete(keys.shift());
 }
 return response;
}
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);
 if(event.request.method!=='GET'||url.origin!==BASE.origin||!url.pathname.startsWith(BASE.pathname))return;
 const path=url.pathname.slice(BASE.pathname.length);
 if(!SHELL.includes(path)&&!/^((content|search|assets)\/|icon\.svg|manifest\.webmanifest)/.test(path))return;
 event.respondWith((async()=>{
  const cache=await caches.open(CACHE);
  const cached=await cache.match(event.request);
  if(event.request.mode==='navigate'){
   try{const response=await fetch(event.request,{signal:AbortSignal.timeout(4000)});if(await acceptable(url,response))return await remember(cache,url,response);if(cached)return cached;return response;}
   catch{if(cached)return cached;const shell=await cache.match(versioned(''));if(shell)return shell;throw Error('尚未缓存，请联网打开一次网站。');}
  }
  if(cached){event.waitUntil(fetch(event.request).then(r=>remember(cache,url,r)).catch(()=>{}));return cached;}
  return remember(cache,url,await fetch(event.request));
 })());
});
