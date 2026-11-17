"""Consolidate current solar-B8 evidence and executed benchmarks into v3.0.

Documentation only. No theory, input package, array, saved benchmark, scientific
gate or model default is changed. --check compares generated text without writes.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/solar_b8_onboarding_v3/20261109_layout_r1'
JOINT = ROOT / 'docs/experiments/PandaX4T_XENONnT_SolarB8'
CENTRAL = JOINT / 'SOLAR_B8_ONBOARDING.v3.0.md'
FAMILIES = [('PandaX4T', 'PandaX4T_2024_US2'), ('XENONnT', 'XENONnT_2024_SolarB8')]
SM = ROOT / 'outputs/solar_b8_sm/20261107_run1'
VECTOR = ROOT / 'outputs/solar_b8_vector/20261108_run1'
SIMPLIFIED = ROOT / 'outputs/solar_b8_sm/20261110_pandax_simplified_run1'
sys.path.insert(0, str(ROOT))
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.solar_vector import with_solar_light_vector


def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def fmt(x):
    if isinstance(x, (bool, np.bool_)): return str(bool(x))
    if isinstance(x, (int, np.integer)): return str(int(x))
    if isinstance(x, (float, np.floating)): return f'{float(x):.12g}'
    return str(x)
def seq(x): return '[' + ', '.join(fmt(v) for v in x) + ']'
def link(origin, target, label, anchor=''):
    return '[' + label + '](<' + os.path.relpath(target, origin.parent).replace('\\', '/') + anchor + '>)'
def table(headers, rows):
    return '| ' + ' | '.join(headers) + ' |\n|' + '|'.join('---' for _ in headers) + '|\n' + ''.join(
        '| ' + ' | '.join(str(v).replace('|', r'\|').replace('\n', '<br>') for v in row) + ' |\n' for row in rows)


def stats(value):
    a = np.asarray(value)
    result = {'shape': list(a.shape), 'dtype': str(a.dtype)}
    if a.dtype.kind in 'iufb' and a.size:
        assert np.isfinite(a).all()
        flat = a.reshape(-1)
        result.update(minimum=float(a.min()), maximum=float(a.max()),
            representative_first_middle_last=[float(flat[i]) for i in [0, len(flat)//2, len(flat)-1]])
        if a.ndim == 1 and a.size <= 50: result['all_values'] = a.tolist()
    elif a.dtype.kind in 'US' and a.ndim == 1:
        result['labels'] = a.tolist()
    return result


def content_info(path):
    if path.suffix == '.npz':
        with np.load(path, allow_pickle=False) as arrays:
            return {'arrays': {key: stats(arrays[key]) for key in arrays.files if key != 'provenance_json'}}
    if path.suffix == '.json':
        value = read(path); result = {'keys': list(value)}
        if 'parameters' in value: result['parameters'] = value['parameters']
        for key in ['coordinate_system', 'map', 'rate']:
            if key in value: result[key] = stats(value[key])
        return result
    if path.suffix == '.csv':
        a = np.genfromtxt(path, delimiter=',', names=True, encoding='utf8')
        return {'rows': int(a.size), 'columns': {name: stats(np.atleast_1d(a[name])) for name in a.dtype.names}}
    if path.name == 'b8_bahcall1996_official.txt':
        # Preserve the official prose header. Numeric data begin at the first
        # four-float row; all subsequent nonempty rows must remain four floats.
        lines = path.read_text(encoding='utf8').splitlines()
        start = next(i for i, line in enumerate(lines) if re.match(r'^\s*0(?:\.0*)?\s+', line))
        a = np.loadtxt(lines[start:]); assert a.shape == (829, 4)
    else:
        a = np.loadtxt(path)
    return {'table': stats(a), 'columns': [stats(a[:, i]) for i in range(a.shape[1])],
        'header': '\n'.join(line for line in path.read_text(encoding='utf8').splitlines() if line.startswith('#'))}


def role(claim_id):
    if claim_id.startswith('PandaX4T'):
        number = int(claim_id.split('-C')[-1])
        if number in [6, 7, 29]: return '本轮前向输入的直接来源，已封入正式NPZ'
        if number == 1: return '2026-11-10简化平均映射主输入；不是完整Ne迁移概率'
        if number == 2: return '简化平均映射的best-fit产额敏感性对照；非独立标定'
        if number == 3: return 'Qy包络参考；未提供Ne迁移概率或联合协方差'
        if number in [4, 5]: return '图线拟合/参考投影；非独立prefit背景'
        if number in [8, 9, 10]: return '后续259日事件参考；2024完整事件身份未认证'
        if number == 11: return '通用标定参考；非US2 sub-keV完整响应'
        return '原2024总数/率误差参考；完整形状另需取得'
    number = int(claim_id.split('-C')[-1])
    if number in [18, 19, 34, 37, 40, 43]: return '本轮前向输入的直接来源，已封入正式NPZ'
    if number in [16, 17]: return '官方SR0/SR1观测核对与绘图；不进入信号前向积分'
    if number in [42, 45]: return '早期发布名义背景/信号对照；B8不是额外背景'
    if number in [20, 21, 22, 23, 24, 25]: return '2026发布候选；未替换本轮早期响应/背景'
    if number in [12, 13]: return '早期WIMP Qy参考；不是本轮YBe产额'
    if number in [14, 15]: return '原图拟合/benchmark投影参考；非prefit原生模板'
    if number in [33, 35, 36, 38]: return 'YBe上下曲线参考；未据此虚构协方差或profile'
    if number == 39: return '官方已折叠CEvNS参考谱/CDF；不是中微子源谱'
    if number in [41, 44]: return '项目推导的一维名义响应对照；Runtime直接插值基底'
    if number == 31: return '原2024边际接受度对照；当前响应含选择，不再相乘'
    if number == 32: return '原2024真实反冲SM参考谱；验证用途'
    return '原2024标定/prefit总数/约束参考；完整likelihood未实例化'


def load(family, dataset):
    base = ROOT / 'data/experiments' / family / dataset
    run = ROOT / 'workflows/cevns-pyeft/runs' / family / dataset
    docs = ROOT / 'docs/experiments' / family / 'datasets' / dataset
    package = read(base / 'experiment.input.yaml')
    with np.load(base / 'experiment.resources.npz', allow_pickle=False) as archive:
        arrays = {key: archive[key].copy() for key in archive.files}
    ledger = read(run / 'P01_EVIDENCE_LEDGER.yaml')
    sources = {s['source_id']: s for s in read(run / 'P00_SOURCE_REGISTER.yaml')['sources']}
    raw = []
    for claim in ledger['claims']:
        p = base / str(claim['field'])
        if '-C' in claim['claim_id'] and p.is_file():
            assert sha(p) == claim['value']['sha256'], str(p)
            raw.append({'claim_id': claim['claim_id'], 'file': rel(p), 'sha256': sha(p),
                'source_id': claim['source_id'], 'locator': claim['locator'], 'unit': claim['unit'],
                'conversion': claim.get('derivation', ''), 'verification_scope': claim.get('verification_scope', ''),
                'current_role': role(claim['claim_id']), 'content': content_info(p)})
    exp = load_experiment_package(base)
    sm = read(SM / dataset / 'SM_RESULT.json')
    vector = read(VECTOR / dataset / 'DATASET_RESULT.json')
    assert exp.physics_fingerprint == sm['physics_fingerprint']
    for point in read(VECTOR / 'BENCHMARK_CONFIG.json')['points']:
        prepared = exp if point['id'] == 'SM' else with_solar_light_vector(exp,
            mass_MeV=point['mass_MeV'], coupling=point['coupling'], scenario=point['scenario'])
        assert prepared.physics_fingerprint == vector['results'][point['id']]['physics_fingerprint']
    return {'family': family, 'dataset': dataset, 'xenon': family == 'XENONnT', 'base': base, 'run': run,
        'docs': docs, 'package': package, 'arrays': arrays, 'sources': sources, 'raw': raw,
        'claims': {c['claim_id']: c for c in ledger['claims']}, 'experiment': exp, 'sm': sm, 'vector': vector}


def refs(d, origin, ids):
    lines = ['\n### 本章参考文献与核验范围\n']
    for sid in dict.fromkeys(ids):
        row = d['sources'][sid]
        citation = row['citation']
        if sid == 'R19':
            citation = read(VECTOR / 'BENCHMARK_CONFIG.json')['formula_source']['citation'].replace(
                'DOI: 10.1088/1475-7516/2025/05/012.', 'DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012).')
        p = Path(row['uri_or_path'])
        local = ' ' + link(origin, p, '本地直接采用源') if p.is_file() else ''
        lines.append('- [' + sid + '] ' + citation + local)
    return '\n'.join(lines) + '\n'


def param_table(d, origin, keys):
    rows = []
    for key in keys:
        p = d['package']['parameters'][key]
        source = ', '.join(s for s in p['source_refs'] if s.startswith('R'))
        if not source: source = '项目配置选择；不是文献测量'
        rows.append(['`' + key + '`', fmt(p['value']), p['unit'], source + '；' + p['meaning'],
            link(origin, d['base'] / 'experiment.input.yaml', '实际标量卡')])
    return table(['输入/配置', '实际值', '单位', '直接出处/处理性质', '本地文件'], rows)


def array_text(a):
    info = stats(a)
    shape = '×'.join(str(n) for n in a.shape) or 'scalar'
    result = shape + '; dtype=' + str(a.dtype)
    if 'minimum' in info:
        result += '; 范围 ' + seq([info['minimum'], info['maximum']]) + '; 首/中/末 ' + seq(info['representative_first_middle_last'])
    return result


def array_table(d, origin, keys):
    rows = []
    for key in keys:
        a = d['arrays'][key]; meta = d['package']['resources']['arrays'][key]
        claims = [c for c in d['claims'].values() if c['field'] == 'resources/arrays/' + key]
        claim = claims[0] if claims else None
        rows.append(['`' + key + '`', array_text(a), meta['unit'],
            ','.join(meta['source_refs']) + '；' + meta['meaning'] + ('；' + claim['status'] if claim else ''),
            link(origin, d['base'] / 'experiment.resources.npz', '完整数值')])
    return table(['数组键', 'shape/范围/代表值', '单位', '直接出处、转换与采用范围', '本地文件'], rows)


def raw_table(d, origin, endings):
    rows = []
    for item in d['raw']:
        if not any(item['file'].endswith(s) for s in endings): continue
        content = item['content']
        if 'table' in content:
            numbers = str(content['table']['shape']) + '; 各列范围 ' + '; '.join(seq([s['minimum'], s['maximum']]) for s in content['columns'])
        elif 'map' in content:
            numbers = 'coordinate ' + str(content['coordinate_system']['shape']) + '; map ' + str(content['map']['shape'])
        else: numbers = str(content.get('rows', '')) + ' 记录；完整数组/标量见文件'
        rows.append([link(origin, ROOT / item['file'], Path(item['file']).name), numbers, item['unit'],
            item['source_id'] + '；' + item['locator'], item['current_role']])
    return table(['实际数值文件', 'shape/范围', '单位', '直接原文定位', '采用/验证范围'], rows)


def scalar_reference(d, origin, filename):
    item = next(item for item in d['raw'] if item['file'].endswith(filename))
    rows = []
    for p in item['content']['parameters']:
        uncertainty = '未单列'
        if p.get('sigma') is not None: uncertainty = '±' + fmt(p['sigma'])
        elif p.get('uncertainty_minus') is not None: uncertainty = '−' + fmt(p['uncertainty_minus']) + '/+' + fmt(p['uncertainty_plus'])
        rows.append([p['name'], fmt(p['value']), uncertainty, p['unit'], item['source_id'] + '；' + p.get('locator', item['locator'])])
    return '\n' + link(origin, ROOT / item['file'], '完整原文摘录文件：' + filename) + '\n\n' + table(['参考参数', '值', '误差/变化', '单位', '直接出处'], rows)


class Equations:
    def __init__(self, prefix, offset=0): self.prefix = prefix; self.count = offset; self.records = []
    def add(self, name, expression, source, symbols):
        self.count += 1
        anchor = self.prefix + 'eq-' + name
        self.records.append({'id': anchor, 'number': self.count, 'source': source, 'symbols': symbols})
        return '<a id="' + anchor + '"></a>\n\n$$\n' + expression + r' \tag{' + str(self.count) + '}\n$$\n\n公式依据：' + source + '\n\n' + table(
            ['符号/输入', '定义、值或取得情况', '单位', '具体依据/依赖'], symbols)


def simplified_note(origin, detailed=False):
    result = read(SIMPLIFIED / 'RESULT.json')
    nominal = result['nominal']; cal = result['effective_calibration']
    text = '**2026-11-10新增、已实际计算：PandaX SM简化平均映射八箱谱。** '
    text += '采用R01 PDF p5式(11)–(13)、p6式(15)，nominal Qy来自R02 PDF p5 Fig.4下图；'
    text += 'Total(US2)已含ROI且只乘一次，忽略分辨率。直接积分（项目c_i=1基线）为'
    text += f'**{nominal["total_events"]:.6f}事例**，SSM通量固定为5.46×10⁶。R02 PDF p6 Fig.5后验拟合谱乘5.46/8.4的'
    text += f'历史参考为**{cal["total_events"]:.6f}事例**；它仍带实验拟合响应参数，不是同一基准响应下独立校准的SM预测，不作为验证。\n\n'
    text += ' · '.join([link(origin, SIMPLIFIED / 'REPORT.md', '结果、逐步物理及标准文献引用'),
        link(origin, SIMPLIFIED / 'events_by_bin.tsv', '真正计算的八箱表'),
        link(origin, ROOT / 'data/benchmarks/pandax_us2_simplified_v1/benchmark.input.json', '来源/方法参数卡')]) + '\n\n'
    if detailed:
        edges=result['electron_edges']; t=nominal['inverse_recoil_edges_keV']
        text += table(['Ne箱', '映射T[keVnr]', '固定SSM直接SM [events]', '拟合谱×0.65参考 [events]', '历史经验比值（非独立校准）'], [
            [f'{a:g}–{b:g}', f'{t[i]:.6f}–{t[i+1]:.6f}', f'{nominal["counts"][i]:.6f}',
             f'{cal["calibrated_counts"][i]:.6f}', f'{cal["coefficients"][i]:.6f}']
            for i,(a,b) in enumerate(zip(edges[:-1],edges[1:]))])
        tails=nominal['outside_mean_window_events_low_high']
        text += f'\n同轮完整已提取接受度T域积分为{nominal["accepted_domain_total_events"]:.6f}事例；平均映射窗口以下/以上为{tails[0]:.6f}/{tails[1]:.6f}事例。'
        text += '这量化了用含ROI的总接受度再作均值窗口裁剪的近似损失；未强制重归一化。完整Response路线继续保留，不能用此简化结果声称已取得概率迁移核。\n\n'
        text += '![本轮实际八箱计算](<' + os.path.relpath(SIMPLIFIED / 'events.png',origin.parent).replace('\\','/') + '>)\n\n'
    return text


def sections(d, origin, prefix='', offset=0):
    x = d['xenon']; a = d['arrays']; p = d['package']['parameters']; base = d['base']; run = d['run']
    eq = Equations(prefix, offset); sections = []
    s = '**版本3.0，2026-11-09整合；2026-11-10新增PandaX SM简化分支。** 本版收齐已有来源、数据、完整Response合同、SM与V/B−L计算和剩余依赖；不需要拼接v2.0–v2.3。数值依据是实际文件与运行记录，旧版保持原位。\n\n'
    s += ('本轮已实现：SM与V/B−L三箱重建谱。使用官方早期YBe重铸响应，精确2024原生likelihood等价性仍待核。' if x else
          '原Response路线已实现SM与V/B−L真实反冲投影；2026-11-10按用户要求新增SM简化平均映射八箱谱。**完整US2逐Ne箱概率核仍MISSING，简化谱已实际计算。**') + '\n\n'
    s += table(['对象/目标', '采用范围', '当前能力'], [
        ['数据身份', d['dataset'], '同一dataset；不新增采集期或默认全局激活'],
        ['物理benchmark', 'R01 arXiv:2411.11749v1 SM；R19正式期刊V/B−L定义', '固定点前向谱完成；本轮未计算Fig.2拟合或Fig.4排除线'],
        ['方法', 'Source→Target→共享截面→完整选后箱概率→counts；PandaX另有显式均值映射简化分支', 'SSM通量固定；简化c=1是直接预测，后验拟合谱缩放只作参考'],
        ['审核状态', '文档整合完成；科学结果Human=NOT_REVIEWED', '机器PASS不代替科学接受；PARTIAL能力逐项列于第10章']])
    s += '\n机器输入权威为' + link(origin, base / 'experiment.input.yaml', '正式YAML') + '与' + link(origin, base / 'experiment.resources.npz', '正式NPZ') + '；当前人读说明为本版。旧Compiler派生MD保留，不把旧模板的“靶未绑定”等通用文字当作当前实际数组/执行状态。\n'
    s += refs(d, origin, ['R01', 'R02' if not x else 'R03', 'R19'])
    if not x: s += '\n' + simplified_note(origin)
    sections.append(('scope', '1. 实验范围、身份与版本', s))
    s = eq.add('flux', r'\frac{d\phi}{dE_\nu}=\Phi_{8B}f_{8B}(E_\nu)',
        'R01 PDF p5式(11)及后文；R04官网b8spectrum.txt列1–4。总量×谱形为项目对输入的显式分解。', [
        [r'$E_\nu$', '定义变量；829节点0–16.56', 'MeV', 'R04第一列；`source_energy_MeV`'],
        ['$f_{8B}$', '已取得；中心谱829点；原积分0.999986544', 'MeV⁻¹', 'R04第二列；`source_shape_per_MeV`'],
        [r'$\Phi_{8B}$', '已取得；实际值见下表', 'cm⁻²s⁻¹', 'R01 PDF p5式(11)后；形状表不含它'],
        ['味态', '本轮味普适；用trace-one I₃/3代表等价状态，不当作太阳真实味比例', '1', 'R01 PDF p3 Sec.II B的味普适范围；solar_b8.UniversalSMState']])
    s += '\n' + param_table(d, origin, ['source.total_flux']) + '\n' + array_table(d, origin, ['source_energy_MeV', 'source_shape_per_MeV'])
    s += '\n官网四列表完整保留：' + link(origin, base / 'b8_bahcall1996_official.txt', '829×4原数值表') + '。列3/4是原有效±3σ谱形，不是12%的整体通量误差，未转成逐点独立高斯。\n\n'
    s += '实际处理为表内分段线性插值、表外零；中心谱不重归一化。源只生成每秒微分flux，参考年秒数在事件归一化中施加一次，源不含效率或曝光。12%仅作为R01 PDF p6式(17)后的统计参考约束，本轮固定点未profile。传统味相关NSI需要另给太阳传播与味分量；这些数据本轮未取得，也不被I₃/3替代。\n'
    s += refs(d, origin, ['R01', 'R04', 'R05'])
    sections.append(('source', '2. Source：总通量、谱形与味态', s))
    mean = float(np.dot(a['target_atomic_mass_u'], a['target_number_fraction']))
    counts = 1e6 * p['constants.avogadro']['value'] * a['target_number_fraction'] / mean
    s = eq.add('inventory', r'\overline M=\sum_A f_A M_A,\qquad n_A^{(t)}=\frac{10^6N_{\rm A}f_A}{\overline M}',
        '项目按R09全部九种天然Xe中心值及R13 SI阿伏伽德罗常量推导；10⁶为g/t换算。', [
        ['$f_A$', '已取得；九核素数丰度，和为1', '1', 'R09 Xe对应A行；不能直接当质量分数'],
        ['$M_A$', '已取得；原子质量u的数值按1g/mol近似转换', 'g/mol', 'R09第二列；R13 §2.3.1；不是裸核质量'],
        [r'$N_{\rm A}$', '已取得；SI精确常量，值见下表', 'mol⁻¹', 'R13 §2.2/Table1'],
        ['$n_A^{(t)}$', '项目推导；每吨各核素核数见表', 'nuclei/t', '本式与九行中心值；未传播丰度误差']])
    s += '\n' + param_table(d, origin, ['target.anchor_mass_kg', 'target.Z', 'constants.avogadro', 'constants.amu_GeV', 'constants.electron_mass_GeV'])
    s += '\n' + table(['核素A', '原子质量[u]', '数丰度', '每吨核数[推导]', '直接出处'], [[int(A), fmt(m), fmt(f), f'{n:.12g}', 'R09 Xe对应A行；本式']
        for A, m, f, n in zip(a['target_mass_number'], a['target_atomic_mass_u'], a['target_number_fraction'], counts)])
    s += f'\n平均摩尔质量 {mean:.12g} g/mol；每吨总核数 {counts.sum():.12g}。上述组成是NIST天然Xe参考，未冒充两实验独立样品化验。完整输入：' + link(origin, base / 'xenon_natural_isotopes_nist_v2.txt', '九核素原表') + '。\n\n'
    s += '物质数使用原子质量；运动学使用 `m_kin[GeV]=atomic_mass[u]×amu_GeV−54×m_e[GeV]`，忽略电子结合能。计算中的1000kg和31557600s是代数归一化锚点，不是虚构实测质量/活时间。现代SI下将u数值当g/mol是明确的摩尔质量常量近似，未称为精确恒等。\n\n'
    s += array_table(d, origin, ['target_mass_number', 'target_atomic_mass_u', 'target_number_fraction', 'run_exposures_tyr'])
    s += ('\nR17早期发布曝光SR0=1.174398、SR1=2.342593 t·yr，合计3.516991。R03/R01打印3.51另列，当前结果没有暗中缩放到3.51。\n' if x else
          '\n本轮采用R02 PDF p3的US2总曝光1.04t·yr。原文Run0/Run1 US2 FV质量2.78/2.16t可作参考；afterglow veto后的逐run有效曝光仍MISSING，未按质量比拆造。\n')
    s += refs(d, origin, ['R09', 'R13', 'R18', 'R17' if x else 'R02'])
    sections.append(('target', '3. Target、核数与曝光', s))
    s = table(['选择维度', '本轮实际组件/实现', '参数、具体依据与边界'], [
        ['Interaction：SM', '`coherent_sm_kn_v1`；' + link(origin, ROOT / 'cevns_pyeft/theory/sm_coherent.py', 'StandardModelKN'), 'R01 PDF p3式(1)–(3)；含−T/E树级SM；拒绝一般BSM系数'],
        ['Interaction：V/B−L', '`light_vector_kn_v1`；' + link(origin, ROOT / 'cevns_pyeft/theory/light_vector.py', 'LightVectorKN'), 'R19 PDF p5/印刷p4式(2.6),(2.10)；实数、味普适对角耦合，κ=1/−1/3'],
        ['Nuclear Structure', '`klein_nystrand_v1`解析KN', 'R01式(3)与参数表；覆盖九核素；本轮不读取多项式核响应JSON'],
        ['Kinematics', '现有ElasticKinematics', '精确弹性端点；与SM截面低反冲近似分开'],
        ['Cross-section', '上述共享组件的dsigma_dT', '输入Eν MeV、T keVnr、核质量GeV；输出cm²/keV；不夹带核数或效率'],
        ['Detector', '`xenon_mono_basis_v1`' if x else '`recoil_efficiency_projection_v1`', '探测器Response独立于Nuclear Structure；具体数学定义见第5章']])
    s += '\n' + param_table(d, origin, ['interaction.sin2thetaW', 'interaction.include_sm', 'nuclear.radius_fm', 'nuclear.skin_fm',
        'constants.G_F', 'constants.hbarc_GeV_fm', 'constants.GeV_inverse2_to_cm2'])
    s += '\nV/B−L只通过现有interaction组件替换接口加入，正式SM包保持原样。耦合定义采用**期刊版C_V=3Ag²**；v1 PDF p4式(10)印成C_V²，期刊版式(2.10)已经明确。本版显式保留这个版本差别，没有用sqrt(3A)g误代，也未把旧v1 SM输入换成另一套实验模型。公共截面内部公式不在实验章节重写，原公式与独立解析检查见' + link(origin, VECTOR / 'REPORT.md', '共享矢量模型报告', '#model') + '。\n\n'
    s += '未采用的Full EFT候选：本地responses_all.json含Xe128/129/130/131/132/134/136，缺Xe124/126；上游核系数出处、绝对归一化及与S/A/T算符的匹配尚未闭合。这个缺口**不阻断当前解析KN的SM/V/B−L**；完整资源内容与后续适用性在第9、10章分别登记。\n'
    s += refs(d, origin, ['R01', 'R19', 'R18', 'R16'])
    sections.append(('modules', '4. 实际共享模块与参数选择', s))
    # Detector, observables, prediction, statistics and resources follow below.
    return finish_sections(d, origin, prefix, eq, sections)


def finish_sections(d, origin, prefix, eq, sections):
    x = d['xenon']; a = d['arrays']; base = d['base']; run = d['run']; exp = d['experiment']
    if x:
        s = eq.add('response', r'P_{ri}(T)=\sum_{j,k,l}\mathcal B_r(T,L_y(T),Q_y(T);i,j,k,l),\qquad0\leq\sum_iP_{ri}(T)\leq1',
            '项目对R17原HDF5接受后四维箱概率的精确边际化；原单能模板与utils.py::Template.interpolator。', [
            ['$r,i$', 'SR0/SR1与各run自身的cS2箱序号；三箱', '1', 'R17原HDF5 /bins/0；第6章完整边界'],
            [r'$\mathcal B_r$', '已取得；原基底每run16×10×10×3×3×3×3', '1，接受后箱概率', 'R17 orthonormal_basis；原文件1600个/run'],
            ['$T,L_y,Q_y$', 'T核反冲；Ly/Qy是物理产额坐标，分别1…10', 'keVnr；photon/keVnr；electron/keVnr', '正式response_energy_keV/response_Ly/response_Qy与501点YBe中位数'],
            ['$j,k,l$', 'shadow、S1BDT、S2BDT三个观测轴各三箱', '1', 'R17原/bin轴；求和后保留cS2边际'],
            ['$P_{ri}$', '已取得的数值核，经插值推导；Runtime形状16×10×10×3/run', '1', 'SM20261107数组claims；solar_b8.XenonBasisObservation']])
        s += '\n' + eq.add('interpolation', r'\mathcal B_r(T,L,Q)=\sum_{a,b,c\in\{0,1\}}w_a^E(T)w_b^L(L)w_c^Q(Q)\,\mathcal B_{r,e+a,\ell+b,q+c}',
            'R17 utils.py::Template.interpolator的三线性内插；当前实现为RegularGridInterpolator(method=linear)，不是任意平滑。', [
            ['$e,\ell,q$', '包含输入坐标的相邻网格单元索引', '1', '显式16×10×10的物理坐标网格'],
            ['$w_0,w_1$', '项目线性权重：(x_high−x)/Δx与(x−x_low)/Δx；和为1', '1', '同一网格单元的三轴权重乘积'],
            ['$L(T),Q(T)$', '已取得；原YBe median JSON map在T上线性插值', 'photon/keVnr、electron/keVnr', 'R17 ly_ybe_model_median.json/qy_ybe_model_median.json']])
        s += '\n原YBe表的**存储域0.3–10keV**不等于已认证响应域。当前只在单能基底 **0.51–5keVnr** 内使用；T域外本重铸模型返回零，不外推；Ly/Qy超网格时拒绝，不裁剪成端点。已有模板包含选择，不再乘另一条接受度曲线。当前实现对九种Xe同位素共用这一真实反冲NR响应，核素差异在核数/质量/共享截面中进入；这是实际组件的采用约定，不是额外同位素标定。\n\n'
        s += array_table(d, origin, ['response_energy_keV', 'response_Ly', 'response_Qy', 'response_SR0', 'response_SR1', 'yield_energy_keV', 'yield_Ly_median', 'yield_Qy_median'])
        s += '\n轴顺序：正式响应为(T,Ly,Qy,cS2箱)。原始7维基底为(T,Ly,Qy,cS2,shadow,S1BDT,S2BDT)。**Ly/Qy=1…10是物理产额，不能误当作±3 nuisance坐标。**背景文件的tLy/tQy七点坐标是另一种约定，见第8章。\n\n'
        rows = []
        for r, obs in zip(exp.model.run_ids, exp.model.observation):
            grid = np.array([.51, 1., 2., 3.])
            probs = obs.bin_probabilities(target=exp.model.targets.isotopes[0], recoil_keV=grid,
                binning=exp.model.binning, component_id='solar_B8_all_flavors').values
            for t, values in zip(grid, probs): rows.append([r, fmt(t), seq(values), fmt(values.sum()), 'R17原基底+YBe中位数；项目插值值'])
        s += table(['run', 'T[keVnr]', '三箱P（代表值）', 'ΣP', '来源/性质'], rows)
        s += '\n### 已取得但未另行施加的标定与接受度\n\n'
        s += scalar_reference(d, origin, 'xenonnt_2024_calibration_inputs.v2.1.json')
        s += '\nR01 PDF p6式(14)使用g₂=16.9PE/electron与R07早期WIMP Qy作均值换算；它不是当前YBe模板的外乘参数。已提取的R07曲线保留原可见/原虚线外推标志；不能改称YBe专用Qy。当前模板已经包含读出与选择效应。\n\n'
        s += raw_table(d, origin, ['xenonnt_qy_sr0_23Vcm.txt', 'xenonnt_qy_sr0_band.txt', 'xenonnt_2024_fig1_acceptance.txt', 'xenonnt_2024_fig1_sm_recoil_spectra.txt'])
        s += '\n六份YBe lower/median/upper文件都已保存；当前采用median，上下曲线没有被自动解释为独立高斯或完整联合协方差。R08的2026新版响应另存候选，不与本轮R17基底混用。\n'
        s += refs(d, origin, ['R17', 'R12', 'R03', 'R07', 'R01', 'R08', 'R14'])
    else:
        s = '**MISSING：2024 US2八个Ne箱的接受后概率P(Ne箱|T)。** 已有Qy、边际接受度和通用校准数值；它们不能唯一决定重建Ne的完整分布。\n\n'
        s += eq.add('mean-yield', r'\overline N_e(T)=TQ_y(T)',
            'R01 PDF p6式(15)；Qy曲线实际来自R02 PDF p5 Fig.4下图。本式只定义均值，不提供迁移核。', [
            ['$T$', '定义变量；Qy原表范围见下表', 'keVnr', 'R02 Fig.4横轴'],
            ['$Q_y$', '已取得nominal、best-fit、nominal包络；简化分支采用nominal，完整涨落核仍缺', 'electron/keVnr', 'R02 Fig.4下图对应线型；完整数值文件如下'],
            [r'$\overline N_e$', '均值/项目派生量；不是逐次观测分布', 'electron', '缺少涨落、损失与选择，不能以均值代替P']])
        s += '\n' + raw_table(d, origin, ['pandax_qy_nominal.txt', 'pandax_qy_bestfit.txt', 'pandax_qy_nominal_band.txt'])
        s += '\nNominal与best-fit的数值含义不同：best-fit为paired+US2联合拟合后的均值曲线，不冒充US2独立标定；包络不是参数协方差。\n\n'
        s += eq.add('response', r'P_{ri}(T)=\int_{n_i}^{n_{i+1}}dn\int dw\,p_r(n,w\mid T)\,\mathcal S_r(n,w,T)',
            '项目对“通过选择并进入Ne箱”的概率定义；R02原生Ne/width分析沿width边际化到本次一维目标。', [
            ['$P_{ri}$', '**MISSING**：US2低能八箱接受后核', '1', '阻断Ne重建谱、对应χ²与排除限'],
            ['$p_r(n,w|T)$', '**MISSING**：给定T的重建Ne/width联合分布或等价一维核', '密度单位取决于坐标', '量子涨落、电子损失、读出及选择的完整配置可替代直接矩阵'],
            [r'$\mathcal S_r$', '条件选择MISSING；边际总接受度已取得', '1', 'R02 PDF p3 Fig.1黑色Total(US2)只约束ΣP(T)'],
            ['$n_i$', '4,4.5,…,8，八箱完整边界见第6章', 'electron', 'R01 PDF p5式(12)后与R02 Fig.5']])
        s += '\n完整响应矩阵指“固定真实反冲T时，每个观测箱的通过概率”；模拟配置指能生成同一概率的涨落、电子输运/读出和选择参数及算法。均值Qy、总接受度或已对源谱积分的事例数图都不能唯一反演该核。未自行补Poisson/Gaussian宽度。\n\n'
        s += array_table(d, origin, ['efficiency_energy_keV', 'efficiency'])
        s += '\n原Response路线在正式真实反冲箱可见域内对这99个PDF矢量节点分段线性插值。**R02 PDF p3 ROI说明及Fig.1标题明确，Total(US2)已包含Ne∈[4,8]选择。** 原27箱是该选后样本的真实T分布，总效率本身不提供每个Ne箱的分配。完整Response不能重复裁剪均值窗口；简化分支明确采用平均映射裁窗并量化损失；后验拟合谱缩放只作历史参考，不用于补成SSM预测。\n\n'
        s += eq.add('simplified-counts', r'S_i^{\rm raw}=\mathcal E\int_{T(n_i)}^{T(n_{i+1})}dT\,\frac{dR}{dT}',
            'R01 PDF p5式(11)–(13)、p6式(15)；dR/dT含源、靶核数、SM与R02 Fig.1总接受度。此式为c_i=1的项目基线。', [
            ['$T(n_i)$', '由R02 nominal Qy线性插值并反解TQy(T)=n_i；0.660084–1.186893', 'keVnr', 'R01 p5脚注3与p6式(15)；显式参数卡记录算法'],
            ['$dR/dT$', '本轮共享Source/Target/SM积分并乘Total(US2)一次', 'events/(t·yr·keVnr)', 'R01式(11)；第2–4章；原正式包'],
            ['$S_i^{raw}$', '固定SSM通量下计算8箱；后验拟合谱缩放仅为参考', 'events/bin', 'RESULT.json与events_by_bin.tsv；第7章完整数值']])
        s += '\n历史经验比值=实验Fig.5拟合信号/[直接SM×(8.4/5.46)]；8.4×10⁶与75±28来自R02 PDF p6。该缩放仍保留实验拟合的产额/系统参数，不能视为同一基准Response下的SSM校准预测。独立前向计算始终固定Φ₀=5.46×10⁶、c_i=1；作者原始c_i未取得。\n\n### 通用响应标定参考（未绑定本轮Ne核）\n'
        s += scalar_reference(d, origin, 'pandax_response_calibration_2403.04239v2.json')
        s += '\ng₂b是bottom-array增益，不是总S2增益。以上10个印刷值及误差来自R06 PDF p21 Table II；没有US2 sub-keV专用的完整时间依赖/选择函数，不能把该表宣称为已取得完整响应配置。\n'
        s += refs(d, origin, ['R02', 'R01', 'R06', 'R10', 'R11'])
    s += '\n**c_i的地位：** R01式(12)的c_i是作者简化分析的有效修正，原Response路线不引入。PandaX直接预测固定SSM通量且c=1；历史字段effective_calibration只保存后验拟合谱缩放比值，不代表独立的探测器校准或SSM预测。作者原始c_i仍未获得，严格论文等价性未认证。\n'
    sections.append(('detector', '5. Detector Response、Qy与数值取得状态', s))
    if x:
        observed = np.loadtxt(base / 'statistics/xenonnt_official_observed_bins.txt')
        s = table(['run', '原生cS2完整箱界[PE]', '逐箱D', '直接出处'], [
            [r, seq(a['cs2_edges_' + r]), seq(observed[observed[:, 0] == i, 4].astype(int)), 'R08原事件CSV与binning；R17原HDF5相同分箱核对'] for i, r in enumerate(exp.model.run_ids)])
        s += '\n合计输出坐标是项目定义的箱序号1、2、3，`observable_edges=' + seq(a['observable_edges']) + '`，单位1；**各run按自身箱序号相加，不将所有事件放入一套公共PE箱界**。D合计[16,14,7]、总37；原37事件完整值保留。\n\n'
        s += 'R01正文写[120,500]PE，而其Fig.1绘图约[90,155,235,500]PE；官方SR1事件中有cS2=118.58632PE。当前采用上表官方原生90起点，未加cS2≥120筛选，也不声称已经解决作者120阈值与原37事件的关系。这个冲突只限制严格R01图/拟合复现。\n\n'
        s += raw_table(d, origin, ['xenonnt_official_observed_bins.txt', 'xenonnt_official_observed_events.txt'])
        s += refs(d, origin, ['R08', 'R17', 'R03', 'R01'])
    else:
        s = table(['能力/坐标', '完整边界', '采用状态与出处'], [
            ['目标Ne谱', seq(np.linspace(4, 8, 9)), 'electron；R01式(12)后与R02 Fig.5；信号P(Ne箱|T) MISSING'],
            ['当前真实反冲投影', seq(a['observable_edges']), 'keVnr；27箱项目输出选择，完整值来自正式NPZ；已含ROI选取，横轴仍为T，未分配Ne箱']])
        original = np.loadtxt(base / 'statistics/pandax_original_fig5.txt')
        s += '\n原实验Fig.5观测八箱D=' + seq(original[:, 3].astype(int)) + '，合计' + str(int(original[:, 3].sum())) + '；后续官方事件CSV只用于核对，不凭相同一维计数认证2024完整事件ID。width的µs单位关联R11后续论文，原CSV表头未独立编码单位。\n'
        s += refs(d, origin, ['R02', 'R01', 'R10', 'R11'])
    sections.append(('observable', '6. Observable、完整分箱与观测身份', s))
    if x:
        expression = r'\mu_i^{\rm sig}=\sum_r\mathcal E_r t_{\rm yr}\sum_A n_A^{(t)}\int dT\,P_{ri}(T)\int_{E_{\nu,\min}(T)}^{E_{\nu,\max}}dE_\nu\,\frac{d\phi}{dE_\nu}\frac{d\sigma_A}{dT}'
    else:
        expression = r'N_j^{\rm diag}=\mathcal E t_{\rm yr}\sum_A n_A^{(t)}\int_{T_j}^{T_{j+1}}dT\,\epsilon_{\rm US2}(T)\int_{E_{\nu,\min}(T)}^{E_{\nu,\max}}dE_\nu\,\frac{d\phi}{dE_\nu}\frac{d\sigma_A}{dT}'
    s = eq.add('prediction', expression,
        '项目对R01式(11)–(13)采用Response后的实验侧折叠；Source、核数、截面、选择和曝光各一次。' if x else
        '项目真实反冲接受度投影；R02 Fig.1接受度与既有Source/Target/共享截面。不是R01 Ne事件数公式的已实现替代。', [
        [r'$\mathcal E_r$或$\mathcal E$', '已取得；具体曝光见第3章', 't·yr', 'R17或R02；参考年注量×参考吨核数×曝光/anchor_tonne'],
        [r'$t_{\rm yr}$', '31557600；每年秒数只施加一次', 's/yr', 'R18 SEC_PER_YEAR=365.25×86400；单位约定'],
        [r'$n_A^{(t)}$', '已由九核素中心值推导', 'nuclei/t', '第3章核数表'],
        [r'$d\sigma_A/dT$', '已存在的共享SM或V/B−L组件输出', 'cm²/keVnr', '第4章模块/参数；不把核数或效率放进截面'],
        ['$P_{ri}$' if x else r'$\epsilon_{\rm US2}$', '已取得的接受后箱概率' if x else '已取得边际总接受度；Ne概率仍MISSING', '1', '第5章实际数值与有效域'],
        [r'$\mu_i^{\rm sig}$' if x else r'$N_j^{\rm diag}$', '项目派生的重建事件数' if x else '项目派生真实反冲诊断事件数', 'events/bin', '当前已执行的数值结果如下']])
    s += '\n完整Response路线直接在真实T上积分，不使用1/Qy代替能量相关均值映射的Jacobian，也不把均值转换当作概率迁移。\n\n' + param_table(d, origin, ['constants.seconds_per_year', 'numerics.n_er', 'numerics.n_enu'])
    s += '\n上表401/240为正式包默认基础节点；已保存benchmark显式覆盖为T=201/401/801、Eν=120/480并分别加密，另并入原源谱、响应、产额与输出箱断点。积分为共享recoil/folding的梯形求积；预定逐箱条件max(2×10⁻⁴ events,0.2%)，两种维度分别检查。不能只凭一个相对差异超过0.2%就忽略其绝对容差条件。\n\n'
    points = read(VECTOR / 'BENCHMARK_CONFIG.json')['points']
    rows = []
    for point in points:
        value = d['vector']['results'][point['id']]
        rows.append([point['id'], '—' if point['mass_MeV'] is None else fmt(point['mass_MeV']), fmt(point['coupling']),
            '—' if point['id'] == 'SM' else ('1' if point['scenario'] == 'universal' else '−1/3')]
            + ([f'{v:.9f}' for v in value['counts']] if x else []) + [f'{value["total_events"]:.9f}'])
    s += '<a id="' + prefix + 'benchmark-results"></a>\n\n' + table(['点', 'm[MeV]', 'g', 'κ'] + (['箱1', '箱2', '箱3'] if x else []) + ['信号/投影总量[events]'], rows)
    s += '\n**非零m/g数值是项目选取的测试点，不是论文最佳拟合或排除界；κ与耦合定义来自R19。** 直接采用卡：' + link(origin, ROOT / 'data/benchmarks/solar_b8_vector_v1/benchmark.input.json', '全部测试点、值的性质与固定输入哈希') + '。SM总数与上一轮逐箱一致；所有核素、run和逐箱数组已保存。\n\n'
    if not x:
        s += '**上述历史数字是约0.3–3keVnr域内、含ROI的信号总量估计及真实T分布；原V/B−L运行尚无八箱Ne预测。** 新增的SM八箱简化计算如下，不能把不同方法、通量或拟合点的总数直接当同条件复现比。\n\n'
    else:
        compare = read(SM / d['dataset'] / 'REFERENCE_COMPARISON.json')
        native = np.asarray(compare['native_release_signal_reference']).sum(axis=0)
        delta = (np.asarray(d['sm']['counts']) / native - 1) * 100
        s += '相对R17原发布名义SM信号，三箱差异为' + seq(delta) + '%；逐run最大差异另见原比较记录。曝光3.516991与打印3.51以及早期重铸模型适用性均未通过c_i强行消除。该差异与此前同一官方CDF谱重铸的6.30%核对不是同一检查。\n\n'
    s += '干涉分解的和允许含负项，完整逐箱表：\n\n' + table(['点', 'SM总量', '干涉项', '纯NP项', '闭合最大误差[events]'], [
        [sid, f'{sum(v["SM"]):.9f}', f'{sum(v["interference"]):.9f}', f'{sum(v["pure_NP"]):.9f}', f'{v["maximum_absolute_closure_error_events"]:.3g}'] for sid, v in d['vector']['decomposition'].items()])
    s += '\n依据为共享矢量振幅的有符号分解及逐核素真实反冲重权重后独立折叠；它是内部解析闭合检验，不是外部非零点模板复现。\n\n'
    for title, folder in [('SM前向图', SM), ('V/B−L前向图', VECTOR)]:
        s += '### ' + title + '\n\n![' + title + '](' + '<' + os.path.relpath(folder / d['dataset'] / 'events.png', origin.parent).replace('\\', '/') + '>)\n\n'
    s += table(['实际结果/复算', '入口'], [
        ['SM逐箱、run/核素分量、收敛、参数指纹', link(origin, SM / d['dataset'] / 'SM_RESULT.json', 'SM_RESULT.json')],
        ['V/B−L全部点、分解及逐箱数组', link(origin, VECTOR / d['dataset'] / 'DATASET_RESULT.json', 'DATASET_RESULT.json') + ' · ' + link(origin, VECTOR / d['dataset'] / 'counts_by_point.tsv', '全部逐箱TSV')],
        ['SM复算', '`python -B tools/run_solar_b8_sm_benchmark.py --output outputs/solar_b8_sm/repeat_run`'],
        ['V/B−L复算', '`python -B tools/run_solar_b8_vector_benchmark.py --output outputs/solar_b8_vector/repeat_run`']])
    s += '\n标准API可直接运行（以下为本实验路径）：\n\n```python\nfrom cevns_pyeft.experiments.package_loader import load_experiment_package\nfrom cevns_pyeft.experiments.solar_vector import with_solar_light_vector\nfrom cevns_pyeft.experiments.runtime import predict_experiment\nsm = load_experiment_package("' + rel(base) + '")\nvector = with_solar_light_vector(sm, mass_MeV=10., coupling=2e-5, scenario="universal")\nresult = predict_experiment(vector, numerics={"n_er": 801, "n_enu": 480})\nprint(result.counts)\n```\n\nPandaX路径的返回量始终是keVnr投影；更换interaction不会凭空补出电子数Response。\n'
    s += refs(d, origin, ['R01', 'R19', 'R17' if x else 'R02', 'R18'])
    if not x:
        s += '\n### 2026-11-10：SM简化平均映射八箱结果\n\n' + simplified_note(origin, detailed=True)
        s += '复算：`python -B tools/run_pandax_us2_simplified_benchmark.py --output outputs/solar_b8_sm/repeat_simplified`。标准Runtime仍负责源、靶、SM和直接反冲积分，新局部适配器只负责逆映射与连续T区间积分。两种Qy曲线均分别检查T和Eν收敛。\n'
    sections.append(('prediction', '7. Prediction folding、执行结果与复算', s))
    s = '**已执行的是固定点前向预测与观测/名义背景作图；统计evaluator、χ²最小化、置信区间未实现/未运行。** 下列R01统计合同作为后续明确依据保留，不因公式写出就声称统计能力已完成。\n\n'
    s += eq.add('mean-counts', r'\mu_i=(1+\alpha)(1+\beta_s)S_i(\theta)+\sum_k(1+\beta_k)B_i^k',
        '项目将R01 PDF p6式(16)–(17)后归一化因子说明显式展开；不是当前已经执行的拟合。', [
        ['$D_i$', '观测计数已有；原始身份/当前范围见下表', 'events/bin', '不是背景扣除残差'],
        ['$S_i$', 'XENONnT当前SM/V/B−L三箱可计算' if x else 'Ne重建信号MISSING；当前T投影不能代入', 'events/bin', '第7章相应能力'],
        ['$B_i^k$', '当前R17名义背景已有，精确原2024配套性待核' if x else '拟合/参考投影已有，原prefit形状另待补', 'events/bin', '下表严格区分来源版本与用途'],
        [r'$\alpha,\beta_s,\beta_k$', '定义的统计归一化nuisance；本轮未profile', '1', 'R01 PDF p6式(17)后；σ按单独模型表采用']])
    s += '\n' + eq.add('deviance', r'\chi^2_{\rm prof}=\min_{\alpha,\boldsymbol\beta}\left[2\sum_i\left(\mu_i-D_i+D_i\ln\frac{D_i}{\mu_i}\right)+\left(\frac{\alpha}{\sigma_\alpha}\right)^2+\sum_k\left(\frac{\beta_k}{\sigma_k}\right)^2\right]',
        'R01 PDF p6式(17)及后文；零观测的Dlog项取连续极限0。当前只记录合同，无minimizer结果。', [
        [r'$\sigma_\alpha$', '0.12，太阳总通量整体约束', '1', 'R01式(17)后；联合实验只计一次'],
        [r'$\sigma_k$', '下列再分析模型的率不确定度', '1', '不能与原实验native表或light-WIMP约束静默合并'],
        [r'$\mu_i>0$', 'Poisson模型合法域；尚未选择具体优化参数化', 'events/bin', '统计方法要求；未虚构协方差或置信阈值']])
    s += '\n上式pull求和覆盖信号率与各背景率的全部β参数；前一式背景求和中的k仅枚举背景组分。\n'
    nuisance = [('signal FV', .05), ('AC', .048), ('neutron', .50), ('ER', 1.)] if x else [('signal', .22), ('cathode', .31), ('MD', .23)]
    s += '\n' + table(['R01再分析归一化项', '相对σ', '直接出处/实际采用状态'], [[name, fmt(v), 'R01 PDF p6式(17)后；后续统计参考，本轮未profile'] for name, v in nuisance])
    if x:
        comp = read(SM / d['dataset'] / 'REFERENCE_COMPARISON.json')
        bkg = {key: np.asarray(value).sum(axis=0) for key, value in comp['backgrounds'].items()}
        observed = np.asarray(comp['observed']).sum(axis=0).astype(int)
        s += '\n### 当前绘图的直接名义背景与观测\n\n'
        s += table(['箱序号', 'D', 'AC', 'neutron', 'ER', 'B合计', 'SM+B'], [[i+1, int(observed[i]),
            f'{bkg["AC"][i]:.9f}', f'{bkg["neutron"][i]:.9f}', f'{bkg["ER"][i]:.9f}',
            f'{sum(bkg.values())[i]:.9f}', f'{sum(bkg.values())[i]+d["sm"]["counts"][i]:.9f}'] for i in range(3)])
        s += '\nB合计' + f'{sum(bkg.values()).sum():.9f}' + '，SM+B合计' + f'{(sum(bkg.values())+np.asarray(d["sm"]["counts"])).sum():.9f}' + '，观测37。R17 AC/ER原数组为3⁴；neutron为7×7×3⁴，取tLy=tQy=0（索引3,3），对其余观测轴求和并乘相应run曝光。**R17的b8模板只作信号对照，没有作为额外背景加到本项目SM上。**\n\n'
        s += raw_table(d, origin, ['xenonnt_sr0_background_and_b8_early_release.npz', 'xenonnt_sr1_background_and_b8_early_release.npz', 'xenonnt_original_fig2.txt', 'xenonnt_benchmark_fig1.txt'])
        s += '\n原图postfit与benchmark参考背景完整三箱如下，均为数字化参考，未取代上表R17直接名义模板：\n\n'
        for filename, sid in [('xenonnt_original_fig2.txt', 'R03 PDF p6 Fig.2'), ('xenonnt_benchmark_fig1.txt', 'R01 PDF p7 Fig.1')]:
            values = np.loadtxt(base / 'statistics' / filename)
            extracted = values[:, [0, 1, 2, 3, 4, 5]] if filename.startswith('xenonnt_original') else values[:, [0, 3, 4, 5, 6, 7]]
            s += '**' + sid + '**：\n\n' + table(['箱', 'D', 'AC', 'neutron', 'ER', '参考信号'], [[fmt(v) for v in row] for row in extracted]) + '\n'
        s += '\n### 原2024实验印刷的prefit与率约束（独立参考）\n' + scalar_reference(d, origin, 'xenonnt_prefit_inputs_2024.v2.1.json')
        s += '\n原实验声明AC率按run独立，其余参数联合约束（R03 PDF p6）。完整tLy/tQy约束函数/相关性与2024版本配套仍待核；不能把R17 light-WIMP分析中受约束的8B背景nuisance直接用于本任务自由信号拟合。\n'
        s += refs(d, origin, ['R01', 'R03', 'R08', 'R12', 'R17'])
    else:
        s += '\n### 原图观测、拟合背景与参考信号（八箱完整投影）\n\n'
        for filename, caption in [('pandax_original_fig5.txt', 'R02 2407.10892v3 PDF p6 Fig.5上图'), ('pandax_benchmark_fig1.txt', 'R01 2411.11749v1 PDF p7 Fig.1左图')]:
            values = np.loadtxt(base / 'statistics' / filename)
            s += '**' + caption + '**；' + link(origin, base / 'statistics' / filename, '原数值文件') + '：\n\n' + table(
                ['箱', 'Ne下界', 'Ne上界', 'D', 'cathode', 'MD', '参考信号'], [[fmt(v) for v in row] for row in values]) + '\n'
        s += '\n以上背景/信号由堆叠多边形厚度数字化，非独立测得背景，也非无条件可用prefit形状。数字化精度不等于物理误差；不从包络推断协方差。\n\n'
        s += scalar_reference(d, origin, 'pandax_prefit_inputs_2024.v2.1.json')
        s += '\n原US2逐run总率误差另列：\n' + scalar_reference(d, origin, 'pandax_us2_rate_uncertainties_2024.v2.1.json')
        s += '\n上述是R02 Table III/IV原实验的约束与总数，不等于R01采用的22/31/23%再分析约束。后续官方259日Ne/width事件表只作来源可核的参考；不能凭8箱D一致认证2024完整事件身份或原prefit背景形状。\n'
        s += refs(d, origin, ['R01', 'R02', 'R10', 'R11'])
    s += '\nFig.2的通量扫描如何重参数化12% flux pull，以及Fig.4的90% CL构造/自由度/阈值，目前都未通过本项目统计实现认证。本轮没有选择单位协方差、擅补独立高斯或把χ²公式存在当作已有扫描结果。\n'
    sections.append(('statistics', '8. Statistics、观测与背景的来源和适用范围', s))
    s = '正式Runtime数值权威是每实验YAML+NPZ。下列目录同时保存原始摘录、转换结果、候选与对照；“本地有文件”和“用于本轮计算”分别列出。完整哈希/原文件到正式键的关系见' + link(origin, OUT / 'NUMERICAL_INVENTORY.json', '本轮机器可读资源与溯源清单') + '。\n\n'
    s += '### 正式包全部数组索引\n\n' + table(['键', 'shape', '单位', '本版详细定义/数值所在章', '完整文件'], [[
        '`' + key + '`', str(meta['shape']), meta['unit'], '[' + array_owner(key) + '](#' + prefix + array_owner_id(key) + ')',
        link(origin, base / 'experiment.resources.npz', '正式NPZ')] for key, meta in d['package']['resources']['arrays'].items()])
    s += '\n### 全部辅助数值文件：出处、处理和当前用途\n\n'
    s += table(['文件/claim', '数值覆盖', '单位', '直接出处及转换', '本轮用途/限制'], [[
        link(origin, ROOT / item['file'], Path(item['file']).name) + ' `' + item['claim_id'] + '`',
        coverage(item['content']), item['unit'], item['source_id'] + '；' + item['locator'] + '；' + item['conversion'], item['current_role']] for item in d['raw']])
    if x:
        s += '\n### 辅助NPZ/产额JSON内的实际轴、shape和代表值\n\n'
        for item in d['raw']:
            if 'arrays' not in item['content'] and 'map' not in item['content']: continue
            s += '**' + link(origin, ROOT / item['file'], Path(item['file']).name) + '**；' + item['source_id'] + '，' + item['locator'] + '；用途：' + item['current_role'] + '。\n\n'
            arrays = item['content'].get('arrays', {k: v for k, v in item['content'].items() if k in ['coordinate_system', 'map', 'rate']})
            s += table(['原字段/轴', 'shape', '范围与代表值/完整小轴', '单位/解释'], [[
                key, str(value['shape']), info_values(value), auxiliary_unit(key, item)] for key, value in arrays.items()]) + '\n'
    s += '\n### 未采用的共享核多项式候选\n\n'
    nuclear = read(ROOT / 'data/responses/responses_all.json')['nuclei']
    nrows = []
    for key in ['Xe128', 'Xe129', 'Xe130', 'Xe131', 'Xe132', 'Xe134', 'Xe136']:
        q = nuclear[key]; channel = np.asarray(q['responses']['M'], dtype=float)
        nrows.append([key, fmt(q['basic']['J']), fmt(q['basic']['b']), ', '.join(q['responses']), str(channel.shape), seq(channel.reshape(-1)[[0, len(channel.reshape(-1))//2, -1]])])
    s += table(['核素键', 'J', '本地b数值', '实际通道键', 'M系数shape', 'M首/中/末系数'], nrows)
    s += '\n完整本地资源：' + link(origin, ROOT / 'data/responses/responses_all.json', 'responses_all.json，R16') + '；b及系数的外部原始单位/基底/归一化对应仍未独立闭合，表内只报告实际容器值，不认证外部核源。Xe124/Xe126键缺失。当前SM/V/B−L未读取这些系数，不将其覆盖缺口误列为解析KN所需输入。\n'
    s += refs(d, origin, sorted({item['source_id'] for item in d['raw']} | {'R16', 'R18'}))
    sections.append(('resources', '9. 全部数值资源、轴与逐项来源', s))
    s = '本版对已运行SM/V/B−L和待补能力分别给出状态；未把过时“无响应/未绑定”或候选模型当作当前事实。\n\n'
    s += handoff_table(d)
    s += '\n### 实际验证层次\n\n' + table(['记录', '实际结论', '不能替代的验证'], [
        ['2026-11-09文档整合', '当轮实际包/组件指纹与保存结果一致；数字文件和旧版本哈希保护；链接/数学/跳转另有验收', '该文档整合未重算物理谱；2026-11-10新增的简化谱另外记录'],
        ['2026-11-07 SM计算', '95项通过、4项既有文档/资源清单检查失败；新增solar 7项通过；所选旧数值回归通过', '不是“全仓库全部通过”；旧数组/容差未改'],
        ['2026-11-08 V/B−L计算', '27项相关测试全部通过；两实验各7点分别T/Eν收敛；带符号闭合通过', '不是非零点外部模板复现或官方likelihood认证']])
    s += '\n' + ' · '.join([link(origin, SM / 'TEST_RESULTS.json', 'SM实际测试/失败原因'), link(origin, SM / 'VALIDATION.json', 'SM输入与保存核验'),
        link(origin, VECTOR / 'TEST_RESULTS.json', 'V/B−L实际27项测试'), link(origin, VECTOR / 'VALIDATION.json', 'V/B−L验证范围'), link(origin, OUT / 'README.md', '本轮v3.0生成与验收')]) + '\n\n'
    if not x:
        s += '2026-11-10简化分支：10项相关测试通过；nominal与best-fit均独立加密T/Eν收敛，量化全T域与平均窗口的差值；作者c_i与nuisance点等价性不在机器PASS的认证范围。' + link(origin, SIMPLIFIED / 'README.md', '本轮实际结果和验收') + '。\n\n'
    s += '本轮来源核验分为：①文件存在与数值回读；②本地哈希与已登记来源一致；③原文真实性/转换/适用性继承P00/P01明确核验范围。文件或schema PASS不自动证明第三层完整。R18常量是项目明确采用的本地约定；R05 SSM只核书目，通量标量的直接出处是R01；R16外部核源未闭合；R13在线SI原文未缓存。\n\n'
    s += '### 标准参考文献总表\n\n'
    for sid in d['sources']:
        row = d['sources'][sid]
        s += '<a id="' + prefix + 'ref-' + sid + '"></a>\n\n**[' + sid + ']** ' + reference_citation(row) + '\n\n'
        q = Path(row['uri_or_path'])
        if q.is_file(): s += link(origin, q, '本地直接出处') + '；登记SHA256 `' + str(row.get('sha256')) + '`。\n\n'
        s += '核验范围：' + row.get('verification_scope', '按P01各claim定位') + '\n\n'
    s += '### 旧版保留与本版责任\n\n'
    s += 'v2.0/v2.1的提取记录、v2.2的SM报告、v2.3的矢量报告及原图/数组均保留。旧版只作为历史，不再要求读者来回拼接；版本列表统一在本实验README中。P00/P01/P03继续拥有来源、证据和配置权威；v3.0的输出映射另登记，不将文档整理当作新增科学批准。\n'
    sections.append(('status', '10. 缺失、交接、验证与完整参考文献', s))
    return sections, eq.records


def info_values(value):
    if 'all_values' in value: return seq(value['all_values'])
    if 'labels' in value: return ', '.join(value['labels'])
    if 'minimum' in value: return '范围' + seq([value['minimum'], value['maximum']]) + '；首/中/末' + seq(value['representative_first_middle_last'])
    return '文本/标识，完整值见原文件'


def coverage(content):
    if 'table' in content: return str(content['table']['shape']) + '，各列范围：' + '; '.join(seq([s['minimum'], s['maximum']]) for s in content['columns'])
    if 'arrays' in content: return '; '.join(k + ':' + str(v['shape']) for k, v in content['arrays'].items())
    if 'parameters' in content: return str(len(content['parameters'])) + '条标量及原误差'
    if 'rows' in content: return str(content['rows']) + '行；' + ', '.join(content['columns'])
    return '; '.join(k + ':' + str(v['shape']) for k, v in content.items() if isinstance(v, dict) and 'shape' in v)


def auxiliary_unit(key, item):
    if key in ['tLy', 'tQy']: return '无量纲nuisance坐标；不能当物理Ly/Qy'
    if key.startswith('energy_') or key == 'coordinate_system': return '能量坐标keVnr（JSON坐标）；完整字段定义见R17原件'
    if key.startswith('Ly_'): return 'photon/keVnr；物理产额坐标'
    if key.startswith('Qy_'): return 'electron/keVnr；物理产额坐标'
    if key.startswith('bin_edges_0'): return 'cS2，PE'
    if key.startswith('bin_edges_'): return '原shadow/S1BDT/S2BDT维度，无量纲'
    if 'probability' in key: return '1；接受后箱概率，Σ≤1'
    if key == 'rate': return 'events/(t·yr)，原CDF文件的积分总率；不是中微子通量'
    if 'rate_per_tyr_bin' in key or key in ['AC', 'ER', 'neutron']: return 'events/(t·yr·bin)'
    if key == 'observed': return 'events/bin'
    if key == 'events': return '原四观测量；各轴单位由axis_names/bin_edges确定'
    if key == 'map':
        if 'ly_ybe_' in item['file']: return 'photon/keVnr'
        if 'qy_ybe_' in item['file']: return 'electron/keVnr'
        return 'CDF无量纲；非中微子flux'
    return '轴标签/原字段，保持原约定'


def reference_citation(row):
    if row['source_id'] == 'R19':
        return read(VECTOR / 'BENCHMARK_CONFIG.json')['formula_source']['citation'].replace(
            'DOI: 10.1088/1475-7516/2025/05/012.', 'DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012).')
    return row['citation']


def handoff_table(d):
    common = [
        ['Fig.2/一维统计', '未运行；不能把公式存在当拟合完成', '明确采用分箱、flux nuisance参数化与数据/背景角色，再实现统计；联合通量约束仅一次'],
        ['Fig.4 V/B−L排除限', '未请求/未运行；前向测试点已完成', '具体χ²/CL构造、阈值与profile方案；无需S/A/T的自旋核输入'],
        ['S/A/T/Full EFT', '未实现本任务benchmark', '对应标量或自旋输入、匹配/归一化与外源核验；本地JSON存在不等于原文已核'],
        ['味相关接触NSI', '不在当前模型范围', '具体ε定义、flavor矩阵及太阳传播/味组成；不能沿用味普适代表态']]
    first = [
        ['当前SM/V/B−L重建谱', '可运行；早期R17重铸模型范围内已算', '严格2024复现仍需模型版本等价性/重铸误差核验'],
        ['XENONnT精确原生4D likelihood', '未实现/未认证', '2024配套81箱模板及tLy/tQy数值约束/相关性；R17已有模板与R08后续候选分开']
    ] if d['xenon'] else [
        ['当前SM/V/B−L真实反冲投影', '可运行；ROI选后总量估计及T分布；缺Ne箱分配', '可见T域内无新增必需数据；域外贡献待核，保留1.04t·yr合计曝光'],
        ['PandaX SM简化Ne八箱谱', 'SSM通量固定、c=1直接预测；后验拟合谱仅作参考', '严格作者等价性仍需原c_i及全套拟合点；参考谱缩放不提供独立验证'],
        ['PandaX完整Response Ne谱', '**BLOCKED / MISSING**', '2024 US2的P(Ne箱|T)，或能生成它的完整低能响应与选择配置；简化谱不解决该缺口'],
        ['PandaX逐run预测/原生2D likelihood', '部分输入已有，能力仍待补', 'afterglow veto后逐run有效曝光；width完整边界、prefit背景形状及约束/相关性']]
    return table(['下一步能力', '当前状态', '具体需要什么/阻断范围'], first + common)


def array_owner_id(key):
    if key.startswith('source_'): return 'source'
    if key.startswith('target_') or key == 'run_exposures_tyr': return 'target'
    if key.startswith('cs2_edges') or key == 'observable_edges': return 'observable'
    return 'detector'


def array_owner(key):
    return {'source': '第2章Source', 'target': '第3章Target', 'detector': '第5章Detector', 'observable': '第6章Observable'}[array_owner_id(key)]


def nav(d, origin):
    items = [(d['docs'] / 'experiment.physics.v3.0.md', '详细版v3.0'),
        (d['docs'] / 'experiment.physics.summary.v3.0.md', '精简版v3.0'),
        (d['docs'] / 'EXPERIMENT_USER_INPUT.v3.0.md', '用户资料v3.0'), (CENTRAL, '两实验完整总文档'),
        (d['run'] / 'P00_SOURCE_REGISTER.yaml', 'P00来源'), (d['run'] / 'P01_EVIDENCE_LEDGER.yaml', 'P01证据'),
        (d['run'] / 'P02_MISSING_AND_CONFLICTS.md', 'P02当前缺口'), (d['run'] / 'P03_PHYSICS_CONTRACT.yaml', 'P03配置'),
        (d['base'] / 'experiment.input.yaml', '机器标量卡'), (d['base'] / 'experiment.resources.npz', '完整数组'),
        (ROOT / 'data/benchmarks/solar_b8_vector_v1/benchmark.input.json', 'V/B−L Benchmark卡'), (OUT / 'README.md', '文档整合验收')]
    if not d['xenon']:
        items += [(ROOT / 'data/benchmarks/pandax_us2_simplified_v1/benchmark.input.json', '简化SM参数卡'),
                  (SIMPLIFIED / 'REPORT.md', '简化八箱结果与图')]
    return ' · '.join(link(origin, target, label) for target, label in items) + '\n\n'


def render_detailed(d, origin):
    bodies, equations = sections(d, origin)
    text = '# ' + d['dataset'] + ' — onboarding v3.0 完整整合版\n\n'
    text += ('**2026-11-09。文档整合版；科学接受NOT_REVIEWED，能力限制按章保留。**' if d['xenon'] else
             '**2026-11-10修订。新增SM简化八箱实际计算；完整Response与严格论文等价性仍待补，科学接受NOT_REVIEWED。**') + '\n\n' + nav(d, origin)
    text += '<a id="report-toc"></a>\n\n## 目录\n\n' + '\n'.join('- [' + title + '](#' + key + ')' for key, title, _ in bodies)
    text += '\n- [公式索引](#equation-index)\n- [参数/数组索引](#parameter-index)\n\n'
    for key, title, body in bodies:
        text += '<a id="' + key + '"></a>\n\n## ' + title + '\n\n' + body + '\n[返回目录](#report-toc)\n\n'
    text += '<a id="equation-index"></a>\n\n## 公式索引\n\n' + table(['式', '位置', '来源/推导性质'], [[
        item['number'], '[' + item['id'] + '](#' + item['id'] + ')', item['source']] for item in equations]) + '\n[返回目录](#report-toc)\n\n'
    text += '<a id="parameter-index"></a>\n\n## 参数/数组索引\n\n' + parameter_index(d) + '\n[返回目录](#report-toc)\n'
    return text, equations


def parameter_index(d, prefix=''):
    rows = []
    for key in d['package']['parameters']:
        owner = 'source' if key.startswith('source.') else ('target' if key.startswith('target.') or key in ['constants.avogadro', 'constants.amu_GeV', 'constants.electron_mass_GeV'] else
            ('prediction' if key.startswith('numerics.') or key == 'constants.seconds_per_year' else 'modules'))
        rows.append(['`' + key + '`', '[' + owner + '](#' + prefix + owner + ')', '正式YAML；本版对应章已列值、单位、出处'])
    rows += [['`' + key + '`', '[' + array_owner(key) + '](#' + prefix + array_owner_id(key) + ')', '正式NPZ；第9章完整索引'] for key in d['package']['resources']['arrays']]
    return table(['精确ID/数组键', '正文位置', '输入权威'], rows)


def render_combined(datasets):
    text = '# 太阳⁸B onboarding v3.0 — PandaX 与 XENONnT 完整整合版\n\n'
    text += '**2026-11-09整合，2026-11-10新增PandaX SM简化八箱结果。** 本文件可顺序读完两实验的现行输入、Response、D/B、SM/V/B−L计算、逐数据出处和交接。旧版本保留；固定SSM直接预测与后验拟合谱缩放参考分别标注，后者不作为独立校准的SM预测。\n\n'
    text += table(['实验', '本轮已完成', '仍受限/待补', '同源单实验版本'], [[
        d['dataset'], 'SM/V/B−L重建三箱谱' if d['xenon'] else 'SM/V/B−L真实反冲投影；新增SM简化Ne八箱谱',
        '早期重铸与精确2024分析等价性；统计/排除限未运行' if d['xenon'] else 'SM简化八箱谱已新增；完整US2逐Ne箱Response仍MISSING',
        link(CENTRAL, d['docs'] / 'experiment.physics.v3.0.md', '详细版') + ' · ' + link(CENTRAL, d['docs'] / 'experiment.physics.summary.v3.0.md', '精简版')
    ] for d in datasets])
    text += '\n' + ' · '.join([link(CENTRAL, OUT / 'README.md', 'v3.0来源/文件与渲染验收'), link(CENTRAL, OUT / 'NUMERICAL_INVENTORY.json', '45份辅助数据＋26正式数组清单'),
        link(CENTRAL, ROOT / 'workflows/_shared/references/onboarding/experiment-physics-report-contract.md', '共同文档规范'), link(CENTRAL, ROOT / 'workflows/_shared/references/onboarding/data-provenance-contract.md', '数据溯源规范')]) + '\n\n'
    text += '<a id="all-toc"></a>\n\n## 总目录\n\n'
    rendered = []; offset = 0; equations = []
    for d in datasets:
        prefix = 'xenon-' if d['xenon'] else 'pandax-'
        bodies, records = sections(d, CENTRAL, prefix, offset)
        offset += len(records); equations += records
        text += '- [' + d['dataset'] + '](#' + prefix + 'part)\n'
        text += '\n'.join('  - [' + title + '](#' + prefix + key + ')' for key, title, _ in bodies) + '\n'
        rendered.append((d, prefix, bodies))
    text += '- [全篇公式索引](#all-equations)\n\n'
    for d, prefix, bodies in rendered:
        text += '<a id="' + prefix + 'part"></a>\n\n## ' + d['dataset'] + '\n\n'
        for key, title, body in bodies:
            text += '<a id="' + prefix + key + '"></a>\n\n### ' + title + '\n\n' + re.sub(r'^### ', '#### ', body, flags=re.M) + '\n[返回总目录](#all-toc)\n\n'
    text += '<a id="all-equations"></a>\n\n## 全篇公式索引\n\n' + table(['连续编号', '实际公式', '出处/推导'], [[
        q['number'], '[' + q['id'] + '](#' + q['id'] + ')', q['source']] for q in equations]) + '\n[返回总目录](#all-toc)\n'
    return text, equations


def summary(d, origin, user=False):
    detailed = d['docs'] / 'experiment.physics.v3.0.md'
    title = '用户资料' if user else '精简阅读版'
    text = '# ' + d['dataset'] + ' — onboarding v3.0 ' + title + '\n\n2026-11-09，完整整合版本。' + link(origin, detailed, '详细版：全部数值、公式、来源和交接') + ' · ' + link(origin, CENTRAL, '两实验完整总文档') + '\n\n'
    text += '<a id="toc"></a>\n\n## 目录\n\n- [范围与决定](#scope)\n- [实际输入](#inputs)\n- [结果与限制](#results)\n- [下一步交接](#handoff)\n\n'
    text += '<a id="scope"></a>\n\n## 范围与决定\n\n'
    text += '用户已指定：使用完整Response、严格逐数据出处、保留旧版；先SM，再按同论文做V与B−L轻媒介子事例数谱。质量/耦合测试点是项目明示选择，不冒充文献拟合。当前不是Fig.2或Fig.4统计复现。\n\n'
    text += ('XENONnT采用R17早期官方YBe响应；原2024严格等价性限制保留。' if d['xenon'] else 'PandaX原Response路线保留；2026-11-10用户新增简化方法，SM八箱已计算，完整Ne响应仍MISSING。') + '\n\n[返回目录](#toc)\n\n'
    text += '<a id="inputs"></a>\n\n## 实际输入\n\n' + table(['模块', '已有数据/范围', '直接来源与采用范围'], [
        ['Source', 'Bahcall 829×4原表；中心谱积分0.999986544；Φ=5.46×10⁶cm⁻²s⁻¹', 'R04官网原表列1/2；R01 PDF p5式(11)后；不重归一化'],
        ['Target', '天然Xe九核素；NIST数丰度和原子质量；参考吨核数', 'R09全部九行；R13 SI常量；R18本地质量换算约定'],
        ['Response', '每run16×10×10×3接受后概率；YBe Ly/Qy各501点；T支撑0.51–5keVnr' if d['xenon'] else '99点US2总接受度；Qy nominal/best-fit/带已取得；Ne箱概率MISSING', 'R17 HDF5/median JSON' if d['xenon'] else 'R02 PDF p3 Fig.1、p5 Fig.4；Qy不能替代涨落核'],
        ['Observable/曝光', '两run各自3箱；1.174398/2.342593t·yr；按箱序号合计' if d['xenon'] else '简化Ne=4…8八箱已算；原0.3–3keVnr的27箱保留；1.04t·yr', 'R17原bins/livetime；R08官方D' if d['xenon'] else 'R01 p5式(12)后；R02 PDF p3及Fig.5'],
        ['共享理论', 'SM/KN；轻矢量V、B−L', 'R01 PDF p3式(1)–(3)；R19 PDF p5式(2.6),(2.10)；无需本地多项式核响应']])
    text += '\n' + link(origin, d['base'] / 'experiment.input.yaml', '正式YAML') + ' · ' + link(origin, d['base'] / 'experiment.resources.npz', '完整NPZ') + ' · ' + link(origin, d['run'] / 'P00_SOURCE_REGISTER.yaml', 'P00标准书目') + '\n\n'
    text += refs(d, origin, ['R01', 'R04', 'R09', 'R17' if d['xenon'] else 'R02', 'R19']) + '\n[返回目录](#toc)\n\n'
    text += '<a id="results"></a>\n\n## 结果与限制\n\n'
    text += table(['m=10MeV、g=2×10⁻⁵的项目测试点', 'SM', 'V', 'B−L'], [[
        '信号总数[events]' if d['xenon'] else '真实反冲投影[events]',
        f'{d["vector"]["results"]["SM"]["total_events"]:.9f}', f'{d["vector"]["results"]["V10_g2"]["total_events"]:.9f}', f'{d["vector"]["results"]["BL10_g2"]["total_events"]:.9f}']])
    text += '\n两实验各7点通过分维度收敛；2026-11-08相关27项测试通过。未运行χ²/90%CL。' + ('使用公开早期重铸Response，不宣称精确2024官方分析认证。' if d['xenon'] else '**这些数不是Ne∈[4,8]重建事件数。**') + '\n\n'
    if not d['xenon']: text += simplified_note(origin)
    text += link(origin, detailed, '完整逐箱、干涉分解及测试限制', '#prediction') + '\n\n[返回目录](#toc)\n\n'
    text += '<a id="handoff"></a>\n\n## 下一步交接\n\n' + handoff_table(d) + '\n[返回目录](#toc)\n'
    return text


def inventory(datasets):
    sources = datasets[0]['sources']; checks = []
    for sid, row in sources.items():
        path = Path(row['uri_or_path'])
        actual = sha(path) if path.is_file() else None
        status = 'HASH_MATCH' if actual and actual == row.get('sha256') else ('ONLINE_NOT_CACHED' if str(row['uri_or_path']).startswith('https://') else 'MISSING_OR_HASH_MISMATCH')
        checks.append({'source_id': sid, 'direct_source': row['uri_or_path'], 'expected_sha256': row.get('sha256'),
            'actual_sha256': actual, 'file_check_status': status, 'verification_scope': row.get('verification_scope')})
    return {'date': '2026-11-09', 'source_register_owner': 'canonical P00 per dataset; R IDs retained', 'source_file_checks': checks,
        'datasets': {d['dataset']: {'package': rel(d['base']), 'parameters': d['package']['parameters'],
            'formal_arrays': {key: dict(d['package']['resources']['arrays'][key], observed=stats(a)) for key, a in d['arrays'].items()},
            'auxiliary_files': d['raw'], 'SM_physics_fingerprint': d['sm']['physics_fingerprint'],
            'vector_physics_fingerprints': {key: v['physics_fingerprint'] for key, v in d['vector']['results'].items()}}
            for d in datasets},
        'verification_limit': 'Current files, values and fingerprints re-read; primary-source authenticity, conversions and applicability retain the specific P00/P01 verification scope. No new universal source authentication claimed.'}


def retire_old_navigation(path, before):
    """Replace obsolete solar navigation blocks, preserving the actual old reports."""
    name = rel(path)
    if name == 'tools/README.md' or name.startswith('outputs/'):
        return before
    retired = False
    for marker in ['response-onboarding-v2', 'pointwise-onboarding-v2.1', 'solar-b8-sm-20261107', 'solar-vector-20261108']:
        pattern = r'\n*<!-- ' + re.escape(marker) + r':start -->.*?<!-- ' + re.escape(marker) + r':end -->\n*'
        if re.search(pattern, before, re.S):
            before = re.sub(pattern, '\n\n', before, flags=re.S); retired = True
    before = before.replace('太阳 8B Response onboarding v2.1 修订草稿（新版本）', '太阳8B onboarding v3.0完整整合版')
    before = before.replace('— v2.1 修订草稿 Response 文档', '— 当前v3.0完整整合版')
    before = before.replace('SM结果和实际Gate由本轮计算后回填；不将计划当作已计算。', 'SM与V/B−L实际结果已保存；当前进度记录区分机器验证和待人类审阅的科学结果。')
    if name == 'data/experiments/README.md':
        before = before.replace('2026-11-06 新增的文献摘录资料（未注册、未绑定 Runtime）：', '太阳8B文献摘录与显式输入包：旧原表用于来源核对，标准Runtime读取正式YAML/NPZ；默认全局活动清单未变。')
        before = before.replace('本地三套正式 YAML/NPZ 齐全', '默认活动的三套COHERENT正式YAML/NPZ齐全，太阳8B另有可显式加载的正式包')
    if name == 'docs/experiments/README.md':
        before = before.replace('本目录目前说明 COHERENT 及三个已接入数据集，沿用程序的精确 `dataset_id`。', '本目录说明实验与精确dataset_id；下表COHERENT是三个默认活动数据集，太阳8B显式输入包及当前文档见上方v3.0入口。')
    if re.fullmatch(r'data/experiments/(PandaX4T|XENONnT)/README.md', name):
        current = '已可通过正式包运行SM/V/B−L真实反冲投影；US2 Ne响应仍缺' if 'PandaX4T' in name else '已可通过正式包运行SM/V/B−L三箱谱；保留早期重铸模型限制'
        before = before.replace('文献摘录数据', '实验输入与来源').replace('尚未绑定 Runtime', current).replace('尚未绑定Runtime', current)
    if retired:
        start='<!-- solar-onboarding-history:start -->';end='<!-- solar-onboarding-history:end -->'
        history='## 历史记录（当前内容已整合到v3.0）\n\n' + ' · '.join([
            link(path, ROOT / 'docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_SM_BENCHMARK_20261107.md', '2026-11-07 SM执行记录'),
            link(path, ROOT / 'docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_VECTOR_BENCHMARK_20261108.md', '2026-11-08 V/B−L执行记录')]) + '。旧实验报告与数值保留，各版本链接集中在dataset版本导航；本页仅以上方v3.0为当前说明。'
        block=start+'\n\n'+history+'\n\n'+end
        if start in before: before=re.sub(re.escape(start)+'.*?'+re.escape(end),lambda _:block,before,flags=re.S)
        else: before=before.rstrip()+'\n\n'+block+'\n'
    return before


def joint_readme(datasets):
    origin = JOINT / 'README.md'
    text = '# PandaX4T + XENONnT：太阳⁸B联合分析文档\n\n'
    text += '**组合对象：PandaX-4T 2024 US2 与 XENONnT 2024 Solar B8。** '
    text += '本目录集中保存两实验共用的onboarding合版、Response来源说明与SM/V/B−L benchmark报告。'
    text += '它是联合分析的文档目录，不是新的实验或dataset，不参与Runtime注册。\n\n'
    text += '## 当前阅读入口\n\n'
    text += table(['文件', '身份与用途'], [[link(origin, CENTRAL, 'onboarding v3.0 完整总文档'),
        '当前统一阅读版；包含两实验的全部现行输入、来源、Response、D/B、SM/V/B−L结果和交接']])
    text += '\n## SM逐步计算与workflow核对\n\n'
    text += link(origin, JOINT / 'SM_RESPONSE_WORKFLOW_AUDIT_20261109.md', '2026-11-09：2411.11749v1 Fig.1的SM Response逐步审计')
    text += '：主项目复算、逐步公式／实际数据／代码入口、run分箱与论文比较边界；各阶段的可计算范围和待补项分别列出。\n'
    text += '\n## 2026-11-10：PandaX SM简化八箱计算\n\n' + simplified_note(origin)
    text += '\n## 历史专题与计算记录\n\n'
    text += '以下文件保留当时的版本、数值和科学状态；当前结论及未决项以v3.0为准。\n\n'
    text += table(['文件', '记录范围'], [
        [link(origin, JOINT / 'SOLAR_B8_RESPONSE_REFERENCES.v2.md', 'Response参考文献 v2.0'), '2026-11-06，历史来源登记'],
        [link(origin, JOINT / 'SOLAR_B8_RESPONSE_REFERENCES.v2.1.md', 'Response参考文献 v2.1'), '2026-11-06，历史来源修订'],
        [link(origin, JOINT / 'SOLAR_B8_SM_BENCHMARK_20261107.md', 'SM benchmark报告'), '2026-11-07，两实验的SM执行入口'],
        [link(origin, JOINT / 'SOLAR_B8_VECTOR_BENCHMARK_20261108.md', 'V/B−L benchmark报告'), '2026-11-08，两实验的轻矢量媒介子执行入口']])
    text += '\n## 各实验独立文档与数据\n\n'
    text += table(['dataset', '独立文档', '数据与来源'], [[d['dataset'],
        link(origin, d['docs'] / 'README.md', '各版本和当前v3.0'),
        link(origin, d['base'] / 'README.md', '正式输入、数组及原表')] for d in datasets])
    text += '\n## 目录维护约定\n\n'
    text += '两实验共同使用的综述、引用与比较报告放在本目录；单实验onboarding继续放在其原dataset目录。'
    text += '数值输入留在`data/experiments/`，原始论文留在`docs/references/`，阶段证据留在各自`workflows/cevns-pyeft/runs/`。'
    text += '后续新增联合文档时同步本表、上级索引和实际生成器，不再平铺到`docs/experiments/`根目录。\n\n'
    text += link(origin, OUT / 'README.md', '本次目录搬迁与链接验收') + ' · '
    text += link(origin, JOINT.parent / 'README.md', '实验文档总目录') + '\n'
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--check', action='store_true')
    parser.add_argument('--validate', action='store_true', help='verify actual artifacts/preservation and write only current-run QA reports')
    args = parser.parse_args()
    if args.validate:
        raise SystemExit(validate())
    # v3.1 owns the current nuclear-Response reports/navigation. Keep this
    # generator available to verify the frozen v3.0 reports, never overwrite
    # current choices from subsequently updated P00/P01/P03 records.
    successor = ROOT / 'outputs/solar_b8_sm/20261110_nuclear_response_run2/ONBOARDING_BUILD_MANIFEST.json'
    if successor.is_file():
        if not args.check:
            raise SystemExit('v3.0 is historical and frozen; use build_solar_b8_onboarding_v3_1.py for current reports.')
        baseline = read(successor)['preserved_history']
        changed = [row['file'] for row in baseline if sha(ROOT / row['file']) != row['sha256']]
        print(json.dumps({'status': 'PASS' if not changed else 'DIFF', 'scope': 'frozen v3.0 history; current version is v3.1',
                          'mismatches': changed, 'protected_files': len(baseline)}, ensure_ascii=False))
        raise SystemExit(bool(changed))
    datasets = [load(*item) for item in FAMILIES]
    expected = {}; equations_by_file = {}; changed = []
    def put(path, text): expected[path] = text.rstrip() + '\n'
    def put_json(path, value): put(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
    def managed(path, text):
        before = expected.get(path, path.read_text(encoding='utf8') if path.exists() else '# ' + path.parent.name + '\n')
        before = retire_old_navigation(path, before)
        start='<!-- solar-onboarding-v3:start -->'; end='<!-- solar-onboarding-v3:end -->'
        block=start+'\n\n'+text.rstrip()+'\n\n'+end
        if start in before: after=re.sub(re.escape(start)+'.*?'+re.escape(end),lambda _:block,before,flags=re.S)
        else:
            first, *rest = before.split('\n', 1)
            after = first + '\n\n' + block + '\n\n' + (rest[0].lstrip() if rest else '')
        put(path, after)
    inv = inventory(datasets)
    put_json(OUT / 'NUMERICAL_INVENTORY.json', inv)
    for d in datasets:
        docs = d['docs']; detailed = docs / 'experiment.physics.v3.0.md'
        content, equations = render_detailed(d, detailed); put(detailed, content); equations_by_file[rel(detailed)] = equations
        put(docs / 'experiment.physics.summary.v3.0.md', summary(d, docs / 'experiment.physics.summary.v3.0.md'))
        put(docs / 'EXPERIMENT_USER_INPUT.v3.0.md', summary(d, docs / 'EXPERIMENT_USER_INPUT.v3.0.md', user=True))
        path = docs / 'README.md'
        text = '# ' + d['dataset'] + '：当前onboarding v3.0\n\n**当前统一阅读版本：v3.0，2026-11-09。** 详细版已整合Qy/Response、观测/背景、来源、SM与V/B−L结果及下一步依赖，不需要拼接旧版。\n\n'
        text += table(['当前入口', '用途'], [[link(path, detailed, '详细版v3.0'), '完整实验专属物理、实际数据、逐项来源、结果和交接'],
            [link(path, docs / 'experiment.physics.summary.v3.0.md', '精简版v3.0'), '快速阅读'], [link(path, docs / 'EXPERIMENT_USER_INPUT.v3.0.md', '用户资料v3.0'), '用户已确定的范围与补充项'],
            [link(path, CENTRAL, '两实验完整总文档'), '单文件连续阅读PandaX与XENONnT'], [link(path, d['run'] / '00_MIGRATION_PROGRESS.md', '主线进度'), '实际Gate/科学接受保留'],
            [link(path, d['base'] / 'experiment.input.yaml', '机器输入') + ' · ' + link(path, d['base'] / 'experiment.resources.npz', '完整数组'), '标准Runtime实际读取的YAML/NPZ']])
        text += '\n' + ('XENONnT的SM/V/B−L重建谱已运行；保留早期重铸版本限制。' if d['xenon'] else 'PandaX原真实反冲诊断保留，SM简化Ne八箱已新增；完整US2 Ne响应仍MISSING。') + '\n\n'
        if not d['xenon']: text += simplified_note(path)
        text += '## 旧版历史（原位保留）\n\n'
        text += table(['历史版本', '当时主要内容', '保留文件'], [[v, description,
            link(path, docs / ('experiment.physics.' + v + '.md'), '详细版') + ' · ' + link(path, docs / ('experiment.physics.summary.' + v + '.md'), '精简版') + ' · ' + link(path, docs / ('EXPERIMENT_USER_INPUT.' + v + '.md'), '用户资料')]
            for v, description in [('v2', '最初Response方案'), ('v2.1', '原文输入和来源修订'), ('v2.2', 'SM执行补充'), ('v2.3', 'V/B−L执行补充')]])
        text += '\n旧版状态按其生成时间保留，当前能力以v3.0和实际运行记录为准。\n'; put(path, text)
        path = d['base'] / 'README.md'
        put(path, '# ' + d['dataset'] + '：数据、正式输入与来源\n\n2026-11-09。当前说明统一为' + link(path, detailed, 'onboarding v3.0完整整合版') + '；' + link(path, CENTRAL, '两实验总文档') + '。\n\n' +
            table(['实际内容', '使用方式/性质'], [[link(path, d['base'] / 'experiment.input.yaml', 'experiment.input.yaml'), '正式标量/模型合同权威'],
                [link(path, d['base'] / 'experiment.resources.npz', 'experiment.resources.npz'), str(len(d['arrays'])) + '个正式数值数组；标准Runtime读取'],
                ['detector/、statistics/、reference/及根目录原表', str(len(d['raw'])) + '份辅助数值；来源、轴、shape、采用/候选身份见v3.0第9章'],
                [link(path, OUT / 'NUMERICAL_INVENTORY.json', '完整机器可读来源清单'), '每文件/正式键的哈希、单位、范围、代表值、原文定位、转换和当前用途'],
                ['experiment.physics.md / experiment.physics.summary.md', '原Compiler包内派生说明保留；当前人读版本为docs中的v3.0，不将旧模板通用“未绑定”文字当作当前执行事实']]) + '\n\n' +
            ('当前信号使用R17早期YBe基底和正式中位产额；R08的2026模板只是候选。官方观测、名义背景、图线拟合参考分别标注。' if d['xenon'] else 'SM简化Ne八箱采用nominal Qy与正式总接受度，固定SSM通量、c=1。后验拟合谱缩放仅作参考，未独立校准Response。原真实反冲投影与完整Ne箱Response缺口保留；259日CSV不冒充2024完整事件原件。') + '\n\n原始表、正式包与旧数值结果字节未变；旧onboarding保留原位。没有恢复旧七份遗留辅助表的读取。\n' + ('' if d['xenon'] else '\n'+simplified_note(path)))
        p02 = d['run'] / 'P02_MISSING_AND_CONFLICTS.md'
        put(p02, '# ' + d['dataset'] + '：当前缺口与交接（v3.0同步）\n\n2026-11-09，文档整合；不改变数值、模型或人工Gate。\n\n' + handoff_table(d) + '\n完整已有数据、原文定位、验证范围见' + link(p02, detailed, 'onboarding v3.0') + '。c_i不作为本项目完整Response前向路线的必需缺失项。\n')
        idx = d['run'] / 'ONBOARDING_V3_INDEX.json'
        put_json(idx, {'version': '3.0', 'date': '2026-11-09' if d['xenon'] else '2026-11-10', 'scope': 'documentation consolidation and explicitly separated benchmark branches', 'detailed': rel(detailed),
            'summary': rel(docs / 'experiment.physics.summary.v3.0.md'), 'user_input': rel(docs / 'EXPERIMENT_USER_INPUT.v3.0.md'), 'combined': rel(CENTRAL),
            'source_register': rel(d['run'] / 'P00_SOURCE_REGISTER.yaml'), 'evidence_ledger': rel(d['run'] / 'P01_EVIDENCE_LEDGER.yaml'),
            'physics_contract': rel(d['run'] / 'P03_PHYSICS_CONTRACT.yaml'),
            'claim_outputs': [{'claim_id': c['claim_id'], 'field': c['field'], 'v3_output': rel(detailed), 'prior_output_locations_retained': c.get('output_locations', [])} for c in d['claims'].values()],
            'simplified_benchmark': None if d['xenon'] else rel(SIMPLIFIED / 'RESULT.json'),
            'scientific_gates_changed_by_generator': False, 'data_or_runtime_changed_by_generator': False})
        progress_path = d['run'] / '00_MIGRATION_PROGRESS.md'
        before = progress_path.read_text(encoding='utf8'); progress = json.loads(re.search(r'```json\n(.*?)\n```', before, re.S)[1])
        if progress['artifact_refs'].get('onboarding_v3') != rel(idx):
            progress['previous_revision'] = progress['revision']; progress['revision'] += 1; progress['updated_at'] = '2026-11-09'
            progress['artifact_refs']['onboarding_v3'] = rel(idx)
        progress_intro = ('当前已新增用户授权的SM简化平均映射八箱分支；原Response与历史结果保留。各能力的机器检查和科学接受分别登记。' if progress['artifact_refs'].get('simplified_benchmark') else
                          '当前人读说明：onboarding v3.0完整整合版；当前生成只更新文档索引，科学Gate与checkpoint由已有执行记录保留。')
        put(progress_path, '# 主线进度：' + d['dataset'] + '\n\n' + progress_intro + '\n\n```json\n' + json.dumps(progress, ensure_ascii=False, indent=2) + '\n```')
        managed(d['run'] / 'README.md', '## 当前统一onboarding：v3.0\n\n' + link(d['run'] / 'README.md', detailed, '全部物理输入、来源、SM/V/B−L与交接') + ' · ' + link(d['run'] / 'README.md', idx, '同一证据链的v3.0输出索引') + '。旧阶段记录保留；文档合版不授予新的科学接受。')
        for path in [docs.parent / 'README.md', docs.parent.parent / 'README.md', d['base'].parent / 'README.md']:
            if path.exists(): managed(path, '## 当前太阳8B onboarding v3.0\n\n' + link(path, detailed, '本实验完整整合版') + ' · ' + link(path, CENTRAL, 'PandaX与XENONnT单文件总文档'))
    text, equations = render_combined(datasets); put(CENTRAL, text); equations_by_file[rel(CENTRAL)] = equations
    put(JOINT / 'README.md', joint_readme(datasets))
    for name in ['README.md', 'docs/experiments/README.md', 'data/README.md', 'data/experiments/README.md', 'workflows/cevns-pyeft/README.md', 'workflows/cevns-pyeft/runs/README.md']:
        path = ROOT / name; managed(path, '## 当前太阳⁸B onboarding：v3.0完整整合版（2026-11-09）\n\n' + link(path, CENTRAL, '单文件阅读PandaX与XENONnT：全部输入、来源、SM/V/B−L结果及交接') + '。本版合并v2.0–v2.3的有效内容；旧版本保留。')
    managed(ROOT / 'tools/README.md', '## Solar B8 onboarding v3.0\n\n[build_solar_b8_onboarding_v3.py](build_solar_b8_onboarding_v3.py)从实际正式包、P00/P01及保存的SM/矢量结果同源生成完整总文档和两套详细/精简/用户资料；`--check`只读核对，`--validate`检查实际来源/文档/旧文件保护并只写本轮QA；科学Gate/输入/Runtime不变。[validate_solar_b8_onboarding_v3.mjs](validate_solar_b8_onboarding_v3.mjs)验证实际数学渲染、目录跳转、公式编号与窄屏布局。')
    parent = OUT.parent / 'README.md'; managed(parent, '## 当前文档与目录验收\n\n' + link(parent, OUT / 'README.md', '20261109_layout_r1/') + '：联合文档归位、来源/数据回读、文件保护和图文验收。\n\n[20261109/](20261109/README.md)：整理前的v3.0合版验收，按当时文件路径原样保留；当前文档位置见联合目录。')
    managed(ROOT / 'outputs/README.md', '## Solar B8 onboarding v3.0整合验收\n\n[solar_b8_onboarding_v3/](solar_b8_onboarding_v3/README.md)保存文档合版的输入/来源清单、文件保护、生成一致性与阅读性检查。物理结果沿用既有SM/矢量运行。')
    put_json(OUT / 'EQUATION_RECORDS.json', equations_by_file)
    for path, text in expected.items():
        content = text.encode('utf8')
        if not path.exists() or path.read_bytes() != content:
            changed.append(rel(path))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(content)
    if args.check:
        print(json.dumps({'status': 'PASS' if not changed else 'DIFF', 'mismatches': changed}, ensure_ascii=False))
        raise SystemExit(bool(changed))
    manifest = {'date': '2026-11-09', 'documents_and_records': [rel(p) for p in expected], 'changed_files': changed,
        'combined_document': rel(CENTRAL), 'source_inputs': [{'file': rel(d['base'] / name), 'sha256': sha(d['base'] / name)}
            for d in datasets for name in ['experiment.input.yaml', 'experiment.resources.npz']],
        'equation_counts': {name: len(rows) for name, rows in equations_by_file.items()}, 'runtime_and_scientific_changes': False}
    (OUT / 'BUILD_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'generated_documents_and_records': len(expected), 'auxiliary_files': sum(len(d['raw']) for d in datasets),
        'formal_arrays': sum(len(d['arrays']) for d in datasets), 'combined': rel(CENTRAL)}, ensure_ascii=False))


def validate():
    from urllib.parse import unquote
    from tools.validate_docs import audit, link_targets
    from cevns_pyeft.experiments.input_package import validate_package
    manifest = read(OUT / 'BUILD_MANIFEST.json'); inv = read(OUT / 'NUMERICAL_INVENTORY.json')
    protected = read(OUT / 'PRESERVATION_BASELINE.json')
    changed_protected = [r['file'] for r in protected if sha(ROOT / r['file']) != r['sha256']]
    errors = [{'protected_file_changed': name} for name in changed_protected]
    datasets = [load(*item) for item in FAMILIES]
    packages = []
    for d in datasets:
        p = validate_package(d['base']); packages.append({'dataset': d['dataset'], 'status': p['status']}); errors += p['errors']
        for item in d['raw']:
            assert sha(ROOT / item['file']) == item['sha256']
            assert item['source_id'] in d['sources'] and item['locator'] and item['current_role']
        for key, meta in d['package']['resources']['arrays'].items():
            assert list(d['arrays'][key].shape) == meta['shape']
            assert sha(d['base'] / 'experiment.resources.npz') == d['sm']['resource_archive_sha256']
    assert sum(len(d['raw']) for d in datasets) == 45
    assert sum(len(d['arrays']) for d in datasets) == 26
    for row in inv['source_file_checks']:
        if row['file_check_status'] != 'HASH_MATCH' and not (row['source_id'] == 'R13' and row['file_check_status'] == 'ONLINE_NOT_CACHED'):
            errors.append({'source_file': row})
    selected = sorted({name for name in manifest['documents_and_records'] if name.endswith('.md')} | {rel(OUT / 'README.md')})
    ordinary = [name for name in selected if not name.startswith('outputs/')]
    docs = audit(ROOT, files=ordinary); errors += docs['broken_current_links']
    output_links = []
    for name in [name for name in selected if name.startswith('outputs/')]:
        source = ROOT / name
        for line, raw in link_targets(source.read_text(encoding='utf8')):
            value = raw.strip().strip('<>')
            if re.match(r'^(https?:|mailto:|data:|#)', value): continue
            exists = (source.parent / unquote(value.split('#', 1)[0])).resolve().exists()
            output_links.append({'file': name, 'line': line, 'target': raw, 'exists': exists})
            if not exists: errors.append(output_links[-1])
    equations = read(OUT / 'EQUATION_RECORDS.json')
    for name, rows in equations.items():
        text = (ROOT / name).read_text(encoding='utf8')
        assert not text.startswith('\ufeff') and '\r' not in text and '\ufffd' not in text
        numbers = [int(n) for n in re.findall(r'\\tag\{(\d+)\}', text)]
        assert numbers == list(range(1, len(rows) + 1)), name
        assert all(row['source'] and row['symbols'] for row in rows)
    result = {'date': '2026-11-09', 'scope': 'documentation-only v3.0 consolidation; existing execution fingerprints checked without rerunning event spectra',
        'formal_packages': packages, 'auxiliary_numeric_files': 45, 'formal_arrays': 26,
        'registered_sources': len(inv['source_file_checks']), 'local_source_hash_matches': sum(r['file_check_status'] == 'HASH_MATCH' for r in inv['source_file_checks']),
        'online_source_not_cached': ['R13'], 'preserved_files': len(protected), 'changed_protected_files': changed_protected,
        'documents': len(selected), 'local_links': docs['local_links'] + len(output_links),
        'numbered_equations': {name: len(rows) for name, rows in equations.items()}, 'errors': errors,
        'scientific_scope_preserved': 'XENONnT early-response SM/V/B-L forward; PandaX true-recoil only; Ne response MISSING; inference not run',
        'source_verification_limit': 'Local files/hash/array reads and existing P00/P01 scope, not new universal primary-source authentication.',
        'physics_tests': 'Not rerun for documentation-only changes. Earlier 95 passed/4 existing failed SM checks and 27 passed vector-targeted tests are preserved and cited.'}
    for path, value in [(OUT / 'DOC_LINKS.json', dict(docs, explicit_output_navigation=output_links)), (OUT / 'DOC_SELECTION.json', selected), (OUT / 'VALIDATION.json', result)]:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({key: result[key] for key in ['formal_packages', 'auxiliary_numeric_files', 'formal_arrays', 'preserved_files', 'documents', 'local_links', 'errors']}, ensure_ascii=False))
    return bool(errors)


if __name__ == '__main__': main()


