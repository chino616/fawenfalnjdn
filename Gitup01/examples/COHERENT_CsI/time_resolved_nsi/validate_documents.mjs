// Standalone Markdown/KaTeX/Edge QA; no runtime dependency or source certification.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {pathToFileURL,fileURLToPath} from 'node:url';

const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const workspace=path.resolve(repo,'../..');
const run=path.join(repo,'outputs/csi2021_time_nsi_20261108');
const base=path.join(repo,'workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved');
const doc=path.join(repo,'docs/experiments/COHERENT/CsI2021/time_resolved');
const modules=process.env.CSI_MARKDOWN_MODULES ?? path.join(workspace,'.experiment-auto-runs/cevns-threephase-20261105-high01/tmp/math-render-check/node_modules');
const sha=file=>createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const relative=file=>path.relative(repo,file).replaceAll('\\','/');
const imports=async name=>import(pathToFileURL(path.join(modules,name,'index.js')).href);
const {unified}=await imports('unified');
const [parse,gfm,math,toHtml,raw,slug,katex,stringify]=await Promise.all(
  ['remark-parse','remark-gfm','remark-math','remark-rehype','rehype-raw','rehype-slug','rehype-katex','rehype-stringify']
  .map(async name=>(await imports(name)).default));
function mathInventory(){return (tree,file)=>{let count=0;const visit=node=>{if(['math','inlineMath'].includes(node.type))count++;for(const child of node.children??[])visit(child);};visit(tree);file.data.mathNodes=count;};}
function capture(){return (tree,file)=>{file.data.ids=[];file.data.links=[];const visit=node=>{
  if(node.type==='element'){
    if(node.properties?.id)file.data.ids.push(String(node.properties.id));
    if(node.tagName==='a'&&node.properties?.href)file.data.links.push(String(node.properties.href));
    if(node.tagName==='img'&&node.properties?.src)file.data.links.push(String(node.properties.src));
  }for(const child of node.children??[])visit(child);
};visit(tree);};}
const processor=unified().use(parse).use(gfm).use(math).use(mathInventory).use(toHtml,{allowDangerousHtml:true})
  .use(raw).use(slug).use(katex,{throwOnError:true,strict:'error'}).use(capture).use(stringify);
const reportFiles=[path.join(run,'BENCHMARK.md'),path.join(base,'nsi_benchmark_20261108/08_NSI_FORWARD_BENCHMARK_REPORT.md'),path.join(doc,'NSI_BENCHMARK.md')];
const selected=[...new Set([
  ...['examples/COHERENT_CsI/README.md','examples/COHERENT_CsI/time_resolved_nsi/README.md','outputs/README.md'].map(name=>path.join(repo,name)),
  path.join(run,'README.md'),path.join(base,'README.md'),path.join(base,'nsi_benchmark_20261108/README.md'),path.join(doc,'README.md'),...reportFiles,
])];
const compiled=new Map();
async function compile(file){
  if(compiled.has(file))return compiled.get(file);
  const text=fs.readFileSync(file,'utf8');
  if(text.includes('\ufffd')||text.charCodeAt(0)===0xfeff)throw Error('Encoding: '+file);
  if(reportFiles.includes(file)&&text.includes('\r'))throw Error('Report must use LF: '+file);
  const result=await processor.process(text);
  const html=String(result);
  if(html.includes('katex-error')||result.messages.some(m=>m.fatal))throw Error('Math rendering failed: '+file);
  if(new Set(result.data.ids).size!==result.data.ids.length)throw Error('Duplicate IDs: '+file);
  const value={html,...result.data};compiled.set(file,value);return value;
}
let count=0;const records=[];const generatedTargets=[];
for(const file of selected){
  const data=await compile(file);let n=0;
  for(const href of data.links){
    if(/^(https?:|mailto:|data:)/.test(href))continue;
    const hash=href.indexOf('#');const name=hash<0?href:href.slice(0,hash);
    const anchor=hash<0?'':decodeURIComponent(href.slice(hash+1));
    const target=name?path.resolve(path.dirname(file),decodeURIComponent(name)):file;
    if(!fs.existsSync(target)){
      const produced=[path.join(run,'DOCUMENT_LINK_CHECKS.json'),path.join(run,'document-preview-nsi.png')];
      if(produced.includes(target)){generatedTargets.push(target);continue;}
      throw Error('Missing target: '+relative(file)+' -> '+href);
    }
    if(anchor&&target.endsWith('.md')&&!(await compile(target)).ids.includes(anchor))throw Error('Missing anchor: '+href);
    n++;
  }
  count+=n;records.push({file:relative(file),sha256:sha(file),localLinksAndAnchors:n,mathNodes:data.mathNodes});
}
const require=createRequire(import.meta.url);
const katexRequire=createRequire(path.join(fs.realpathSync(path.join(modules,'rehype-katex')),'package.json'));
const css=katexRequire.resolve('katex/dist/katex.min.css');
const {chromium}=require(process.env.CSI_PLAYWRIGHT_MODULE ?? path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
const browser=await chromium.launch({executablePath:process.env.CSI_EDGE_EXECUTABLE??'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
const clicks=[];
const sections=['scope','inputs','nsi','counts','validation','figures','limits','reproduce'];
const style='body{font:16px/1.7 "Microsoft YaHei",sans-serif;max-width:1120px;margin:26px auto;padding:0 24px}a{color:#1761a0;overflow-wrap:anywhere}h1{font-size:28px}h2{margin-top:2em;border-bottom:1px solid #dce3eb}table{display:block;max-width:100%;overflow:auto;border-collapse:collapse;margin:20px 0;font-size:14px}th,td{border:1px solid #dce3eb;padding:8px 12px;min-width:100px;max-width:470px;vertical-align:top;overflow-wrap:anywhere}th{background:#f2f5f9}code{font:14px Consolas,monospace;overflow-wrap:anywhere}pre{overflow:auto;padding:15px;background:#f5f7fa}a[id]{scroll-margin-top:20px}.katex-display{overflow-x:auto;overflow-y:hidden}img{max-width:100%;height:auto}';
try{
  const page=await browser.newPage({viewport:{width:1200,height:900}});
  for(let i=0;i<reportFiles.length;i++){
    const file=reportFiles[i];const data=await compile(file);
    const html=data.html.replace(/(href|src)="([^"]+)"/g,(match,key,href)=>{
      if(/^(https?:|mailto:|#|data:)/.test(href))return match;
      const hash=href.indexOf('#');const name=hash<0?href:href.slice(0,hash);const anchor=hash<0?'':href.slice(hash);
      return key+'="'+pathToFileURL(path.resolve(path.dirname(file),decodeURIComponent(name))).href+anchor+'"';
    });
    const preview=path.join(run,'document-preview-'+i+'.html');
    fs.writeFileSync(preview,'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><link rel="stylesheet" href="'+pathToFileURL(css).href+'"><style>'+style+'</style><body>'+html+'</body></html>');
    await page.goto(pathToFileURL(preview).href);await page.evaluate(()=>document.fonts.ready);
    if(await page.locator('.katex-error').count())throw Error('Browser math error');
    if(await page.locator('a[href="#report-toc"]').count()!==sections.length)throw Error('Incomplete returns');
    if(i===0)await page.screenshot({path:path.join(run,'document-preview-desktop.png')});
    for(let j=0;j<sections.length;j++){
      const section=sections[j];await page.locator('a[href="#'+section+'"]').first().click();
      const top=await page.locator('#'+section).evaluate(e=>e.getBoundingClientRect().top);
      if(new URL(page.url()).hash!=='#'+section||top < -1||top > 820)throw Error('Jump failed: '+section);
      if(i===0&&['nsi','counts'].includes(section))await page.screenshot({path:path.join(run,'document-preview-'+section+'.png')});
      await page.locator('a[href="#report-toc"]').nth(j).click();
      if(new URL(page.url()).hash!=='#report-toc')throw Error('Return failed');
    }
    await page.setViewportSize({width:720,height:900});await page.goto(pathToFileURL(preview).href);
    const width=await page.evaluate(()=>document.documentElement.scrollWidth);
    if(width>720)throw Error('Whole-page overflow: '+relative(file));
    if(i===0)await page.screenshot({path:path.join(run,'document-preview-narrow.png')});
    clicks.push({file:relative(file),actualSectionJumpsAndReturns:sections.length,mathNodes:data.mathNodes,narrowWidth:width,status:'PASS'});
    await page.setViewportSize({width:1200,height:900});
  }
}finally{await browser.close();}
const result={date:'2026-11-08',timezone:'Asia/Shanghai',status:'PASS',documents:records,localLinksAndAnchors:count,browserChecks:clicks,
  scope:'Selected local links/images, rendered anchors, actualTOC/returns, Markdown math/KaTeX and720px standalone Edge preview',
  outsideScope:'Live external URLs, Codex internal renderer, source authenticity and scientific paper equivalence',
  katexCSS:{path:css,sha256:sha(css)},validationScript:{path:fileURLToPath(import.meta.url),sha256:sha(new URL(import.meta.url))}};
fs.writeFileSync(path.join(run,'DOCUMENT_LINK_CHECKS.json'),JSON.stringify(result,null,2)+'\n');
for(const file of generatedTargets)if(!fs.existsSync(file))throw Error('Checker did not create its linked output: '+file);
console.log(JSON.stringify({status:result.status,documents:records.length,links:count,browserChecks:clicks},null,2));
