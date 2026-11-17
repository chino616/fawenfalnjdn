// Offline GFM/KaTeX and actual local Edge navigation for the v3.5 contract.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const doc=path.join(repo,'docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_ONBOARDING.v3.5.md');
const out=path.join(repo,'outputs/external/solar_rho_snudd/20261112_trace_onboarding');
const deps=path.resolve(repo,'../../.experiment-auto-runs/cevns-threephase-20261105-high01/tmp/math-render-check');
const req=createRequire(path.join(deps,'package.json'));
const get=async name=>(await import(pathToFileURL(req.resolve(name)).href)).default;
const {unified}=await import(pathToFileURL(req.resolve('unified')).href);
const [parse,gfm,math,rehype,raw,slug,katex,html]=await Promise.all(['remark-parse','remark-gfm','remark-math','remark-rehype','rehype-raw','rehype-slug','rehype-katex','rehype-stringify'].map(get));
const {chromium}=createRequire(import.meta.url)('C:/Users/Ultimator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const selected=[doc,path.join(out,'README.md'),...['README.md','tools/README.md','extensions/solar_rho_snudd/README.md',
 'outputs/external/solar_rho_snudd/README.md','docs/experiments/README.md','docs/experiments/LATEST_EXPERIMENTS.md',
 'docs/experiments/PandaX4T_XENONnT_SolarB8/README.md','docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md',
 'workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/README.md','workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/README.md'].map(p=>path.join(repo,p))];
const preview=path.join(out,'preview');fs.mkdirSync(preview,{recursive:true});
const report=path.join(out,'READABILITY_VALIDATION.json');
if(!fs.existsSync(report))fs.writeFileSync(report,JSON.stringify({status:'RUNNING'})+'\n');
fs.writeFileSync(path.join(preview,'README.md'),'# v3.5文档实际渲染\n\n[HTML](onboarding.html) · [首页](desktop.png) · [截面](cross-section.png) · [事例数](events.png) · [实验差别](experiments.png) · [窄屏](narrow.png)\n');
const errors=[],cache=new Map();let mathCount=0,links=0,clicks=0;
function walk(n,f){f(n);for(const c of n.children??[])walk(c,f);}
function capture(){return(tree,file)=>{file.data.ids=[];file.data.links=[];walk(tree,n=>{if(n.type!=='element')return;
 if(n.properties?.id)file.data.ids.push(String(n.properties.id));if(n.tagName==='a'&&n.properties?.href)file.data.links.push(String(n.properties.href));});};}
const processor=unified().use(parse).use(gfm).use(math).use(rehype,{allowDangerousHtml:true}).use(raw).use(slug).use(katex,{throwOnError:true,strict:'error'}).use(capture).use(html);
async function compile(file){
 if(cache.has(file))return cache.get(file);
 const text=new TextDecoder('utf8',{fatal:true}).decode(fs.readFileSync(file));
 walk(unified().use(parse).use(gfm).use(math).parse(text),n=>{if(n.type==='math'||n.type==='inlineMath')mathCount++;});
 const value=await processor.process(text),result={html:String(value),ids:value.data.ids,links:value.data.links};cache.set(file,result);
 if(result.ids.some((id,i,a)=>a.indexOf(id)!==i)||value.messages.length||result.html.includes('katex-error'))errors.push({file,reason:'duplicate anchors or math error'});
 return result;
}
for(const file of selected){for(const href of (await compile(file)).links){
 links++;if(/^[a-z][a-z0-9+.-]*:/i.test(href))continue;
 const [name,anchor]=href.split('#'),target=name?path.resolve(path.dirname(file),decodeURIComponent(name)):file;
 if(!fs.existsSync(target)){errors.push({file,href,reason:'missing file'});continue;}
 if(anchor&&target.endsWith('.md')&&!(await compile(target)).ids.includes(decodeURIComponent(anchor)))errors.push({file,href,reason:'missing anchor'});
}}
const value=await compile(doc),destination=path.join(preview,'onboarding.html');
const body=value.html.replace(/href="([^"#][^"]*)"/g,(all,href)=>/^[a-z][a-z0-9+.-]*:/i.test(href)?all:'href="'+pathToFileURL(path.resolve(path.dirname(doc),decodeURIComponent(href.split('#')[0]))).href+(href.includes('#')?'#'+href.split('#')[1]:'')+'"');
const css=pathToFileURL(path.join(deps,'node_modules/katex/dist/katex.min.css')).href;
fs.writeFileSync(destination,'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="'+css+'"><style>body{font:16px/1.8 "Microsoft YaHei",sans-serif;max-width:1160px;margin:24px auto;padding:0 24px 85vh;color:#243142;overflow-wrap:anywhere}h1{font-size:26px}a{color:#1761a0}table{display:block;max-width:100%;overflow:auto;border-collapse:collapse;font-size:14px}th,td{border:1px solid #dce3eb;padding:8px;min-width:70px}pre{overflow:auto;background:#f5f7fa;padding:12px}code{white-space:pre-wrap;overflow-wrap:anywhere}.katex{white-space:nowrap;overflow-wrap:normal;word-break:normal;vertical-align:middle}.katex-display{max-width:100%;overflow-x:auto;overflow-y:hidden;padding:8px 0}</style><body>'+body+'</body>');
const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu','--no-first-run']});
let narrow;
try{
 const page=await browser.newPage({viewport:{width:1360,height:1000}});await page.goto(pathToFileURL(destination).href);await page.evaluate(()=>document.fonts.ready);
 await page.screenshot({path:path.join(preview,'desktop.png')});
 for(const id of ['scope','source','cross-section','events','experiments','statistics','implementation','handoff','references']){
  await page.locator('a[href="#'+id+'"]').first().click();if(new URL(page.url()).hash!=='#'+id)errors.push({id,reason:'TOC click failed'});clicks++;
  await page.locator('a[href="#toc"]').first().click();if(new URL(page.url()).hash!=='#toc')errors.push({id,reason:'return click failed'});clicks++;
 }
 for(const id of ['cross-section','events','experiments']){
  await page.locator('#'+id).evaluate(n=>n.scrollIntoView());
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.screenshot({path:path.join(preview,id+'.png')});
 }
 await page.setViewportSize({width:420,height:1000});await page.goto(pathToFileURL(destination).href);
 narrow=await page.evaluate(()=>({viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,mathErrors:document.querySelectorAll('.katex-error').length}));
 await page.screenshot({path:path.join(preview,'narrow.png')});if(narrow.pageWidth>narrow.viewport+1||narrow.mathErrors)errors.push({narrow});
}finally{await browser.close();}
const result={documents:selected.length,linksChecked:links,mathExpressions:mathCount,tocAndReturnClicks:clicks,narrow,errors,
 scope:'document equations, file/anchor navigation and rendering only; no new physical-runtime implementation or numerical reproduction claim'};
fs.writeFileSync(report,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));process.exitCode=errors.length?1:0;
