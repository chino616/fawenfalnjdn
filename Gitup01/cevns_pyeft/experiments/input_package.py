"""Read-only experiment-input contract checks. No model binding or assembly.

Only JSON-compatible YAML 1.2 is accepted. JSON Schema validation is an optional
QA dependency (the same jsonschema engine as workflow QA); no physics module is
imported. Mathematical text and source locators are never executed/imported.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import io
import json
import math
from pathlib import Path
import re
import zipfile

import numpy as np

SCHEMA_VERSION = 'cevns-experiment-input/1'
ROLES = ('direct_input', 'derived', 'materialized_derived_resource', 'reference_only',
         'unused_snapshot', 'runtime_control')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode('utf-8')).hexdigest()


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    def constant(value):
        raise ValueError('non-JSON numeric constant: ' + value)
    data = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    # This also rejects overflow such as 1e400, which json.loads maps to infinity.
    json.dumps(data, allow_nan=False)
    return data


def schema_document():
    return strict_json(Path(__file__).with_name('input_package.schema.json').read_text(encoding='utf-8'))


def dependency_fingerprint(data, parameter_refs, model_refs=(), resource_refs=(), formula_id=None):
    """Canonical dependencies, not an invocation of a physical formula."""
    return fingerprint({
        'formula_id': formula_id,
        'parameter_order': list(parameter_refs),
        'parameters': {p: {'value': data['parameters'][p]['value'], 'unit': data['parameters'][p]['unit']}
                       for p in sorted(parameter_refs)},
        'models': {m: data['models'][m]['model_revision'] for m in sorted(model_refs)},
        'resources': {r: data['resources']['arrays'][r]['sha256_raw_c_order'] for r in sorted(resource_refs)},
    })


def derived_value(formula_id, values):
    """Small closed set of audit derivations; no eval and no runtime dispatch."""
    if formula_id == 'spherical_fluence.v1':
        r, pot, baseline = values
        return r * pot / (4 * math.pi * (100 * baseline) ** 2)
    if formula_id == 'pion_line_energy.v1':
        pion, muon = values
        return 1000 * (pion ** 2 - muon ** 2) / (2 * pion)
    if formula_id == 'muon_dar_endpoint.v1':
        muon, electron = values
        return 1000 * (muon ** 2 - electron ** 2) / (2 * muon)
    if formula_id == 'mass_fraction.v1':
        isotope, *composition = values
        return isotope / sum(composition)
    if formula_id == 'product.v1':
        return math.prod(values)
    if formula_id == 'nucleus_inventory.v1':
        mass, fraction, single_mass = values
        return mass * fraction / single_mass
    if formula_id == 'identity.v1':
        if len(values) != 1:
            raise ValueError('identity requires one input')
        return values[0]
    raise ValueError('unknown audit derivation: ' + formula_id)


def _cycles(graph):
    visiting, done, errors = set(), set(), []
    def visit(node):
        if node in visiting:
            errors.append('dependency cycle: ' + node)
            return
        if node in done:
            return
        visiting.add(node)
        for dependency in graph.get(node, ()):
            if dependency not in graph:
                errors.append('missing dependency: ' + dependency)
            else:
                visit(dependency)
        visiting.remove(node)
        done.add(node)
    for node in graph:
        visit(node)
    return errors


def validate_document(data):
    """Check JSON Schema and semantic cross-references, without reading arrays."""
    if isinstance(data, dict) and data.get('package', {}).get('schema_version') == 'cevns-experiment-input/2':
        from .generic_input import validate
        return validate(data)
    try:
        from jsonschema import Draft202012Validator
    except ImportError as error:
        raise RuntimeError('Schema QA needs jsonschema; install the validation optional dependency') from error
    schema = schema_document()
    structural = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: str(list(e.absolute_path)))
    if structural:
        return ['schema ' + '/'.join(map(str, e.absolute_path)) + ': ' + e.message for e in structural]
    errors = _report_metadata_errors(data)
    def check(condition, message):
        if not condition:
            errors.append(message)
    parameters, models, resources = data['parameters'], data['models'], data['resources']['arrays']
    sources = data['provenance']['sources']
    slots = schema['x-model-contracts']
    inactive = ('reference_only', 'unused_snapshot')
    for section in ('source','target','interaction','detector','prediction','statistics'):
        value=data[section]
        references=value.get('model_refs',[]) + ([value['model_ref']] if 'model_ref' in value else [])
        check(all(mid in models for mid in references), 'section model reference: '+section)
    for field in ('observed_ref','background_ref','uncertainty_ref'):
        check(data['statistics'][field] in resources, 'statistics resource reference: '+field)
    check(data['observable']['edges_ref'] in resources, 'observable resource reference')
    check(data['source']['normalization']['prompt_weight_ref'] in parameters, 'prompt weight parameter reference')
    for component in data['source']['components']:
        for field in ('rho_ref','continuum_ref'):
            check(component[field] is None or component[field] in resources, 'source resource reference: '+component['component_id'])
    check(data['source']['component_order'] == [c['component_id'] for c in data['source']['components']], 'source component order')
    errors += _cycles({key: value['depends_on'] for key, value in models.items()})
    errors += _cycles({key: value['derivation']['input_refs'] if value['role'] == 'derived' else []
                       for key, value in parameters.items()})
    for key, model in models.items():
        check(key == model['model_id'], 'model map identity: ' + key)
        check(all(s in sources for s in model['source_refs']), 'model provenance: ' + key)
        check(set(model['contract']['variable_units']) == set(model['variables']), 'variable/unit coverage: ' + key)
        expected_refs = {pid for pid, p in parameters.items() if any(c['model_id'] == key for c in p['consumers'])}
        check(set(model['parameter_refs']) == expected_refs, 'model parameter consumer mismatch: ' + key)
        check(all(parameters[r]['role'] not in inactive for r in model['parameter_refs'] if r in parameters), 'inactive model input: ' + key)
        check(model['formula_purpose'] == 'audit_only', 'executable formula forbidden: ' + key)
        if model['contract']['binding_status'] in ('BOUND_AND_TESTED', 'BOUND_UNVERIFIED'):
            contracts = strict_json(Path(__file__).with_name('model_bindings.json').read_text(encoding='utf-8'))
            specification = fingerprint({field: model[field] for field in ('mathematical_definition', 'variables', 'depends_on')})
            check(key in contracts and contracts[key]['specification_fingerprint'] == specification,
                  'registered binding specification mismatch: ' + key)
    for key, p in parameters.items():
        check(p['value'] == p['adopted_value'], 'parameter adopted-value mismatch: ' + key)
        check((type(p['value']) is bool) == (p['unit']=='boolean'), 'boolean/numeric parameter type: '+key)
        check(all(s in sources for s in p['source_refs']), 'parameter source reference: ' + key)
        check(p['package_consumption_status'] == 'NOT_RUN', 'unearned package consumption: ' + key)
        if p['role'] in inactive:
            check(not p['consumers'] and not p['affects_fingerprint'] and p['fingerprint_scope'] == 'none', 'inactive parameter marked active: ' + key)
        else:
            check(bool(p['consumers']) and p['affects_fingerprint'], 'active parameter has no consumer: ' + key)
        check(p['role'] != 'materialized_derived_resource', 'scalar cannot be a materialized array: ' + key)
        for consumer in p['consumers']:
            mid, slot = consumer['model_id'], consumer['slot']
            check(mid in models and mid in slots, 'unknown consumer model: ' + key)
            unit = slots.get(mid, {}).get('parameter_units', {}).get(slot)
            check(unit == p['unit'], 'consumer unit/slot mismatch: ' + key + ' -> ' + mid + '.' + slot)
            if slot in ('n_er','n_enu','n_observed_bin','tabulation_nodes'):
                check(type(p['value']) is int and p['value']>=2, 'grid size must be integer >=2: '+key)
            check(all(e['source_ref'] in sources for e in consumer['code_evidence']), 'consumer code evidence: ' + key)
        if p['source_kind'] == 'official_primary':
            check(any(sources[s]['kind'] == 'official_primary' and sources[s]['independently_officially_verified']
                      for s in p['source_refs'] if s in sources), 'false official parameter provenance: ' + key)
        check(not p['human_confirmed'] and p['decision_status'] == 'DRAFT', 'pilot human approval must remain separate: ' + key)
        if p['role'] == 'derived':
            derivation = p['derivation']
            check(not p['editable'] and derivation['read_only'], 'editable derived authority: ' + key)
            try:
                refs = derivation['input_refs']
                expected = derived_value(derivation['formula_id'], [parameters[r]['value'] for r in refs])
                check(math.isclose(float(p['value']), expected, rel_tol=1e-14, abs_tol=0), 'derived value differs from inputs: ' + key)
                check(derivation['dependency_fingerprint'] == dependency_fingerprint(data, refs, formula_id=derivation['formula_id']), 'stale derived dependency: ' + key)
            except (KeyError, ValueError, TypeError, ZeroDivisionError, OverflowError) as error:
                errors.append('invalid derivation ' + key + ': ' + str(error))
        else:
            check(p['derivation'] is None, 'non-derived parameter with derivation: ' + key)
    for key, resource in resources.items():
        check(key == resource['key'], 'resource key identity: ' + key)
        norm = resource['normalization']
        check(not set(norm['included_factors']) & set(norm['runtime_factors']), 'duplicate normalization: ' + key)
        if norm['quantity_kind'] == 'integrated_detector_fluence_density':
            check(set(norm['included_factors']) == {'POT', 'yield', 'geometry'} and not norm['runtime_factors'], 'normalized fluence cannot be normalized twice: ' + key)
            check(resource['unit'] == 'cm^-2 MeV^-1' and resource['role'] == 'materialized_derived_resource', 'fluence resource authority: ' + key)
        check(norm['runtime_authority'] == 'array', 'ambiguous array authority: ' + key)
        check(len(resource['axes']) == len(resource['shape']), 'array axis rank: ' + key)
        check(len({a['name'] for a in resource['axes']}) == len(resource['axes']), 'duplicate axis names: ' + key)
        check(all(s in sources for s in resource['source_refs']), 'resource provenance: ' + key)
        for axis in resource['axes']:
            if 'values' in axis:
                check(len(axis['values']) == resource['shape'][resource['axes'].index(axis)], 'axis labels/shape: ' + key)
            for field in ('coordinate_ref', 'edges_ref'):
                if field in axis:
                    reference = resources.get(axis[field])
                    check(reference is not None, 'missing coordinate: ' + key)
                    if reference:
                        expected_length = resource['shape'][resource['axes'].index(axis)] + (field == 'edges_ref')
                        check(reference['shape'] == [expected_length], 'coordinate/shape mismatch: ' + key)
                        check(reference['unit'] == axis['unit'], 'coordinate unit mismatch: ' + key)
        for consumer in resource['consumers']:
            mid, slot = consumer['model_id'], consumer['slot']
            check(mid in models, 'missing resource consumer: ' + key)
            check(slots.get(mid, {}).get('resource_units', {}).get(slot) == resource['unit'], 'resource consumer unit/slot: ' + key)
        generation = resource['generation']
        if resource['role'] == 'materialized_derived_resource':
            check(generation is not None, 'missing materialized provenance: ' + key)
        if generation:
            try:
                expected = dependency_fingerprint(data, generation['parameter_refs'], generation['model_refs'], generation['resource_refs'])
                check(expected == generation['dependency_fingerprint'], 'stale materialized resource: ' + key)
            except KeyError as error:
                errors.append('missing generation dependency ' + key + ': ' + str(error))
    resource_graph = {k: v['generation']['resource_refs'] if v['generation'] else [] for k, v in resources.items()}
    errors += _cycles(resource_graph)
    issue_ids = {i['id'] for i in data['provenance']['issues']}
    for name, capability in data['capabilities'].items():
        check(all(i in issue_ids for i in capability['blocker_refs']), 'unknown capability blocker: ' + name)
        check(capability['human_approval'] == 'NOT_REVIEWED', 'unearned capability approval: ' + name)
        if capability['package_runtime_validation'] == 'PASS':
            evidence = data.get('extensions', {}).get('codex.runtime_evidence', {})
            check(name in evidence and isinstance(evidence[name], dict) and bool(evidence[name].get('report'))
                  and bool(re.fullmatch('[0-9a-f]{64}', evidence[name].get('evidence_sha256', ''))),
                  'unearned package runtime PASS: ' + name)
        if capability['readiness'] == 'BLOCKED':
            check(bool(capability['blocker_refs']), 'blocked capability lacks explanation: ' + name)
    if data['package']['runtime_ready']:
        evidence = data.get('extensions', {}).get('codex.runtime_evidence', {})
        check('standalone' in evidence and data['capabilities']['package_backed_prediction']['package_runtime_validation'] == 'PASS',
              'unearned runtime readiness: independent evidence missing')
    check(data['package']['status'] == 'DRAFT' and data['package']['completeness'] == 'PARTIAL', 'pilot science status promoted')
    check(data['capabilities']['official_likelihood']['readiness'] == 'BLOCKED', 'official likelihood promoted')
    legacy = data['legacy_spec']
    check(legacy['status'] == 'legacy_compatibility' and legacy['runtime_authority'] in ('existing_python_definition', 'package_yaml_npz'), 'legacy spec authority conflict')
    check(legacy['package_authority'] == 'experiment.input.yaml' and bool(legacy['conflicts']), 'missing historical conflict declaration')
    return errors


def read_arrays(raw, metadata):
    """Validate ZIP identity before NumPy loading; no path extraction or pickle."""
    if len(raw) > 128 * 1024 ** 2:
        raise ValueError('NPZ archive exceeds 128 MiB validation limit')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        expected = {key + '.npy' for key in metadata}
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError('NPZ key set/duplicate members differs from declarations')
        if sum(member.file_size for member in archive.infolist()) > 512 * 1024 ** 2:
            raise ValueError('NPZ uncompressed size exceeds validation limit')
    with np.load(io.BytesIO(raw), allow_pickle=False) as stored:
        return {key: stored[key] for key in stored.files}


def validate_arrays(data, arrays, raw):
    errors = []
    metadata = data['resources']['arrays']
    if set(arrays) != set(metadata):
        errors.append('NPZ key bijection')
    if hashlib.sha256(raw).hexdigest() != data['resources']['sha256']:
        errors.append('archive SHA256 mismatch')
    for key in set(arrays) & set(metadata):
        array, meta = arrays[key], metadata[key]
        if array.dtype.hasobject or array.dtype.kind not in 'biufc' or not np.all(np.isfinite(array)):
            errors.append('unsafe/non-finite numerical array: ' + key)
        if list(array.shape) != meta['shape'] or str(array.dtype) != meta['dtype']:
            errors.append('array shape/dtype mismatch: ' + key)
        if hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest() != meta['sha256_raw_c_order']:
            errors.append('array content SHA256 mismatch: ' + key)
        if meta['normalization']['quantity_kind'] == 'coordinate':
            if array.ndim != 1 or len(array) < 2 or np.iscomplexobj(array) or not np.all(np.diff(array) > 0):
                errors.append('coordinate must be finite strictly increasing real vector: ' + key)
    observable = data['observable']
    edges = arrays.get(observable['edges_ref'])
    if edges is None or edges.shape != (observable['bin_count'] + 1,):
        errors.append('observable bin edges missing/misaligned')
    if 'state_rho_e' in arrays and 'state_rho_mu' in arrays:
        for key in ('state_rho_e','state_rho_mu'):
            value = arrays[key]
            if value.shape != (3,3) or not np.allclose(value,value.conj().T) or not np.isclose(np.trace(value),1):
                errors.append('density-matrix normalization: ' + key)
    return errors



# Explicit report selections for the existing audited binding contracts. These
# declarations implement the 2026-11-05 report review; they are not name/AST rules.
# New physics descriptions belong to the H3-reviewed lab.physics_report metadata.
_REPORT_CONTENT = {
    'sns_fluence_legacy_v1': ('source', 'experiment_specific', 'SNS 探测器注量', '', ('fluence',)),
    'sns_michel_tabulation_legacy_v1': ('source', 'experiment_specific', '延迟连续谱', '', ('michel','source_table','source_interpolation','source_endpoint')),
    'sns_prompt_line_v1': ('source', 'experiment_specific', 'Prompt 谱线', '', ('line',)),
    'sns_fixed_state_v1': ('source', 'experiment_specific', '入射味态', '', ('state',)),
    'csi_target_inventory_v1': ('target', 'experiment_specific', 'CsI 核素计数', '', ('target_masses','inventory')),
    'li2026_sm_left_v1': ('theory', 'shared_framework', 'SM 与 EFT 输入',
        'SM 贡献由显式开关与弱混合角控制；空 BSM 映射是默认参数点。公共 LEFT 系数表不在本报告展开。', ()),
    'li2026_matching_v1': ('theory', 'shared_framework', '质子与中子 matching', '', ('matching',)),
    'elastic_kinematics_v1': ('kinematics', 'shared_framework', '弹性反冲支撑', '', ('kinematics',)),
    'nuclear_np_polynomial_v1': ('nuclear', 'shared_framework', '所选核响应', '', ('nuclear',)),
    'li2026_R_W_kernel_v1': ('theory', 'shared_framework', '粒子响应与核响应收缩',
        '粒子响应与核响应形成味空间的 Hermitian 核；MPhiPP 干涉项取 Hermitian 部分，LNC/LNV 扇区不交叉干涉。', ('kernel',)),
    'li2026_dsigma_v1': ('kinematics', 'shared_framework', '每核微分截面', '', ('dsigma',)),
    'csi_quenching_legacy_v1': ('detector', 'experiment_specific', 'CsI 淬灭映射', '', ('quenching',)),
    'legacy_csi_gamma': ('detector', 'experiment_specific', 'Gamma PE 响应', '', ('gamma',)),
    'csi2021_logistic_legacy': ('detector', 'experiment_specific', 'PE 选择效率', '', ('logistic',)),
    'legacy_component_acceptance': ('detector', 'experiment_specific', '分量接受率', '', ('acceptance',)),
    'legacy_csi2021_v1': ('prediction', 'experiment_specific', '逐箱预测与数值顺序', '', ('fold','density_fold')),
    'gaussian_two_pull_legacy_v1': ('statistics', 'experiment_specific', '双 pull 近似统计', '', ('two_pull','profiling')),
    'integrated_fluence_components_v1': ('source', 'experiment_specific', '已积分的源分量',
        '连续谱直接读取声明的探测器注量数组，离散谱线使用各自能量和权重。POT、产额和几何已包含，运行时不再相乘，也不额外乘活时间。', ()),
    'explicit_target_inventory_v1': ('target', 'experiment_specific', '显式核素计数',
        '核素质量分数、单核质量和核数由机器输入逐项登记；kg 质量用于核数归一化，GeV 质量用于反冲运动学。运行采用 detector_mass，run_mass_metadata 仅作历史元数据。', ('inventory',)),
    'nuclear_polynomial_arrays_v1': ('nuclear', 'shared_framework', '所选核响应',
        '使用本包核素的质子/中子多项式系数；保留原始归一化，不额外除以核自旋或 4π。', ('nuclear',)),
    'li2026_package_interaction_v1': ('theory', 'shared_framework', '本包的 EFT 截面接口',
        '使用 np 核子基底、显式 SM 开关和 LEC 参数；默认 BSM 映射为空。公共 matching 和粒子响应由已登记引擎提供，不在实验文档复制逐项表达式。', ('matching', 'kernel', 'kinematics', 'dsigma')),
    'deterministic_pe_legacy_v1': ('detector', 'experiment_specific', '确定性 PE 映射',
        '核反冲线性映射到 PE，沿现有采样谱和箱边界插值积分；该模型没有 Gamma 展宽。Slow 与 Fast 使用各自登记的网格，不将形式积分等同于收敛证明。', ('linear_pe',)),
    'observed_gaussian_legacy_v1': ('detector', 'experiment_specific', '观测坐标 Gaussian 响应',
        '平均观测量是反冲能量的二次函数；宽度使用观测 PE 的平方根。它不是以真实反冲能量决定宽度的通常 Gaussian；保留原实现的积分顺序和边界。', ('observed_gaussian',)),
    'legacy_efficiency_curve_v1': ('detector', 'experiment_specific', '表格效率与阈值',
        '效率在声明的 PE 坐标上线性插值，左侧取 efficiency_low，右侧取最后表值；仅当合同给出阈值时，对不高于阈值的点取低值。', ()),
    'gaussian_one_pull_legacy_v1': ('statistics', 'experiment_specific', '单 pull 近似统计',
        '观测和误差使用 counts/bin，信号已是逐箱计数，不再除 PE 箱宽。该 Gaussian 近似不代表官方 likelihood。', ('one_pull',)),
    'asymmetric_irls_legacy_v1': ('statistics', 'experiment_specific', '非对称误差 IRLS',
        '使用声明的观测、背景及上下侧误差；按模型残差选择误差侧，迭代求解带归一化 pull 的旧 Gaussian 近似。这里保留程序合同，不另造闭式 likelihood，也不宣称官方统计。', ()),
}
_REPORT_GROUPS = (
    ('source', 'Neutrino Source'), ('target', 'Target and Exposure'),
    ('theory', 'Theory and EFT Input'), ('nuclear', 'Nuclear Response Input'),
    ('kinematics', 'Kinematics and Cross Section'), ('detector', 'Detector Response'),
    ('prediction', 'Observable and Numerical Controls'), ('statistics', 'Statistical Data'),
)
_REPORT_ISSUES = {
    'official_experiment_sources': '缺官方论文、补充材料与 release 的独立核对；旧代码值不能称为官方原值。',
    'eft_primary_conventions': '算符 Lorentz/Lagrangian 定义、尺度及公共 matching 约定尚未逐项对照原始文献。',
    'nuclear_source_audit': '外部核响应源、转换流程和归一化仍待核实；I 的 M_nn(0) 差异保留为未决问题。',
    'antineutrino_kernel': '反中微子标签保留，但当前使用同一味核；一般 EFT 的符号和 helicity 尚未独立验证。',
    'statistics_semantics': 'observed 是旧 residual/excess；是否已扣除所列背景尚无原始证据，不消除负值，也不宣称官方 likelihood。',
    'legacy_status_and_reference': '历史阶段标签不能授予当前包人工批准；内部回归只支持对应技术范围。',
    'source_endpoint': '源表端点、裁剪和插值不等同理想 Michel 谱的精确端点归一化。',
    'detector_validity': '淬灭、分辨率、效率和时间选择的原始校准及适用区间待补。',
    'pilot_runtime': '历史 pilot 的独立运行缺口保留；是否已有后续技术证据须分别查看当前 capability，不自动关闭历史问题。',
}


def _report_metadata_errors(data):
    """Semantic references supplement the strict report extension schema."""
    meta = data.get('extensions', {}).get('lab.physics_report', {})
    errors = []
    ids = set()
    for mid, record in meta.get('models', {}).items():
        if mid not in data['models']:
            errors.append('report unknown model: ' + mid)
        for equation in record.get('equations', []):
            if equation['id'] in ids:
                errors.append('report duplicate equation: ' + equation['id'])
            ids.add(equation['id'])
            symbols = [s['symbol'] for s in equation['symbols']]
            if len(symbols) != len(set(symbols)):
                errors.append('report duplicate symbol: ' + equation['id'])
            for symbol in equation['symbols']:
                if '|' in symbol['symbol']:
                    errors.append('report table symbol must use lvert/rvert: ' + equation['id'])
                ref = symbol['parameter_ref']
                if ref is not None:
                    records=[mapping[ref] for mapping in (data['parameters'],data['resources']['arrays']) if ref in mapping]
                    if len(records)!=1 or records[0]['unit']!=symbol['unit']:
                        errors.append('report parameter/resource reference/unit: ' + str(ref))
    return errors


def _report_selection(data):
    """Accept authored H3 metadata or exact registered contracts, never fuzzy IDs."""
    from .generic_input import binding_contracts
    authored = data.get('extensions', {}).get('lab.physics_report', {}).get('models', {})
    v2 = data['package']['schema_version'] == 'cevns-experiment-input/2'
    bindings = (binding_contracts() if v2 else
                strict_json(Path(__file__).with_name('model_bindings.json').read_text('utf8')))
    selected, unknown = {}, []
    for mid, model in data['models'].items():
        if mid in authored:
            selected[mid] = authored[mid]
            continue
        contract = bindings.get(mid, {})
        registered = (model.get('implementation_contract') == contract.get('contract') and
                      model.get('formula') == contract.get('formula')) if v2 else (
            fingerprint({k:model[k] for k in ('mathematical_definition','variables','depends_on')}) ==
            contract.get('specification_fingerprint'))
        if mid not in _REPORT_CONTENT or not registered:
            unknown.append(mid)
            continue
        group, classification, title, explanation, equations = _REPORT_CONTENT[mid]
        selected[mid] = {'group':group, 'content_class':classification, 'title':title,
                         'explanation':explanation or model['physical_explanation'],
                         'equation_keys':equations, 'equations':[]}
    return selected, unknown


def _report_equation(key, data, isotopes):
    """Paper notation explicitly transcribed from the selected bound contracts."""
    params = data['parameters']
    def symbol(tex, meaning, unit='1', ref=None):
        if ref is not None:
            if ref not in params:
                raise ValueError('report missing parameter: ' + ref)
            unit = params[ref]['unit']
        return (tex, meaning, unit, ref)
    def parameter(tex, meaning, ref):
        return symbol(tex, meaning, ref=ref)
    def resource(tex, meaning, key):
        record=data['resources']['arrays'].get(key)
        if record is None:
            raise ValueError('report missing resource: '+key)
        return (tex,meaning,record['unit'],key)
    n=symbol('i', '本包靶核素索引')
    l=symbol(r'\ell', '本包源分量索引')
    b=symbol('b', '观测分箱索引')
    x=symbol('x', '重建光电子数', 'PE')
    mi=symbol('m_i', '由下列核素参数选取的动力学质量', 'GeV')
    if key=='fluence':
        return ('每分量积分注量', r'F=\frac{rN_{\mathrm{POT}}}{4\pi(100L)^2}', [
            parameter('F','每种源分量在探测器的积分注量','source.fluence_per_species'),
            parameter('r','每 POT、每分量产额','source.yield_per_pot'),
            parameter(r'N_{\mathrm{POT}}','积分质子数','source.total_pot'),
            parameter('L','基线；100 将 m 转为 cm','source.baseline_m')])
    if key=='michel':
        return ('延迟 Michel 形状',
            r'\begin{aligned}f_e(E_M)&=\frac{192E_M^2}{m_{\mu,M}^3}\left(\frac12-\frac{E_M}{m_{\mu,M}}\right)\\f_{\bar\mu}(E_M)&=\frac{64E_M^2}{m_{\mu,M}^3}\left(\frac34-\frac{E_M}{m_{\mu,M}}\right)\end{aligned}', [
            symbol(r'f_e,f_{\bar\mu}','理想解析形状；实际使用已裁剪、掩码且未重新归一的表','MeV^-1'),
            symbol('E_M','连续谱能量坐标','MeV'),
            symbol(r'm_{\mu,M}','下列 muon 质量乘 1000 后的 MeV 表示','MeV'),
            parameter(r'm_\mu','机器登记的 muon 质量','constants.m_mu')])
    if key=='line':
        ref='source.prompt_energy' if 'source.prompt_energy' in params else 'source.line_energy'
        return ('Prompt pion 衰变线', r'E_0=10^3\frac{m_\pi^2-m_\mu^2}{2m_\pi},\qquad\phi_\mu(E_M)=F\delta(E_M-E_0)', [
            parameter('E_0','谱线能量；GeV 质量换算为 MeV',ref),
            parameter(r'm_\pi','带电 pion 质量','constants.m_pi_charged'),
            parameter(r'm_\mu','muon 质量','constants.m_mu'),
            parameter('F','谱线的积分权重','source.fluence_per_species'),
            symbol('E_M','入射能量坐标','MeV'),symbol(r'\phi_\mu','prompt 注量密度','cm^-2 MeV^-1'),
            symbol(r'\delta','Dirac delta 分布','MeV^-1')])
    if key=='state':
        return ('固定纯味态', r'\rho_e=\begin{pmatrix}1&0&0\\0&0&0\\0&0&0\end{pmatrix},\qquad\rho_\mu=\begin{pmatrix}0&0&0\\0&1&0\\0&0&0\end{pmatrix}', [
            resource(r'\rho_e','电子味纯态，味序 e、mu、tau；trace 为 1','state_rho_e'),
            resource(r'\rho_\mu','muon 味纯态，味序 e、mu、tau；trace 为 1','state_rho_mu')])
    if key=='inventory':
        return ('核数与质量归一化', r'N_i=\frac{M_{\mathrm{det}}w_i}{m_{i,\mathrm{kg}}},\qquad\sum_iN_i m_{i,\mathrm{kg}}=M_{\mathrm{det}}', [
            n, parameter(r'M_{\mathrm{det}}','实际计算靶质量','target.detector_mass'),
            symbol('N_i','各核素核数','nuclei'),symbol('w_i','各核素质量分数'),
            symbol(r'm_{i,\mathrm{kg}}','单核 kg 质量','kg')] +
            [parameter(tex, i+' '+meaning, 'target.'+i+'.'+field) for i in isotopes
             for tex,meaning,field in [(r'N_{\mathrm{'+i+'}}','核数','nuclei'),
                                      (r'w_{\mathrm{'+i+'}}','质量分数','mass_fraction'),
                                      (r'm_{\mathrm{'+i+r'},kg}','单核质量','mass_kg')]])
    if key=='quenching':
        return ('CsI 淬灭', r't=10^{-3}T_{\mathrm{keV}},\qquad E_{\mathrm{ee}}=10^3\sum_{j=1}^{4}q_j t^j', [
            symbol(r'T_{\mathrm{keV}}','核反冲能','keV'),symbol('t','换为 MeV 的核反冲能','MeV'),
            symbol(r'E_{\mathrm{ee}}','电子等效能量','keVee'),symbol('j','淬灭多项式阶数')] +
            [parameter('q_'+str(j),'第 '+str(j)+' 阶淬灭系数；不同于四动量平方','detector.quenching_q'+str(j)) for j in range(1,5)])
    if key=='gamma':
        return ('Shape-rate Gamma 响应',
            r'\begin{aligned}k&=1+b_0E_{\mathrm{ee}},&\lambda&=\frac{a_0}{E_{\mathrm{ee}}}k\\p(x\mid T)&=\frac{\lambda^k}{\Gamma(k)}x^{k-1}e^{-\lambda x},&\langle x\rangle&=\frac{E_{\mathrm{ee}}}{a_0},\quad\operatorname{Var}(x)=\frac{k}{\lambda^2}\end{aligned}', [
            x,symbol('T','真实反冲，先经淬灭映射','keV'),symbol(r'E_{\mathrm{ee}}','电子等效能量','keVee'),
            parameter('a_0','Gamma 能量/PE 系数','detector.gamma_a'),parameter('b_0','Gamma shape 系数','detector.gamma_b'),
            symbol('k','shape；不是 rate'),symbol(r'\lambda','rate；scale 是其倒数','PE^-1'),
            symbol('p','条件 PE 密度','PE^-1'),symbol(r'\Gamma','Euler Gamma 函数'),symbol(r'\langle x\rangle','条件平均 PE','PE'),symbol(r'\operatorname{Var}(x)','条件方差','PE^2')])
    if key=='logistic':
        return ('重建 PE 上的效率', r'\epsilon(x)=\max\left\{\frac{a}{1+e^{-b_\epsilon(x-c)}}+d,\ 0\right\}', [
            x,symbol(r'\epsilon','选择效率')] + [parameter(tex,meaning,'detector.efficiency_'+f) for tex,meaning,f in [
                ('a','振幅','a'),(r'b_\epsilon','斜率','b'),('c','中心','c'),('d','偏移','d')]])
    if key=='fold':
        return ('实验折叠的物理关系',
            r'\begin{aligned}Y_{\ell i}(T)&=\int_{\mathrm{allowed}}dE\,\phi_\ell(E)\frac{d\sigma_{\ell i}}{dT}+\sum_s F_s\frac{d\sigma_{\ell i}(E_s,T)}{dT}\\N_b&=\sum_{\ell,i}N_i A_\ell\int_{x_b}^{x_{b+1}}dx\,\epsilon(x)\int dT\,p(x\mid T)Y_{\ell i}(T)\end{aligned}', [
            l,n,b,symbol('T','核反冲积分变量','keV'),symbol('E','源能量积分变量','MeV'),x,
            symbol(r'Y_{\ell i}','每核反冲产额','events/nucleus/keV'),symbol(r'\phi_\ell','已积分连续注量密度','cm^-2 MeV^-1'),
            symbol(r'd\sigma_{\ell i}/dT','每核截面','cm^2/keV'),symbol('s','离散谱线索引'),
            parameter('F_s','当前谱线使用的积分注量','source.fluence_per_species'),parameter('E_s','当前谱线能量','source.prompt_energy'),symbol('N_i','靶核数','nuclei'),
            symbol(r'A_\ell','分量接受率'),symbol('N_b','逐箱信号','events/bin'),symbol(r'\epsilon','PE 选择效率'),
            symbol('p','Gamma 条件密度','PE^-1'),symbol('x_b,x_{b+1}','NPZ 登记的相邻箱边界','PE')] +
            [parameter(r'A_{\mathrm{'+name+'}}',name+' 分量接受率','detector.acceptance_'+name) for name in ('e','mu','mub')]+[parameter(r'N_{\mathrm{'+iso+'}}',iso+' 靶核数','target.'+iso+'.nuclei') for iso in isotopes])
    if key=='two_pull':
        return ('旧双 pull Gaussian 近似',
            r'\begin{aligned}s_b&=\frac{N_b}{x_{b+1}-x_b}\\\chi^2&=\sum_b\left[\frac{d_b-(1+\alpha)s_b-(1+\beta)B_b}{\sigma_b}\right]^2+\left(\frac{\alpha}{\sigma_\alpha}\right)^2+\left(\frac{\beta}{\sigma_\beta}\right)^2\end{aligned}', [
            b,symbol('s_b','信号只除一次箱宽','counts/PE'),symbol('N_b','预测逐箱信号','events/bin'),
            symbol('x_b,x_{b+1}','PE 箱边界','PE'),resource('d_b','旧 observed-like residual/excess','statistics_observed'),
            resource('B_b','背景数组','statistics_background'),
            resource(r'\sigma_b','误差取声明下限后使用','statistics_uncertainty'),symbol(r'\alpha,\beta','信号与背景归一化 nuisance'),
            symbol(r'\chi^2','近似目标函数'),parameter(r'\sigma_\alpha','信号 pull 宽度','statistics.sigma_alpha'),
            parameter(r'\sigma_\beta','背景 pull 宽度','statistics.sigma_beta'),
            parameter(r'\sigma_{\mathrm{floor}}','逐箱误差下限','statistics.sigma_floor')])
    if key=='linear_pe':
        return ('确定性观测映射', r'x=Y_{\mathrm{PE}}T_{\mathrm{keV}}', [
            x,symbol(r'T_{\mathrm{keV}}','真实核反冲','keV'),parameter(r'Y_{\mathrm{PE}}','PE 转换系数','detector.pe_per_keV')])
    if key=='observed_gaussian':
        return ('观测坐标上的 Gaussian 关系',
            r'\begin{aligned}\mu(T)&=(a+b_TT)T,&s(x)&=c\sqrt{x}\\p(x\mid T)&=\begin{cases}\dfrac{\exp[-(x-\mu(T))^2/(2s(x)^2)]}{\sqrt{2\pi}s(x)},&x>0\\0,&x\le0\end{cases}\end{aligned}', [
            x,symbol('T','真实核反冲','keV'),symbol(r'\mu','平均观测 PE','PE'),symbol('s','使用观测 x 的宽度','PE'),
            symbol('p','旧观测响应密度；不声称在固定 T 下严格单位归一','PE^-1'),
            parameter('a','线性响应','detector.mean_linear'),parameter('b_T','二次响应','detector.mean_quadratic'),
            parameter('c','分辨率系数','detector.sigma_coefficient')])
    if key=='one_pull':
        return ('旧单 pull Gaussian 近似',
            r'\chi^2=\sum_b\left[\frac{d_b-(1+\alpha)s_b}{\sigma_b}\right]^2+\left(\frac{\alpha}{\sigma_\alpha}\right)^2', [
            b,symbol('d_b,s_b','观测和预测逐箱计数','counts/bin'),symbol(r'\sigma_b','逐箱误差','counts/bin'),
            symbol(r'\alpha','信号归一化 nuisance'),symbol(r'\chi^2','近似目标函数'),
            parameter(r'\sigma_\alpha','归一化 pull 宽度','statistics.sigma_alpha')])

    if key=='source_table':
        return ('谱表网格、裁剪与 mask（数值物化规则）',
            r'\begin{aligned}E_j&=E_{\mathrm{tab,min}}+\frac{j}{n_{\mathrm{tab}}-1}(E_{\mathrm{tab,max}}-E_{\mathrm{tab,min}})\\\Phi_{\ell j}&=F\max\{f_\ell(E_j),0\}\,\mathbf1_{[E_{\mathrm{mask,min}},E_{\mathrm{mask,max}}]}(E_j)\end{aligned}', [
            resource('E_j','等间距表格的能量坐标；j=0..n_tab-1','source_energy_MeV'),
            symbol('j','谱表节点索引'),l,symbol(r'f_\ell','上一式的 Michel 解析形状','MeV^-1'),
            symbol(r'\Phi_{\ell j}','节点上的探测器积分注量密度','cm^-2 MeV^-1'),
            resource(r'\Phi_{ej}','电子分量节点表','source_fluence_e'),
            resource(r'\Phi_{\bar\mu j}','反 muon 分量节点表','source_fluence_mub'),
            parameter('F','每分量积分注量','source.fluence_per_species'),
            parameter(r'E_{\mathrm{tab,min}}','谱表下界','source.tabulation_min'),
            parameter(r'E_{\mathrm{tab,max}}','谱表上界','source.tabulation_max'),
            parameter(r'n_{\mathrm{tab}}','谱表节点数','source.tabulation_nodes'),
            parameter(r'E_{\mathrm{mask,min}}','mask 下界','source.mask_min'),
            parameter(r'E_{\mathrm{mask,max}}','mask 上界','source.mask_max'),
            symbol(r'\mathbf1','区间指示函数：在 mask 内为 1，否则为 0')])
    if key=='source_interpolation':
        return ('连续谱的线性插值（数值读取规则）',
            r'\phi_\ell(E)=\begin{cases}(1-t)\Phi_{\ell j}+t\Phi_{\ell,j+1},& E_j\le E\le E_{j+1}\\0,&E<E_{\mathrm{tab,min}}\ \text{or}\ E>E_{\mathrm{tab,max}}\end{cases},\qquad t=\frac{E-E_j}{E_{j+1}-E_j}', [
            l,symbol('E','查询能量','MeV'),symbol(r'\phi_\ell','插值后的积分注量密度','cm^-2 MeV^-1'),
            resource('E_j,E_{j+1}','包围查询点的相邻节点，j=0..n_tab-2','source_energy_MeV'),
            symbol(r'\Phi_{\ell j},\Phi_{\ell,j+1}','上一式定义的相邻节点密度；按分量取对应 NPZ 表','cm^-2 MeV^-1'),
            symbol('j','插值区间索引'),symbol('t','插值权重'),
            parameter(r'E_{\mathrm{tab,min}}','谱表下界','source.tabulation_min'),
            parameter(r'E_{\mathrm{tab,max}}','谱表上界','source.tabulation_max')])
    if key=='source_endpoint':
        return ('连续积分的实际 DAR 上界（衰变运动学）',
            r'E_{\mathrm{int,max}}=10^3\frac{m_\mu^2-m_e^2}{2m_\mu}', [
            parameter(r'E_{\mathrm{int,max}}','当前运行使用的 MeV 上界','source.integration_max'),
            parameter(r'm_\mu','muon 质量','constants.m_mu'),
            parameter(r'm_e','电子质量','constants.m_e')])
    if key=='target_masses':
        return ('CsI 化学计量与两种质量单位',
            r'w_i=\frac{A_i}{\sum_{j\in\mathrm{target}}A_j},\qquad m_{i,\mathrm{kg}}=A_i u_{\mathrm{kg}},\qquad m_{i,\mathrm{GeV}}=A_i u_{\mathrm{GeV}}', [
            n,symbol('j','化学式中核素索引，每个 CsI 单元各一个 Cs 和 I'),
            symbol('A_i','核素质量数'),symbol('w_i','核素质量分数'),
            symbol(r'm_{i,\mathrm{kg}}','用于核数的单核质量','kg'),
            symbol(r'm_{i,\mathrm{GeV}}','用于运动学的单核质量','GeV'),
            parameter(r'u_{\mathrm{kg}}','kg 原子质量常数','target.atomic_mass_kg'),
            parameter(r'u_{\mathrm{GeV}}','GeV 原子质量常数','constants.AMU_GEV')]+
            [parameter('A_{'+iso+'}',iso+' 质量数','target.'+iso+'.A') for iso in isotopes])
    if key=='acceptance':
        return ('分量选择接受率的施加',
            r'N_{\ell i,b}=A_\ell N_i N^{\mathrm{pre}}_{\ell i,b}', [
            l,n,b,symbol(r'N_{\ell i,b}','该分量/核素的选后逐箱计数','events/bin'),
            symbol('N_i','第 3 节登记的核数','nuclei'),
            symbol(r'N^{\mathrm{pre}}_{\ell i,b}','已经完成 PE 响应、效率和分箱的每核产额','events/nucleus/bin'),
            symbol(r'A_\ell','独立分量接受率；不包含在注量、PE 响应或效率中')]+
            [parameter(r'A_{\mathrm{'+name+'}}',name+' 分量接受率','detector.acceptance_'+name) for name in ('mu','e','mub')])
    if key=='density_fold':
        return ('当前 PE 密度采样与箱积分（数值执行约定）',
            r'\begin{aligned}h_{\ell i}(x_j)&=\max\!\left\{\operatorname{Trapz}_{T}\!\left[\frac{Y_{\ell i}(T)p(x_j\mid T)}{m_{i,\mathrm{kg}}}\right],0\right\}\\N^{\mathrm{pre}}_{\ell i,b}&=m_{i,\mathrm{kg}}\operatorname{Trapz}_{x\in[x_b,x_{b+1}]}\!\left[\operatorname{Interp}(x_j,h_{\ell i};x)\epsilon(x)\right]\end{aligned}', [
            l,n,b,symbol('j','PE 密度节点索引'),symbol('T','反冲能积分变量','keV'),
            symbol('x,x_j,x_b,x_{b+1}','重建坐标、密度采样点和相邻箱边界','PE'),
            symbol(r'Y_{\ell i}','每核反冲产额，定义见前式','events/nucleus/keV'),
            symbol('p','Gamma 条件 PE 密度','PE^-1'),symbol(r'm_{i,\mathrm{kg}}','单核 kg 质量，见第 3 节','kg'),
            symbol(r'h_{\ell i}','每 kg 的中间 PE 密度','events/kg/PE'),
            symbol(r'N^{\mathrm{pre}}_{\ell i,b}','效率和箱积分后的每核产额','events/nucleus/bin'),
            symbol(r'\epsilon','PE 选择效率'),symbol(r'\operatorname{Trapz}','实际所选节点上的复合梯形积分'),
            symbol(r'\operatorname{Interp}','PE 密度线性插值，采样范围外为 0')])
    if key=='profiling':
        return ('双 pull 的解析 profiling',
            r'\begin{aligned}r_b&=d_b-s_b-B_b,\quad u_b=\max\{\sigma_b,\sigma_{\mathrm{floor}}\}\\\begin{pmatrix}\sum_b s_b^2/u_b^2+\sigma_\alpha^{-2}&\sum_b s_bB_b/u_b^2\\\sum_b s_bB_b/u_b^2&\sum_b B_b^2/u_b^2+\sigma_\beta^{-2}\end{pmatrix}\begin{pmatrix}\widehat\alpha\\\widehat\beta\end{pmatrix}&=\begin{pmatrix}\sum_b s_br_b/u_b^2\\\sum_b B_br_b/u_b^2\end{pmatrix}\\\chi^2_{\mathrm{prof}}&=\chi^2(\widehat\alpha,\widehat\beta)\end{aligned}', [
            b,resource('d_b','旧 observed-like residual/excess','statistics_observed'),
            resource('B_b','背景数组','statistics_background'),
            resource(r'\sigma_b','原生逐箱不确定度','statistics_uncertainty'),
            symbol('s_b','逐箱信号除一次 PE 宽度后的密度','counts/PE'),
            symbol('r_b','零 pull 下的残差','counts/PE'),symbol('u_b','施加误差下限后的宽度','counts/PE'),
            symbol(r'\widehat\alpha,\widehat\beta','无边界解析极小点'),
            symbol(r'\chi^2,\chi^2_{\mathrm{prof}}','前式目标函数及其 profile 值'),
            parameter(r'\sigma_{\mathrm{floor}}','逐箱误差下限','statistics.sigma_floor'),
            parameter(r'\sigma_\alpha','信号 Gaussian pull 宽度','statistics.sigma_alpha'),
            parameter(r'\sigma_\beta','背景 Gaussian pull 宽度','statistics.sigma_beta')])

    raise ValueError('unknown reviewed report equation: '+key)



def render_physics(data, arrays, *, summary=False):
    """Both reading views share one policy and the same read-only input metadata."""
    errors=_report_metadata_errors(data)
    if errors:
        raise ValueError('; '.join(errors))
    selected,unknown=_report_selection(data)
    package=data['package'];params=data['parameters'];resources=data['resources']['arrays']
    meta=data.get('extensions',{}).get('lab.physics_report',{})
    v2=package['schema_version']=='cevns-experiment-input/2'
    cfg=data.get('assembly',{})
    components=cfg.get('source',{}).get('components',[]) if v2 else data['source']['components']
    isotopes=([i['id'] for i in cfg.get('target',{}).get('isotopes',[])] if v2 else data['target']['isotope_order'])
    observable=data['observable'];edges=arrays[observable['edges_ref']]
    stats=cfg.get('statistics',{}) if v2 else data['statistics']
    approval=package.get('human_approval',package.get('human_physics_approval','NOT_RECORDED'))
    bt=chr(96)
    lines=[]
    def code(value):return bt+str(value)+bt
    def text(value):
        value=str(value)
        return value if '\ufffd' not in value else '上游说明含编码损坏；需回 H3 核对原记录'
    def cell(value):return text(value).replace('|','&#124;').replace('\n',' ')
    def table(head,rows):
        return '\n'.join(['| '+' | '.join(head)+' |','| '+' | '.join('---' for _ in head)+' |']+
                         ['| '+' | '.join(cell(v) for v in row)+' |' for row in rows])
    def paragraph(value):lines.extend([text(value),''])
    def anchor(value):return re.sub('[^a-zA-Z0-9_-]','-',value)
    def ref(value):
        if value in params:return '['+code(value)+'](#param-'+anchor(value)+')'
        if value in resources:return '['+code(value)+'](#res-'+anchor(value)+')'
        return code(value)
    def value(raw):return 'MISSING' if raw is None else json.dumps(raw.item() if isinstance(raw,np.generic) else raw,ensure_ascii=False)
    def entries(group):
        return [(mid,m) for mid,m in selected.items() if m['group']==group and m['content_class']=='experiment_specific']
    title=package.get('experiment',package['experiment_slug'])+' — '+package['dataset_id']
    description=meta.get('summary',title+' 使用 '+('、'.join(c.get('id',c.get('component_id','')) for c in components) or '尚未绑定的源')+
                         '，靶核素为 '+('、'.join(isotopes) or '尚未绑定')+'；观测量为 '+observable['name']+'，共 '+
                         str(observable['bin_count'])+' 个 '+observable['unit']+' 分箱。')
    shared=[(mid,m) for mid,m in selected.items() if m['content_class']=='shared_framework']
    dimension={'theory':'Interaction / 组合接口','nuclear':'Nuclear Structure','kinematics':'Kinematics / Cross-section'}
    def module_rows():
        return [(dimension.get(m['group'],m['group']),code(mid),
                 data['models'][mid].get('binding_status',data['models'][mid].get('contract',{}).get('binding_status','未登记')))
                for mid,m in shared]
    if summary:
        paragraph('# '+title+' — Physics Summary')
        paragraph('状态：'+package['status']+' / '+package.get('completeness','见能力记录')+'；人工科学审核 '+approval+'。')
        paragraph(description)
        paragraph('[详细实现说明](experiment.physics.md) 包含完整实验公式、符号、参数、分箱、逐 bin 数据和数值约定。')
        paragraph('## 关键实验输入')
        key_ids=['source.baseline_m','source.total_pot','source.yield_per_pot','source.fluence_per_species',
                 'source.prompt_energy','source.line_energy','source.integration_max','target.detector_mass']
        paragraph(table(['输入','当前值','单位'],[(code(pid),value(params[pid]['value']),params[pid]['unit']) for pid in key_ids if pid in params]))
        if isotopes:paragraph('靶核素：'+', '.join(isotopes)+'。核素质量分数、单核质量及核数见详细版 Target。')
        paragraph(table(['探测器组件','本次选择'],[(m['title'],code(mid)) for mid,m in entries('detector')]))
        paragraph('## 共享模块选择')
        paragraph(table(['独立维度','已登记 model ID','绑定状态'],module_rows()))
        paragraph('Interaction 与 Nuclear Structure 分开选择；表中的状态是已有记录，不代表本次重新运行或科学接受。')
        paragraph('## Observable / Statistics')
        paragraph('观测量：'+observable['name']+'；'+str(observable['bin_count'])+' 箱，范围 '+
                  value(edges[0])+'–'+value(edges[-1])+' '+observable['unit']+'。完整边界见详细版第 6 节。')
        paragraph('统计选择：'+(', '.join(code(mid) for mid,_ in entries('statistics')) or '未提供')+
                  '。数据单位：'+(stats.get('observable_unit','未声明') if v2 else observable['statistics_unit'])+'。')
        if not v2:
            paragraph('预测为 events/bin，统计前只除一次 PE 箱宽；保留 observed-like residual 的负值。当前是旧 Gaussian 近似，背景扣除语义尚未确认。')
        paragraph('## 主要限制')
        for issue in data['provenance']['issues'][:5]:
            paragraph('- '+issue['id']+'：'+_REPORT_ISSUES.get(issue['id'],issue['detail']))
        for mid in unknown:paragraph('- H3_UNCLASSIFIED_MODEL: '+code(mid)+'；需 H3 补充说明。')
        paragraph('完整限制、来源与能力记录见[详细版第 10 节](experiment.physics.md#section-10)。')
        return '\n'.join(lines).rstrip()+'\n'

    paragraph('# '+title)
    paragraph('[精简阅读版](experiment.physics.summary.md)')
    paragraph('## 目录')
    headings=('实验范围','Source','Target','本实验选择的共享模块','Detector','Observable','Prediction folding','Statistics','数值资源','来源、限制与状态')
    for number,name in enumerate(headings,1):paragraph('['+str(number)+'. '+name+'](#section-'+str(number)+')')
    paragraph('[公式索引](#equation-index) · [参数索引](#parameter-index)')
    def section(number):
        paragraph('<a id="section-'+str(number)+'"></a>')
        paragraph('## '+str(number)+'. '+headings[number-1])
    # Values are printed once, in their actual experiment-side consumer's module.
    groups={g:[] for g in ('source','target','detector','prediction','statistics','observable')}
    locations={}
    for pid,p in params.items():
        consumers=[c.get('model_id') if isinstance(c,dict) else c for c in p['consumers']]
        group=next((selected[mid]['group'] for mid in consumers if mid in selected and
                    selected[mid]['content_class']=='experiment_specific'),None)
        if group not in groups:
            group={'source':'source','target':'target','detector':'detector','numerics':'prediction',
                   'statistics':'statistics','observable':'observable'}.get(pid.split('.')[0])
        if p['role'] in ('reference_only','unused_snapshot'):group=None
        if group in groups:
            groups[group].append((pid,p));locations[pid]=group
    def parameters(group):
        if groups[group]:
            paragraph(table(['Parameter ID','采用值','单位 / 角色','定义'],[
                (ref(pid),value(p['value']),p['unit']+' / '+p['role'],p['meaning']) for pid,p in groups[group]]))
    equation_index=[];emitted=set();used_models=set()
    def equation(eid,name,latex,symbols,mid):
        if eid in emitted:return
        emitted.add(eid)
        if len({s_[0] for s_ in symbols})!=len(symbols):raise ValueError('duplicate report symbol: '+eid)
        number=len(equation_index)+1;equation_index.append((number,name,mid))
        paragraph('<a id="eq-'+str(number)+'"></a>')
        paragraph('**('+str(number)+') '+name+'**')
        lines.extend(['$$',latex,'$$',''])
        paragraph(table(['符号','定义','单位','Parameter ID / NPZ key'],[
            ('$'+symbol+'$',meaning,unit,ref(link) if link else 'derived/constant（见定义）')
            for symbol,meaning,unit,link in symbols]))
    def models(group):
        for mid,m in entries(group):
            used_models.add(mid)
            paragraph('### '+m['title'])
            paragraph('模型：'+code(mid)+'。'+m['explanation'])
            for key in m.get('equation_keys',[]):
                equation(key,*_report_equation(key,data,isotopes),mid)
            for e in m.get('equations',[]):
                equation(e['id'],e['title'],e['latex'],[
                    (a['symbol'],a['definition'],a['unit'],a['parameter_ref']) for a in e['symbols']],mid)
            original=data['models'][mid]
            details=[]
            if original.get('inputs'):details.append(('输入','; '.join(ref(x) if x in params or x in resources else x for x in original['inputs'])))
            if original.get('output'):details.append(('输出',original['output']))
            for field,label in [('domain','定义域'),('normalization','归一化'),('boundary_behavior','边界/裁剪'),('boundary','边界/裁剪')]:
                if original.get(field):details.append((label,original[field]))
            if details:paragraph(table(['合同项','当前约定'],details))
    section(1)
    paragraph(description)
    paragraph('科学主张：'+package['scientific_claim']+'。包状态 '+package['status']+' / '+
              package.get('completeness','见能力记录')+'；人工科学审核 '+approval+'。')
    paragraph('YAML 是标量与模型合同权威，NPZ 是数组权威；两份 Markdown 是同源派生说明。本文记录当前实验适配所需的输入与执行约定，不把旧实现恢复值认作官方论文原值。')
    if not v2:paragraph('当前是 POT 积分、无时间坐标的九箱配置；source.time_coordinate 为 null。不能据此构造 ROOTTime 或二维时间–能量分析。')
    section(2)
    if components:
        paragraph(table(['源分量 / 粒子标签','味态 NPZ','连续谱 NPZ','离散谱线'],[
            (c.get('id',c.get('component_id'))+' / '+c['particle_kind'],ref(c['rho_ref']),ref(c['continuum_ref']) if c.get('continuum_ref') else '无',
             '; '.join(ref(line['energy_ref'])+' / '+ref(line['fluence_ref']) for line in c.get('lines',[])) or c.get('line_model_ref') or '无') for c in components]))
    parameters('source');models('source')
    if not v2:
        paragraph('公式性质：积分注量是球面几何稀释与实验归一化输入；Michel 形状是无电子质量的理想衰变谱；prompt 线与积分上界来自衰变运动学；网格、mask 和插值是数值物化/读取规则。每 POT 产额的官方来源仍待核实。')
        paragraph('理论 Michel 形状只在其理想支撑区间具有相应归一化。实际表先裁剪和 mask 再插值，包含末单元 taper；不在每个查询点重新截断到理想端点，也不将表重新归一化到 F。运行时 NPZ 已含 POT、产额和几何，连续谱不再乘 F；prompt 权重使用 F 一次。没有额外活时间因子。')
    section(3)
    paragraph('本包靶核素：'+(', '.join(isotopes) or '未绑定')+'。质量分数、单核质量和核数的采用值只列于本节。')
    parameters('target');models('target')
    section(4)
    paragraph('Interaction 与 Nuclear Structure 是独立选择维度；下表只登记现有模块，不展开 matching、Particle Response、Nuclear Response、Helm、运动学或公共截面公式。')
    paragraph(table(['选择维度','实际 model ID','已记录绑定状态'],module_rows()))
    if not v2:
        interaction=data['interaction']
        paragraph(table(['必要配置','当前选择'],[
            ('theory / revision',code(interaction['theory_id'])+' / '+str(interaction['theory_revision'])),
            ('核子基底 / matching 质量方案',interaction['basis']+' / '+interaction['c10_mass_mode']),
            ('默认 BSM coefficient map',json.dumps(interaction['default_bsm_coefficients'],ensure_ascii=False)),
            ('SM / 弱混合角',ref('interaction.include_sm')+' = '+value(params['interaction.include_sm']['value'])+'; '+
             ref('interaction.sin2thetaW')+' = '+value(params['interaction.sin2thetaW']['value'])),
            ('LEC 配置','YAML 中 lecs.* 的直接输入/只读状态；本报告参数索引给出精确 ID'),
            ('味序 / 系数矩阵轴',str(interaction['flavor_order'])+' / '+str(interaction['coefficient_axes'])),
            ('Nuclear Structure 资源','各核素/通道的 NPZ 系数绑定见第 9 节；未选择 Helm')]))
    elif cfg.get('interaction'):
        paragraph('组合配置：'+json.dumps(cfg['interaction'],ensure_ascii=False)+'；资源按 assembly.target 的显式绑定读取。')
    paragraph('当前实际绑定合同入口：[v1 模型合同](../../../../cevns_pyeft/experiments/model_bindings.json)、'
              '[v2 组件合同](../../../../cevns_pyeft/experiments/component_bindings.json)。'
              '外部理论与核结构约定的未决问题保留在第 10 节，不以失效的历史文档链接代替证据。')
    section(5)
    parameters('detector');models('detector')
    if 'legacy_csi_gamma' in selected:
        paragraph('施加顺序：真实反冲 → 淬灭得到 Eee → Gamma PE 条件密度 → 反冲积分和 PE 密度采样 → PE 插值 → 重建 PE 效率 → 箱积分 → 分量接受率及靶核数。Gamma 使用 shape-rate，scale 为 rate 的倒数；分析窗口损失不重分配。效率只有零下限，查询网格超出 [0,1] 会由已有 folding 合同拒绝。')
    section(6)
    paragraph('观测量：'+observable['name']+'；坐标单位 '+observable['unit']+'；共 '+str(observable['bin_count'])+' 箱。')
    parameters('observable')
    paragraph('唯一 bin-edge 数组：'+ref(observable['edges_ref'])+'。完整边界为 '+', '.join(value(x_) for x_ in edges)+' '+observable['unit']+'。')
    paragraph(table(['Bin','下边界','上边界','宽度'],[(i+1,value(lo),value(hi),value(hi-lo)) for i,(lo,hi) in enumerate(zip(edges[:-1],edges[1:]))]))
    paragraph('边界约定：'+observable.get('boundary','按显式边界逐箱积分；不从箱数猜测坐标。'))
    if not v2:
        paragraph('预测单位 '+observable['prediction_unit']+'；统计原生单位 '+observable['statistics_unit']+'。预测是 signal only，已含效率、接受率、POT 与核数，不在预测阶段扣背景或除箱宽。')
    section(7)
    steps=meta.get('calculation_steps')
    if steps is None:
        steps=[]
        if components:steps.append('读取声明的连续积分注量、谱线与入射味态，不重复乘源归一化因子。')
        if isotopes:steps.append('逐核素调用第 4 节选定公共截面，得到每核反冲产额；公共模块的输入输出按既有合同。')
        steps.extend(m['explanation'] for _,m in entries('detector'))
        steps.extend(m['explanation'] for _,m in entries('prediction'))
        if not steps:steps=['当前为 specification-only；尚无可执行的实验计算路径，交回 H3。']
    for number,step in enumerate(steps,1):paragraph(str(number)+'. '+step)
    parameters('prediction');models('prediction')
    for group,_ in _REPORT_GROUPS:
        if group not in ('source','target','detector','prediction','statistics'):
            models(group)
    if 'legacy_csi2021_v1' in selected:
        paragraph('数值网格：连续能量在 source.integration_min/max 上取 numerics.n_enu 个线性节点；与显式 breakpoints（若有）合并、排序去重。每个反冲只保留正能量且达到公共运动学阈值的已有节点，不补插阈值节点，再做梯形积分；谱线按阈值单独加权。各核素反冲从 numerics.recoil_min_keV 到公共模块给出的支撑上界取 numerics.n_er 个含端点线性节点；上界覆盖所有分量的积分能量上界及谱线能量。')
        paragraph('PE 密度网格从首个箱边界起，按 numerics.observed_step 递增，以最后箱边界加半步为开区间停止位置。先采样每 kg 密度并裁剪为非负，再插值到每箱 numerics.n_observed_bin 个含端点线性节点，乘效率后梯形积分，恢复单核质量因子，最后乘接受率和实际核数。中间 kg 因子抵消，不再额外乘 Mdet；插值范围外为零，窗口损失不重归一。')
        paragraph('实际误差控制：'+data['prediction']['error_control']+'。另有积分路径不等于当前绑定策略；这里不替换数值次序，也不据此声称收敛。')
    section(8)
    parameters('statistics');models('statistics')
    if stats:
        fields=[(name,stats[name+'_ref']) for name in ('observed','background','uncertainty','lower','upper','spectrum') if stats.get(name+'_ref')]
        if fields:
            paragraph('逐 bin 数据保持原生单位 '+(stats.get('observable_unit','未声明') if v2 else observable['statistics_unit'])+'；以下每列直接读取所列 NPZ key。')
            paragraph(table(['Bin']+[ref(key) for _,key in fields],[
                [i+1]+[value(arrays[key][i]) for _,key in fields] for i in range(observable['bin_count'])]))
    if 'gaussian_two_pull_legacy_v1' in selected:
        paragraph('数据语义：observed 是旧 residual/excess，允许负值，不是 raw Poisson count；是否已扣除所列 BRN/NIN 背景尚未确认。信号从 events/bin 除一次 bin width，观测/背景/不确定度已是 counts/PE，不再次除宽度。')
        paragraph('当前没有 covariance 资源；使用与参数无关的对角逐 bin Gaussian 误差。alpha 和 beta 的先验是独立、零均值 Gaussian，但每个归一化 nuisance 同时作用于所有箱，产生共同归一化变化。实际 binding 无 clip_bounds，执行无边界 2×2 正规方程；奇异时返回 alpha=beta=0、success=False。')
        paragraph('本模型提供 profiled approximate chi2；没有在此定义官方 likelihood、指定零假设下的 test statistic、自由度或显著度/CL 映射。不能从模板补造这些科学主张。')
    section(9)
    if isotopes:
        bindings=([(i['id'],i['responses']) for i in cfg['target']['isotopes']] if v2 else
                  [(iso,{ch:'nuclear_'+iso+'_'+ch for ch in data['interaction']['nuclear_channels']}) for iso in isotopes])
        paragraph(table(['核素','Nuclear Structure 通道 → NPZ key'],[
            (iso,'; '.join(ch+' → '+ref(key) for ch,key in mapping.items())) for iso,mapping in bindings]))
        paragraph('核系数资源按左核子 p/n、右核子 p/n、升幂系数轴绑定；此处只记录资源接口，核结构计算由所选公共模块负责。原始归一化不改变，外部来源/约定待核。')
    paragraph(table(['NPZ key','shape / dtype','单位 / 含义','来源 ID'],[
        ('<a id="res-'+anchor(key)+'"></a>'+code(key),str(r['shape'])+' / '+r['dtype'],r['unit']+' / '+r['meaning'],', '.join(r['source_refs']))
        for key,r in resources.items()]))
    paragraph('数组保留原 dtype、精度和顺序，以 allow_pickle=False 读取；哈希、生成依赖和完整轴声明以 YAML 为准，不在正文 dump。')
    section(10)
    paragraph(table(['能力','已记录状态','人工审核'],[(k,c.get('status',c.get('readiness')),c['human_approval']) for k,c in data['capabilities'].items()]))
    paragraph('以上是输入中已有的状态，报告生成不重新执行 Runtime，也不提升能力或人工科学接受。')
    paragraph(table(['问题 ID / 状态','限制','影响范围'],[
        (i['id']+' / '+i['status'],_REPORT_ISSUES.get(i['id'],i['detail']),', '.join(i['blocks'])) for i in data['provenance']['issues']]))
    for mid in unknown:paragraph('H3_UNCLASSIFIED_MODEL: '+code(mid)+'。缺少已审阅的分类/解释，不自动展开公式；原来源保留在 YAML。')
    hidden=[mid for mid,m in selected.items() if m['content_class']=='implementation_detail']
    if hidden:paragraph('仅保留在机器合同的实现审计项：'+', '.join(code(mid) for mid in hidden)+'。')
    paragraph(table(['来源 ID','路径 / locator','种类 / 独立官方核实'],[
        (key,s_.get('path',s_.get('locator','未登记')),s_.get('kind','未登记')+' / '+str(s_.get('independently_officially_verified','未登记')))
        for key,s_ in data['provenance']['sources'].items()]))
    paragraph('<a id="equation-index"></a>')
    paragraph('## Appendix A. 公式索引')
    paragraph(table(['编号','实验公式','模型 ID'],[('['+str(number)+'](#eq-'+str(number)+')',name,code(mid)) for number,name,mid in equation_index]))
    paragraph('<a id="parameter-index"></a>')
    paragraph('## Appendix B. 唯一参数索引')
    paragraph('实验采用值只在对应模块表中列一次；共享模块参数通过精确 ID 回到 YAML 配置，不复制公共模块公式或 LEC 数值表。')
    paragraph(table(['Parameter ID','主文位置 / 配置入口','来源定位'],[
        ('<a id="param-'+anchor(pid)+'"></a>'+code(pid),locations.get(pid,'第 4 节共享配置 / YAML；非实验公式'),
         ', '.join(p['source_refs'])+'; '+p.get('locator',p.get('status',p.get('provenance_status','未登记')))) for pid,p in params.items()]))
    return '\n'.join(lines).rstrip()+'\n'


def validate_package(directory, check_md=True):
    """Read and validate the package. Never construct an experiment or execute it."""
    directory = Path(directory).resolve()
    try:
        data = strict_json((directory/'experiment.input.yaml').read_text(encoding='utf-8'))
        errors = validate_document(data)
        if errors:
            return {'status':'FAIL','errors':errors,'scope':'schema/semantics only'}
        archive_path = directory/data['resources']['archive']
        if archive_path.resolve().parent != directory:
            raise ValueError('archive path escapes input package')
        raw = archive_path.read_bytes()
        arrays = read_arrays(raw,data['resources']['arrays'])
        if data['package']['schema_version'] == 'cevns-experiment-input/2':
            from .generic_input import validate_resources
            errors += validate_resources(data,arrays,raw)
        else:
            errors += validate_arrays(data,arrays,raw)
        if check_md and not errors:
            expected = render_physics(data,arrays)
            if (directory/'experiment.physics.md').read_text(encoding='utf-8') != expected:
                errors.append('Physics MD differs from deterministic YAML/NPZ rendering')
            summary_path=directory/'experiment.physics.summary.md'
            if summary_path.exists() and summary_path.read_text(encoding='utf-8') != render_physics(data,arrays,summary=True):
                errors.append('Physics summary MD differs from deterministic YAML/NPZ rendering')
        return {'status':'FAIL' if errors else 'PASS','errors':errors,'schema_version':data['package']['schema_version'],
                'parameter_roles':dict(Counter(p['role'] for p in data['parameters'].values())),
                'models':len(data['models']),'parameters':len(data['parameters']),'arrays':len(arrays),
                'runtime_binding':data.get('engine_compatibility',{}).get('status','see model binding states'),
                'package_runtime_validation':data['capabilities'].get('package_backed_prediction',{}).get('package_runtime_validation','NOT_RUN'),
                'human_approval':data['package'].get('human_physics_approval',data['package'].get('human_approval'))}
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        return {'status':'FAIL','errors':[str(error)],'scope':'schema/semantics only'}
