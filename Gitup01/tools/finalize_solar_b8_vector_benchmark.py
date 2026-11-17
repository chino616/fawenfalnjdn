"""Publish versioned vector benchmark records, or validate their exact artifacts.

Only additive NSI/NGI evidence and navigation are updated. Existing SM packages,
source modules, numerical references and reports are preserved. --validate-only
writes validation results in the selected run, without changing canonical files.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cevns_pyeft.experiments.input_package import validate_package
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.solar_vector import with_solar_light_vector
from jsonschema import Draft202012Validator

CHANGED = []


def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def link(p, target, label): return '[' + label + '](<' + os.path.relpath(target, p.parent).replace('\\', '/') + '>)'


def write(p, content):
    CHANGED.append({'file': rel(p), 'operation': 'modify' if p.exists() else 'create'})
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.rstrip() + '\n', encoding='utf8', newline='\n')


def dump(p, obj): write(p, json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False))


def managed(p, content):
    start = '<!-- solar-vector-20261108:start -->'; end = '<!-- solar-vector-20261108:end -->'
    before = p.read_text(encoding='utf8') if p.exists() else '# ' + p.parent.name + '\n'
    block = start + '\n\n' + content.rstrip() + '\n\n' + end
    if start in before:
        assert before.count(start) == before.count(end) == 1
        after = re.sub(re.escape(start) + '.*?' + re.escape(end), lambda _: block, before, flags=re.S)
    else:
        after = before.rstrip() + '\n\n' + block
    write(p, after)


def phase(run, name, capability, handoff, artifacts, inputs, status='PASS'):
    path = run / 'phases' / (name + '_vector_benchmark.md')
    record = {'schema_version': 1, 'phase': name, 'capability_id': 'solar_b8.vector.' + capability,
        'workspace': 'canonical', 'plan_status': 'READY' if status == 'PASS' else 'BLOCKED',
        'machine_gate': status, 'human_gate': 'NOT_REVIEWED', 'scope_ref': rel(OUT / 'EXECUTION_PLAN.json'),
        'input_refs': [rel(p) for p in inputs],
        'input_fingerprint': hashlib.sha256(''.join(sha(p) for p in inputs).encode()).hexdigest(),
        'evidence_refs': [rel(run / 'P01_EVIDENCE_LEDGER.yaml')], 'decision_refs': ['D0002'], 'approval_refs': [],
        'artifacts': [{'path': rel(p), 'sha256': sha(p), 'role': 'actual vector benchmark result'} for p in artifacts],
        'checks': [{'name': 'fixed-point Slow and independent signed-interference closure', 'status': status,
            'command': 'python -B tools/run_solar_b8_vector_benchmark.py --output ' + rel(OUT),
            'result_ref': rel(artifacts[0])}], 'handoff': handoff}
    write(path, '# ' + name + ': ' + capability + '\n\n2026-11-08。按用户选择继续V与B−L事例数谱。机器验证与科学接受分开；Human仍为NOT_REVIEWED。\n\n```json phase-result\n' +
        json.dumps(record, ensure_ascii=False, indent=2) + '\n```')
    return path, record


def publish(config):
    tests = read(OUT / 'TEST_RESULTS.json')
    assert tests['passed'] == tests['tests'] and tests['failures'] == tests['errors'] == 0
    datasets = []
    for row in config['packages']:
        family = row['family']; dataset = row['dataset_id']; xenon = family == 'XENONnT'
        data = ROOT / row['path']; run = ROOT / 'workflows/cevns-pyeft/runs' / family / dataset
        docs = ROOT / 'docs/experiments' / family / 'datasets' / dataset; output = OUT / dataset
        result = read(output / 'DATASET_RESULT.json')
        register = read(run / 'P00_SOURCE_REGISTER.yaml')
        source = config['formula_source']
        r19 = {'source_id': 'R19', 'citation': source['citation'] + ' DOI: [' + source['doi'] + '](' + source['doi'] + ').',
            'uri_or_path': str(ROOT / source['file']), 'sha256': source['sha256'],
            'download_url': source['download_url'], 'locator': source['locator'],
            'verification_scope': '本地PDF原文与第5页渲染核对；仅用式(2.6),(2.10)及κ/g定义明确新矢量耦合。' + source['version_difference']}
        register['sources'] = [s for s in register['sources'] if s['source_id'] != 'R19'] + [r19]
        dump(run / 'P00_SOURCE_REGISTER.yaml', register)
        ledger = read(run / 'P01_EVIDENCE_LEDGER.yaml')
        ledger['claims'] = [c for c in ledger['claims'] if not c['claim_id'].startswith('VECTOR20261108-')]
        inherited = [c['claim_id'] for c in ledger['claims'] if c['claim_id'].startswith('SM20261107-A') or c['claim_id'].startswith('SM20261107-P')]
        ledger['claims'] += [
            {'claim_id': 'VECTOR20261108-MODEL', 'field': 'theory_response/light_vector', 'status': 'SOURCE_EXTRACTED',
             'source_id': 'R19', 'locator': source['locator'], 'value': {'C_V': '3 A g^2', 'kappa_V': 1., 'kappa_BL': -1/3},
             'unit': '1', 'input_claims': [], 'decision_refs': ['D0002'],
             'verification_scope': '原文公式及版本差异已目视核验；SM源/靶/Response沿既有显式输入，不认证完整官方likelihood'},
            {'claim_id': 'VECTOR20261108-POINTS', 'field': 'benchmark/project_test_points', 'status': 'PROJECT_DERIVED',
             'source_id': None, 'locator': '显式项目测试点卡，数值用于抵消/回升/传播子质量测试；不是原文拟合点',
             'value': {'file': rel(ROOT / 'data/benchmarks/solar_b8_vector_v1/benchmark.input.json'),
                 'sha256': sha(ROOT / 'data/benchmarks/solar_b8_vector_v1/benchmark.input.json'), 'points': config['points']},
             'unit': 'mass MeV; g dimensionless', 'input_claims': ['VECTOR20261108-MODEL'], 'decision_refs': ['D0002'],
             'verification_scope': '用户确认V/B−L事例数谱范围；各m/g为执行者明确标注的项目测试选择，不伪造用户指定参数'}]
        for point in config['points']:
            item = result['results'][point['id']]
            ledger['claims'].append({'claim_id': 'VECTOR20261108-' + point['id'], 'field': 'prediction/vector/' + point['id'],
                'status': 'PROJECT_DERIVED', 'source_id': None,
                'value': {'file': rel(output / point['id'] / 'RESULT.json'), 'counts': item['counts'],
                    'total_events': item['total_events'], 'physics_fingerprint': item['physics_fingerprint']},
                'unit': 'events/bin', 'locator': '标准load_experiment_package→interaction组件替换→predict_experiment；共享Slow/Response',
                'input_claims': ['VECTOR20261108-MODEL', 'VECTOR20261108-POINTS'] + inherited, 'decision_refs': ['D0002'],
                'verification_scope': '独立T/Eν收敛、逐核素带符号分解闭合、同参数SM回归；非外部非零点模板/置信边界复现'})
        dump(run / 'P01_EVIDENCE_LEDGER.yaml', ledger)
        contract = read(run / 'P03_PHYSICS_CONTRACT.yaml')
        contract['sections']['theory_response']['fields']['light_vector_benchmark'] = {
            'value': {'model': 'light_vector_kn_v1', 'scope': 'flavor-universal V and B-L fixed-point spectra',
                'implementation': 'cevns_pyeft/theory/light_vector.py', 'parameter_card': 'data/benchmarks/solar_b8_vector_v1/benchmark.input.json'},
            'unit': '1', 'evidence_claims': ['VECTOR20261108-MODEL', 'VECTOR20261108-POINTS'],
            'provenance_status': 'PROJECT_DERIVED', 'decision_status': 'DRAFT', 'blocking_scope': []}
        contract['sections']['slow_counts']['fields']['light_vector_results'] = {
            'value': {key: r['counts'] for key, r in result['results'].items()}, 'unit': 'events/bin',
            'evidence_claims': ['VECTOR20261108-' + p['id'] for p in config['points']],
            'provenance_status': 'PROJECT_DERIVED', 'decision_status': 'DRAFT',
            'blocking_scope': [] if xenon else ['PandaX reconstructed Ne spectrum: MISSING P(Ne-bin|T)']}
        dump(run / 'P03_PHYSICS_CONTRACT.yaml', contract)
        decisions = read(run / 'P04_DECISION_LOG.yaml')
        decisions['entries'] = [e for e in decisions['entries'] if e['decision_id'] != 'D0002'] + [{
            'decision_id': 'D0002', 'date': config['date'], 'user_quote': '请你继续做NSI的benchmark',
            'scope_confirmation': config['scope_confirmation']['user_reply'], 'scope': 'same-paper V/B-L light-mediator event spectra',
            'interpretation': '沿用正式太阳8B输入包与Response；六个m/g数值是明确标注的项目测试点。采用期刊版矢量耦合定义，记录v1记号差异。',
            'execution_authorized': True, 'result_acceptance': 'NOT_REVIEWED',
            'scope_limits': ['no Fig.4 exclusion fit', 'no contact epsilon or flavor-dependent propagation', 'no fabricated PandaX Ne kernel', 'no c_i']}]
        dump(run / 'P04_DECISION_LOG.yaml', decisions)
        auth = read(run / 'AUTHORIZATION_LOG.yaml')
        auth['entries'] = [e for e in auth['entries'] if e['authorization_id'] != 'W0002'] + [{
            'authorization_id': 'W0002', 'status': 'ACTIVE', 'date': config['date'], 'approval_kind': 'manual_write',
            'approval_message_ref': 'conversation:2026-11-08-vector-benchmark-confirmation',
            'user_quote': '请你继续做NSI的benchmark；' + config['scope_confirmation']['user_reply'], 'scope': 'existing_dataset',
            'allowed_actions': ['create', 'modify'], 'create_paths': ['cevns_pyeft/theory/light_vector.py', 'cevns_pyeft/experiments/solar_vector.py',
                'data/benchmarks/solar_b8_vector_v1/', rel(OUT), rel(run / 'phases'), rel(docs)],
            'modify_paths': [rel(run), 'README/navigation owners'], 'delete_paths': [], 'production_paths_affected': True,
            'recovery_plan': 'backup/solar-b8-vector-20261108-01/MANIFEST.json', 'result_acceptance_separate': True}]
        dump(run / 'AUTHORIZATION_LOG.yaml', auth)
        inputs = [data / 'experiment.input.yaml', data / 'experiment.resources.npz', ROOT / 'data/benchmarks/solar_b8_vector_v1/benchmark.input.json',
            ROOT / 'cevns_pyeft/theory/light_vector.py', ROOT / 'cevns_pyeft/experiments/solar_vector.py']
        artifacts = [output / 'DATASET_RESULT.json', output / 'BENCHMARK_REPORT.md', output / 'events.png']
        handoffs = {
            'P04': {'theory_scope': 'Real flavor-universal light V/B-L; published JCAP Eqs.(2.6),(2.10)',
                'coefficient_convention': 'C_V=3 A g^2; kappa=1 or -1/3; SM+NP amplitudes squared together',
                'nuclear_responses': 'Existing analytic KN per natural Xe isotope; no spin table for vector',
                'coverage': 'universal diagonal vector only; no scalar/axial/tensor or generic flavor LEFT',
                'runtime_binding': 'LightVectorKN via standard interaction override', 'external_evidence_limits': config['limits']},
            'P05': {'process_and_mass': 'elastic nu-Xe, exact existing mass/endpoint conventions', 'kinematics': 'existing ElasticKinematics',
                'cross_section_api': 'LightVectorKN.dsigma_dT -> DifferentialCrossSection',
                'units_and_axes': 'E MeV, recoil keVnr, internal GeV, output cm2/keVnr',
                'support_and_limits': 'positive mediator mass; real universal coupling; no massless/IR extrapolation',
                'benchmark': 'g=0 SM, heavy decoupling, g^4 NP-only, signed interference and cancellation, weak-charge zero case'},
            'P07': {'normalization_ledger': result['results']['SM']['normalization_ledger'],
                'output_contract': result['observable'], 'numerics_and_convergence': {k: r['convergence'] for k, r in result['results'].items()},
                'reference_comparison': 'Previous SM counts matched; independent per-isotope reweight/fold closure for each nonzero point',
                'freeze_scope': {'kind': 'versioned fixed-point numerical candidate', 'human_freeze': 'NOT_REVIEWED', 'Fast_authorized': False}},
            'P10': {'delivery_scope': {'mode': 'theory_change', 'target': 'V/B-L event spectra', 'completion': 'partial'},
                'capability_matrix': [{'id': 'vector_forward' if xenon else 'vector_true_recoil', 'requested': True, 'required_for_claim': True,
                    'machine_gate': 'PASS', 'human_gate': 'NOT_REVIEWED', 'result_ref': rel(output / 'DATASET_RESULT.json')},
                    {'id': 'vector_reconstructed_spectrum', 'requested': True, 'required_for_claim': True,
                     'machine_gate': 'PASS' if xenon else 'BLOCKED', 'human_gate': 'NOT_REVIEWED', 'result_ref': rel(output / 'BENCHMARK_REPORT.md')}],
                'validation_levels': {'numerical_and_analytic': 'PASS', 'targeted_regressions': str(tests['passed']) + ' passed',
                    'published_nonzero_point_template': 'UNAVAILABLE', 'Fig4_exclusion': 'NOT_REQUESTED'},
                'runtime_integration': 'existing standard component API; formal SM packages and default registry unchanged',
                'final_claim': 'fixed-point vector forward spectra; explicit response/source limitations', 'limitations': config['limits']}}
        phases = {}
        for name in ['P04', 'P05', 'P07', 'P10']:
            p, record = phase(run, name, name.lower(), handoffs[name], artifacts, inputs,
                status='BLOCKED' if name == 'P10' and not xenon else 'PASS')
            phases[name] = (p, record)
        impl = read(run / '00_IMPLEMENTATION_MANIFEST.yaml')
        impl.setdefault('extensions', {})['light_vector_20261108'] = {'date': config['date'], 'decision_ref': 'D0002', 'authorization_ref': 'W0002',
            'inputs': [rel(p) for p in inputs], 'actual_outputs': [rel(p) for p in artifacts],
            'standard_api': 'with_solar_light_vector -> load_experiment(components=interaction) -> predict_experiment',
            'human_result_acceptance': 'NOT_REVIEWED'}
        dump(run / '00_IMPLEMENTATION_MANIFEST.yaml', impl)
        index = run / '00_MIGRATION_PROGRESS.md'
        old_text = index.read_text(encoding='utf8'); progress = json.loads(re.search(r'```json\n(.*?)\n```', old_text, re.S)[1])
        previous = progress['revision']
        progress['previous_revision'] = previous; progress['revision'] = previous + 1; progress['updated_at'] = config['date']
        progress['previous_checkpoint'] = progress['checkpoint']
        progress['checkpoint'] = {'phase_id': 'P10', 'phase_name': 'V/B-L fixed-point benchmark delivery', 'skill': 'cevns-experiment',
            'step_id': 'vector_forward.result_review', 'next_action': 'review benchmark and retained public response limitations' if xenon else 'obtain US2 Ne-bin response to complete reconstructed vector spectra', 'resume_requires': []}
        for name, (p, record) in phases.items():
            progress['gates'][name + '_vector'] = {'machine': record['machine_gate'], 'human': 'NOT_REVIEWED', 'report_ref': rel(p),
                'capability': record['capability_id'], 'decision_refs': ['D0002']}
            progress['artifact_refs']['phase_reports'][name + '_vector'] = rel(p)
        progress['authorization_refs']['vector_scope'] = 'D0002'; progress['authorization_refs']['vector_write'] = 'W0002'
        assert index.read_text(encoding='utf8') == old_text, 'Concurrent progress revision change'
        write(index, '# 主线进度：' + dataset + '\n\nSM与V/B−L固定点结果均已落盘；科学结果仍为NOT_REVIEWED。旧SM记录和数值保留。\n\n```json\n' + json.dumps(progress, ensure_ascii=False, indent=2) + '\n```')
        detailed = docs / 'experiment.physics.v2.3.md'
        content = (output / 'BENCHMARK_REPORT.md').read_text(encoding='utf8')
        content = content.replace('# ' + dataset + ': vector benchmark', '# ' + dataset + '：onboarding v2.3（新版本，V/B−L benchmark草稿）', 1)
        content = re.sub(r'\]\(<([^>]+)>\)', lambda m: '](<' + os.path.relpath((output / m[1]).resolve(), docs).replace('\\', '/') + '>)', content)
        content = content.replace('## 目录', '旧版本保留：' + link(detailed, docs / 'experiment.physics.v2.2.md', 'v2.2 SM详细版') + ' · ' + link(detailed, run / 'P00_SOURCE_REGISTER.yaml', 'P00来源') + ' · ' + link(detailed, run / 'P01_EVIDENCE_LEDGER.yaml', 'P01证据') + '\n\n## 目录', 1)
        write(detailed, content)
        write(docs / 'experiment.physics.summary.v2.3.md', '# ' + dataset + '：onboarding v2.3精简草稿\n\n2026-11-08。' +
            link(docs / 'experiment.physics.summary.v2.3.md', detailed, '全部参数、数值、出处、干涉与缺口') + '\n\n' +
            ('V/B−L重建谱已计算；保留公开早期Response的适用性限制。' if xenon else '只计算真实反冲投影；US2逐Ne箱Response仍缺。') + '本轮没有计算Fig.4排除限；结果尚未由用户验收。')
        write(docs / 'EXPERIMENT_USER_INPUT.v2.3.md', '# ' + dataset + '：用户资料v2.3（新版本）\n\n2026-11-08。用户明确选择：' +
            config['scope_confirmation']['user_reply'] + '。\n\n' + link(docs / 'EXPERIMENT_USER_INPUT.v2.3.md', detailed, '实际输入、具体出处和计算结果') +
            '\n\n沿用Response、不引入c_i、保留旧版本。质量/耦合数值为项目测试选择；采用期刊版矢量C_V定义并显式记录v1差异。结果接受NOT_REVIEWED。')
        for p in [run / 'README.md', docs / 'README.md']:
            managed(p, '## 新版v2.3：V与B−L事例数谱\n\n' + ' · '.join([link(p, detailed, 'onboarding v2.3'),
                link(p, output / 'BENCHMARK_REPORT.md', '逐项来源、实际计算与限制'), link(p, index, '当前主线进度')]))
        datasets.append({'family': family, 'dataset_id': dataset, 'docs': detailed, 'phases': phases})
    central = ROOT / 'docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_VECTOR_BENCHMARK_20261108.md'
    write(central, '# 太阳8B：V/B−L benchmark主线入口\n\n2026-11-08，新版本，DRAFT/PARTIAL。正式SM输入包、既有源/靶/Response和Slow均复用，只替换共享相互作用组件。\n\n' +
        link(central, OUT / 'REPORT.md', '共享模型、测试点、来源与完整结果') + ' · ' + link(central, OUT / 'TEST_RESULTS.json', '27项实际测试') + ' · ' + link(central, OUT / 'VALIDATION.json', '本轮验收记录') + '\n\n' +
        '\n'.join('- ' + link(central, row['docs'], row['dataset_id'] + ' onboarding v2.3') for row in datasets) +
        '\n\nXENONnT：V/B−L重建谱已计算。PandaX：只完成真实反冲诊断，Ne响应仍缺。不是Fig.4排除限拟合。旧onboarding和SM数值保留。')
    for name in ['README.md', 'docs/experiments/README.md', 'data/README.md', 'workflows/cevns-pyeft/README.md', 'workflows/cevns-pyeft/runs/README.md']:
        p = ROOT / name
        navigation = ' · ' + link(p, ROOT / 'data/benchmarks/README.md', 'benchmark配置目录') if name == 'data/README.md' else ''
        managed(p, '## 太阳8B V/B−L benchmark（2026-11-08）\n\n' + link(p, central, '新onboarding、共享矢量模型、事例数图和完整来源') + navigation + '。显式项目测试点，标准Runtime计算；不更改原SM包或旧版结果。')
    for name, content in {
        'cevns_pyeft/theory/README.md': '[light_vector.py](light_vector.py)在既有StandardModelKN核上加入味普适轻矢量V/B−L弱荷与干涉，采用JCAP05(2025)012式(2.6),(2.10)。不接受一般LEFT系数；测试点与物理适用性见主报告。',
        'cevns_pyeft/experiments/README.md': '[solar_vector.py](solar_vector.py)用已有interaction组件替换接口加载太阳8B的V/B−L固定点；保留原正式SM输入包、源、靶与Response。`load_solar_light_vector`或`with_solar_light_vector`返回标准PreparedExperiment。',
        'tools/README.md': '[run_solar_b8_vector_benchmark.py](run_solar_b8_vector_benchmark.py)读取显式卡、执行标准Slow、收敛、带符号分解与出图；--resume仅复用相同参数/物理指纹。[finalize_solar_b8_vector_benchmark.py](finalize_solar_b8_vector_benchmark.py)维护同源v2.3/阶段/导航，--validate-only只核验并写本轮QA。[validate_solar_b8_vector_rendering.mjs](validate_solar_b8_vector_rendering.mjs)检查公式、链接、实际目录点击与420px排版。',
        'tests/README.md': '[test_solar_b8_vector_contract.py](test_solar_b8_vector_contract.py)验证g=0、g⁴纯NP标度、重质量退耦、干涉符号与抵消、弱荷零点、味普适性、运动学端点和组件物理指纹。',
        'docs/references/Solar_CEvNS/README.md': '[期刊原件](JCAP_2025_05_012_published.pdf)：DE ROMERI V, PAPOULIAS D K, TERNES C A. JCAP, 2025, 05:012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012)。PDF p5/印刷p4式(2.6),(2.10)用于核实C_V=3Ag²；与既有arXiv v1的C_V²记号差异单独记录。下载来源和SHA见矢量卡R19。',
        'data/benchmarks/README.md': '[solar_b8_vector_v1/](solar_b8_vector_v1/README.md)保存V/B−L显式项目测试点及固定正式输入包哈希。它是benchmark配置，不是新测量数组或实验注册。',
        'outputs/solar_b8_vector/README.md': '[20261108_run1/](20261108_run1/README.md)保存SM与六个非零V/B−L点的标准Runtime结果、来源、干涉分解、图和验收。',
        'outputs/README.md': '[solar_b8_vector/](solar_b8_vector/README.md)保存太阳8B的轻媒介子事例数benchmark；明确区分XENONnT重建谱与PandaX真实反冲投影。'
    }.items(): managed(ROOT / name, '## Solar B8 vector benchmark\n\n' + content)
    p = OUT / 'README.md'; managed(p, '## 主线交付与核验\n\n' + ' · '.join([link(p, central, '新onboarding入口'),
        link(p, OUT / 'VALIDATION.json', '实际验收'), link(p, OUT / 'READABILITY_VALIDATION.json', '渲染/跳转'),
        link(p, OUT / 'TEST_RESULTS.json', '27项测试'), link(p, OUT / 'CHANGE_MANIFEST.json', '文件与README归属')]))
    dump(OUT / 'PUBLISHED_DOCUMENTS.json', {'changes': CHANGED, 'central_report': rel(central),
        'phase_reports': [rel(p) for row in datasets for p, _ in row['phases'].values()]})


def validate(config):
    from tools.validate_docs import audit, link_targets
    from urllib.parse import unquote
    records = read(OUT / 'PUBLISHED_DOCUMENTS.json'); errors = []; phases = []; packages = []
    summary = read(OUT / 'BENCHMARK_SUMMARY.json')
    card = ROOT / 'data/benchmarks/solar_b8_vector_v1/benchmark.input.json'
    assert read(card) == config
    assert sha(card) == summary['config_sha256']
    assert sha(ROOT / 'tools/run_solar_b8_vector_benchmark.py') == summary['runner_sha256']
    assert sha(ROOT / config['formula_source']['file']) == config['formula_source']['sha256']
    for row in read(OUT / 'PRESERVATION_BASELINE.json'):
        assert sha(ROOT / row['file']) == row['sha256'], row['file']
    old = ROOT.parent / '重构/20261106_Onboarding_provenance_revision'
    preserved_old = read(old / 'PRESERVED_VERSIONS.json')
    assert all(sha(Path(p)) == digest for p, digest in preserved_old.items())
    assert all(sha(ROOT / row['file']) == row['sha256'] for row in read(old / 'DATA_FILES.json'))
    spec = importlib.util.spec_from_file_location('phaseqa', ROOT / 'workflows/cevns-pyeft/qa/validate_phase_contract.py')
    qa = importlib.util.module_from_spec(spec); spec.loader.exec_module(qa)
    for name in records['phase_reports']:
        p = ROOT / name; e = qa.validate_record(qa.read_record(p), artifact_root=ROOT)
        phases.append({'file': name, 'errors': e}); errors.extend(e)
    for row in config['packages']:
        package = ROOT / row['path']; base = load_experiment_package(package); output = OUT / row['dataset_id']
        v = validate_package(package); packages.append({'dataset': row['dataset_id'], 'status': v['status']}); errors.extend(v['errors'])
        result = read(output / 'DATASET_RESULT.json'); fingerprints = []
        for point in config['points']:
            stored = result['results'][point['id']]
            assert read(output / point['id'] / 'RESULT.json') == stored
            exp = base if point['id'] == 'SM' else with_solar_light_vector(base, mass_MeV=point['mass_MeV'], coupling=point['coupling'], scenario=point['scenario'])
            assert exp.physics_fingerprint == stored['physics_fingerprint']
            assert stored['convergence']['passed']; fingerprints.append(exp.physics_fingerprint)
            with np.load(output / point['id'] / 'prediction.npz', allow_pickle=False) as arrays:
                np.testing.assert_array_equal(arrays['counts'], stored['counts'])
            if point['id'] != 'SM':
                split = read(output / point['id'] / 'INTERFERENCE.json'); assert split['passed']
                np.testing.assert_allclose(split['reconstructed_total'], stored['counts'], rtol=5e-12, atol=1e-12)
                signed = np.asarray(split['interference'])
                assert np.all(signed < 0) if point['scenario'] == 'universal' else np.all(signed > 0)
        assert len(set(fingerprints)) == len(config['points'])
        run = ROOT / 'workflows/cevns-pyeft/runs' / row['family'] / row['dataset_id']
        sources = {s['source_id']: s for s in read(run / 'P00_SOURCE_REGISTER.yaml')['sources']}
        assert sources['R19']['sha256'] == config['formula_source']['sha256']
        ledger = read(run / 'P01_EVIDENCE_LEDGER.yaml')
        claims = {c['claim_id']: c for c in ledger['claims']}
        assert len(claims) == len(ledger['claims'])
        for claim in ledger['claims']:
            if claim['claim_id'].startswith('VECTOR20261108-'):
                assert set(claim.get('input_claims', [])) <= set(claims)
                assert claim.get('source_id') is None or claim['source_id'] in sources
                if isinstance(claim.get('value'), dict) and 'file' in claim['value']:
                    assert (ROOT / claim['value']['file']).is_file()
        assert claims['VECTOR20261108-POINTS']['value']['sha256'] == sha(card)
        for record, schema in [('P01_EVIDENCE_LEDGER.yaml', 'evidence-ledger.schema.yaml'), ('P03_PHYSICS_CONTRACT.yaml', 'physics-contract.schema.yaml')]:
            errors.extend(e.message for e in Draft202012Validator(read(ROOT / 'workflows/_shared/schemas' / schema)).iter_errors(read(run / record)))
    selected = sorted({c['file'] for c in records['changes'] if c['file'].endswith('.md')})
    current = [p for p in selected if not p.startswith('outputs/')]
    docs = audit(ROOT, files=current); errors.extend(docs['broken_current_links'])
    # Only explicit current output reports/nav are checked; do not relax the
    # global output/backup quarantine or discover scientific inputs there.
    output_docs = {p for p in selected if p.startswith('outputs/')}
    output_docs.update(rel(p) for p in OUT.rglob('*.md') if 'preview' not in p.parts)
    output_docs.add(rel(OUT / 'REPORT.md'))
    extra = []
    for name in sorted(output_docs):
        source = ROOT / name
        for line, raw in link_targets(source.read_text(encoding='utf8')):
            value = raw.strip().strip('<>')
            if re.match(r'^(https?:|mailto:|data:|#)', value): continue
            target = (source.parent / unquote(value.split('#', 1)[0])).resolve()
            record = {'file': name, 'line': line, 'target': raw, 'exists': target.exists()}; extra.append(record)
            if not target.exists(): errors.append(record)
    docs['explicit_task_output_links'] = extra
    selected = sorted(set(current) | output_docs)
    dump(OUT / 'DOC_LINKS.json', docs); dump(OUT / 'DOC_SELECTION.json', selected)
    tests = read(OUT / 'TEST_RESULTS.json'); assert tests['passed'] == 27 and tests['failures'] == tests['errors'] == 0
    report = {'date': config['date'], 'packages': packages, 'phase_reports': phases, 'points_per_dataset': len(config['points']),
        'preserved_current_physics_files': len(read(OUT / 'PRESERVATION_BASELINE.json')),
        'older_reports_preserved': len(preserved_old), 'original_numeric_files_preserved': 45,
        'documents': len(selected), 'current_source_links': docs['local_links'], 'explicit_task_output_links': len(extra),
        'tests': tests, 'errors': errors, 'scientific_delivery': 'DRAFT/PARTIAL; vector spectra, no Fig4 contours; PandaX Ne still missing',
        'verification_limit': 'Numerical/analytic/runtime contracts; not a certified external nonzero-signal template or official likelihood reproduction.'}
    dump(OUT / 'VALIDATION.json', report)
    print(json.dumps({k: report[k] for k in ['packages', 'points_per_dataset', 'preserved_current_physics_files', 'documents', 'errors']}, ensure_ascii=False))
    return bool(errors)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs/solar_b8_vector/20261108_run1')
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args(); OUT = args.output.resolve()
    config = read(OUT / 'BENCHMARK_CONFIG.json')
    if args.validate_only:
        raise SystemExit(validate(config))
    publish(config)
    print('Published vector evidence, eight phase reports, v2.3 onboarding and managed navigation.')
