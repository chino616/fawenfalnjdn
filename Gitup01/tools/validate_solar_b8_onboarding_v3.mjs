// Current v3.0 reports only: real KaTeX, file/anchor/image checks and TOC clicks.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(repo,'outputs/solar_b8_onboarding_v3/20261109_layout_r1');
const dependencyRoot=path.resolve(repo,'../../.experiment-auto-runs/cevns-threephase-20261105-high01/tmp/math-render-check');
const require=createRequire(path.join(dependencyRoot,'package.json'));
const get=async n=>(await import(pathToFileURL(require.resolve(n)).href)).default;
const {unified}=await import(pathToFileURL(require.resolve('unified')).href);
const [parse,gfm,math,rehype,raw,slug,katex,html]=await Promise.all(['remark-parse','remark-gfm','remark-math','remark-rehype','rehype-raw','rehype-slug','rehype-katex','rehype-stringify'].map(get));
const {chromium}=createRequire(import.meta.url)('C:/Users/Ultimator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const selected=JSON.parse(fs.readFileSync(path.join(out,'DOC_SELECTION.json'),'utf8')).map(p=>path.join(repo,p));
const records=JSON.parse(fs.readFileSync(path.join(out,'EQUATION_RECORDS.json'),'utf8'));
const preview=path.join(out,'preview');fs.mkdirSync(preview,{recursive:true});
const errors=[],cache=new Map();let formulas=0,clicks=0,images=0;
function walk(n,f){f(n);for(const c of n.children??[])walk(c,f);}
function capture(){return(tree,file)=>{file.data.ids=[];file.data.links=[];file.data.images=[];walk(tree,n=>{if(n.type!=='element')return;
  if(n.properties?.id)file.data.ids.push(String(n.properties.id));
  if(n.tagName==='a'&&n.properties?.href)file.data.links.push(String(n.properties.href));
  if(n.tagName==='img'&&n.properties?.src)file.data.images.push(String(n.properties.src));
});};}
const processor=unified().use(parse).use(gfm).use(math).use(rehype,{allowDangerousHtml:true}).use(raw).use(slug).use(katex,{throwOnError:true,strict:'error'}).use(capture).use(html);
async function compile(file){
  if(cache.has(file))return cache.get(file);
  const source=new TextDecoder('utf8',{fatal:true}).decode(fs.readFileSync(file));
  const tree=unified().use(parse).use(gfm).use(math).parse(source);let h1=0;
  walk(tree,n=>{if(n.type==='math'||n.type==='inlineMath')formulas++;if(n.type==='heading'&&n.depth===1)h1++;});
  const rendered=await processor.process(source);
  const result={html:String(rendered),ids:rendered.data.ids,links:rendered.data.links,images:rendered.data.images};cache.set(file,result);
  if(result.ids.some((id,i,a)=>a.indexOf(id)!==i)||rendered.messages.length||result.html.includes('katex-error'))errors.push({file,reason:'duplicate anchor or math error'});
  if(file.includes('.v3.0.md')&&h1!==1)errors.push({file,h1,reason:'one H1 required'});
  return result;
}
for(const file of selected){
  const rendered=await compile(file);
  for(const href of [...rendered.links,...rendered.images]){
    if(/^[a-z][a-z0-9+.-]*:/i.test(href))continue;
    const hash=href.indexOf('#'),name=decodeURIComponent(hash<0?href:href.slice(0,hash)),anchor=hash<0?'':decodeURIComponent(href.slice(hash+1));
    const target=name?path.resolve(path.dirname(file),name):file;
    if(!fs.existsSync(target)){errors.push({file,href,reason:'missing file or image'});continue;}
    if(anchor&&target.endsWith('.md')&&!(await compile(target)).ids.includes(anchor))errors.push({file,href,reason:'missing rendered anchor'});
  }
}
const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu','--no-first-run']});
const screens=[];
try{
  const targets=selected.filter(p=>p.endsWith('.v3.0.md'));
  for(const file of targets){
    const rendered=await compile(file),combined=file.endsWith('SOLAR_B8_ONBOARDING.v3.0.md');
    const label=combined?'Combined':(file.includes(path.sep+'PandaX4T'+path.sep)?'PandaX4T':'XENONnT')+'_'+path.basename(file).split('.v3.0')[0];
    const destination=path.join(preview,label+'.html');
    const body=rendered.html.replace(/(href|src)="([^"#][^"]*)"/g,(all,attribute,href)=>/^[a-z][a-z0-9+.-]*:/i.test(href)?all:attribute+'="'+pathToFileURL(path.resolve(path.dirname(file),decodeURIComponent(href.split('#')[0]))).href+(href.includes('#')?'#'+href.split('#')[1]:'')+'"');
    const css=pathToFileURL(path.join(dependencyRoot,'node_modules/katex/dist/katex.min.css')).href;
    fs.writeFileSync(destination,'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="'+css+'"><style>body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1160px;margin:24px auto;padding:0 24px 85vh;color:#243142;overflow-wrap:anywhere}h1{font-size:26px}a{color:#1761a0}table{display:block;max-width:100%;overflow:auto;border-collapse:collapse;font-size:14px}th,td{border:1px solid #dce3eb;padding:8px;min-width:70px}pre{overflow:auto;background:#f5f7fa;padding:12px}code{overflow-wrap:anywhere}.katex{white-space:nowrap;overflow-wrap:normal;word-break:normal}.katex-display{max-width:100%;overflow:auto}img{max-width:100%}</style><body>'+body+'</body>');
    const page=await browser.newPage({viewport:{width:1280,height:1000}});await page.goto(pathToFileURL(destination).href);await page.evaluate(()=>document.fonts.ready);
    await page.screenshot({path:path.join(preview,label+'_desktop.png')});
    const brokenImages=await page.locator('img').evaluateAll(nodes=>nodes.filter(n=>!n.complete||n.naturalWidth===0).length);
    images+=rendered.images.length;if(brokenImages)errors.push({file,brokenImages});
    const ids=combined?['pandax-','xenon-'].flatMap(prefix=>['scope','source','target','modules','detector','observable','prediction','statistics','resources','status'].map(s=>prefix+s)):
      file.includes('experiment.physics.v3.0')?['scope','source','target','modules','detector','observable','prediction','statistics','resources','status']:['scope','inputs','results','handoff'];
    const back=combined?'all-toc':file.includes('experiment.physics.v3.0')?'report-toc':'toc';
    for(const id of ids){
      await page.locator('a[href="#'+id+'"]').first().click();if(new URL(page.url()).hash!=='#'+id)errors.push({file,id,reason:'TOC click failed'});clicks++;
      await page.locator('a[href="#'+back+'"]').first().click();clicks++;
    }
    if(file.includes('experiment.physics.v3.0')||combined){
      const id=combined?'xenon-benchmark-results':'benchmark-results';
      await page.locator('#'+id).evaluate(n=>n.scrollIntoView());await page.screenshot({path:path.join(preview,label+'_numbers.png')});
      const detector=combined?'xenon-detector':'detector';await page.locator('#'+detector).evaluate(n=>n.scrollIntoView());await page.screenshot({path:path.join(preview,label+'_response.png')});
    }
    await page.setViewportSize({width:420,height:1000});await page.goto(pathToFileURL(destination).href);
    const narrow=await page.evaluate(()=>({viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,mathErrors:document.querySelectorAll('.katex-error').length}));
    await page.screenshot({path:path.join(preview,label+'_narrow.png')});
    if(narrow.pageWidth>narrow.viewport+1||narrow.mathErrors)errors.push({file,narrow});
    screens.push({file:path.relative(repo,file).replaceAll('\\','/'),label,narrow});await page.close();
  }
}finally{await browser.close();}
const result={documents:selected.length,mathExpressions:formulas,numberedEquationCounts:Object.fromEntries(Object.entries(records).map(([k,v])=>[k,v.length])),tocAndReturnClicks:clicks,loadedImages:images,screens,errors,
  scope:'Standalone Markdown/GFM/KaTeX and file images in Edge; desktop application internal renderer not inspected.'};
fs.writeFileSync(path.join(out,'READABILITY_VALIDATION.json'),JSON.stringify(result,null,2)+'\n');
fs.writeFileSync(path.join(preview,'README.md'),'# Onboarding v3 previews\n\n'+screens.map(s=>'- ['+s.label+' desktop]('+s.label+'_desktop.png) · [narrow]('+s.label+'_narrow.png)').join('\n')+'\n');
console.log(JSON.stringify(result,null,2));process.exitCode=errors.length?1:0;
