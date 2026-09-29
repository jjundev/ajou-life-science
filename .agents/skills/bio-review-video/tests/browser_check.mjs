// Run: node browser_check.mjs RUN PUPPETEER_PACKAGE_JSON CHROME_EXE
// Uses installed local tooling, never downloads a browser.
import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import {createRequire} from 'node:module';
const [runArg,pkg,executablePath]=process.argv.slice(2);
const root=path.resolve(runArg);
const require=createRequire(path.resolve(pkg));
const puppeteer=require('puppeteer-core');
const server=http.createServer(async(req,res)=>{
  try {
    const relative=decodeURIComponent(new URL(req.url,'http://localhost').pathname).slice(1);
    const p=path.resolve(root,relative || 'index.html');
    if(!p.startsWith(root+path.sep)) throw Error('outside');
    const types={'.html':'text/html','.css':'text/css','.js':'text/javascript','.woff2':'font/woff2','.svg':'image/svg+xml'};
    res.setHeader('Content-Type',types[path.extname(p)]||'application/octet-stream');
    res.end(await fs.readFile(p));
  } catch {res.statusCode=404;res.end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base='http://127.0.0.1:'+server.address().port+'/';
const browser=await puppeteer.launch({executablePath,headless:true,args:['--no-sandbox','--hide-scrollbars']});
const results=[];
try{
 const timeline=JSON.parse(await fs.readFile(path.join(root,'source/timeline.json'),'utf8'));
 const theme=JSON.parse(await fs.readFile(path.join(root,'source/theme.json'),'utf8'));
 const manifest=JSON.parse(await fs.readFile(path.join(root,'manifest.json'),'utf8'));
 await fs.mkdir(path.join(root,'verification/frames'),{recursive:true});
 for(const scene of timeline.scenes){
  const meta=manifest.scenes.find(s=>s.id===scene.id);
  for(const osTheme of ['light','dark']){
   const page=await browser.newPage(); await page.setViewport({width:1920,height:1080});
   await page.emulateMediaFeatures([{name:'prefers-color-scheme',value:osTheme}]);
   const failures=[]; page.on('pageerror',e=>failures.push(e.message));
   await page.goto(base+scene.id+'.html',{waitUntil:'networkidle0'});
   await page.evaluate(()=>document.fonts.ready);
   const duration=(scene.last_frame-scene.first_frame)/30;
   const segs=timeline.segments.filter(s=>s.scene_id===scene.id);
   const times=new Set([.01,duration/2,Math.max(.01,duration-.01)]);
   for(const s of segs) for(const offset of [-.01,.01]){
     times.add(Math.max(0,(s.start_sample-scene.start_sample)/24000+offset));
     times.add(Math.min(duration-.001,(s.end_sample-scene.start_sample)/24000+offset));
   }
   for(const t of [...times].sort((a,b)=>b-a)){
    const result=await page.evaluate(({id,t})=>{
     window.__timelines[id].seek(t,false);
     const style=getComputedStyle(document.documentElement);
     const keys=['--bg','--surface','--ink','--ink-2','--line','--accent','--accent-ink','--warn','--prof','--supp','--danger'];
     const captions=[...document.querySelectorAll('.video-caption')].filter(e=>getComputedStyle(e).visibility!=='hidden'&&Number(getComputedStyle(e).opacity)>0);
     const clipping=[...document.querySelectorAll('h1,h3,.layer,.tag,.badge,.figure,.video-caption')].filter(e=>{
       if(getComputedStyle(e).visibility==='hidden')return false;
       const r=e.getBoundingClientRect();
       const limit=e.matches('.video-caption')?1080:908;
       return r.left<0||r.right>1920||r.top<0||r.bottom>limit||e.scrollHeight>e.clientHeight+2;
     }).map(e=>e.id||e.className);
     return {tokens:Object.fromEntries(keys.map(k=>[k,style.getPropertyValue(k).trim()])),
       fontReady:document.fonts.check('32px Pretendard')&&[...document.fonts].some(f=>f.family==='Pretendard'&&f.status==='loaded'),
       clipping,captionCount:captions.length};
    },{id:scene.id,t});
    const tokenMatch=Object.entries(theme.tokens[meta.template_kind]).every(([k,v])=>!Object.hasOwn(result.tokens,k)||result.tokens[k]===v.trim());
    results.push({scene:scene.id,osTheme,time:t,...result,tokenMatch,errors:[...failures]});
   }
   await page.evaluate(({id,t})=>window.__timelines[id].seek(t,false),{id:scene.id,t:duration/2});
   await page.screenshot({path:path.join(root,'verification/frames',scene.id+'-'+osTheme+'.png')});
   await page.close();
  }
 }
 const passed=results.every(r=>r.fontReady&&r.tokenMatch&&!r.clipping.length&&r.captionCount<=1&&!r.errors.length);
 await fs.writeFile(path.join(root,'verification/browser.json'),JSON.stringify({status:passed?'passed':'failed',results},null,2));
 if(!passed)process.exitCode=1;
}finally{await browser.close();server.close();}
