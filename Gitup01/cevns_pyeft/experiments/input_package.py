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
    errors = []
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


def render_physics(data, arrays):
    """Deterministic contract view; scientific explanation is authored in YAML."""
    if data['package']['schema_version'] == 'cevns-experiment-input/2':
        from .generic_input import render
        return render(data, arrays)
    def cell(value):
        return str(value).replace('|','&#124;').replace('\n',' ')
    def table(headers, rows):
        return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |'] +
                         ['| '+' | '.join(cell(v) for v in row)+' |' for row in rows])
    lines = ['# '+data['package']['experiment']+' — '+data['package']['dataset_id']+' 物理输入', '',
             '> DRAFT / PARTIAL。参数角色、机器验证、Runtime 执行和人工科学接受分别记录。', '',
             '## 身份与权威', '', data['package']['scientific_claim'], '',
             'YAML 是直接标量和模型规格权威；NPZ 是数组权威。derived 只读缓存必须与上游推导一致；materialized_derived_resource 只能在依赖指纹匹配时使用。本文由机器输入渲染，不能独立维护数值。', '',
             '当前运行权威：'+data['legacy_spec']['runtime_authority']+'。数学表达、源码位置和 symbolic_equations 都是审计信息，禁止 eval 或动态导入。', '',
             '## 能力与人工审核', '', table(['能力','已有引擎','就绪状态','旧回归证据','Package Runtime','人工审核','阻断项'],
                 [(k,c['engine_support'],c['readiness'],c['legacy_evidence'],c['package_runtime_validation'],c['human_approval'],c['blocker_refs']) for k,c in data['capabilities'].items()]), '',
             '## 参数及真实消费者', '',
             '每项 value/adopted_value 为当前采用值；原来源值来自项目代码或数据，不等同官方论文原值。派生关系只允许校验器中明列的审计运算，不能自由执行公式。reference_only/unused_snapshot 没有计算消费者、不进入 canonical 数值指纹；旧引擎仍可能因整体代码/元数据哈希变化而失效。', '']
    for group in dict.fromkeys(k.split('.')[0] for k in data['parameters']):
        lines += ['### '+group, '', table(['参数','采用值','来源原值','单位','角色','物理意义','真实消费者（阶段）','指纹范围','来源与状态'],
            [(k,json.dumps(p['value'],ensure_ascii=False),p['original_source_value'],p['unit'],p['role'],p['meaning'],
              '; '.join(c['model_id']+'.'+c['slot']+' ('+c['stage']+')' for c in p['consumers']) or '无计算消费者',
              p['fingerprint_scope'],str(p['source_refs'])+' :: '+p['locator']+'; '+p['extraction_method']+'/'+p['provenance_status']+'; DRAFT/human=false')
             for k,p in data['parameters'].items() if k.startswith(group+'.')]), '']
    lines += ['## 派生量和预计算归一化', '', table(['派生参数','只读推导规格','依赖指纹'],
        [(k,p['derivation']['formula_id']+' '+str(p['derivation']['input_refs']),p['derivation']['dependency_fingerprint'])
         for k,p in data['parameters'].items() if p['role']=='derived']), '',
        'source_fluence_e/source_fluence_mub 是已经含 POT、yield、1/(4πL²) 的物化探测器注量。运行时数组为权威，不得再乘这些因子。上游参数、生成模型版本或坐标变化使数组指纹失效。prompt 线权重使用同一组源参数推导的 F；连续谱表不能被再次乘 F。', '',
        '靶质量分数、单核质量和核数由显式输入只读推导；kg 质量用于核数，GeV 质量用于运动学，折叠的中间每 kg 因子按旧次序恢复。没有额外活时间因子。', '',
        '## 模型公式与物理解释', '']
    for key, model in data['models'].items():
        lines += ['### '+key, '', model['physical_explanation'], '', '```text',model['mathematical_definition'],'```', '',
                  table(['变量','单位（结构化）','定义'],[(v,model['contract']['variable_units'][v],description) for v,description in model['variables'].items()]), '',
                  '输入：'+str(model['inputs'])+'。输出：'+model['output']+'。', '',
                  '实际参数引用：'+str(model['parameter_refs'])+'；模型依赖：'+str(model['depends_on'])+'。', '',
                  '定义域：'+model['domain']+'。', '', '归一化：'+model['normalization']+'。', '',
                  '边界行为：'+model['boundary_behavior']+'。', '',
                  '结构化合同：'+str(model['contract'])+'。', '',
                  '来源：'+str(model['source_refs'])+' :: '+model['locator']+'；'+model['extraction_method']+'/'+model['provenance_status']+'；DRAFT，未人工确认。', '']
    lines += ['## 共同 EFT 数学审计与算符', '',data['interaction']['symbolic_notation'], '',
              table(['内部算符','key','维度','扇区','系数单位','LNV 对角必须为零'],
                    [(o['name'],o['key'],o['dimension'],o['lepton_number'],'GeV^'+str(o['unit_power_GeV']),o['lnv_diagonal_must_vanish']) for o in data['interaction']['supported_operators']]), '']
    for name, equations in data['interaction']['symbolic_equations'].items():
        lines += ['### '+name+'（audit_only，不可执行）', '',table(['左端','数学表达（旧代码记号）','源行'],
                  [(e['lhs'],e['rhs'],e['source_line']) for e in equations]), '']
    edges = arrays[data['observable']['edges_ref']]
    lines += ['## 观测坐标、统计数组与数值设置', '',
              data['observable']['boundary'], '',
              '预测为 events/bin，已含源、核数、效率和接受率；统计输入是 counts/PE。仅对预测除一次箱宽，统计数组不再除宽度；负 residual 保留。', '',
              table(['bin','左边界 PE','右边界 PE','宽度 PE','observed counts/PE','background counts/PE','sigma counts/PE'],
                    [(i+1,lo,hi,hi-lo,arrays[data['statistics']['observed_ref']][i],arrays[data['statistics']['background_ref']][i],arrays[data['statistics']['uncertainty_ref']][i])
                     for i,(lo,hi) in enumerate(zip(edges[:-1],edges[1:]))]), '',
              data['prediction']['error_control'], '',data['prediction']['alternative_bin_probability_path'], '',
              '\n'.join('- '+s for s in data['prediction']['model_graph']), '',
              '## 全部 NPZ 数组', '', '归档 SHA256：`'+data['resources']['sha256']+'`。', '',
              table(['NPZ key','用途','单位','shape','dtype','轴/坐标','角色','归一化/生成'],
                    [(k,r['meaning'],r['unit'],r['shape'],r['dtype'],r['axes'],r['role'],r['normalization']) for k,r in data['resources']['arrays'].items()]), '',
              table(['物化数组','生成参数','生成模型','生成资源','依赖指纹'],
                    [(k,r['generation']['parameter_refs'],r['generation']['model_refs'],r['generation']['resource_refs'],r['generation']['dependency_fingerprint'])
                     for k,r in data['resources']['arrays'].items() if r['generation']]), '',
              '数值数组保留原精度和顺序，可用 allow_pickle=False 读取。SigmaPDelta 未打包，因为旧粒子响应为零；没有添加协方差或 ROOTTime。', '',
              '## 来源与缺失/冲突', '', table(['来源ID','相对路径','SHA256','来源种类','独立官方核实'],
                    [(k,s['path'],s['sha256'],s['kind'],s['independently_officially_verified']) for k,s in data['provenance']['sources'].items()]), '',
              table(['问题','状态','内容','影响能力','所需材料'],[(i['id'],i['status'],i['detail'],i['blocks'],i['needed']) for i in data['provenance']['issues']]), '',
              '## 历史 spec 与迁移边界', '',json.dumps(data['legacy_spec'],ensure_ascii=False,indent=2), '',
              '旧 experiment.yaml 为兼容说明；运行权威见上表。新包不继承旧 fast_validated 或官方统计批准。Schema、模型绑定、消费、Runtime 和人工科学接受分别记录；技术证据声明不等于校验器重跑了相关计算。', '']
    return '\n'.join(lines)


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
        return {'status':'FAIL' if errors else 'PASS','errors':errors,'schema_version':data['package']['schema_version'],
                'parameter_roles':dict(Counter(p['role'] for p in data['parameters'].values())),
                'models':len(data['models']),'parameters':len(data['parameters']),'arrays':len(arrays),
                'runtime_binding':data.get('engine_compatibility',{}).get('status','see model binding states'),
                'package_runtime_validation':data['capabilities'].get('package_backed_prediction',{}).get('package_runtime_validation','NOT_RUN'),
                'human_approval':data['package'].get('human_physics_approval',data['package'].get('human_approval'))}
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        return {'status':'FAIL','errors':[str(error)],'scope':'schema/semantics only'}
