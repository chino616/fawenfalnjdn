import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(repo,'outputs/solar_b8_sm/20261107_run1');
const dependencies=path.resolve(repo,'../../.experiment-auto-runs/cevns-threephase-20261105-high01/tmp/math-render-check');
const require=createRequire(path.join(dependencies,'package.json'));
const get=async name=>(await import(pathToFileURL(require.resolve(name)).href)).default;
const {unified}=await import(pathToFileURL(require.resolve('unified')).href);
const [parse,gfm,math,rehype,raw,slug,katex,html]=await Promise.all(['remark-parse','remark-gfm','remark-math','remark-rehype','rehype-raw','rehype-slug','rehype-katex','rehype-stringify'].map(get));
const {chromium}=createRequire(import.meta.url)('C:/Users/Ultimator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const selected=JSON.parse(fs.readFileSync(path.join(out,'DOC_SELECTION.json'),'utf8')).map(p=>path.join(repo,p));
const preview=path.join(out,'preview');fs.mkdirSync(preview,{recursive:true});
function walk(n,fn){fn(n);for(const child of n.children??[])walk(child,fn);}
function capture(){return(tree,file)=>{file.data.ids=[];file.data.links=[];walk(tree,n=>{if(n.type==='element'){if(n.properties?.id)file.data.ids.push(String(n.properties.id));if(n.tagName==='a'&&n.properties?.href)file.data.links.push(String(n.properties.href));}});};}
const processor=unified().use(parse).use(gfm).use(math).use(rehype,{allowDangerousHtml:true}).use(raw).use(slug).use(katex,{throwOnError:true,strict:'error'}).use(capture).use(html);
const cache=new Map(),errors=[];let formulas=0;
async function compile(file){
 if(cache.has(file))return cache.get(file);
 const source=new TextDecoder('utf8',{fatal:true}).decode(fs.readFileSync(file));
 const ast=unified().use(parse).use(gfm).use(math).parse(source);walk(ast,n=>{if(n.type==='math'||n.type==='inlineMath')formulas++;});
 const rendered=await processor.process(source);
 const record={html:String(rendered),ids:rendered.data.ids,links:rendered.data.links};cache.set(file,record);
 if(record.ids.some((id,i,a)=>a.indexOf(id)!==i)||rendered.messages.length||record.html.includes('katex-error'))errors.push({file,reason:'duplicate anchor or math rendering error'});
 return record;
}
for(const file of selected){
 const result=await compile(file);
 for(const href of result.links){
  if(/^[a-z][a-z0-9+.-]*:/i.test(href))continue;
  const i=href.indexOf('#');const name=decodeURIComponent(i<0?href:href.slice(0,i));const anchor=i<0?'':decodeURIComponent(href.slice(i+1));
  const target=name?path.resolve(path.dirname(file),name):file;
  if(!fs.existsSync(target)){errors.push({file,href,reason:'missing file'});continue;}
  if(anchor&&target.endsWith('.md')&&!(await compile(target)).ids.includes(anchor))errors.push({file,href,reason:'missing rendered anchor'});
 }
}
const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu','--no-first-run']});
const screens=[];let clicks=0;
try{
 for(const family of ['XENONnT','PandaX4T']){
  const file=selected.find(p=>p.includes(path.sep+family+path.sep)&&p.endsWith('experiment.physics.v2.2.md'));
  const result=await compile(file);const destination=path.join(preview,family+'_onboarding.html');
  const css=pathToFileURL(path.join(dependencies,'node_modules/katex/dist/katex.min.css')).href;
  const body=result.html.replace(/href="([^"#][^"]*)"/g,(all,href)=>/^[a-z]+:/i.test(href)?all:'href="'+pathToFileURL(path.resolve(path.dirname(file),decodeURIComponent(href.split('#')[0]))).href+(href.includes('#')?'#'+href.split('#')[1]:'')+'"');
  fs.writeFileSync(destination,'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="'+css+'"><style>body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1100px;margin:24px auto;padding:0 24px 85vh;color:#243142}h1{font-size:26px}h2{margin-top:2em}a{color:#1761a0}table{display:block;max-width:100%;overflow:auto;border-collapse:collapse;font-size:14px}th,td{border:1px solid #dce3eb;padding:8px;min-width:75px}pre{overflow:auto;background:#f5f7fa;padding:12px}code{overflow-wrap:anywhere}.katex-display{max-width:100%;overflow:auto}img{max-width:100%}</style><body>'+body+'</body>');
  const page=await browser.newPage({viewport:{width:1200,height:1000}});await page.goto(pathToFileURL(destination).href);await page.evaluate(()=>document.fonts.ready);
  await page.screenshot({path:path.join(preview,family+'_desktop.png')});
  for(const id of ['model','numbers','validation','reproduce']){
   await page.locator('a[href="#'+id+'"]').first().click();if(new URL(page.url()).hash!=='#'+id)errors.push({file,id,reason:'TOC click failed'});clicks++;
   if(id==='numbers')await page.screenshot({path:path.join(preview,family+'_numbers.png')});
   await page.locator('a[href="#toc"]').first().click();clicks++;
  }
  await page.setViewportSize({width:420,height:1000});await page.goto(pathToFileURL(destination).href);
  const narrow=await page.evaluate(()=>({viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,mathErrors:document.querySelectorAll('.katex-error').length}));
  await page.screenshot({path:path.join(preview,family+'_narrow.png')});
  if(narrow.pageWidth>narrow.viewport+1||narrow.mathErrors)errors.push({file,narrow});
  screens.push({family,narrow});await page.close();
 }
}finally{await browser.close();}
const report={documents:selected.length,mathExpressions:formulas,tocAndReturnClicks:clicks,errors,screens,scope:'Standalone Markdown/GFM/KaTeX in Edge; application internal renderer not inspected.'};
fs.writeFileSync(path.join(out,'READABILITY_VALIDATION.json'),JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(path.join(preview,'README.md'),'# Solar SM report previews\n\n'+screens.map(s=>'- ['+s.family+' desktop]('+s.family+'_desktop.png) · [counts]('+s.family+'_numbers.png) · [narrow]('+s.family+'_narrow.png)').join('\n')+'\n');
console.log(JSON.stringify(report,null,2));process.exitCode=errors.length?1:0;
