// Offline GFM/KaTeX, file links, actual Edge TOC clicks and narrow rendering.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(repo,'outputs/external/solar_rho_snudd/20261112_fig4_run2');
const doc=path.join(repo,'docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_BENCHMARK.v3.4.1.md');
const deps=path.resolve(repo,'../../.experiment-auto-runs/cevns-threephase-20261105-high01/tmp/math-render-check');
const require=createRequire(path.join(deps,'package.json'));
const get=async name=>(await import(pathToFileURL(require.resolve(name)).href)).default;
const {unified}=await import(pathToFileURL(require.resolve('unified')).href);
const [parse,gfm,math,rehype,raw,slug,katex,html]=await Promise.all(['remark-parse','remark-gfm','remark-math','remark-rehype','rehype-raw','rehype-slug','rehype-katex','rehype-stringify'].map(get));
const {chromium}=createRequire(import.meta.url)('C:/Users/Ultimator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const selected=[doc,...['README.md','tools/README.md','tests/README.md','extensions/README.md','extensions/solar_rho_snudd/README.md',
 'outputs/README.md','outputs/external/README.md','outputs/external/solar_rho_snudd/README.md','docs/experiments/README.md',
 'docs/experiments/LATEST_EXPERIMENTS.md','docs/experiments/PandaX4T_XENONnT_SolarB8/README.md',
 'docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md'].map(p=>path.join(repo,p))];
for(const directory of ['', 'propagation_source','validation_cache','kernels','source_evidence','source','PandaX_paired','PandaX_US2','XENONnT'])selected.push(path.join(out,directory,'README.md'));
for(const [family,dataset] of [['PandaX4T','PandaX4T_2024_US2'],['XENONnT','XENONnT_2024_SolarB8']]){
 for(const f of ['README.md','phases/P09_snudd_full_inference.md','phases/P10_snudd_full_inference.md'])selected.push(path.join(repo,'workflows/cevns-pyeft/runs',family,dataset,f));
}
const preview=path.join(out,'preview');fs.mkdirSync(preview,{recursive:true});
const errors=[],cache=new Map();let formulas=0,clicks=0,images=0,links=0;
function walk(n,f){f(n);for(const c of n.children??[])walk(c,f);}
function capture(){return(tree,file)=>{file.data.ids=[];file.data.links=[];file.data.images=[];walk(tree,n=>{
 if(n.type!=='element')return;
 if(n.properties?.id)file.data.ids.push(String(n.properties.id));
 if(n.tagName==='a'&&n.properties?.href)file.data.links.push(String(n.properties.href));
 if(n.tagName==='img'&&n.properties?.src)file.data.images.push(String(n.properties.src));
});};}
const processor=unified().use(parse).use(gfm).use(math).use(rehype,{allowDangerousHtml:true}).use(raw).use(slug).use(katex,{throwOnError:true,strict:'error'}).use(capture).use(html);
async function compile(file){
 if(cache.has(file))return cache.get(file);
 const source=new TextDecoder('utf8',{fatal:true}).decode(fs.readFileSync(file));
 walk(unified().use(parse).use(gfm).use(math).parse(source),n=>{if(n.type==='math'||n.type==='inlineMath')formulas++;});
 const value=await processor.process(source),result={html:String(value),ids:value.data.ids,links:value.data.links,images:value.data.images};cache.set(file,result);
 if(result.ids.some((id,i,a)=>a.indexOf(id)!==i)||value.messages.length||result.html.includes('katex-error'))errors.push({file,reason:'duplicate anchor or math error',messages:value.messages.map(String)});
 return result;
}
const report=path.join(out,'READABILITY_VALIDATION.json');
if(!fs.existsSync(report))fs.writeFileSync(report,JSON.stringify({status:'RUNNING',scope:'this execution has not finished yet'})+'\n');
fs.writeFileSync(path.join(preview,'README.md'),'# v3.4.1实际渲染\n\n[HTML](inference.html) · [桌面](inference_desktop.png) · [Source](inference_source.png) · [Statistics](inference_statistics.png) · [论文比较](inference_comparison.png) · [420px](inference_narrow.png)\n');
for(const file of selected){
 const value=await compile(file);
 for(const href of [...value.links,...value.images]){
  links++;
  if(/^[a-z][a-z0-9+.-]*:/i.test(href))continue;
  const hash=href.indexOf('#'),name=decodeURIComponent(hash<0?href:href.slice(0,hash)),anchor=hash<0?'':decodeURIComponent(href.slice(hash+1));
  const target=name?path.resolve(path.dirname(file),name):file;
  if(!fs.existsSync(target)){errors.push({file,href,reason:'missing local target'});continue;}
  if(anchor&&target.endsWith('.md')&&!(await compile(target)).ids.includes(anchor))errors.push({file,href,reason:'missing anchor'});
 }
}
const rendered=await compile(doc),destination=path.join(preview,'inference.html');
const body=rendered.html.replace(/(href|src)="([^"#][^"]*)"/g,(all,attribute,href)=>/^[a-z][a-z0-9+.-]*:/i.test(href)?all:attribute+'="'+pathToFileURL(path.resolve(path.dirname(doc),decodeURIComponent(href.split('#')[0]))).href+(href.includes('#')?'#'+href.split('#')[1]:'')+'"');
const css=pathToFileURL(path.join(deps,'node_modules/katex/dist/katex.min.css')).href;
fs.writeFileSync(destination,'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="'+css+'"><style>body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1160px;margin:24px auto;padding:0 24px 85vh;color:#243142;overflow-wrap:anywhere}h1{font-size:26px}a{color:#1761a0}table{display:block;max-width:100%;overflow:auto;border-collapse:collapse;font-size:14px}th,td{border:1px solid #dce3eb;padding:8px;min-width:70px}pre{overflow:auto;background:#f5f7fa;padding:12px}code{white-space:pre-wrap;overflow-wrap:anywhere}.katex{white-space:nowrap;overflow-wrap:normal;word-break:normal;display:inline-block;max-width:100%;overflow-x:auto;vertical-align:middle}.katex-display{max-width:100%;overflow:auto}img{max-width:100%}</style><body>'+body+'</body>');
const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu','--no-first-run']});
let narrow;
try{
 const page=await browser.newPage({viewport:{width:1360,height:1000}});
 await page.goto(pathToFileURL(destination).href);await page.evaluate(()=>document.fonts.ready);
 await page.screenshot({path:path.join(preview,'inference_desktop.png')});
 const broken=await page.locator('img').evaluateAll(nodes=>nodes.filter(n=>!n.complete||!n.naturalWidth).length);
 images=rendered.images.length;if(broken)errors.push({file:doc,brokenImages:broken});
 for(const id of ['status','source','nuclear','detector','prediction','statistics','comparison','controls','validation','gaps','references']){
  await page.locator('a[href="#'+id+'"]').first().click();if(new URL(page.url()).hash!=='#'+id)errors.push({file:doc,id,reason:'TOC click failed'});clicks++;
  await page.locator('a[href="#toc"]').first().click();if(new URL(page.url()).hash!=='#toc')errors.push({file:doc,id,reason:'return click failed'});clicks++;
 }
 for(const id of ['source','statistics','comparison']){await page.locator('#'+id).evaluate(n=>n.scrollIntoView());await page.screenshot({path:path.join(preview,'inference_'+id+'.png')});}
 await page.setViewportSize({width:420,height:1000});await page.goto(pathToFileURL(destination).href);
 narrow=await page.evaluate(()=>({viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,mathErrors:document.querySelectorAll('.katex-error').length}));
 await page.screenshot({path:path.join(preview,'inference_narrow.png')});
 if(narrow.pageWidth>narrow.viewport+1||narrow.mathErrors)errors.push({file:doc,narrow});
}finally{await browser.close();}
const result={documents:selected.length,checkedLinks:links,mathExpressions:formulas,tocAndReturnClicks:clicks,loadedImages:images,narrow,errors,
 scope:'offline GFM/KaTeX and actual Edge navigation; no authentication of scientific source equivalence'};
fs.writeFileSync(report,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));process.exitCode=errors.length?1:0;
