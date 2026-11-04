"""One-dataset extraction/render/check tool; never a runtime package loader.

Default/--check is read-only. --write creates the three pilot files and report,
refusing every existing destination. JSON syntax is a YAML 1.2 subset, so the
pilot does not add a YAML parser dependency. Formula strings are never evaluated.
"""
from __future__ import annotations

import argparse
import ast
from copy import deepcopy
from dataclasses import asdict
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATASET = Path('data/experiments/COHERENT_CsI/CsI2021')
HEAD = '520e1d0a33913a6793b326ed493f5b66e0004a0a'
BRANCH = 'refactor/07-gitup01-20261104'
REPORT = Path('docs/CSI2021_ONBOARDING_PILOT_REPORT.md')
CHANNELS = ('M', 'SigmaPP', 'SigmaP', 'PhiPP', 'PhiPT', 'Delta', 'MPhiPP')
SOURCE_PATHS = {
    'definition': 'cevns_pyeft/experiments/coherent/csi2021_definition.py',
    'assembly': 'cevns_pyeft/experiments/coherent/execution.py',
    'source': 'cevns_pyeft/experiments/coherent/sns.py',
    'source_adapter': 'cevns_pyeft/sources/sns.py',
    'detector_defaults': 'cevns_pyeft/detectors/legacy_parameters.py',
    'detector': 'cevns_pyeft/detectors/csi2021.py',
    'differential': 'cevns_pyeft/rates/differential.py',
    'targets': 'cevns_pyeft/targets/materials.py',
    'recipes': 'cevns_pyeft/targets/recipes.py',
    'constants': 'cevns_pyeft/foundation/constants.py',
    'lecs': 'cevns_pyeft/theory/li2026/lec.py',
    'operators': 'cevns_pyeft/theory/li2026/operators.py',
    'matching': 'cevns_pyeft/theory/li2026/left_to_ci.py',
    'particle_response': 'cevns_pyeft/theory/li2026/responses.py',
    'amplitude': 'cevns_pyeft/theory/li2026/amplitude.py',
    'cross_section': 'cevns_pyeft/theory/li2026/cross_section.py',
    'kinematics': 'cevns_pyeft/theory/kinematics.py',
    'response_reader': 'cevns_pyeft/nuclear/response.py',
    'response_data': 'data/responses/responses_all.json',
    'numerics': 'cevns_pyeft/contracts/parameters.py',
    'prediction': 'cevns_pyeft/core/predict.py',
    'recoil': 'cevns_pyeft/rates/recoil.py',
    'folding': 'cevns_pyeft/rates/folding.py',
    'statistics_binding': 'cevns_pyeft/experiments/coherent/statistics_binding.py',
    'profiling': 'cevns_pyeft/statistics/profiling.py',
    'statistics_provenance': 'data/experiments/COHERENT_CsI/CsI2021/statistics/provenance.yaml',
    'old_spec': 'data/experiments/COHERENT_CsI/CsI2021/experiment.yaml',
    'schema': 'workflows/_shared/schemas/experiment-input/experiment.schema.json',
    'input_standard': 'workflows/_shared/INPUT_STANDARD.md',
    'antinu_audit': 'docs/physics/physics-audits/antineutrino_sign_helicity_audit.md',
    'nuclear_audit': 'docs/physics/nuclear-responses/nuclear_response_convention_audit.md',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def npz_bytes(arrays):
    """Fixed ZIP timestamps and uncompressed NPY retain exact numeric precision."""
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
        for key, value in sorted(arrays.items()):
            payload = io.BytesIO()
            np.save(payload, value, allow_pickle=False)
            info = zipfile.ZipInfo(key + '.npy', date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o600 << 16
            archive.writestr(info, payload.getvalue())
    return stream.getvalue()


def symbolic_equations():
    """Extract mathematical assignments, not executable algorithms or callables."""
    results = {}
    for sid, function in (('matching', 'left_to_ci'), ('particle_response', '_response_polynomials')):
        tree = ast.parse((ROOT / SOURCE_PATHS[sid]).read_text(encoding='utf-8'))
        owner = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
        equations = []
        for node in owner.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            lhs = ast.unparse(node.targets[0])
            selected = lhs.startswith(('cp[', 'cn[')) if sid == 'matching' else lhs.startswith(('R_', 'b', 's', 'a'))
            if selected and (sid == 'matching' or lhs not in ('basis',)):
                rhs = ast.unparse(node.value)
                # No control flow or function implementations are shipped.
                equations.append({'lhs': lhs, 'rhs': rhs, 'source_line': node.lineno})
        results[sid] = equations
    return results


def extract():
    from cevns_pyeft.experiments.loader import load_experiment, ResourceCatalog
    from cevns_pyeft.experiments.specs import validate_experiment_spec_data
    from cevns_pyeft.foundation import constants as c
    from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS
    from cevns_pyeft.theory.li2026.operators import LI2026_OPERATOR_SPECS
    from cevns_pyeft.experiments.coherent.sns import build_neutrino_empirical_flux_sns, sns_component_state
    from cevns_pyeft.contracts import IntegrationSettings
    import scipy

    exp = load_experiment('CsI2021', resources=ResourceCatalog(ROOT))
    d, physical = exp.definition, exp.definition.physical
    run = physical.run
    fluence = exp.model.source.for_run(exp.model.run)
    source = build_neutrino_empirical_flux_sns(run.legacy_dataset(d.dataset_id),
                                              num_points=run.num_points, use_interpolation=run.interpolation)
    response = json.loads(exp.resolved_resources['responses'].read_text(encoding='utf-8'))
    params, models, arrays, resources = {}, {}, {}, {}

    def p(key, value, unit, meaning, sid, locator, *, derived=False, derivation=None, original=None):
        if isinstance(value, np.generic):
            value = value.item()
        params[key] = dict(value=value, unit=unit, meaning=meaning,
                           original_source_value=None if derived else value if original is None else original,
                           adopted_value=value, source_refs=[sid], locator=locator,
                           extraction_method='project-derived' if derived else 'legacy-code-derived',
                           provenance_status='PROJECT_DERIVED' if derived else 'SOURCE_EXTRACTED',
                           source_kind='project_derivation' if derived else 'current_project_implementation',
                           converted=derived, derivation=derivation,
                           human_confirmed=False, decision_status='DRAFT', conflict_refs=[])

    def a(key, value, unit, meaning, axes, sid, locator, normalization):
        array = np.asarray(value)
        if array.dtype.hasobject:
            raise ValueError('object arrays forbidden')
        arrays[key] = array
        resources[key] = dict(key=key, meaning=meaning, unit=unit, shape=list(array.shape), dtype=str(array.dtype),
                              axes=axes, coordinate_convention='axes ordered as listed; no sorting or rebinning',
                              normalization=normalization, source_refs=[sid], locator=locator,
                              provenance_status='SOURCE_EXTRACTED', extraction_method='legacy-code-derived',
                              decision_status='DRAFT', human_confirmed=False,
                              sha256_raw_c_order=sha(np.ascontiguousarray(array).tobytes()))

    def m(key, group, formula, explanation, variables, inputs, output, refs, dependencies, sid, locator,
          domain, normalization, boundary):
        models[key] = dict(model_id=key, model_type=group, mathematical_definition=formula,
                           physical_explanation=explanation, variables=variables, inputs=inputs, output=output,
                           parameter_refs=refs, depends_on=dependencies, source_refs=[sid], locator=locator,
                           domain=domain, normalization=normalization, boundary_behavior=boundary,
                           provenance_status='SOURCE_EXTRACTED', extraction_method='legacy-code-derived',
                           decision_status='DRAFT', human_confirmed=False, implementation_owner='existing_engine')

    p('source.baseline_m', run.baseline_m, 'm', '源到探测器距离；几何稀释只在注量中施加。', 'definition', 'CsI2021Settings.run')
    p('source.total_pot', run.total_pot, 'POT', '本运行累计 POT；已经承载时间积分。', 'definition', 'CsI2021Settings.run')
    p('source.yield_per_pot', run.yield_per_pot, 'neutrinos/species/POT', '每种 SNS 分量的发射数系数。', 'definition', 'CsI2021Settings.run')
    for key, val in zip(('tabulation_min', 'tabulation_max'), run.energy_tabulation):
        p('source.' + key, val, 'MeV', 'SNS 线性插值表端点；不是积分端点。', 'definition', 'SNSRun.energy_tabulation')
    for key, val in zip(('mask_min', 'mask_max'), run.node_support):
        p('source.' + key, val, 'MeV', '仅在生成表格节点时使用的旧程序掩码。', 'definition', 'SNSRun.node_support')
    p('source.tabulation_nodes', run.num_points, '1', 'SNS 等间距表节点数，含两端。', 'definition', 'SNSRun.num_points')
    p('source.interpolation', run.interpolation, 'boolean', '采用线性插值的旧复现设置。', 'definition', 'SNSRun.interpolation')
    p('source.fluence_per_species', source['basic']['NTimeIntegratedFlux_cm^-2'], 'cm^-2', '每种分量的积分注量权重；连续谱未重新归一化。', 'source', '_n_time_integrated_flux_cm2', derived=True,
      derivation='yield_per_pot * total_pot / (4*pi*(100*baseline_m)^2)')
    line = fluence.components[0].lines[0]
    p('source.prompt_energy', line.energy_MeV, 'MeV', '静止带电 pion 两体衰变的 prompt νμ 能量。', 'source', 'build_neutrino_empirical_flux_sns:E0', derived=True,
      derivation='1000*(m_pi_charged^2-m_mu^2)/(2*m_pi_charged)')
    p('source.integration_min', fluence.components[0].support.integration_domain_MeV[0], 'MeV', '连续谱积分网格下限；零能节点不送入截面。', 'source_adapter', 'SNSLegacySource.for_run')
    p('source.integration_max', fluence.components[0].support.integration_domain_MeV[1], 'MeV', '包含电子质量的 muon DAR 积分上限。', 'differential', 'emax_muon_dar_mev', derived=True,
      derivation='1000*(m_mu^2-m_e^2)/(2*m_mu)')
    p('target.detector_mass', physical.mass_kg, 'kg', '探测器总质量，只用于构造核数。', 'definition', 'CsI2021Settings.mass_kg')
    p('target.run_mass_metadata', run.mass_metadata_kg, 'kg', '旧源配置中的质量元数据；实际 SNSSource 组装传零，不参与注量。', 'definition', 'CsI2021Settings.run.mass_metadata_kg')
    p('target.atomic_mass_kg', physical.atomic_mass_kg, 'kg', '旧程序核数换算的原子质量常数。', 'recipes', 'LEGACY_ATOMIC_MASS_KG')
    for isotope, response_key, mass_number in physical.targets:
        nuclear = response['nuclei'][response_key]
        inventory = next(t for t in exp.model.targets.isotopes if t.isotope_id == isotope)
        for field in ('A', 'Z', 'N', 'J', 'T', 'b'):
            p(f'target.{isotope}.{field}', nuclear['basic'][field], 'GeV^-1' if field == 'b' else '1',
              {'A':'质量数', 'Z':'质子数', 'N':'中子数', 'J':'核自旋', 'T':'源表记录的同位旋', 'b':'谐振子长度；用于 y=(qb/2)^2'}[field],
              'response_data', f'nuclei/{response_key}/basic/{field}')
        p(f'target.{isotope}.isotopic_fraction', 1.0, '1', '被建模元素中的同位素占比为一；实际材料丰度测量来源未登记。', 'assembly', 'assemble_csi2021:single isotope per element')
        p(f'target.{isotope}.mass_fraction', mass_number/sum(t[2] for t in physical.targets), '1', 'Cs:I=1:1 化学计量转成质量分数。', 'assembly', 'assemble_csi2021', derived=True, derivation='A_i/(A_Cs+A_I)')
        for field, val, unit, why in (
            ('mass_GeV', inventory.kinematic_mass_GeV, 'GeV', '弹性运动学的 A*AMU_GEV 近似质量。'),
            ('mass_kg', inventory.nucleus_mass_kg, 'kg', '核数换算的 A*atomic_mass_kg 质量。'),
            ('nuclei', inventory.number_of_nuclei, 'nuclei', '实际参与计算的靶核数。')):
            p(f'target.{isotope}.{field}', val, unit, why, 'assembly', 'assemble_csi2021', derived=True,
              derivation={'mass_GeV':'A_i*AMU_GEV', 'mass_kg':'A_i*atomic_mass_kg', 'nuclei':'detector_mass*mass_fraction_i/mass_kg_i'}[field])
        p(f'nuclear.{isotope}.exp_factor', nuclear['exp_factor'], '1', '所有该核响应多项式共用的指数因子。', 'response_data', f'nuclei/{response_key}/exp_factor')
        for channel in CHANNELS:
            a(f'nuclear_{isotope}_{channel}', np.asarray(nuclear['responses'][channel], dtype=np.float64), '1',
              f'{isotope} 的 {channel} 核响应多项式系数；升幂顺序。',
              [{'name':'nucleon_left','values':['p','n']}, {'name':'nucleon_right','values':['p','n']},
               {'name':'polynomial_power','rule':'0..shape[-1]-1'}], 'response_data', f'nuclei/{response_key}/responses/{channel}',
              'W_ab(y)=exp(exp_factor*y)*sum_k coefficients[a,b,k]*y^k; preserve np source normalization')
    p('interaction.include_sm', True, 'boolean', '缺省 TheoryPoint 加入 SM 系数。', 'numerics', 'TheoryPoint.include_sm')
    p('interaction.sin2thetaW', d.reproduction_sin2thetaW, '1', '实验复现入口显式给定的弱混合角平方。', 'definition', 'ExperimentDefinition.reproduction_sin2thetaW')
    for name, unit, meaning in (
        ('G_F','GeV^-2','Fermi 常数'), ('alpha_em','1','精细结构常数'), ('m_mu','GeV','muon 质量'),
        ('m_e','GeV','电子质量'), ('m_pi_charged','GeV','带电 pion 质量'), ('AMU_GEV','GeV','运动学原子质量常数'),
        ('GEV_INV2_TO_CM2','cm^2/GeV^-2','自然单位截面转换因子')):
        p('constants.' + name, float(getattr(c, name)), unit, meaning + '；记录当前公共常数版本的实际值。', 'constants', name)
    lecs = asdict(DEFAULT_LECS)
    for name, val in lecs.items():
        unit = 'GeV^2' if name.startswith('B0_') else '1' if name in ('g_A','Sigma_ud','L1','L2','L3','L4','g5','g6','g7','g8','g9') else 'GeV'
        if name.startswith('B0_'):
            meaning = '手征常数 B0 与轻夸克质量的乘积，控制 c10 的 pion-pole 项；不是 B0 本身。'
        elif name.startswith('sigma_'):
            meaning = '核子中指定轻夸克的标量 sigma term，进入维七标量算符到 c3 的匹配。'
        elif name.startswith('L'):
            index = int(name[1:])
            meaning = ({1:'矢量/磁型匹配常数，进入 c6 与 dipole c12。', 2:'同位旋交叉矢量/磁型匹配常数，进入 c6。',
                        3:'核子轴矢匹配常数，进入 c2/c7。', 4:'轴矢同位旋混合匹配常数，进入 c2/c7。',
                        5:'LNV tensor 型匹配常数，进入 c4/c8/c9。', 6:'LNV tensor 型同位旋交叉常数，进入 c4/c8/c9。',
                        7:'LNV tensor 型附加匹配常数，进入 c9。', 8:'LNV tensor 型同位旋交叉附加常数，进入 c9。',
                        9:'公共理论版本保留的 LEC，当前 matching 不消费。', 10:'公共理论版本保留的 LEC，当前 matching 不消费。',
                        11:'轻夸克 pseudoscalar 的局域匹配常数，进入 c10。', 12:'轻夸克 pseudoscalar 的同位旋交叉局域常数，进入 c10。',
                        13:'gluonic scalar 算符匹配到 c3 的常数。', 14:'gluonic pseudoscalar 算符匹配到 c10 的常数。'})[index]
        elif name.startswith('g') and name[1:].isdigit():
            meaning = {'g1':'维七矢量算符到 c1 的直接匹配常数。', 'g2':'维七矢量算符到 c1 的同位旋交叉匹配常数。',
                       'g3':'维七轴矢算符到 c11 的直接匹配常数。', 'g4':'维七轴矢算符到 c11 的同位旋交叉匹配常数。',
                       'g5':'维八导数算符到 c13 的直接匹配常数。', 'g6':'维八导数算符到 c13 的同位旋交叉匹配常数。',
                       'g7':'维八轴矢导数算符到 c14 的直接匹配常数。', 'g8':'维八轴矢导数算符到 c14 的同位旋交叉匹配常数。',
                       'g9':'维八 gluonic 算符到 c13 的匹配常数。'}[name]
        else:
            meaning = {'g_A':'核子轴矢耦合，进入 c10 的 pion-pole 项。', 'Sigma_ud':'公共理论版本的轻夸克组合常数。',
                       'm_u':'公共理论版本的 up 夸克质量。', 'm_d':'公共理论版本的 down 夸克质量。',
                       'm_pi':'pion-pole 分母所用的带电 pion 质量。', 'm_N':'核子平均质量，进入粒子响应与 dipole/pion-pole 匹配。'}[name]
        if name in ('L9','L10','m_u','m_d','Sigma_ud'):
            meaning += ' 当前 matching 公式未直接使用，保留公共版本快照身份。'
        p('lecs.' + name, val, unit, meaning, 'lecs', 'Li2026LECs.' + name)
    for i, val in enumerate(physical.quenching):
        p(f'detector.quenching_q{i+1}', val, '1' if i == 0 else f'MeV^-{i}', f'按一至四次幂顺序的 quenching 系数 q{i+1}；输入数值以 MeVnr 表示。', 'detector_defaults', 'CsIResponseDefaults.quenching')
    p('detector.gamma_a', physical.gamma_a, 'keVee/PE', 'Gamma 参数 a0；均值 PE=Eee/a0。', 'detector_defaults', 'CsIResponseDefaults.gamma_a')
    p('detector.gamma_b', physical.gamma_b, 'keVee^-1', 'Gamma 参数 b0；shape=1+b0*Eee。', 'detector_defaults', 'CsIResponseDefaults.gamma_b')
    for name, val, unit in zip(('a','b','c','d'), physical.efficiency, ('1','PE^-1','PE','1')):
        p('detector.efficiency_' + name, val, unit,
          {'a':'logistic 振幅','b':'logistic 陡度','c':'logistic 中心','d':'logistic 常数偏移'}[name],
          'detector_defaults', 'CsIResponseDefaults.efficiency:(a,b,c,d)')
    for name, val in physical.acceptance:
        p('detector.acceptance_' + name, val, '1', '源分量选择接受率；在 PE 折叠后施加一次。', 'detector_defaults', 'CSI_COMPONENT_ACCEPTANCE')
    ns = IntegrationSettings.legacy_csi2021_v1(**dict(d.numerical_profiles['slow']))
    for name, val in asdict(ns).items():
        if name == 'strategy':
            continue
        p('numerics.' + name, val, 'keV' if name == 'recoil_min_keV' else 'PE' if name == 'observed_step' else '1',
          {'n_er':'每核素反冲网格节点数；线性且含端点。', 'n_enu':'连续谱能量网格节点数；各反冲只保留运动学允许节点。',
           'n_observed_bin':'每 PE bin 子网格节点数；含端点。', 'observed_step':'先采样 PE 密度的等间距步长。',
           'recoil_min_keV':'实际反冲网格下限。'}[name], 'numerics', 'IntegrationSettings/' + name)
    p('statistics.sigma_alpha', d.statistics.signal_sigma, '1', '信号归一化 Gaussian pull 的宽度。', 'definition', 'StatisticsDefinition.signal_sigma')
    p('statistics.sigma_beta', d.statistics.background_sigma, '1', '背景归一化 Gaussian pull 的宽度。', 'definition', 'StatisticsDefinition.background_sigma')
    p('statistics.sigma_floor', 1e-12, 'counts/PE', '对逐箱误差的下限裁剪；当前输入均大于下限。', 'profiling', 'profile_gaussian_two_pull:sig')
    grid = np.linspace(*run.energy_tabulation, run.num_points)
    a('source_energy_MeV', grid, 'MeV', 'SNS 插值表的完整节点坐标，保留掩码外零节点。', [{'name':'source_table_node','rule':'increasing; includes both endpoints'}], 'source', 'build_neutrino_empirical_flux_sns:grid', 'coordinate only')
    for flavor in ('e','mub'):
        a('source_fluence_' + flavor, source['measured'][flavor](grid), 'cm^-2 MeV^-1', '当前运行的 delayed ' + flavor + ' 插值表节点注量。', [{'name':'source_table_node','coordinate_ref':'source_energy_MeV'}], 'source', 'build_neutrino_empirical_flux_sns:phi_' + flavor,
          'includes POT, yield and 1/(4*pi*L^2); excludes target nuclei, efficiency and acceptance; bound to declared source parameters')
    for flavor in ('e','mu'):
        a('state_rho_' + flavor, sns_component_state(flavor).rho, '1', '固定纯味密度矩阵 ' + flavor + '；mu 与 mub 共用 rho_mu，粒子标签不同。',
          [{'name':'flavor_row','values':['e','mu','tau']}, {'name':'flavor_column','values':['e','mu','tau']}], 'source', 'sns_component_state', 'Hermitian PSD; trace=1')
    a('observable_pe_edges', np.asarray(d.observation.edges, dtype=np.float64), 'PE', '九箱的十条精确边界。', [{'name':'edge_index','rule':'ascending edge order'}], 'definition', 'ObservationDefinition.edges', 'coordinate only; no background or exposure')
    for field in ('observed','background','uncertainty'):
        a('statistics_' + field, np.asarray(getattr(d.statistics, field), dtype=np.float64), 'counts/PE',
          {'observed':'旧 residual/excess 观测数组，末箱负值保留；背景扣除细节待官方证据。', 'background':'旧 BRN+NIN 背景数组；实际 χ² 在信号之外加入该项。', 'uncertainty':'逐箱对称 Gaussian 一标准差；不含额外协方差矩阵。'}[field],
          [{'name':'pe_bin','edges_ref':'observable_pe_edges','order':'ascending PE'}], 'definition', 'StatisticsDefinition.' + field, 'already per PE width; never divide this array by width again')

    m('sns_fluence_legacy_v1','source', 'F=r*N_POT/(4*pi*L_cm^2); L_cm=100*L_m',
      '静止 pion 源用球面几何因子将每 POT 的每种产额转成探测器注量。该因子已经积分整个运行时间。',
      {'F':'cm^-2; per-species integrated fluence','r':'neutrinos/species/POT','N_POT':'POT','L_m':'m','L_cm':'cm'},
      ['source.total_pot','source.yield_per_pot','source.baseline_m'], 'F [cm^-2]',
      ['source.total_pot','source.yield_per_pot','source.baseline_m','source.fluence_per_species'], [], 'source', '_n_time_integrated_flux_cm2', 'positive baseline; nonnegative POT/yield', 'per source component once', 'no live-time or target-mass multiplier')
    m('sns_michel_tabulation_legacy_v1','source', 'f_e(E)=192*E^2*(1/2-E/m_mu)/m_mu^3; f_mub(E)=64*E^2*(3/4-E/m_mu)/m_mu^3; table_l=F*max(f_l(E_j),0)*1_mask(E_j); phi_l(E)=linear_interp(E_j,table_lj)',
      'delayed νe 与反νμ 的 Michel 形状先在完整等间距表上计算、裁剪并掩码，再线性插值。不是每个查询点都重新施加物理端点截断。',
      {'E':'MeV; neutrino energy','m_mu':'MeV; 1000*constants.m_mu','E_j':'MeV; source_energy_MeV','F':'cm^-2','phi_l':'cm^-2 MeV^-1','f_l':'MeV^-1','mask':'source.mask_min <= E_j <= source.mask_max'},
      ['source_energy_MeV','source_fluence_e','source_fluence_mub'], 'phi_e,phi_mub [cm^-2 MeV^-1]',
      [k for k in params if k.startswith('source.') and k not in ('source.prompt_energy',)] + ['constants.m_mu'], ['sns_fluence_legacy_v1'], 'source', 'build_neutrino_empirical_flux_sns',
      'integration uses declared DAR domain; table and mask domains are separately declared', 'no re-normalization of clipped/interpolated table to F; analytic Michel functions integrate to 1 only on massless-electron ideal domain', 'linear interpolation; table-outside zero; final interpolation cell taper preserved')
    m('sns_prompt_line_v1','source', 'E0=(m_pi^2-m_mu^2)/(2*m_pi); phi_mu(E)=F*delta(E-E0)',
      '静止带电 pion 衰变产生 prompt νμ 谱线；积分直接加谱线权重乘截面。',
      {'E0':'GeV in formula; converted to MeV','m_pi':'GeV; charged pion mass','m_mu':'GeV','F':'cm^-2','delta':'inverse-energy Dirac distribution'},
      ['constants.m_pi_charged','constants.m_mu','source.fluence_per_species'], 'line energy [MeV], weight [cm^-2]',
      ['source.prompt_energy','source.fluence_per_species','constants.m_pi_charged','constants.m_mu'], ['sns_fluence_legacy_v1'], 'source', 'build_neutrino_empirical_flux_sns:muLine', 'stationary two-body pion decay', 'F once; no continuum prompt contribution', 'contributes iff E0 >= E_min(T)')
    m('sns_fixed_state_v1','source', 'rho_e=|e><e|; rho_mu=|mu><mu|; prompt=(nu,rho_mu); delayed_e=(nu,rho_e); delayed_mub=(antinu,rho_mu)',
      '固定纯味入射态，无传播或随能量变化；particle_kind 单独保存。',
      {'rho_e':'dimensionless 3x3 matrix','rho_mu':'dimensionless 3x3 matrix','flavor_order':'e,mu,tau'},
      ['state_rho_e','state_rho_mu'], 'incident density and particle label', [], [], 'source', 'sns_component_state', 'constant state only', 'trace(rho)=1', 'state parameters rejected; antinu tag does not alter current kernel')
    m('csi_target_inventory_v1','target', 'w_i=A_i/(A_Cs+A_I); m_i_kg=A_i*u_kg; m_i_GeV=A_i*u_GeV; N_i=Mdet*w_i/m_i_kg',
      '每个 CsI 化学式单元各含一个 Cs 和 I，质量分数不同而核数相等。动力学质量与核数质量采用各自显式常数。',
      {'w_i':'1; mass fraction','A_i':'1; isotope mass number','u_kg':'kg','u_GeV':'GeV','Mdet':'kg','m_i_kg':'kg','m_i_GeV':'GeV','N_i':'nuclei'},
      ['target.detector_mass','target.atomic_mass_kg','constants.AMU_GEV'], 'isotope inventory with true nucleus counts',
      [k for k in params if k.startswith('target.')] + ['constants.AMU_GEV'], [], 'assembly', 'assemble_csi2021; inventory_from_mass_fractions', 'Cs133/I127 only; equal Cs:I stoichiometry; no explicit Na dopant model', 'sum_i N_i*m_i=Mdet; source does not contain nuclei or mass', 'zero detector mass gives zero counts')
    m('li2026_sm_left_v1','interaction', 'P=-G_F/sqrt(2); C6u1_SM=P*(1-8*s2/3)*I3; C6d1_SM=-P*(1-4*s2/3)*I3; C6u2_SM=-P*I3; C6d2_SM=P*I3; C_total=C_BSM+C_SM',
      'SM 以四个维六 LEFT 系数加入通用 EFT 参数；零 BSM 是缺省参数点而非缺失占位。',
      {'P':'GeV^-2','G_F':'GeV^-2','s2':'sin^2(theta_W), dimensionless','I3':'3x3 flavor identity','C_BSM':'GeV^(4-d), 3x3 final-row/initial-column matrix'},
      ['interaction.include_sm','interaction.sin2thetaW'], 'total LEFT Wilson coefficient matrices', ['interaction.include_sm','interaction.sin2thetaW','constants.G_F'], [], 'differential', '_sm_left_dim6', '22 supported operators; default BSM mapping empty', 'no flux or target factor in Wilson coefficients', 'unknown operators rejected; LNV diagonal constrained to zero by engine')
    m('li2026_matching_v1','interaction', 'c_i^N=sum_o M_io^N(Ebar,q2,LECs)*C_o; Ebar=E-q0/2; c10_ud_p=B0_m_u*C7u5-B0_m_d*C7d5; c10_ud_n=-c10_ud_p; c_i^0=(cp_i+cn_i)/2; c_i^1=(cp_i-cn_i)/2',
      '通用引擎把 LEFT 矩阵匹配成质子/中子非相对论系数。完整线性表达式在本包 symbolic_equations.matching 中保存为数学审计定义。',
      {'c_i^N':'GeV^-2 for i=1..12; GeV^-3 for i=13,14','C_o':'GeV^(4-d), final-row/initial-column','M_io^N':'matching linear map, implied unit GeV^(d-6) or GeV^(d-7)','Ebar':'GeV','q0':'GeV; recoil','q2':'GeV^2; signed Lorentz transfer','LECs':'parameter registry lecs.*'},
      ['LEFT coefficients','kinematics','lecs.*'], 'cp[1..14], cn[1..14]', [k for k in params if k.startswith('lecs.')] + ['constants.alpha_em'], ['li2026_sm_left_v1','elastic_kinematics_v1'], 'matching', 'left_to_ci:c10_mass_mode=quark_mass_resolved', 'one-body current Li2026 proof convention; no SMEFT running pipeline', 'np basis; LNC/LNV interference forbidden downstream', 'safe_ratio(n,q2)=0 when abs(q2)<=1e-30; safe_pion(n)=0 when abs(m_pi^2-q2)<=1e-30; this is a legacy numerical prescription')
    m('elastic_kinematics_v1','interaction', 'Tmax(E)=2*E^2/(mA+2*E); Emin(T)=(T+sqrt(T^2+2*mA*T))/2; q0=T; qabs^2=2*mA*T; q2=T^2-qabs^2; y=(qabs*b/2)^2',
      '两体弹性散射的精确支撑决定连续积分中保留的节点。核响应使用三动量模，匹配使用带符号四动量转移。',
      {'T':'GeV (input recoil keV multiplied by 1e-6)','E':'GeV (input MeV multiplied by 1e-3)','mA':'GeV','q0':'GeV','qabs':'GeV','q2':'GeV^2','b':'GeV^-1','y':'1'},
      ['target kinematic masses','recoil','energy'], 'thresholds, momentum and dimensionless y',
      [k for k in params if k.endswith(('.mass_GeV','.b'))], [], 'kinematics', 'two_body_recoil_max_GeV; minimum_neutrino_energy_GeV', 'T>=0; E>0', 'no normalization factor', 'T>Tmax gives zero; negative recoil/nonfinite inputs rejected')
    m('nuclear_np_polynomial_v1','interaction', 'W_X,ab(y)=exp(e_i*y)*sum_k w_X,ab,k*y^k; a,b in (p,n)',
      '核结构响应矩阵按质子/中子排列。系数以最高保留精度打包；没有额外除以核自旋或 4π。M 为相干密度，Sigma 为纵/横自旋，Phi 为自旋轨道类，Delta 为轨道类，MPhiPP 为干涉。',
      {'W_X':'dimensionless 2x2 nuclear response','w_X,ab,k':'dimensionless polynomial coefficient','e_i':'1; isotope exponential factor','y':'1','k':'nonnegative integer power'},
      ['nuclear_* arrays','target.*.b'], 'W_X matrices [1]', [k for k in params if k.startswith('nuclear.') or k.endswith('.b')], ['elastic_kinematics_v1'], 'response_reader', 'ResponseW.W_np', 'current tabulated polynomial model; no independently documented validity range', 'source normalization preserved; M(0) internal checks do not prove external source convention', 'SigmaPDelta table excluded: corresponding particle response is identically zero')
    m('li2026_R_W_kernel_v1','interaction', 'B_ij^ab=(c_i^a)^dagger*c_j^b; S_ij=B_ij+B_ji; A_ij=B_ij-B_ji; K=sum_X,sum_ab R_X^ab*W_X^ab; MPhiPP contribution=(V+V^dagger)/2; R_SigmaPDelta=0',
      '粒子响应 R 与核响应 W 收缩为入射味空间的 Hermitian 振幅核 K。R 的多项式表达式列于 symbolic_equations.particle_response；同扇区内才允许干涉。',
      {'B_ij':'ordered matrix bilinear','S_ij':'symmetric bilinear','A_ij':'antisymmetric bilinear','c_i^a':'NR flavor coefficient matrix','R_X':'GeV^-2, flavor 3x3 and nucleon 2x2','W_X':'1, nucleon 2x2','K':'GeV^-2, flavor 3x3','V':'MPhiPP unhermitianized 3x3 contribution'},
      ['matched coefficients','nuclear matrices'], 'K [GeV^-2]', [], ['li2026_matching_v1','nuclear_np_polynomial_v1'], 'amplitude', 'flavor_kernel_onebody_li2026', 'one-body current operator sectors; constant SNS states for Fast', 'no implicit 4*pi, spin-average, flux, exposure or target count added', 'Hermiticity/positivity checked by engine; antinu uses same kernel, audit open')
    m('li2026_dsigma_v1','interaction', 'd_sigma/dT_keV=Tr(rho*K)*mA/(8*pi*E^2)*GEV_INV2_TO_CM2*1e-6',
      '先将味核与入射密度矩阵收缩，再乘相空间因子及 GeV 到 cm² 和每 keV 的单位转换。',
      {'rho':'dimensionless 3x3 density','K':'GeV^-2','mA':'GeV','E':'GeV','GEV_INV2_TO_CM2':'cm^2 per GeV^-2','T_keV':'keV'},
      ['K','incident state','energy'], 'cm^2/keV', ['constants.GEV_INV2_TO_CM2'], ['li2026_R_W_kernel_v1','sns_fixed_state_v1'], 'cross_section', 'amplitude_kernel_to_dsigma_cm2_per_GeV; units.cm2_per_GeV_to_cm2_per_keV', 'elastic support only', 'per nucleus; no source/efficiency/exposure factors', 'zero outside elastic support or at rates-grid E=0')
    m('csi_quenching_legacy_v1','detector', 't=T_keV*1e-3; Eee_keV=1e3*(q1*t+q2*t^2+q3*t^3+q4*t^4)',
      '真实核反冲映射成电子等效能量；四个系数的顺序固定。这里没有另乘一组光产额参数。',
      {'T_keV':'keVnr','t':'MeVnr','Eee_keV':'keVee','q1':'1','q2':'MeV^-1','q3':'MeV^-2','q4':'MeV^-3'},
      ['recoil'], 'electron-equivalent energy [keVee]', [f'detector.quenching_q{i}' for i in range(1,5)], [], 'differential', 'eee_quenching_csi', 'actual sampled recoil range from declared grid; official calibration range missing', 'energy conversion only', 'nonpositive Eee causes response density zero')
    m('legacy_csi_gamma','detector', 'a=a0/Eee; b=b0*Eee; k=1+b; lambda=a*(1+b); p(x|T)=lambda^k/Gamma(k)*x^(k-1)*exp(-lambda*x); mean=k/lambda=Eee/a0; variance=k/lambda^2',
      'Gamma 用 shape-rate 参数化：k 是 shape，lambda 是 rate，scale=1/lambda。它表示 PE 的条件密度而非 bin 概率。',
      {'Eee':'keVee','a0':'keVee/PE','b0':'keVee^-1','a':'PE^-1','b':'1','k':'1; shape','lambda':'PE^-1; rate','x':'PE','p':'PE^-1','mean':'PE','variance':'PE^2'},
      ['electron-equivalent energy','observed PE'], 'response density [PE^-1]', ['detector.gamma_a','detector.gamma_b'], ['csi_quenching_legacy_v1'], 'differential', 'p_smearing_csi', 'Eee>0 and x>0', 'integral over x in (0,infinity)=1; not renormalized to analysis window', 'x<=0 or Eee<=0 gives zero; log evaluation uses max(x,1e-300)')
    m('csi2021_logistic_legacy','detector', 'epsilon(x)=max(a/(1+exp(-b*(x-c)))+d,0)',
      '重建 PE 上的选择效率，参数按 (a,b,c,d) 顺序。实现只有零下限，不能擅自改成双边裁剪。',
      {'x':'PE','a':'1; amplitude','b':'PE^-1; slope','c':'PE; center','d':'1; offset','epsilon':'1; efficiency'},
      ['observed PE'], 'efficiency [1]', ['detector.efficiency_' + k for k in ('a','b','c','d')], [], 'detector', 'efficiency_csi2021', 'sampled analysis window', 'dimensionless; applied after interpolation in current Slow strategy', 'lower-clamped at zero; folding rejects efficiency outside [0,1] on queried grid')
    m('legacy_component_acceptance','detector', 'N_l,i,b=acceptance_l*N_pre_l,i,b*N_i; N_b=sum_l,i N_l,i,b',
      'prompt 与 delayed 分量使用各自的选择接受率；时间变化、时间坐标和硬件阈值没有由此补造。',
      {'acceptance_l':'1; source-component selection','N_pre':'events/nucleus/bin before acceptance','N_i':'nuclei','N_b':'events/bin'},
      ['preselection counts','target inventory'], 'counts [events/bin]', ['detector.acceptance_' + k for k in ('mu','e','mub')], [], 'prediction', 'predict:selection.acceptance', 'three declared SNS components', 'exactly once; not already in fluence or efficiency', 'analysis-window losses are excluded, not redistributed')
    m('legacy_csi2021_v1','prediction', 'Y_li(T)=Trapz_E[phi_l(E)*dsigma_li(E,T)]_allowed + sum_lines F_line*dsigma_li(Eline,T); h_li(x_j)=max(Trapz_T[Y_li(T)*p(x_j|T)/m_i_kg],0); N_pre_li,b=m_i_kg*Trapz_x[linear_interp(x_j,h_li)*epsilon(x)]_bin; N_b=sum_li N_i*acceptance_l*N_pre_li,b',
      '总预测式同时保留当前数值运算次序：先按反冲积分出 PE 密度，按每 kg 中间量裁剪，再插值、效率、bin 积分，最后恢复每核归一化并乘真实核数。中间质量因子代数抵消，不能再额外乘 Mdet。',
      {'Y_li':'events/nucleus/keV; time-integrated','phi_l':'cm^-2 MeV^-1','dsigma_li':'cm^2/keV','F_line':'cm^-2','T':'keVnr','x_j':'PE density sample','m_i_kg':'kg/nucleus','h_li':'events/kg/PE','N_pre_li,b':'events/nucleus/bin','N_i':'nuclei','N_b':'events/bin','Trapz':'composite trapezoid on actual selected nodes'},
      ['source','interaction','target','detector','observable'], 'nonnegative 9-bin expected signal [events/bin]', [k for k in params if k.startswith('numerics.')],
      ['sns_michel_tabulation_legacy_v1','sns_prompt_line_v1','li2026_dsigma_v1','legacy_csi_gamma','csi2021_logistic_legacy','csi_target_inventory_v1','legacy_component_acceptance'],
      'folding', 'rates/recoil.integrate_recoil_yield; legacy_density_fold; core/predict.predict',
      'T grid: linspace(Tmin,max_i endpoint,n_er) per isotope; E grid: linspace(0,DAR_endpoint,n_enu), filter E>=Emin(T),E>0 without threshold-node insertion; PE samples: arange(first_edge,last_edge+0.5*step,step); subnodes: linspace(each edge pair,n_observed_bin)',
      'fluence includes POT/geometry; nuclei include mass/stoichiometry; efficiency and acceptance each once; no live time, background or bin-width division in prediction',
      'PE density interpolation outside sampled domain zero; negative density nodes clipped; endpoints shared by quadrature have measure zero; nine half-open bins and final upper edge retained by observation convention')
    m('gaussian_two_pull_legacy_v1','statistics', 's_b=N_b/(edge[b+1]-edge[b]); model_b=(1+alpha)*s_b+(1+beta)*background_b; chi2=sum_b((observed_b-model_b)/sigma_b)^2+(alpha/sigma_alpha)^2+(beta/sigma_beta)^2',
      '旧 residual/excess 数组的近似 Gaussian 统计。信号从 events/bin 转 counts/PE 一次。误差对角且与参数无关，两项归一化 pull 在全箱间相关；alpha/beta 无约束解析极小化。',
      {'N_b':'events/bin','edge':'PE','s_b':'counts/PE','observed_b':'counts/PE; may be negative','background_b':'counts/PE','sigma_b':'counts/PE','alpha':'1; signal normalization nuisance','beta':'1; background normalization nuisance','sigma_alpha':'1','sigma_beta':'1','chi2':'1'},
      ['signal prediction','statistics_observed','statistics_background','statistics_uncertainty','observable_pe_edges'], 'profiled approximate chi2 [1]',
      ['statistics.sigma_alpha','statistics.sigma_beta','statistics.sigma_floor'], ['legacy_csi2021_v1'], 'profiling', 'profile_gaussian_two_pull; statistics_binding.evaluate',
      'nine bins; independent symmetric errors plus two Gaussian normalization pulls', 'observed/background/sigma already counts/PE; no covariance resource used; no Poisson interpretation',
      'sigma=max(sigma,sigma_floor); solve 2x2 normal equations; singular solve returns alpha=beta=0,success=False; no clip_bounds in actual binding')

    source_records = {sid: dict(path=path, sha256=sha((ROOT/path).read_bytes()), role='audit_source_only',
                                kind='project_data' if sid == 'response_data' else 'project_document' if path.endswith(('.yaml','.md','.json')) else 'project_code',
                                independently_officially_verified=False) for sid, path in SOURCE_PATHS.items()}
    issues = [
        dict(id='official_experiment_sources', status='MISSING', detail='未获得旧九箱实验的官方论文/补充材料版本、数据表及逐参数原值；不能比较官方值与采用值是否舍入或冲突。', blocks=['official_forward_reproduction','official_likelihood'], needed='官方实验论文、补充材料、release 和校准参数表'),
        dict(id='eft_primary_conventions', status='MISSING', detail='22 个内部算符 key、系数单位、味轴、扇区和完整 matching 数学表达式已提取；一手文献的逐算符 Lorentz/Lagrangian 定义与重整化尺度未独立核对，不能由内部名称反推并伪称物理约定已确认。', blocks=['official_EFT_operator_interpretation'], needed='原理论文献中算符基、Lagrangian、matching 和尺度约定'),
        dict(id='nuclear_source_audit', status='MISSING', detail='聚合 JSON 可读且打包无损，但外部源表、转换流程、所有通道符号/归一化未独立确认；I 的 M_nn(0) 存在已记录残差。', blocks=['externally_validated_nuclear_response'], needed='核响应原始源表和生成流水线'),
        dict(id='antineutrino_kernel', status='MISSING', detail='antinu 标签已保存，当前与相同 rho 的 nu 共用截面核。一般 EFT 的反中微子符号/螺旋度尚未逐算符审查。', blocks=['fully_validated_general_antineutrino_EFT'], needed='逐算符反中微子公式和外部检验'),
        dict(id='statistics_semantics', status='CONFLICT', detail='旧 spec/README 写统计阻断；当前 definition/runtime 实际提供 legacy Gaussian。observed 称 residual/background-subtracted，而公式又加 BRN+NIN，具体已扣背景组成缺原始证据；两者保留，不把代码可运行等同物理确认。', blocks=['official_likelihood','verified_background_subtraction_semantics'], needed='官方 residual、BRN/NIN 定义、背景扣除过程、完整 likelihood/covariance'),
        dict(id='legacy_status_and_reference', status='CONFLICT', detail='旧 spec 标 fast_validated，旧 README 停在 DATASET_VALIDATED，所引 CsI2021 run/reference 路径不存在。当前 tests/reference/interface_refactor_v1 与 interface_kernel_v1 确实存在，属于内部冻结兼容基线。', blocks=['historical_human_approval_reconstruction'], needed='有效阶段报告和人工批准记录'),
        dict(id='source_endpoint', status='MISSING', detail='旧节点掩码上限与 DAR 积分上限不同；谱被裁剪、线性插值且不重归一化，保留实际行为；不能宣称精确物理 Michel 端点归一化。', blocks=['independent_source_endpoint_claim'], needed='源谱/插值约定人工审查'),
        dict(id='detector_validity', status='MISSING', detail='Gamma/quenching/efficiency 原始校准适用区间、CsI[Na] 掺杂影响、硬件阈值和分量接受率的确切时间选择未登记；仅声明当前代码和实际采样范围。', blocks=['official_detector_reproduction'], needed='官方探测器校准、时间窗和有效域说明'),
        dict(id='pilot_runtime', status='MISSING', detail='当前 Loader 不读取 experiment.input.yaml/NPZ；未实现或执行只用两个机器文件的独立 Runtime 加载。', blocks=['standalone_two_file_runtime'], needed='后续显式 schema/model binding/NPZ adapter 任务'),
    ]
    data = dict(
        dataset_name=d.dataset_id, source_type='stopped_pion', target_mode='CsI_equal_stoichiometry',
        package=dict(schema_version='cevns-experiment-input-pilot/1', dataset_id=d.dataset_id,
                     experiment='COHERENT CsI[Na]', experiment_slug=d.experiment_slug, analysis_revision=d.analysis_revision,
                     scientific_claim='legacy_9bin_input_description; audit-ready extraction, not official physics confirmation',
                     status='DRAFT', completeness='PARTIAL', human_physics_approval='NOT_REVIEWED',
                     formal_files=['experiment.input.yaml','experiment.resources.npz','experiment.physics.md'],
                     machine_authority='YAML: scalar/model specification; NPZ: arrays; MD: derived explanation',
                     runtime_ready=False, external_runtime_data_dependencies=[],
                     excluded_datasets=['CsI2017','CsI2021 ROOTTime','time-resolved','9x11 demo','all other experiments']),
        capabilities=dict(prediction='CURRENT_ENGINE_AVAILABLE_LEGACY; package description extracted; standalone loading NOT_IMPLEMENTED',
                          fast='CURRENT_ENGINE_INTERFACE_KERNEL_V1; fixed state and supported bilinear operator basis; package-only NOT_TESTED',
                          statistics='CURRENT_ENGINE_LEGACY_GAUSSIAN_AVAILABLE; scientific provenance PARTIAL',
                          official_likelihood='BLOCKED', general_antineutrino_EFT='NOT_INDEPENDENTLY_VALIDATED'),
        source=dict(model_refs=['sns_fluence_legacy_v1','sns_michel_tabulation_legacy_v1','sns_prompt_line_v1','sns_fixed_state_v1'],
                    component_order=['prompt_numu','delayed_nue','delayed_numubar'],
                    components=[dict(component_id=c.component_id, legacy_label=l, particle_kind=c.particle_kind,
                                     flavor='e' if l == 'e' else 'mu', rho_ref='state_rho_e' if l == 'e' else 'state_rho_mu',
                                     continuum_ref='source_fluence_'+l if l != 'mu' else None,
                                     line_model_ref='sns_prompt_line_v1' if l == 'mu' else None)
                                for c,l in zip(fluence.components,('mu','e','mub'))],
                    normalization='integrated detector fluence; all three species use F once; no live time multiplier',
                    time_coordinate=None, time_support='POT-integrated; component acceptance distinct; no time bins'),
        target=dict(model_ref='csi_target_inventory_v1', isotope_order=['Cs133','I127'], response_keys={'Cs133':'Cs133','I127':'I'},
                    exposure='POT in source; detector mass in target inventory; live time and kg day not independently supplied'),
        interaction=dict(model_refs=['li2026_sm_left_v1','li2026_matching_v1','elastic_kinematics_v1','nuclear_np_polynomial_v1','li2026_R_W_kernel_v1','li2026_dsigma_v1'],
                         theory_id='li2026_legacy', theory_revision='current-07-onebody-proof-convention; source hashes pinned',
                         basis='np', c10_mass_mode=physical.c10_mass_mode, flavor_order=['e','mu','tau'],
                         coefficient_axes={'row':'final flavor','column':'initial flavor'}, default_bsm_coefficients={},
                         supported_operators=[asdict(op) for op in LI2026_OPERATOR_SPECS],
                         symbolic_equations=symbolic_equations(),
                         symbolic_notation='Audit equations only, never eval. cp/cn=proton/neutron NR matrices; C5_1 etc from operator table; E=Enu GeV, E2/E3/E4=E powers; qabs2/3/4=qabs powers. ord_(i,j)=dagger(c_i^a)*c_j^b; sym_/anti_=sum/difference with i,j exchanged. b11 etc are aliases expanded in equation table. _safe_div_by_q2(n,q2) and _safe_pion_pole(n,m_pi,q2) follow stated pole boundary; np.zeros_like means identically zero. pi=mathematical pi, j=imaginary unit; all L/g/B0/sigma/m constants reference lecs registry. FormFactors.build is not on this actual chain.',
                         nuclear_channels=list(CHANNELS), excluded_nuclear_channel={'SigmaPDelta':'R is identically zero; nuclear table never contracted'},
                         engine_dependency='generic tested algorithms supplied by future engine; no algorithm code embedded in package'),
        detector=dict(model_refs=['csi_quenching_legacy_v1','legacy_csi_gamma','csi2021_logistic_legacy','legacy_component_acceptance'],
                      parameter_order={'quenching':['q1','q2','q3','q4'],'efficiency':['a','b','c','d'],'gamma':['a0','b0']},
                      gamma_convention='shape-rate', separate_light_yield=None),
        observable=dict(name=d.observation.name, unit=d.observation.unit, edges_ref='observable_pe_edges', bin_order='ascending PE',
                        bin_count=len(d.observation.edges)-1, boundary='half-open adjacent bins; final upper edge retained; quadrature integrates endpoints',
                        prediction_unit='events/bin', statistics_unit='counts/PE', prediction_content='signal only; efficiency, acceptance, POT and nuclei included; no background subtraction'),
        prediction=dict(model_ref='legacy_csi2021_v1', runtime_model_id=exp.model.model_id,
                        numerical_strategy=ns.strategy, slow_fast_profiles_equal=dict(d.numerical_profiles['slow']) == dict(d.numerical_profiles['fast']),
                        error_control='fixed grids, no adaptive tolerance on actual legacy path; convergence not established in pilot',
                        alternative_bin_probability_path='quad(epsabs=1e-11,epsrel=1e-10) exists but is NOT the bound runtime numerical strategy; no substitution in pilot',
                        model_graph=['source + POT -> integrated detector fluence','fluence + interaction + state -> per-nucleus recoil yield',
                                     'recoil yield + response + efficiency + PE bins -> preselection events/nucleus/bin',
                                     'preselection + component acceptance + isotope nuclei -> events/bin','events/bin / width -> approximate Gaussian evaluation']),
        statistics=dict(model_ref='gaussian_two_pull_legacy_v1', observed_ref='statistics_observed', background_ref='statistics_background',
                        uncertainty_ref='statistics_uncertainty', covariance_ref=None, covariance_status='not used by this approximate model; official covariance missing',
                        nuisance_names=['alpha','beta'], nuisance_prior='independent zero-mean Gaussian', profiling='unbounded analytic 2x2 linear normal equations',
                        observed_semantics='legacy residual/excess; exact background-subtraction provenance unresolved', inference_claim='approximate chi2 only; no official CL/likelihood claim'),
        parameters=params, models=models,
        resources=dict(archive='experiment.resources.npz', archive_format='ZIP of non-object NPY arrays', allow_pickle=False,
                       arrays=resources, sha256=sha(npz_bytes(arrays)), undeclared_external_data_allowed=False),
        provenance=dict(branch=BRANCH, audited_head=HEAD, audit_date='2026-11-04', sources=source_records,
                        official_primary_materials=[], official_primary_status='MISSING',
                        decisions=[dict(id='task_scope', status='USER_REQUESTED', meaning='旧九箱 CsI2021 三文件提取；不改变 Runtime 或批准未确认物理'),
                                   dict(id='write_scope', status='USER_AUTHORIZED', meaning='用户在完整路径计划后回复 APPROVE WRITE；本次继续请求延续授权')],
                        standards=dict(input_standard_version=1, schema='existing experiment.schema.json required fields reused; pilot adds explicit parameters/models/resources',
                                       actual_schema_check='existing validate_experiment_spec_data plus pilot validator; not a full future package schema'),
                        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
                        issues=issues))
    validate_experiment_spec_data(data)
    # Normalize tuple metadata to the exact JSON/YAML representation used on disk.
    from tools.csi2021_input_contract import migrate_pilot
    return migrate_pilot(json.loads(dump(data))), arrays


def cell(value):
    return str(value).replace('|','&#124;').replace('\n',' ')


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |'] +
                     ['| ' + ' | '.join(cell(v) for v in row) + ' |' for row in rows])


def render_physics(data, arrays):
    from cevns_pyeft.experiments.input_package import render_physics as canonical_render
    return canonical_render(data, arrays)


def validate(data, arrays, md, archive):
    from cevns_pyeft.experiments.input_package import validate_document, validate_arrays
    errors = validate_document(data)
    if errors:
        return errors
    errors += validate_arrays(data, arrays, archive)
    try:
        if md != render_physics(data, arrays):
            errors.append('Physics MD differs from YAML/NPZ rendering')
    except (KeyError, TypeError, IndexError) as error:
        errors.append(str(error))
    return errors


def negative_checks(data, arrays, md, archive):
    """In-memory corruptions must be refused, without creating test artifacts."""
    cases = []
    bad = deepcopy(data); bad['parameters']['source.baseline_m']['value'] *= 2; cases.append(('scalar/MD drift',bad,arrays,md,archive))
    bad = deepcopy(data); bad['models']['legacy_csi_gamma']['variables'] = {}; cases.append(('missing model units',bad,arrays,md,archive))
    bad = deepcopy(data); del bad['resources']['arrays']['statistics_background']; cases.append(('undeclared NPZ key',bad,arrays,md,archive))
    bad_arrays = dict(arrays); del bad_arrays['statistics_background']; cases.append(('declared NPZ key missing',data,bad_arrays,md,archive))
    bad = deepcopy(data); bad['resources']['arrays']['statistics_observed']['shape'] = [8]; cases.append(('wrong shape',bad,arrays,md,archive))
    bad = deepcopy(data); bad['resources']['arrays']['statistics_observed']['dtype'] = 'float32'; cases.append(('wrong dtype',bad,arrays,md,archive))
    bad = deepcopy(data); del bad['parameters']['source.baseline_m']['provenance_status']; cases.append(('missing parameter provenance',bad,arrays,md,archive))
    bad = deepcopy(data); bad['parameters']['source.total_pot']['source_kind']='official_primary'; cases.append(('false official provenance',bad,arrays,md,archive))
    bad = deepcopy(data); bad['resources']['sha256']='0'*64; cases.append(('bad archive SHA256',bad,arrays,md,archive))
    cases.append(('extra MD parameter',data,arrays,md+'\nInvented_parameter=123\n',archive))
    return {name:bool(validate(d,a,t,z)) for name,d,a,t,z in cases}


def initial_report(data, check, negatives):
    base = '../' + DATASET.as_posix() + '/'
    return '\n'.join([
        '# CsI2021 Onboarding 三文件试点审计报告', '', '日期：2026-11-04。任务范围：旧九箱 CsI2021；正式输入包 DRAFT / PARTIAL。', '',
        f'分支 `{BRANCH}`，起始 HEAD `{HEAD}`；初始 `git status --short --branch` 干净。', '',
        '实际执行目录为已验证的 07 分支 worktree：`261103Gitup1-CONUS-6/.github-publish/gitup01-20261104/Gitup01/`。用户最初给出的同级 Gitup01 目录无有效 Git 身份，未向其写入；本次结果在 07 worktree。', '',
        '## 1. 三份正式输入的位置', '',
        '\n'.join(f'- [{name}]({base}{name})' for name in data['package']['formal_files']), '',
        '本报告与生成工具仅为审计/提取辅助，不是正式输入的必要组成部分。现有 experiment.yaml 和 Python definition 作为提取依据继续保留。', '',
        '## 2. YAML 物理模块和 NPZ 内容', '',
        'YAML 复用现有 dataset_name/source_type/target_mode 与共同输入证据字段；扩展 package、capabilities、source、target、interaction、detector、observable、prediction、statistics、parameters、models、resources 和 provenance。', '',
        f"计数：{len(data['models'])} 个模型、{len(data['parameters'])} 个显式标量参数、{len(data['resources']['arrays'])} 个 NPZ 数组。", '',
        'NPZ：Cs133/I127 实际七类响应系数（两个核素共十四个数组）、SNS 能量/两条连续谱表、两种固定味态、PE 边界、observed/background/uncertainty。Gamma 与效率为解析模型；未加入无消费者的表、协方差或 ROOTTime 资源。', '',
        f"NPZ SHA256：`{data['resources']['sha256']}`。", '',
        '## 3. Physics MD 与机器输入的关系', '',
        'Physics MD 从同一 YAML 结构及 NPZ 内容渲染每个模型、变量、单位、参数表、来源、数学展开、分箱、全部数组清单与问题清单。精确重新渲染检查阻止任意额外参数、公式或数组说明漂移。YAML 是标量/模型权威，NPZ 是数组权威；辅助脚本只在提取/审核时需要。', '',
        '## 4. 官方资料、legacy 来源、缺失与冲突', '',
        '官方实验一手资料：本次没有取得可独立核对的原文/官方数据文件；官方来源条目为空。标量/统计数据来自当前 definition 和共享 legacy 参数；源表由当前 SNS 实现提取；核响应从当前 JSON 逐项无损恢复；计算量标 PROJECT_DERIVED。SOURCE_EXTRACTED 只表示读取到项目源码，不表示官方确认。', '',
        table(['问题','状态','能力影响'], [(i['id'],i['status'],i['detail']) for i in data['provenance']['issues']]), '',
        '## 5. 完整性及验收状态', '',
        table(['验收组','实际结论'], [
            ('A 物理内容','已整理真实调用链、源/靶/理论/探测器/坐标/数值/统计及公式解释；每参数有来源与 DRAFT 状态。官方有效域/语义仍 PARTIAL。'),
            ('B 数值资源','当前九箱链可获得且必需的数值数组已打包，唯一 key、单位/shape/dtype/轴与 SHA256 齐全；无 object、绝对运行路径或外部数值依赖。'),
            ('C 一致性','脚本逐模型/参数/资源核对，MD 精确重渲染，NPZ 安全回读与哈希检查，负向破坏拒绝检查。'),
            ('D 科学状态','官方材料 MISSING，代码恢复与推导已区分；未批准未确认物理，未宣称 standalone Runtime 或官方 likelihood。')]), '',
        '提取与三文件架构试点已完成；科学完整性为 PARTIAL。旧引擎可运行的近似能力与官方科学确认分开；本包只凭机器文件运行尚未实现/未验证。', '',
        '## 6. 本次自动检查', '',
        f"三文件一致性：{'PASS' if not check else 'FAIL'}；错误：{check}。", '',
        table(['负向破坏案例','正确拒绝'], negatives.items()), '',
        '检查范围是本试点声明结构与当前实现的相符性；没有实现或声称通用模型编译器、科学来源认证、官方数据复现和数值收敛。', '',
        '## 7. 后续 Runtime 可复用与需扩展的能力', '',
        '可复用 ExperimentDefinition/ExperimentCatalog、ResourceCatalog 的显式根与指纹、prepare/executor、ExperimentModel、TheoryPoint、POTExposure、TargetInventory、SourceModel/DetectorFluence、InteractionModel、ObservationModel、Prediction、compile_fast 和统计 profiler。', '',
        '后续需建立：版本化 package schema 与严格字段/单位/坐标验证；受约束 model_id 到经过测试实现的绑定；NPZ 原子/安全读取和哈希/形状验证；ResponseW 从声明数组构造的适配；参数驱动的源/靶/探测器/统计装配；生命周期 owned_files 登记与模型版本兼容；隔离环境仅凭两机器文件的加载测试。不得 eval 模型字符串。', '',
        '现有 parser 只支持浅层 experiment.yaml，不适合深层 pilot；此次用标准库 JSON 读取 YAML 1.2 JSON 子集，并调用现有 required-field validator，未改生产 Loader 或公共 schema。', '',
        '## 8. 文件与 README 联动、恢复及授权', '',
        table(['新增/修改内容','说明归属','实际运行绑定'], [
            ('三份正式输入','data/experiments/COHERENT_CsI/CsI2021/README.md','只由 pilot 工具提取/检查，现有 Loader 未绑定'),
            ('本审计报告','docs/README.md','任务审计入口'),
            ('tools/build_csi2021_onboarding_pilot.py','tools/README.md','--write 创建；默认/--check 只读；拒绝覆盖')]), '',
        '用户在精确 WRITE PLAN 后回复 APPROVE WRITE。修改前 README 保存在 backup 对应原相对路径并由 backup/BACKUP_MANIFEST.md 登记；备份只用于恢复。没有删除原文件、提交或推送。未修改 registry/resource manifest、公共理论、核响应核心、Prediction/Statistics 接口、其他实验或冻结基线。', '',
        '新三文件尚未进入 dataset registry owned_files，因此当前 datasets export 不会自动把它们纳入既有安装包；这是 Task 01 的未接入边界，需后续正式 Runtime/生命周期任务处理。', '',
        '## 9. 复核命令', '', '```powershell', 'python -B tools/build_csi2021_onboarding_pilot.py --check',
        'python -B tools/validate_resource_manifest.py --root . --dataset CsI2021',
        'python -B tools/validate_docs.py --files data/experiments/COHERENT_CsI/CsI2021/README.md data/experiments/COHERENT_CsI/CsI2021/experiment.physics.md docs/README.md docs/CSI2021_ONBOARDING_PILOT_REPORT.md tools/README.md', '```', '',
        '额外回归、实际命令及结果在下方执行后追加，未运行项不记 PASS。', ''])


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true', help='create only; refuse any existing output')
    mode.add_argument('--check', action='store_true', help='read-only consistency plus current-source extraction check')
    mode.add_argument('--render-md', action='store_true', help='render stored YAML and NPZ to stdout, without writing')
    args = parser.parse_args()
    destination = ROOT / DATASET
    if args.render_md:
        from cevns_pyeft.experiments.input_package import strict_json
        data = strict_json((destination/'experiment.input.yaml').read_text(encoding='utf-8'))
        with np.load(destination/'experiment.resources.npz', allow_pickle=False) as z:
            arrays = {k:z[k] for k in z.files}
        print(render_physics(data,arrays), end='')
        return 0
    if git('branch','--show-current') != BRANCH or git('rev-parse','HEAD') != HEAD:
        raise ValueError('pilot source branch/HEAD changed; review before regenerating/checking against this extraction')
    data, arrays = extract()
    archive = npz_bytes(arrays)
    md = render_physics(data, arrays)
    checks = validate(data, arrays, md, archive)
    negatives = negative_checks(data, arrays, md, archive)
    if checks or not all(negatives.values()):
        raise ValueError({'errors':checks,'negative_checks':negatives})
    if args.write:
        outputs = {destination/'experiment.input.yaml':dump(data).encode('utf-8'),
                   destination/'experiment.resources.npz':archive,
                   destination/'experiment.physics.md':md.encode('utf-8'),
                   ROOT/REPORT:initial_report(data,checks,negatives).encode('utf-8')}
        existing = [str(p.relative_to(ROOT)) for p in outputs if p.exists()]
        if existing:
            raise FileExistsError('refusing existing pilot outputs: ' + ', '.join(existing))
        for path, content in outputs.items():
            with path.open('xb') as stream:
                stream.write(content)
    else:
        from cevns_pyeft.experiments.input_package import strict_json
        actual = strict_json((destination/'experiment.input.yaml').read_text(encoding='utf-8'))
        content = (destination/'experiment.resources.npz').read_bytes()
        with np.load(io.BytesIO(content), allow_pickle=False) as z:
            actual_arrays = {k:z[k] for k in z.files}
        checks += validate(actual,actual_arrays,(destination/'experiment.physics.md').read_text(encoding='utf-8'),content)
        if actual != data:
            checks.append('stored YAML differs from fresh current-source extraction')
        if set(actual_arrays) != set(arrays) or any(not np.array_equal(actual_arrays[k],v) for k,v in arrays.items() if k in actual_arrays):
            checks.append('stored arrays differ from current consumers')
    print(dump(dict(status='PASS' if not checks else 'FAIL', models=len(data['models']), parameters=len(data['parameters']), arrays=len(arrays),
                    archive_sha256=sha(archive), errors=checks, negative_checks=negatives,
                    scope='pilot structural/legacy-extraction consistency only; no standalone runtime or official physics certification')), end='')
    return bool(checks)


if __name__ == '__main__':
    raise SystemExit(main())
