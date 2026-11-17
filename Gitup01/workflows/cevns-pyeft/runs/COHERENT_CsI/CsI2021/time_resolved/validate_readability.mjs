// Documentation-only QA. Dependencies stay outside the physics Runtime.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const run = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(run, '../../../../../..');
const workspace = path.resolve(repo, '../..');
const modules = process.env.CSI_MARKDOWN_MODULES ?? path.join(workspace,
  '.experiment-auto-runs/cevns-threephase-20261105-high01/tmp/math-render-check/node_modules');
const playwrightModule = process.env.CSI_PLAYWRIGHT_MODULE ?? path.join(os.homedir(),
  '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const edge = process.env.CSI_EDGE_EXECUTABLE ?? 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const output = path.join(run, 'evidence/readability');
fs.mkdirSync(output, {recursive: true});
const relative = file => path.relative(repo, file).replaceAll('\\', '/');
const sha256 = file => createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const moduleValue = async name => import(pathToFileURL(path.join(modules, name, 'index.js')).href);
const {unified} = await moduleValue('unified');
const [remarkParse, remarkGfm, remarkMath, remarkRehype, rehypeRaw, rehypeKatex, rehypeSlug, rehypeStringify] =
  await Promise.all(['remark-parse', 'remark-gfm', 'remark-math', 'remark-rehype', 'rehype-raw',
    'rehype-katex', 'rehype-slug', 'rehype-stringify'].map(async name => (await moduleValue(name)).default));
// Resolve from the real rehype-katex package, so a pnpm root alias cannot supply
// CSS from a different KaTeX version than the renderer's transitive dependency.
const katexRequire = createRequire(fs.realpathSync(path.join(modules, 'rehype-katex/index.js')));
const katexEntry = katexRequire.resolve('katex');
const katexCss = katexRequire.resolve('katex/dist/katex.min.css');
const katexVersion = JSON.parse(fs.readFileSync(path.resolve(katexEntry, '../../package.json'), 'utf8')).version;

const doc = path.join(repo, 'docs/experiments/COHERENT/CsI2021/time_resolved');
const selected = [
  'AGENTS.md',
  'workflows/_shared/references/onboarding/data-provenance-contract.md',
  'workflows/_shared/references/onboarding/experiment-physics-report-contract.md',
  'workflows/cevns-pyeft/skills/onboarding/cevns-onboarding/SKILL.md',
  'data/responses/README.md',
  'docs/references/COHERENT/README.md',
  'docs/experiments/COHERENT/CsI2021/README.md',
  ...['README.md', 'experiment.physics.md', 'experiment.physics.summary.md', 'EXPERIMENT_USER_INPUT.md']
    .map(name => relative(path.join(doc, name))),
  relative(path.join(run, '../README.md')),
  ...['README.md', 'P02_MISSING_AND_CONFLICTS.md', 'data/README.md', 'sources/README.md',
    'sources/official/README.md', 'sources/upstream_nuclear/README.md', 'evidence/README.md',
    'evidence/legacy_resolution/README.md', 'evidence/readability/README.md', 'evidence/REVIEW_REPORT.md',
    'revisions/README.md'].map(name => relative(path.join(run, name))),
].map(name => path.join(repo, name));
const strictEncoding = new Set(['experiment.physics.md', 'experiment.physics.summary.md',
  'EXPERIMENT_USER_INPUT.md'].map(name => path.join(doc, name)));
strictEncoding.add(path.join(run, 'P02_MISSING_AND_CONFLICTS.md'));
const expectedMath = JSON.parse(fs.readFileSync(path.join(run, 'P03_PHYSICS_CONTRACT.yaml'), 'utf8'))
  .report_spec.formulas.length;
if (expectedMath !== 9) throw Error('Review expected display-math count after changing the scientific contract');

function mathCapture() {
  return (tree, file) => {
    file.data.math = [];
    file.data.inlineMath = 0;
    function visit(node) {
      if (node.type === 'math') file.data.math.push(node.value);
      if (node.type === 'inlineMath') file.data.inlineMath++;
      for (const child of node.children ?? []) visit(child);
    }
    visit(tree);
  };
}
function htmlCapture() {
  return (tree, file) => {
    file.data.ids = [];
    file.data.links = [];
    file.data.headings = [];
    function visit(node) {
      if (node.type === 'element') {
        if (node.properties?.id) file.data.ids.push(String(node.properties.id));
        if (node.tagName === 'a' && node.properties?.href) file.data.links.push(String(node.properties.href));
        if (/^h[1-6]$/.test(node.tagName)) file.data.headings.push(Number(node.tagName[1]));
      }
      for (const child of node.children ?? []) visit(child);
    }
    visit(tree);
  };
}
const processor = unified().use(remarkParse).use(remarkGfm).use(remarkMath).use(mathCapture)
  .use(remarkRehype, {allowDangerousHtml: true}).use(rehypeRaw)
  .use(rehypeKatex, {throwOnError: true}).use(rehypeSlug).use(htmlCapture).use(rehypeStringify);
const compiled = new Map();
async function compile(file) {
  if (compiled.has(file)) return compiled.get(file);
  const text = fs.readFileSync(file, 'utf8');
  if (strictEncoding.has(file) && (text.charCodeAt(0) === 0xfeff || text.includes('\r') ||
      /[\u0000-\u0008\u000b\u000c\u000e-\u001f\ufffd]/.test(text))) {
    throw Error('UTF-8/LF/control-character check failed: ' + relative(file));
  }
  const rendered = await processor.process(text);
  if (rendered.messages.some(message => message.fatal || message.source === 'rehype-katex')) {
    throw Error('Math rendering diagnostic: ' + relative(file) + ' ' + rendered.messages.join('; '));
  }
  const result = {html: String(rendered), ...rendered.data};
  if (new Set(result.ids).size !== result.ids.length) throw Error('Duplicate rendered ID: ' + relative(file));
  if (strictEncoding.has(file)) {
    if (result.headings.filter(level => level === 1).length !== 1) throw Error('Expected one H1: ' + relative(file));
    for (let i = 1; i < result.headings.length; i++) {
      if (result.headings[i] > result.headings[i - 1] + 1) throw Error('Skipped heading level: ' + relative(file));
    }
  }
  compiled.set(file, result);
  return result;
}

const records = [];
let localLinks = 0;
let externalLinks = 0;
for (const file of selected) {
  const rendered = await compile(file);
  let count = 0;
  for (const href of rendered.links) {
    if (/^(https?:|mailto:|data:)/.test(href)) {
      externalLinks++;
      continue;
    }
    const delimiter = href.indexOf('#');
    const name = delimiter < 0 ? href : href.slice(0, delimiter);
    const anchor = delimiter < 0 ? '' : decodeURIComponent(href.slice(delimiter + 1));
    const target = name ? path.resolve(path.dirname(file), decodeURIComponent(name)) : file;
    if (!fs.existsSync(target)) throw Error('Missing local link: ' + relative(file) + ' -> ' + href);
    if (anchor && target.endsWith('.md') && !(await compile(target)).ids.includes(anchor)) {
      throw Error('Missing Markdown anchor: ' + relative(file) + ' -> ' + href);
    }
    count++;
  }
  localLinks += count;
  records.push({file: relative(file), sha256: sha256(file), localLinksAndAnchors: count,
    uniqueIds: rendered.ids.length, displayMath: rendered.math.length});
}
const detailed = path.join(doc, 'experiment.physics.md');
const detail = await compile(detailed);
if (detail.math.length !== expectedMath) throw Error('Display-math AST count differs from P03');
const tags = detail.math.map(latex => Number(latex.match(/\\tag\{(\d+)\}/)?.[1]));
if (!tags.every((tag, index) => tag === index + 1)) throw Error('Formula tags must be sequential');

const style = `body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1100px;margin:26px auto;
padding:0 24px;color:#243142;background:white}a{color:#1761a0;text-decoration:none;overflow-wrap:anywhere}
h1{font-size:28px;line-height:1.4}h2{margin-top:2em;border-bottom:1px solid #dce3eb;padding-bottom:.3em;font-size:23px}
table{display:block;max-width:100%;overflow-x:auto;border-collapse:collapse;margin:20px 0;font-size:14px}
th,td{border:1px solid #dce3eb;padding:8px 12px;vertical-align:top;min-width:105px;max-width:420px;overflow-wrap:anywhere}
th{background:#f2f5f9}pre{overflow:auto;padding:15px;background:#f5f7fa}code{font:14px Consolas,monospace;overflow-wrap:anywhere}
a[id]{scroll-margin-top:20px}.katex-display{overflow-x:auto;overflow-y:hidden;padding:4px 0}`;
const previews = [];
for (const [source, name] of [[detailed, 'detailed'],
  [path.join(doc, 'EXPERIMENT_USER_INPUT.md'), 'user_input'],
  [path.join(doc, 'experiment.physics.summary.md'), 'summary']]) {
  const file = path.join(output, name + '.html');
  fs.writeFileSync(file, '<!doctype html><html lang="zh-CN"><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1"><title>CsI2021 ' + name + '</title>' +
    '<style>' + style + '</style><link rel="stylesheet" href="' +
    pathToFileURL(katexCss).href + '"><body>' +
    (await compile(source)).html + '</body></html>');
  previews.push({source, name, file});
}
const require = createRequire(import.meta.url);
const {chromium} = require(playwrightModule);
const context = await chromium.launchPersistentContext(path.join(os.tmpdir(), 'csi-time-onboarding-r2-render'), {
  executablePath: edge, headless: true, viewport: {width: 1200, height: 900},
  args: ['--disable-gpu', '--no-first-run', '--disable-extensions'],
});
const browser = {desktopViewport: [1200, 900], narrowViewport: [720, 900], documents: []};
try {
  const page = await context.newPage();
  for (const preview of previews) {
    await page.setViewportSize({width: 1200, height: 900});
    await page.goto(pathToFileURL(preview.file).href);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({path: path.join(output, preview.name + '_desktop.png')});
    if (await page.locator('.katex-error').count()) throw Error('Visible KaTeX error: ' + preview.name);
    const renderedMath = await page.locator('.katex-display').count();
    if (renderedMath !== (await compile(preview.source)).math.length) throw Error('Browser math-count mismatch');
    if (renderedMath) {
      const positions = await page.locator('.katex-display').evaluateAll(elements => elements.map(element => {
        const tag = element.querySelector('.tag, .katex-tag');
        return {position: tag ? getComputedStyle(tag).position : null,
          rightGap: tag ? element.getBoundingClientRect().right - tag.getBoundingClientRect().right : null};
      }));
      if (positions.some(item => item.position !== 'absolute' || Math.abs(item.rightGap) > 5)) {
        throw Error('Formula-number layout/CSS version mismatch: ' + preview.name);
      }
    }
    const sections = preview.name === 'detailed' ? ['identity', 'source', 'target', 'nuclear', 'constants',
      'detector', 'observable', 'prediction', 'statistics', 'handoff'] :
      preview.name === 'user_input' ? ['input-target', 'input-materials', 'input-values', 'input-gaps',
        'input-qa', 'input-handoff', 'input-sources'] : [];
    if (sections.length && await page.locator('a[href="#report-toc"]').count() !== sections.length) {
      throw Error('Each main section needs its return-to-TOC link: ' + preview.name);
    }
    for (let index = 0; index < sections.length; index++) {
      const section = sections[index];
      await page.locator('a[href="#' + section + '"]').first().click();
      if (new URL(page.url()).hash !== '#' + section ||
          Math.abs(await page.locator('#' + section).evaluate(element => element.getBoundingClientRect().top)) > 100) {
        throw Error('TOC jump/visibility failed: ' + section);
      }
      if (preview.name === 'detailed' && ['source', 'nuclear', 'detector', 'observable', 'statistics'].includes(section)) {
        await page.screenshot({path: path.join(output, 'detailed_' + section + '.png')});
      }
      await page.locator('a[href="#report-toc"]').nth(index).click();
      if (new URL(page.url()).hash !== '#report-toc' ||
          Math.abs(await page.locator('#report-toc').evaluate(element => element.getBoundingClientRect().top)) > 100) {
        throw Error('Return-to-TOC jump/visibility failed: ' + section);
      }
    }
    const mathNodes = await page.locator('.katex-display').all();
    for (let index = 0; index < mathNodes.length; index++) {
      await mathNodes[index].scrollIntoViewIfNeeded();
      await mathNodes[index].screenshot({path: path.join(output, preview.name + '_formula_' + (index + 1) + '.png')});
    }
    await page.setViewportSize({width: 720, height: 900});
    await page.goto(pathToFileURL(preview.file).href);
    await page.screenshot({path: path.join(output, preview.name + '_narrow.png')});
    const narrow = await page.evaluate(() => ({viewport: innerWidth, pageWidth: document.documentElement.scrollWidth,
      scrollableTables: Array.from(document.querySelectorAll('table')).filter(table => table.scrollWidth > table.clientWidth).length}));
    if (narrow.pageWidth > narrow.viewport) throw Error('Whole-page horizontal overflow: ' + preview.name);
    const horizontalTables = page.locator('table');
    for (let index = 0; index < await horizontalTables.count(); index++) {
      const result = await horizontalTables.nth(index).evaluate(table => {
        table.scrollLeft = table.scrollWidth;
        return {needed: table.scrollWidth > table.clientWidth, scrollLeft: table.scrollLeft};
      });
      if (result.needed && result.scrollLeft <= 0) throw Error('Wide table cannot scroll: ' + preview.name);
    }
    if (preview.name === 'detailed') {
      await page.locator('a[href="#detector"]').first().click();
      await page.screenshot({path: path.join(output, 'detailed_detector_narrow_sources.png')});
      await page.locator('table').evaluateAll(tables => tables.forEach(table => { table.scrollLeft = 0; }));
      await page.screenshot({path: path.join(output, 'detailed_detector_narrow.png')});
    }
    browser.documents.push({name: preview.name, sectionJumpsAndReturns: sections.length,
      displayMath: renderedMath, narrow, status: 'PASS'});
  }
} finally {
  await context.close();
}
const result = {revision: 'r2', date: '2026-11-06', timezone: 'Asia/Shanghai', machineStatus: 'PASS',
  documents: records.length, localLinksAndAnchors: localLinks, externalLinksRecordedWithoutNetworkCheck: externalLinks,
  strictEncodingDocuments: strictEncoding.size, records, browser, formulaTags: tags,
  dependencyPaths: {markdownModules: modules, katexRenderer: katexEntry, katexCss, playwright: playwrightModule, browser: edge},
  dependencyVersions: {katex: katexVersion},
  previews: previews.map(item => ({source: relative(item.source), html: relative(item.file)})),
  scope: 'Standalone CommonMark/GFM/math AST, KaTeX and headless Edge; local links and rendered anchors of selected documents',
  outsideScope: 'Codex internal Markdown renderer, live availability of external URLs, scientific source authentication or benchmark reproduction',
  visualReview: 'Recorded separately in REVIEW_REPORT.md after screenshots are inspected'};
fs.writeFileSync(path.join(run, 'evidence/READABILITY_CHECKS.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({machineStatus: result.machineStatus, documents: result.documents,
  localLinksAndAnchors: localLinks, strictEncodingDocuments: strictEncoding.size, browser}, null, 2));
