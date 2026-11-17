// Author one current-results workbook using the bundled artifact-tool runtime.
// Numerical fits and interval topology remain owned by the scientific JSON.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

// Windows sandbox denied a junction to the read-only WindowsApps bundle.
// Resolve the public package from the loader-provided directory instead.
const bundledModules = process.argv[3];
if (!bundledModules || !path.isAbsolute(bundledModules)) throw new Error('Pass the bundled node_modules directory as argument 3');
const bundledRequire = createRequire(path.join(bundledModules, '__public_package_resolver__.cjs'));
const { Workbook, SpreadsheetFile } = await import(pathToFileURL(bundledRequire.resolve('@oai/artifact-tool')).href);

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const out = path.resolve(process.argv[2] ?? path.join(root, 'outputs', 'results_summary_20261115_run2'));
const data = JSON.parse(await fs.readFile(path.join(out, 'TABLES.json'), 'utf8'));
const wb = Workbook.create();
const sheets = new Map();
const formulas = [];
const colors = {navy:'#215B84', text:'#243746', muted:'#5F6D76', pale:'#F1F5F8', rule:'#A5B4BE'};
const errors = /#REF!|#DIV\/0!|#VALUE!|#NAME\?|#N\/A|#NUM!|#NULL!|#SPILL!|#CALC!/;

function letter(index) {
  let out = '', n = index + 1;
  while (n) { out = String.fromCharCode(65 + (n - 1) % 26) + out; n = Math.floor((n - 1) / 26); }
  return out;
}
function address(t, key, r) {
  const i = t.columns.findIndex(c => c.key === key);
  if (i < 0) throw new Error(`Missing column ${t.id}.${key}`);
  return `${letter(i)}${r}`;
}
function setFormula(t, key, r, value, expected) {
  const cell = address(t, key, r);
  sheets.get(t.id).getRange(cell).formulas = [[value]];
  formulas.push({sheet:t.sheet, cell, expected, formula:value});
}
function equal(a,b) {
  if (b === null || b === undefined) return a === '' || a === null || a === undefined;
  return typeof a === 'number' && Math.abs(a-b) <= 2e-7 + 2e-9*Math.abs(b);
}

// Make every sheet before adding cross-sheet formulas.
for (const t of data.tables) sheets.set(t.id, wb.worksheets.add(t.sheet));
for (const [index,t] of data.tables.entries()) {
  const s = sheets.get(t.id);
  s.showGridLines = false;
  if (index < 8) s.tabColor = colors.navy;
  if (t.id === 'definitions') s.tabColor = '#87939B';
  const end = letter(t.columns.length-1), last = t.rows.length+6;
  const used = s.getRange(`A1:${end}${last}`);
  used.format.font = {name:'Arial',size:10,color:colors.text};
  used.format.verticalAlignment = 'center';
  used.format.rowHeight = 23;
  used.format.wrapText = false;
  s.getRange('A1').format.rowHeight = 9;
  s.getRange('A2').values = [[t.title]];
  s.getRange('A2').format.font = {name:'Arial',size:14,bold:true,color:colors.text};
  s.getRange('A2').format.rowHeight = 29;
  s.getRange('A3').values = [[t.note]];
  s.getRange('A3').format.font = {name:'Arial',size:10,italic:true,color:colors.muted};
  s.getRange(`A4:${letter(Math.min(t.preview_columns-1,t.columns.length-1))}4`).format.borders = {bottom:{style:'thin',color:colors.rule}};
  s.getRange('A5').format.rowHeight = 9;
  s.getRange(`A6:${end}6`).values = [t.columns.map(c => c.label)];
  s.getRange(`A7:${end}${last}`).values = t.rows.map(r => t.columns.map(c => r[c.key] ?? null));
  const table = s.tables.add(`A6:${end}${last}`,true,`Result_${t.id}`);
  table.style = 'TableStyleMedium2';
  table.showFilterButton = true;
  s.getRange(`A7:${end}${last}`).format.fill = '#FFFFFF';
  for(let rr=7;rr<=last;rr+=2) s.getRange(`A${rr}:${end}${rr}`).format.fill = colors.pale;
  s.getRange(`A6:${end}6`).format = {
    fill:colors.navy, font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},
    rowHeight:30,horizontalAlignment:'center',verticalAlignment:'center',
    borders:{insideVertical:{style:'thin',color:'#FFFFFF'}},
  };
  for (const [i,c] of t.columns.entries()) {
    const l = letter(i);
    s.getRange(`${l}1:${l}${last}`).format.columnWidth = c.width;
    const body = s.getRange(`${l}7:${l}${last}`);
    body.format.numberFormat = c.format;
    body.format.horizontalAlignment = ['number','integer'].includes(c.kind) ? 'right' : 'left';
    if (c.kind === 'integer') body.format.numberFormat = '0';
    if (c.kind === 'boolean') body.format.horizontalAlignment = 'center';
  }
  const wrapKeys=new Set(['id','analysis','parameter','parameter_x','parameter_y','version','mode','status','physical_status','best_fit_semantics','point_id','nonzero_epsilon_upper_triangle','reference_kind','same_inputs','text_value','interpretation','scope','reference_locator','locator','source','absolute_path','relative_path','global_surface','global_contours','paper_contours','scan']);
  const visible=t.columns.filter(c=>wrapKeys.has(c.key));
  for(const c of visible) {
    const l=letter(t.columns.indexOf(c));
    s.getRange(`${l}7:${l}${last}`).format.wrapText=true;
  }
  for(const [i,r] of t.rows.entries()) {
    let lines=1;
    for(const c of visible) {
      const text=String(r[c.key]??'');
      const units=[...text].reduce((n,ch)=>n+(ch.codePointAt(0)>255?1.8:1),0);
      lines=Math.max(lines,Math.ceil(units/(c.width*1.1)));
    }
    if(lines>1) s.getRange(`A${i+7}:${end}${i+7}`).format.rowHeight=Math.min(150,lines*17+8);
  }
  // Keep every Python function on its own visible line rather than clipping
  // multi-file responsibilities. Full absolute paths are retained for copying.
  if (t.id === 'computation_routes') {
    const ci = t.columns.findIndex(c=>c.key==='python_files');
    s.getRange(`${letter(ci)}7:${letter(ci)}${last}`).format.wrapText = true;
    for (const [i,r] of t.rows.entries()) {
      const lines = Math.max(1,...[r.python_files].map(text=>text.split('\n').reduce((n,line)=>n+Math.max(1,Math.ceil(line.length/(t.columns[ci].width*1.1))),0)));
      s.getRange(`A${i+7}:${end}${i+7}`).format.rowHeight = Math.max(26,lines*18+8);
    }
  }
  s.freezePanes.freezeRows(6);
  s.freezePanes.freezeColumns(t.id==='sources' ? 1 : 2);
}

const defs = data.tables.find(t=>t.id==='definitions');
if (defs.rows[0].id!=='coupling_abs' || defs.rows[1].id!=='GF' || defs.rows[2].id!=='kappa') throw new Error('Constant positions changed');
setFormula(defs,'numeric_value',9,'=SQRT(2)*C8',defs.rows[2].numeric_value);
const coupling = "'定义与文献'!$C$7";
const cut = data.tables.find(t=>t.id==='cutoff_scales');
for (const [i,row] of cut.rows.entries()) {
  const rr=i+7, d=address(cut,'dimension',rr);
  for (const cl of ['90','95']) for (const field of ['global','SM','positive','negative']) {
    const c=address(cut,`cmax_${cl}_${field}`,rr);
    setFormula(cut,`lambda_${cl}_${field}`,rr,`=IF(${c}="","",(${coupling}/${c})^(1/(${d}-4)))`,row[`lambda_${cl}_${field}`]);
  }
}
const intervals = data.tables.find(t=>t.id==='scale_intervals');
for (const [i,row] of intervals.rows.entries()) {
  const rr=i+7, d=address(intervals,'dimension',rr), max=address(intervals,'c_abs_max',rr), min=address(intervals,'c_abs_min',rr);
  const flat = row.status==='ALL_POSITIVE_SCALES_ALLOWED_NO_FINITE_BOUND';
  setFormula(intervals,'lambda_min_GeV',rr,flat ? '=0' : `=IF(${max}="","",(${coupling}/${max})^(1/(${d}-4)))`,row.lambda_min_GeV);
  setFormula(intervals,'lambda_max_GeV',rr,`=IF(${min}="","",IF(${min}=0,"",(${coupling}/${min})^(1/(${d}-4))))`,row.lambda_max_GeV);
}
const overview = data.tables.find(t=>t.id==='overview'), overviewSheet=sheets.get('overview');
const totalRow=overview.rows.length+8;
overviewSheet.getRange(`A${totalRow}`).values=[['路线总计']];
overviewSheet.getRange(`A${totalRow}:G${totalRow}`).format.font={name:'Arial',size:10,bold:true,color:colors.text};
for (const key of ['one_d','two_d','cutoff_main','cutoff_control','cutoff_joint']) {
  const cell=address(overview,key,totalRow), first=address(overview,key,7), last=address(overview,key,overview.rows.length+6);
  const expected=overview.rows.reduce((s,r)=>s+r[key],0);
  overviewSheet.getRange(cell).formulas=[[`=SUM(${first}:${last})`]];
  formulas.push({sheet:overview.sheet,cell,expected,formula:`=SUM(${first}:${last})`});
}

// Meaningful sensitivity test: dimension six must scale by sqrt(|g|).
wb.recalculate();
const sampleIndex=cut.rows.findIndex(r=>r.version==='dim6_self_consistent' && r.analysis==='CONUS_plus' && r.operator==='C6u1');
const sampleAddress=address(cut,'lambda_90_global',sampleIndex+7);
const base=sheets.get('cutoff_scales').getRange(sampleAddress).values[0][0];
sheets.get('definitions').getRange('C7').values=[[4]];
wb.recalculate();
const changed=sheets.get('cutoff_scales').getRange(sampleAddress).values[0][0];
if (!equal(changed,2*base)) throw new Error(`Coupling test failed ${base} -> ${changed}`);
const sensitivity={sample:sampleAddress,coupling_base:1,coupling_test:4,lambda_base:base,lambda_test:changed,expected_ratio:2,observed_ratio:changed/base,restored:true};
sheets.get('definitions').getRange('C7').values=[[1]];
wb.recalculate();

const formulaFailures=[];
for (const f of formulas) {
  const actual=wb.worksheets.getItem(f.sheet).getRange(f.cell).values[0][0];
  if (!equal(actual,f.expected)) formulaFailures.push({...f,actual});
}
if (formulaFailures.length) throw new Error(JSON.stringify(formulaFailures.slice(0,8)));
const cellErrors=[];
for (const t of data.tables) {
  const vals=sheets.get(t.id).getUsedRange().values;
  for(let r=0;r<vals.length;r++) for(let c=0;c<vals[r].length;c++) if(typeof vals[r][c]==='string'&&errors.test(vals[r][c]))cellErrors.push({sheet:t.sheet,address:`${letter(c)}${r+1}`,value:vals[r][c]});
}
if(cellErrors.length) throw new Error(JSON.stringify(cellErrors.slice(0,8)));
const inspected=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'final formula error scan'});
await fs.writeFile(path.join(out,'qa','FORMULA_ERROR_SCAN.ndjson'),inspected.ndjson??'');
for(const [name,range] of [['总览','A6:G21'],['SM参数','A6:H10'],['截断能标','A6:J10']]) {
  const check=await wb.inspect({kind:'table',range:`'${name}'!${range}`,include:'values,formulas',tableMaxRows:8,tableMaxCols:10,maxChars:5000});
  await fs.writeFile(path.join(out,'qa',`INSPECT_${name}.ndjson`),check.ndjson??'');
}

await fs.mkdir(path.join(out,'qa','previews'),{recursive:true});
const rendered=[];
for(const t of data.tables) {
  const end=letter(Math.min(t.preview_columns,t.columns.length)-1), last=t.id==='overview'?totalRow:Math.min(t.rows.length+6,15);
  const preview=await wb.render({sheetName:t.sheet,range:`A1:${end}${last}`,scale:1.3,format:'png'});
  const file=path.join(out,'qa','previews',`${t.id}.png`);
  await fs.writeFile(file,new Uint8Array(await preview.arrayBuffer()));
  rendered.push({sheet:t.sheet,file,range:`A1:${end}${last}`});
  console.log(`Rendered ${t.sheet}`);
}
for(const [id,range,suffix] of [['cutoff_scales','D6:P18','signs_and_flat'],['cutoff_scales','D47:P53','dim8_status'],['definitions','A27:H38','citations'],['computation_routes','H6:J10','python_files']]) {
  const t=data.tables.find(t=>t.id===id);
  const preview=await wb.render({sheetName:t.sheet,range,scale:1.1,format:'png'});
  const file=path.join(out,'qa','previews',`${id}_${suffix}.png`);
  await fs.writeFile(file,new Uint8Array(await preview.arrayBuffer()));
  rendered.push({sheet:t.sheet,file,range});
}
const xlsx=await SpreadsheetFile.exportXlsx(wb);
const output=path.join(out,'CEvNS_Results_Summary_20261115.xlsx');
await xlsx.save(output);
await fs.writeFile(path.join(out,'qa','WORKBOOK_CHECKS.json'),JSON.stringify({status:'PASS_ARTIFACT_RECALCULATION_AND_EXPORT',sheets:data.tables.map(t=>({name:t.sheet,records:t.rows.length,columns:t.columns.length})),formulas_checked:formulas.length,formula_failures:formulaFailures,cell_errors:cellErrors,sensitivity_test:sensitivity,rendered,output,scope:'Rendered with artifact-tool; native Excel UI was not used.'},null,2)+'\n');
console.log(JSON.stringify({output,sheets:data.tables.length,formula_count:formulas.length,rendered:rendered.length}));
