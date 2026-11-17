"""Audit/register the calculated NSI branch and synchronize its documentation.

Default/--check is read-only. --write updates only the authorized NSI delivery,
parallel canonical records and explicitly marked README blocks. It never reruns
or rewrites physical results, old observations, kernels or scientific acceptance.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import numpy as np
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cevns_pyeft.experiments.solar_nsi import load_solar_nsi
from cevns_pyeft.experiments.runtime import validate_snapshot
from cevns_pyeft.kernels.solar_nsi import SolarNSIKernel
from cevns_pyeft.statistics.solar_nsi import SolarNSIJoint
from tools.build_solar_b8_nsi_onboarding import generated, FILE, DOC, DATA, BASE, OUT

SAMPLES = ('PandaX_paired', 'PandaX_US2', 'XENONnT')
BRANCH = 'solar_ee_vector_nsi'
RUNS = [('PandaX4T', 'PandaX4T_2024_US2', 13), ('XENONnT', 'XENONnT_2024_SolarB8', 12)]
MARKER = 'solar-nsi-v33'
CODE = ['cevns_pyeft/sources/solar_msw.py', 'cevns_pyeft/theory/li2026/ee_vector_nsi.py',
        'cevns_pyeft/experiments/solar_nsi.py', 'cevns_pyeft/kernels/solar_nsi.py',
        'cevns_pyeft/statistics/solar_nsi.py', 'tools/prepare_solar_b8_nsi.py',
        'tools/run_solar_b8_nsi_benchmark.py', 'tools/build_solar_b8_nsi_onboarding.py',
        'tools/finalize_solar_b8_nsi.py', 'tools/validate_solar_b8_nsi.mjs', 'tests/test_solar_nsi.py']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf8'))


def rel(p):
    return p.relative_to(ROOT).as_posix()


def put(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf8')


def link(origin, target, label):
    return '[' + label + '](<' + os.path.relpath(target, origin.parent).replace('\\', '/') + '>)'


def progress(text):
    return json.loads(re.search(r'```json\s*\n(.*?)\n```', text, re.S)[1])


def managed(path, body):
    old = path.read_text(encoding='utf8') if path.exists() else ''
    block = f'<!-- {MARKER}:start -->\n\n{body}\n\n<!-- {MARKER}:end -->'
    pattern = r'<!-- ' + MARKER + r':start -->.*?<!-- ' + MARKER + r':end -->'
    new = re.sub(pattern, lambda _: block, old, flags=re.S) if re.search(pattern, old, re.S) else old.rstrip() + '\n\n' + block + '\n'
    put(path, new)


def audit():
    result = read(OUT / 'NSI_RESULTS.json')
    baseline = read(OUT / 'PROTECTED_BASELINE.json')
    changed = [p for p, h in baseline.items() if sha(ROOT / p) != h]
    if changed:
        raise ValueError('Protected originals changed: ' + str(changed))
    cards = [DATA / 'nsi.input.json', BASE / 'analysis.input.json']
    input_checks = []
    for card_path in cards:
        card = read(card_path)
        for name, entry in card['files'].items():
            p = card_path.parent / name
            if sha(p) != entry['sha256']:
                raise ValueError('Changed numerical input: ' + str(p))
            if 'shape' in entry and list(np.loadtxt(p).shape) != entry['shape']:
                raise ValueError('Numerical input shape differs: ' + name)
            input_checks.append({'path': rel(p), 'sha256': sha(p), 'scope': 'local numerical identity/shape, not primary source authentication'})
        for ref in card['references'].values():
            p = ref.get('file', ref.get('direct_local_source'))
            if p and ref.get('sha256') and sha(ROOT / p) != ref['sha256']:
                raise ValueError('Changed source material: ' + p)
    c = read(cards[0])
    if sha(cards[1]) != c['base_card_sha256'] or sha(cards[0]) != result['inputs']['sha256']:
        raise ValueError('Execution card digest differs')
    for name, entry in c['files'].items():
        p, s = DATA / entry['production_raw'], DATA / entry['structure_raw']
        if sha(p) != entry['production_sha256'] or sha(s) != entry['structure_sha256']:
            raise ValueError('Changed direct upstream solar input')
        a, b = np.loadtxt(p), np.loadtxt(s)
        ind = np.searchsorted(b[:, 0], a[:, 0])
        if not np.array_equal(a[:, 0], b[ind, 0]):
            raise ValueError('Radial identity lost')
        derived = np.column_stack([a[:, 0], 10**a[:, 2], b[ind, 1] - 10**a[:, 2], a[:, 8]])
        if not np.allclose(derived, np.loadtxt(DATA / name), rtol=6e-14, atol=0):
            raise ValueError('Profile derivation differs')
    fingerprints = read(OUT / 'SOURCE_FINGERPRINTS.json')
    for module, h in fingerprints.items():
        p = Path(*module.split('.')).with_suffix('.py')
        if sha(ROOT / p) != h or sha(OUT / 'source' / p) != h:
            raise ValueError('Prediction implementation changed: ' + module)
    if sha(ROOT / 'tools/run_solar_b8_nsi_benchmark.py') != result['runner_sha256']:
        raise ValueError('Actual runner changed since execution')
    tests = list(ET.parse(OUT / 'scoped_tests.xml').getroot().iter('testcase'))
    if len(tests) != 42 or any(t.find('failure') is not None or t.find('error') is not None or t.find('skipped') is not None for t in tests):
        raise ValueError('Expected 42 actual passing scoped tests')
    experiments, kernels, models = [], [], {}
    shared = None
    for sample in SAMPLES:
        e = load_solar_nsi(sample, root=ROOT, interaction=shared)
        shared = e.model.interaction
        validate_snapshot(e)
        saved = read(OUT / sample / 'PREPARED_MODEL.json')
        if saved['physics_fingerprint'] != e.physics_fingerprint or saved['analysis_fingerprint'] != e.analysis_fingerprint:
            raise ValueError('Prepared model changed: ' + sample)
        k = SolarNSIKernel.load(OUT / 'kernels' / (sample + '.npz'))
        if k.record['physics_fingerprint'] != e.physics_fingerprint:
            raise ValueError('Kernel model identity differs')
        experiments.append(e)
        kernels.append(k)
        models[sample] = {'physics_fingerprint': e.physics_fingerprint, 'analysis_fingerprint': e.analysis_fingerprint,
                          'kernel_sha256': sha(OUT / 'kernels' / (sample + '.npz')), 'K_shape': list(k.values.shape)}
    joint = SolarNSIJoint(tuple(experiments), tuple(kernels))
    if not np.allclose(joint.signals(0., 0.), result['SM']['signal_events'], rtol=1e-13, atol=1e-13):
        raise ValueError('Saved SM projection changed')
    if abs(float(joint.chi2(0., 0.)) - result['SM']['chi2']) > 1e-12:
        raise ValueError('Saved SM objective changed')
    best = result['primary_minimum']['minimum']
    with np.load(OUT / 'solar_NSI_surfaces.npz', allow_pickle=False) as surfaces:
        for iy, ix in [(0, 0), (35, 440), (300, 300), (407, 300), (600, 600)]:
            u, d = surfaces['epsilon_ee_uV'][ix], surfaces['epsilon_ee_dV'][iy]
            expected = float(joint.chi2(u, d)) - best['chi2']
            if abs(float(surfaces['delta_chi2_flat_sensitivity'][iy, ix]) - expected) > 1e-10:
                raise ValueError('Saved parameter surface does not match current model')
    forward = read(OUT / 'FORWARD_VALIDATION.json')
    if len(forward) != 3 or not all(x['passed'] for s in forward for x in s['independent_grids']):
        raise ValueError('Forward convergence failed')
    return {'date': '2026-11-12', 'status': result['status'], 'scientific_acceptance': 'NOT_REVIEWED',
            'protected_files': len(baseline), 'protected_changed': changed,
            'numerical_inputs': input_checks, 'models': models, 'prediction_source_modules': len(fingerprints),
            'tests_passed': len(tests), 'tests_by_module': {n: sum(t.attrib.get('classname') == n for t in tests) for n in sorted({t.attrib.get('classname') for t in tests})},
            'forward_convergence': 'PASS', 'Slow_Fast_points': sum(len(s['direct_slow_checks']) for s in forward),
            'saved_surface_spot_checks': 5, 'profile_derivation_and_card_hashes': 'PASS',
            'full_COHERENT_dataset_regression': {'status': 'NOT_RUN_COLLECTION_OS_PERMISSION_ERROR',
                'files': ['data/experiments/COHERENT_CsI/CsI2017/experiment.input.yaml', 'data/experiments/COHERENT_CsI/CsI2021/experiment.input.yaml'],
                'attempts': 'default and require_escalated both hit OS PermissionError; not an automatic approval rejection',
                'evidence': 'outputs/solar_b8_nsi/20261112_fig4_run1/regression_collection_os_denied.xml',
                'protection': 'no permissions, reference arrays or legacy data modified'},
            'paper_equivalence': 'NOT_ESTABLISHED; numerical counterexample and controls retained',
            'scope': 'technical/local-source audit; no authentication of original 47-column structure table or nuclear author release'}


def phase_report(run, phase, qa):
    ref = rel(run / 'SOLAR_NSI_BRANCH.json')
    path = run / 'phases' / (phase + '_solar_nsi2601.md')
    blocked = phase in ('P08', 'P10')
    handoff = {
        'P04': {'theory_scope': 'real ee-only uV/dV SM+NSI', 'coefficient_convention': '2601 p22 Eq95 C61q=-sqrt2 Gf epsilon; pp/pn/nn nuclear basis',
                'nuclear_responses': 'seven actual local Xe tables in responses_all.json; shared Li2026 adapter',
                'coverage': 'number fraction .998158, no renormalization; Xe124/126 absent', 'runtime_binding': 'ElectronVectorNSI plus nsi_point; reject all other NSI',
                'external_evidence_limits': ['local reuse authorized; external author nuclear release not certified']},
        'P05': {'process_and_mass': 'solar neutrino elastic scattering, mA=A*amu shared convention', 'kinematics': 'shared ElasticKinematics, E MeV/T keVnr',
                'cross_section_api': 'ElectronVectorNSI delegates coefficient_dsigma / coefficient_values to existing Li2026LegacyInteraction',
                'units_and_axes': 'cm2/keV; energy dimension; six epsilon monomials', 'support_and_limits': 'exact shared recoil support; no second KN/spin multiplier',
                'benchmark': 'original shared API vs new vectorization in tests/test_solar_nsi.py'},
        'P06': {'representation': 'bin_probability', 'unit': '1', 'normalization': 'sum_at_most_one',
                'included_selections': ['experiment Total ROI acceptance, once'], 'axes': 'T keVnr -> one selected bin',
                'response_definition': 'reuse independent singlebin Total tables; X flat/zero/unit/profile controls explicit',
                'selection_ownership': 'Total curve owns ROI; no Qy recut/ci', 'validity_domain': 'PandaX 1.1/.3-3, X .5-3 with unknown2.77-3 tail conditional assumption'},
        'P07': {'normalization_ledger': 'fixed flux5.46e6, one year seconds, nuclei/tonne, exposure, Total once',
                'output_contract': 'three separately identified arrays shape(1), events/bin', 'numerics_and_convergence': rel(OUT / 'FORWARD_VALIDATION.json'),
                'reference_comparison': 'SM frozen branch retained; paper graphic strictly validation-only', 'freeze_scope': 'actual NSI card, source snapshot, fingerprints and arrays'},
        'P08': {'representation': 'eft_quadratic_coefficient_kernel', 'backend': 'energy_resolved_ee_vector_nsi_v1', 'basis_scope': 'declared_subspace',
                'parameter_domain': 'real ee-uV/dV; algebraic energy kernel, changing Pee applied at every point; two-flavor approximation limits retained',
                'state_treatment': 'parameter_dependent', 'slow_reference': {'report_ref': rel(run / 'phases/P07_solar_nsi2601.md'),
                    'sha256': sha(OUT / 'FORWARD_VALIDATION.json'), 'approval_ref': None},
                'cache_dependencies': 'physics fingerprint, all fold input digests, numerics, angle, array digest; no fixed-rho generic kernel',
                'validation_summary': 'technical PASS:9 actual Slow/Fast points; canonical P08 approval prerequisite not claimed: Slow human acceptance still NOT_REVIEWED'},
        'P09': {'channels': [{'id': s, 'representation': 'binned_counts', 'processing': 'other', 'design': 'single_sample',
                             'likelihood': 'gaussian', 'requires_covariance': False} for s in SAMPLES],
                'prediction_binding': 'same three NSI model/kernel/analysis identities, all flavors retained',
                'required_inputs': {'available': True, 'sources': [rel(DATA / 'fitted_yields.json'), rel(DATA / 'nsi.input.json')], 'missing': []},
                'nuisance_model': 'three independent12% Gaussian pulls; exact printed percentages; flat-tail conditional primary, alternatives separate',
                'inference': 'each scheme subtracts its own joint global-parameter minimum; Delta<=4.61;601x601; finite enclosing-domain proof,3DE seeds and independent multistart',
                'claim_level': 'approximate', 'benchmark': rel(OUT / 'PAPER_COMPARISON.json')},
        'P10': {'delivery_scope': {'mode': 'capability_change', 'target': 'computed physical solar ee-vector NSI plus exact paper green comparison', 'completion': 'partial'},
                'capability_matrix': [
                    {'id': 'conditional_NSI_forward_and_joint_region', 'requested': True, 'required_for_claim': True, 'machine_gate': 'PASS', 'human_gate': 'NOT_REVIEWED', 'result_ref': rel(OUT / 'NSI_RESULTS.json')},
                    {'id': 'exact_paper_Fig4_green_reproduction', 'requested': True, 'required_for_claim': True, 'machine_gate': 'BLOCKED', 'human_gate': 'NOT_REVIEWED', 'result_ref': rel(OUT / 'PAPER_COMPARISON.json')}],
                'validation_levels': {'technical': rel(OUT / 'QA.json'), 'paper_match': 'not established;counterexample Delta3.331 at(0,.178)', 'full_legacy_dataset_regression': 'collection OS PermissionError recorded'},
                'runtime_integration': 'scoped PreparedExperiment -> compile/predict/evaluate; all old global IDs and physical files retained',
                'final_claim': qa['status'], 'limitations': read(OUT / 'NSI_RESULTS.json')['limits']},
    }[phase]
    report = {'schema_version': 1, 'phase': phase, 'capability_id': 'solar_b8.ee_vector_nsi2601.' + phase,
              'workspace': 'canonical', 'plan_status': 'DRAFT' if blocked else 'READY', 'machine_gate': 'BLOCKED' if blocked else 'PASS',
              'human_gate': 'NOT_REVIEWED', 'scope_ref': ref, 'input_refs': [rel(DATA / 'nsi.input.json'), rel(DATA / 'fitted_yields.json')],
              'input_fingerprint': sha(DATA / 'nsi.input.json'), 'evidence_refs': [rel(DATA / 'nsi.input.json'), rel(OUT / 'QA.json')],
              'decision_refs': ['D0006'], 'approval_refs': ['W0006'],
              'artifacts': [{'path': rel(OUT / 'NSI_RESULTS.json'), 'sha256': sha(OUT / 'NSI_RESULTS.json'), 'role': 'actual three-sample NSI calculation; assumptions and paper discrepancy explicit'}],
              'checks': [{'name': 'actual numerical forward and inference checks', 'status': 'PASS', 'command': 'python -B tools/finalize_solar_b8_nsi.py --check', 'result_ref': rel(OUT / 'QA.json')}],
              'handoff': handoff}
    if phase == 'P08':
        report['handoff']['slow_reference']['sha256'] = sha(run / 'phases/P07_solar_nsi2601.md')
    jsonschema.validate(report, read(ROOT / 'workflows/_shared/schemas/phase-result.schema.yaml'))
    put(path, f'# {phase}：太阳电子味矢量NSI独立单bin分支\n\n' + link(path, FILE, 'v3.3同源onboarding/来源/代码/实际结果') +
        '\n\n技术计算已执行；执行授权不等于科学结果接受。P08尚无Slow结果人工接受；P10精确图形复现未成立，分别保持正式门槛未通过。旧分支不变。\n\n```json phase-result\n' +
        json.dumps(report, ensure_ascii=False, indent=2) + '\n```\n')
    return rel(path)


def register(qa):
    registered = {}
    for family, dataset, expected in RUNS:
        run = ROOT / f'workflows/cevns-pyeft/runs/{family}/{dataset}'
        pp = run / '00_MIGRATION_PROGRESS.md'
        old_text = pp.read_text(encoding='utf8')
        p = progress(old_text)
        if BRANCH not in p.get('parallel_analyses', {}) and p['revision'] != expected:
            raise ValueError('Concurrent canonical revision changed; reload before writing')
        authorization = read(run / 'AUTHORIZATION_LOG.yaml')
        if not any(x.get('authorization_id') == 'W0006' for x in authorization['entries']):
            authorization['entries'].append({'authorization_id': 'W0006', 'status': 'ACTIVE', 'date': '2026-11-12', 'approval_kind': 'explicit_user_instruction',
                'user_quote': '请你在主线中完成下面内容', 'scope': 'complete solar flavor-dependent NSI forward, joint Fig4 comparison, tail sensitivity, data/source/onboarding and parallel mainline records',
                'allowed_actions': ['read', 'create', 'modify'], 'create_paths': CODE + [rel(DATA), rel(OUT.parent), rel(FILE), rel(run / 'SOLAR_NSI_BRANCH.json'), rel(run / 'phases/Pxx_solar_nsi2601.md')],
                'modify_paths': ['explicit README/navigation owners', rel(run), 'tools/promote_solar_b8_singlebin.py', 'tools/validate_solar_b8_singlebin.py', 'tools/build_solar_b8_singlebin_onboarding.py'],
                'delete_paths': [], 'production_paths_affected': True, 'recovery_plan': 'backup/solar-nsi-20261112-01/MANIFEST.json', 'result_acceptance_separate': True})
            put(run / 'AUTHORIZATION_LOG.yaml', authorization)
        decisions = read(run / 'P04_DECISION_LOG.yaml')
        if not any(x.get('decision_id') == 'D0006' for x in decisions['entries']):
            decisions['entries'].append({'decision_id': 'D0006', 'date': '2026-11-12', 'user_quote': '请你在主线中完成下面内容',
                'scope': 'solar real epsilon_ee_uV/dV, propagation+scattering and three-sample singlebin region per2601',
                'interpretation': 'execute requested continuation with explicitly sourced two-flavor approximation, conditional X tail and separate controls; compute then compare, no tuning to paper reference',
                'execution_authorized': True, 'result_acceptance': 'NOT_REVIEWED',
                'project_choices_not_claimed_as_author_card': ['PEANUTS example oscillation values', 'B16 pinned distribution/derived neutron density', 'flat-tail primary plus bounds', 'existing local nuclear table'],
                'scope_limits': ['retain SM/multibin/light-vector branches', 'no fitted flux/ci', 'all-flavor NSI diagnostic not adopted', 'no scientific acceptance or exact-paper claim']})
            put(run / 'P04_DECISION_LOG.yaml', decisions)
        branch = {'analysis_id': BRANCH, 'version': '3.3', 'date': '2026-11-12', 'status': qa['status'], 'decision_ref': 'D0006', 'write_ref': 'W0006',
                  'samples': list(SAMPLES), 'input_card': rel(DATA / 'nsi.input.json'), 'input_card_sha256': sha(DATA / 'nsi.input.json'),
                  'statistics_input': rel(DATA / 'fitted_yields.json'), 'onboarding': rel(FILE), 'calculation_entry': 'tools/run_solar_b8_nsi_benchmark.py',
                  'result': rel(OUT / 'NSI_RESULTS.json'), 'comparison': rel(OUT / 'PAPER_COMPARISON.json'), 'qa': rel(OUT / 'QA.json'),
                  'model_fingerprints': qa['models'], 'actual_source_snapshot': rel(OUT / 'source'),
                  'analysis_source_fingerprints': rel(OUT / 'ANALYSIS_SOURCE_FINGERPRINTS.json'), 'scientific_result_acceptance': 'NOT_REVIEWED',
                  'exact_paper_reproduction': 'NOT_ESTABLISHED', 'limitations': read(OUT / 'NSI_RESULTS.json')['limits']}
        put(run / 'SOLAR_NSI_BRANCH.json', branch)
        phases = {}
        path = run / 'phases/P03_solar_nsi2601.md'
        put(path, '# P03：太阳电子味NSI源态\n\n' + link(path, FILE, '本版Source数值、公式、直接材料和程序') +
            '\n\n采用2409.04703v2 p10 B4–B9两味绝热产生区平均；显式PEANUTS角度/B16分发和派生nn。真实Pee每参数点重算；μτ等分仅在此散射子空间等价。技术测试与径向加密已完成，科学接受NOT_REVIEWED。P03不伪装成仅支持P04–P10的phase-result结构。\n')
        phases['P03'] = rel(path)
        for phase in ['P04', 'P05', 'P06', 'P07', 'P08', 'P09', 'P10']:
            phases[phase] = phase_report(run, phase, qa)
        branch['phase_reports'] = phases
        put(run / 'SOLAR_NSI_BRANCH.json', branch)
        implementation = read(run / '00_IMPLEMENTATION_MANIFEST.yaml')
        implementation.setdefault('extensions', {})[BRANCH] = branch
        put(run / '00_IMPLEMENTATION_MANIFEST.yaml', implementation)
        if BRANCH not in p.get('parallel_analyses', {}):
            p['previous_revision'] = p['revision']
            p['revision'] += 1
        p.setdefault('parallel_analyses', {})[BRANCH] = branch
        p['updated_at'] = '2026-11-12'
        p['current_analysis'] = BRANCH
        p['checkpoint'] = {'phase_id': 'P10', 'phase_name': 'computed solar NSI / paper discrepancy review', 'skill': 'cevns-experiment',
                           'step_id': 'parallel_analyses.solar_ee_vector_nsi.result_review', 'next_action': 'review actual region and sourced approximations; investigate paper central-gap difference', 'resume_requires': []}
        p['authorization_refs'].update(solar_nsi_scope='D0006', solar_nsi_write='W0006')
        p['artifact_refs'].update(solar_nsi_branch=rel(run / 'SOLAR_NSI_BRANCH.json'), solar_nsi_onboarding=rel(FILE))
        for phase, ref in phases.items():
            p['gates'][phase + '_solar_nsi'] = {'machine': 'BLOCKED' if phase in ('P08', 'P10') else 'PASS', 'human': 'NOT_REVIEWED',
                                             'report_ref': ref, 'capability': 'solar_b8.ee_vector_nsi2601.' + phase, 'decision_refs': ['D0006']}
        if progress(pp.read_text(encoding='utf8'))['revision'] != progress(old_text)['revision']:
            raise ValueError('Concurrent progress update; authoritative records exist, index not overwritten')
        put(pp, '# 主线进度：' + dataset + '\n\n太阳NSI、单bin SM与旧多bin并列；本版已计算区域，论文精确图形复现未成立，科学接受NOT_REVIEWED。\n\n```json\n' + json.dumps(p, ensure_ascii=False, indent=2) + '\n```\n')
        managed(run / 'README.md', '## 太阳电子味矢量NSI：v3.3\n\n' + link(run / 'README.md', run / 'SOLAR_NSI_BRANCH.json', '独立分支/全部阶段/来源与指纹') + ' · ' +
                link(run / 'README.md', FILE, '新版onboarding') + ' · ' + link(run / 'README.md', OUT / 'README.md', '实际联合区域与差异') + '。技术已计算；不以结果执行授权代替科学接受。旧分支及其gates保留。')
        phases_readme = run / 'phases/README.md'
        # New reports share the existing run owner; do not replace manual history.
        if phases_readme.exists():
            managed(phases_readme, '## v3.3太阳NSI阶段\n\n' + ' · '.join(link(phases_readme, ROOT / ref, phase) for phase, ref in phases.items()))
        registered[family] = {'revision': p['revision'], 'phase_reports': phases}
    return registered


def navigation():
    owners = {
        'README.md': '新增太阳⁸B电子味矢量NSI，已完成传播+散射及三样本单bin联合区域；论文Fig.4绿色中间禁区仍不一致。',
        'cevns_pyeft/sources/README.md': 'solar_msw.py负责B16产生区平均Pee及对角入射态；明确两味绝热、θ13,m近似与来源。',
        'cevns_pyeft/theory/README.md': 'li2026/ee_vector_nsi.py负责Eq95实数ee-uV/dV，委托原Li2026核Response振幅，保留其他味SM散射。',
        'cevns_pyeft/kernels/README.md': 'solar_nsi.py保留中微子能量轴；逐参数点重算Pee，不复用固定态通用kernel。',
        'cevns_pyeft/statistics/README.md': 'solar_nsi.py负责三样本独立pull、联合参数最小值与二维Δχ²面，保持旧统计分支。',
        'cevns_pyeft/experiments/README.md': 'solar_nsi.py独立scoped loader/Slow/Fast调用，复用只读单bin表；不改全局默认实验。',
        'data/README.md': '新增solar_b8_nsi_2601_19883来源卡、太阳径向输入和精确百分比误差；旧SM/多bin数据保留。',
        'data/benchmarks/README.md': 'solar_b8_nsi_2601_19883是ee-only接触NSI输入，与太阳SM、轻媒介子和多bin资料分开。',
        'tools/README.md': 'prepare/run/build/finalize/validate_solar_b8_nsi负责来源准备、实际计算、同源onboarding、主线登记和渲染验收；旧单bin工具允许较新并列分支。',
        'tests/README.md': 'test_solar_nsi.py核验原生径向/本征向量传播、共享截面API、状态参数绑定、Slow/Fast/统计与缓存拒绝。',
        'outputs/README.md': 'solar_b8_nsi/保存本轮真实NSI结果、601×601面、核缓存、前向验证和论文差异；不是旧纸面绿色区域。',
        'docs/experiments/README.md': '太阳NSI新v3.3独立于冻结SM v3.2.1与多binv3.1。',
        'docs/experiments/LATEST_EXPERIMENTS.md': '太阳单bin增加电子味NSI v3.3；旧表中的v3.2.1仍是SM入口。NSI已实际计算，精确论文绿色复现未成立。',
        'docs/experiments/PandaX4T_XENONnT_SolarB8/README.md': '新增单bin NSI v3.3；旧SM及多bin入口保留。',
        'docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md': '本目录旧v3.2.1为SM；新v3.3为ee-uV/dV传播+散射和联合区域，来源/误差/缓存独立。',
        'docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/METHODS.md': '本文件上方描述冻结SM处理。本轮NSI由新v3.3接入：每点Pee、三独立pull、明确尾假设及论文差异；不覆盖SM原结果。',
        'docs/references/Solar_CEvNS/README.md': '太阳NSI同时引用General_CEvNS/2409.04703v2 Appendix B传播与2601.19883v2 Eqs84/87/88/95；实验Total效率仍采用原2024实验文章。',
        'docs/references/General_CEvNS/README.md': '2409.04703v2 p10 B4–B9与2601.19883v2 p19–23用于本次NSI来源和验证；论文Fig4轮廓只作外部参考。',
    }
    mapping = {}
    for name, body in owners.items():
        p = ROOT / name
        managed(p, '## 太阳⁸B NSI：v3.3（2026-11-12）\n\n' + body + '\n\n' + link(p, FILE, '完整新onboarding：实际输入、标准引文、物理与程序') + ' · ' +
                link(p, DATA / 'README.md', '独立NSI数据') + ' · ' + link(p, OUT / 'README.md', '实际结果与核对'))
        mapping[name] = []
    for name in CODE:
        owner = 'tools/README.md' if name.startswith('tools/') else 'tests/README.md' if name.startswith('tests/') else name.rsplit('/', 1)[0] + '/README.md'
        if '/theory/li2026/' in name:
            owner = 'cevns_pyeft/theory/README.md'
        mapping.setdefault(owner, []).append(name)
    mapping[rel(DATA / 'README.md')] = [rel(p) for p in DATA.iterdir() if p.is_file()]
    mapping[rel(DOC / 'README.md')] = [rel(FILE)]
    return mapping


def output_readmes():
    root = OUT.parent
    put(root / 'README.md', '# 太阳⁸B电子味矢量NSI\n\n' + link(root / 'README.md', FILE, '新v3.3 onboarding') + ' · ' +
        link(root / 'README.md', OUT / 'README.md', '正式实际计算：20261112_fig4_run2') + ' · ' +
        link(root / 'README.md', root / '20261112_fig4_run1/README.md', '初次运行/原始来源保留') +
        '\n\n独立于solar_b8_singlebin/的SM和solar_b8_sm/的多bin。真实NSI区域已算；论文精确绿色图形未完全复现。\n')
    for run in [root / '20261112_fig4_run1', OUT]:
        if run != OUT:
            put(run / 'README.md', '# NSI首次运行与来源证据\n\n初次执行因通用状态逐能量验证过慢而中止，部分输出不作为正式结果；' +
                link(run / 'README.md', OUT / 'README.md', '后继完整run2') + '。\n\n' + link(run / 'README.md', run / 'ITERATION_STATUS.json', '中止记录') +
                ' · ' + link(run / 'README.md', run / 'source_evidence/README.md', '固定上游archive/源码/页图') +
                '\n\n早期测试和权限失败XML保留；正式42项通过见run2，不将失败记录删去。\n')
        # Every snapshot/evidence/kernel/sample folder gets a local inventory.
        for directory in sorted((p for p in run.rglob('*') if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
            p = directory / 'README.md'
            files = [f for f in sorted(directory.iterdir()) if f.name != 'README.md']
            body = '# ' + directory.name + '：NSI运行材料\n\n'
            body += ('来源核验边界和上游原archive在run1；本目录表/页图不自动认证外部原件。\n\n' if 'source_evidence' in directory.parts else '保存执行快照/缓存/模型，不是新物理输入或结果批准。\n\n')
            body += '\n'.join('- ' + link(p, f / 'README.md' if f.is_dir() and (f / 'README.md').exists() else f, f.name) for f in files)
            body += '\n\n' + link(p, run / 'README.md', '返回本次运行') + '\n'
            if p.exists():
                managed(p, body)
            else:
                put(p, body)
    p = OUT / 'README.md'
    put(p, '# 太阳电子味NSI实际联合区域：2026-11-12\n\n' + link(p, FILE, '新v3.3完整onboarding') + ' · ' +
        link(p, DATA / 'nsi.input.json', '来源/配置') + ' · ' + link(p, OUT / 'NSI_RESULTS.json', '完整数值') +
        '\n\n**已完成NSI传播+散射和三样本单bin联合扫描；精确论文绿色区域复现未成立。** sin²θW=.23857、flux=5.46e6固定，原子核Response进入共享振幅，无ci。主传播为两味绝热近似；主X尾为显式平坦延伸，其他尾段/传播/太阳profile对照分别保存。\n\n' +
        '![本次真实计算与原文参照](solar_Fig4_computed_vs_paper.png)\n\n绿色为本计算，灰虚线为PDF参考。在(εu,εd)=(0,.178)，本计算Δχ²=3.331允许，论文绿色区域排除。没有用灰线或实验信号重标定预测。SM三信号2.487829836/47.043419726/11.857362687，χ²=1.612757889；近似模型全域χ²min=1.119857910，位于(−17.263001515,15.676753288)。大耦合最小值的物理适用范围受两味近似限制。\n\n' +
        '![尾段和传播对照](solar_NSI_controls.png)\n\n![每点Pee](solar_Pee_NSI.png)\n\n' +
        '| 文件 | 内容 |\n|---|---|\n' + ''.join('| ' + link(p, OUT / n, n) + ' | ' + desc + ' |\n' for n, desc in [
            ('NSI_RESULTS.json', 'SM、最小值、传播/尾段对照、统计核验、科学限制'), ('MINIMUMS.json', '有限包围域证明、DE种子和网格多起点'),
            ('FORWARD_VALIDATION.json', '独立网格加密和9个Slow/Fast点'), ('solar_NSI_surfaces.npz', '601×601参数面和逐样本known/tail信号'),
            ('PAPER_COMPARISON.json', '论文参照独立性、反例、mask交并比'), ('SLICE_BOUNDARIES.json', '各控制方案与论文的截线'),
            ('QA.json', '42项测试、164原件保护、当前资源/源码/缓存/统计审计'), ('scoped_tests.xml', '本轮实际42项通过；早期失败记录另存'),
            ('ANALYSIS_SOURCE_FINGERPRINTS.json', '推断、runner和维护工具的实际快照与哈希'), ('FILE_LIFECYCLE.json', '新文件、所属README与上级导航'),
            ('READABILITY_VALIDATION.json', '实际GFM/KaTeX/Edge目录跳转、图片及窄屏验收'), ('preview/README.md', '可查看的渲染与截图')]) +
        '\n\n完整旧COHERENT dataset回归因两份既有YAML的OS权限错误未能collection；没有计入42项通过。旧SM/多bin/核表及原理论保护哈希不变。科学接受NOT_REVIEWED；未声称FULLY_INTEGRATED或论文等价。\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    qa = audit()
    if args.write:
        snapshots = {}
        for name in CODE:
            source = ROOT / name
            if not source.exists():
                raise ValueError('Missing delivery tool: ' + name)
            destination = OUT / 'source' / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                shutil.copyfile(source, destination)
            if sha(destination) != sha(source):
                raise ValueError('Immutable executed/delivery source snapshot differs: ' + name)
            snapshots[name] = {'sha256': sha(source), 'snapshot': rel(destination),
                               'role': 'executed inference/runner' if name in ['cevns_pyeft/statistics/solar_nsi.py', 'tools/run_solar_b8_nsi_benchmark.py'] else 'prediction/test/delivery implementation'}
        put(OUT / 'ANALYSIS_SOURCE_FINGERPRINTS.json', snapshots)
        put(OUT / 'QA.json', qa)
        for path, text in generated().items():
            put(path, text)
        qa['canonical'] = register(qa)
        mapping = navigation()
        output_readmes()
        for family, dataset, _ in RUNS:
            run = ROOT / f'workflows/cevns-pyeft/runs/{family}/{dataset}'
            mapping[rel(run / 'README.md')] = [rel(run / 'SOLAR_NSI_BRANCH.json')] + list(qa['canonical'][family]['phase_reports'].values())
        for p in [OUT.parent / 'README.md', *OUT.parent.rglob('README.md')]:
            mapping[rel(p)] = [rel(f) for f in p.parent.iterdir() if f.name != 'README.md']
        put(OUT / 'FILE_LIFECYCLE.json', {'date': '2026-11-12', 'file_owners': mapping,
            'backup_manifest': 'backup/solar-nsi-20261112-01/MANIFEST.json', 'scientific_acceptance': 'NOT_REVIEWED',
            'old_numerical_and_physical_files': 'protected by PROTECTED_BASELINE.json, unchanged', 'global_default_activation': False, 'git_operations': False})
        put(OUT / 'QA.json', qa)
    else:
        for path, expected in generated().items():
            if path.read_text(encoding='utf8') != expected:
                raise ValueError('Stale generated document: ' + str(path))
        for family, dataset, _ in RUNS:
            run = ROOT / f'workflows/cevns-pyeft/runs/{family}/{dataset}'
            p = progress((run / '00_MIGRATION_PROGRESS.md').read_text(encoding='utf8'))
            if BRANCH not in p.get('parallel_analyses', {}) or p['current_analysis'] != BRANCH:
                raise ValueError('NSI mainline index missing')
            for path in (run / 'phases').glob('P*_solar_nsi2601.md'):
                match = re.search(r'```json phase-result\n(.*?)\n```', path.read_text(encoding='utf8'), re.S)
                if match:
                    jsonschema.validate(json.loads(match[1]), read(ROOT / 'workflows/_shared/schemas/phase-result.schema.yaml'))
        for name, record in read(OUT / 'ANALYSIS_SOURCE_FINGERPRINTS.json').items():
            if sha(ROOT / name) != record['sha256'] or sha(ROOT / record['snapshot']) != record['sha256']:
                raise ValueError('Changed analysis/delivery source: ' + name)
    print(json.dumps({'protected': qa['protected_files'], 'tests_passed': qa['tests_passed'], 'prediction_modules': qa['prediction_source_modules'],
                      'models': list(qa['models']), 'status': qa['status'], 'mode': 'write' if args.write else 'read_only_check'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
