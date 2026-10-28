"""Write an auditable R0-R3 report only after actual validation has passed."""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import replace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from cevns_pyeft.experiments.coherent.csi2021 import make_csi2021_model
from cevns_pyeft.sources.composable import ScaledSource
from cevns_pyeft.detectors.csi2021 import ConstantEfficiency


def main():
    out = ROOT / "outputs/refactor"
    comparison = json.loads((out / "regression_comparison.json").read_text(encoding="utf-8"))
    metadata = json.loads((ROOT / "tests/reference/interface_refactor_v1/metadata.json").read_text(encoding="utf-8"))
    changes = json.loads((out / "changes.json").read_text(encoding="utf-8"))
    xml = ET.parse(out / "final_pytest.xml")
    suites = list(xml.getroot().iter("testsuite"))
    tests = sum(int(s.attrib.get("tests", 0)) for s in suites)
    failures = sum(int(s.attrib.get("failures", 0)) + int(s.attrib.get("errors", 0)) for s in suites)
    skipped = sum(int(s.attrib.get("skipped", 0)) for s in suites)
    if comparison["status"] != "PASS" or failures or skipped or not tests:
        raise SystemExit("Required checks have not passed; refusing a completion report")
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in ("src", "tests", "tools/refactor") for p in sorted((ROOT / folder).rglob("*.py"))
        if "__pycache__" not in p.parts}
    (out / "new_file_hashes.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")
    model = make_csi2021_model(ROOT / "data/responses/responses_all.json")
    (out / "resolved_model.json").write_text(json.dumps(model.describe(), indent=2), encoding="utf-8")
    scaled_model = replace(model, source=ScaledSource(model.source, 2))
    zero_model = replace(model, observation=replace(model.observation, efficiency=ConstantEfficiency(0)))
    replacements = [
        {"replacement_id": "source-scale-2-demonstration", "slot": "source", "classification": "same_contract_model_change",
         "old": model.source.describe().as_dict(), "new": scaled_model.source.describe().as_dict(),
         "old_model_fingerprint": model.describe()["model_fingerprint"],
         "new_model_fingerprint": scaled_model.describe()["model_fingerprint"],
         "physical_change": "explicit detector fluence multiplied by two, for slot validation only; production default unchanged",
         "unit_and_axis_conversion": "none", "normalization_ownership_change": "none; scaling stays in source",
         "additional_slots_required": [], "recompute": ["fluence", "recoil yield", "folded counts", "statistics"],
         "reuse": ["target model", "interaction model", "observation model", "statistical data"],
         "pipeline_checks": ["test_real_source_slot_replacement_scaling_and_instance_isolation"],
         "fast_reuse": "unsupported; no composable Fast compiler"},
        {"replacement_id": "zero-efficiency-demonstration", "slot": "observation.efficiency", "classification": "same_contract_model_change",
         "old": model.observation.efficiency.describe(), "new": zero_model.observation.efficiency.describe(),
         "old_model_fingerprint": model.describe()["model_fingerprint"],
         "new_model_fingerprint": zero_model.describe()["model_fingerprint"],
         "physical_change": "zero probability of detection for slot validation only; production default unchanged",
         "unit_and_axis_conversion": "none", "normalization_ownership_change": "none",
         "additional_slots_required": [], "recompute": ["folded counts", "Prediction", "statistics"],
         "reuse": ["source model", "run", "target model", "interaction model"],
         "pipeline_checks": ["test_observation_efficiency_replacement_and_selection_are_applied_once"],
         "fast_reuse": "unsupported; no composable Fast compiler"},
    ]
    (out / "replacement_cards.json").write_text(json.dumps(replacements, indent=2), encoding="utf-8")
    worst_case, worst = max(((case, error) for case in comparison["cases"] for error in case["comparisons"]),
                           key=lambda pair: pair[1]["max_fraction_of_allowed_error"])
    grid_change = max(abs(v) for v in comparison["sm_grid_changes"]["medium_to_default"]["relative_per_bin"])
    reasons = {"README.md": "更新实际入口、状态与报告链接",
        "src/cevns_pyeft/core/__init__.py": "延迟加载旧 engine，隔离通用核心 import",
        "src/cevns_pyeft/experiments/coherent/sns.py": "抽出显式参数构造，旧 loader 委托且公式不变",
        "src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py": "委托新预测并恢复旧 raw 和五个返回键",
        "src/cevns_pyeft/statistics/predictors.py": "消费同一预测，保留单位转换及分量标签"}
    modified_rows = "\n".join(f"| `{name}` | 修改 | {reasons[name]} |" for name in changes["modified"])
    report = f"""# R0–R3 实施结果

日期：2026-10-28（Asia/Shanghai）。状态：IMPLEMENTED / VERIFIED（范围仅为下述一维 Slow 接口重构）。

## 完成的行为

直接在用户提供的 `261028Gitup1-CONUS-3/Gitup01` 中实施，没有再建立项目副本。首轮范围采用说明包推荐的 R0–R3；本轮保持既有实验数据和物理含义，按根 AGENTS 的普通维护规则执行，未启动新实验接入或改变 Human Gate。

实际调用链为 `make_csi2021_model → predict → integrate_recoil_yield → legacy_density_fold → Prediction`。
源、运行期、靶核、相互作用、观测和分箱由实例组装；通用核心不导入具体实验。`core.engine` 改为按需加载，旧 import 继续可用。旧 Slow 入口在独立新链回归通过后改为委托，并准确重建原 raw 输出。统计路由从相同 Prediction 生成一维向量，保留旧分量标签及近似 chi²。

## 基线与环境

`git status`/提交解析返回 `fatal: not a git repository`，未生成或臆造 commit。以文件哈希、冻结参考和 unified diff 提供审阅与恢复依据。说明包列出的 34 项文件哈希与执行前原始输入全部一致；这不等于验证了整个目录对应某个 Git commit。

所有实际测试使用用户指定的 `F:/Work/.codex_conda_envs/codex-py311/python.exe`：Python 3.11.15、NumPy 2.4.6、SciPy 1.17.1、pytest 9.1.1。指定 Conda 环境未安装或更新包；早先创建的临时 venv 已清理。

修改前在单独运行的原代码进程中冻结 170 组数组。`tests/reference/interface_refactor_v1/metadata.json` 保存 115 个输入文件哈希、具体 Wilson 矩阵、参数和运行时长；`baseline.npz` 保存逐源/逐核素/逐箱及单位转换参考。元数据的文档差异核对在捕获后修正为使用执行前已保存的哈希；参考数组及容差没有更改。

CsI2021 参数点：SM、单算符 NP-only、SM+NP、复系数、多味矩阵；算符选自当前 registry 的有效 LNC 点，不假设 LNV 对角输入合法。

| 网格 | n_er | n_enu | n_pe_bin | pe_step | 覆盖 |
|---|---:|---:|---:|---:|---|
| small | 5 | 12 | 4 | 4.0 | 五种参数点 |
| medium | 11 | 40 | 8 | 3.0 | 五种参数点 |
| default | 21 | 120 | 8 | 3.0 | SM，旧入口默认网格 |

CsI2017 和 Ar2020 各冻结 SM、多味点的计数参考；保留前者既有 14.6 归一化及后者原响应。核响应、源尾部、反中微子处理和统计定义均未修正。

## 文件变化

| 文件 | 动作 | 目的 |
|---|---|---|
{modified_rows}

新增职责的唯一位置：`contracts/` 定义并验证合同；`sources/composable.py`、`sources/sns.py` 负责源适配；`targets/materials.py` 负责核数；`theory/li2026/adapter.py` 包装旧截面；`detectors/` 负责响应、效率及选择；`rates/recoil.py`、`rates/folding.py` 执行积分和折叠；`core/model.py`、`core/predict.py` 负责组装结果及调用链；`experiments/coherent/csi2021.py` 选择实验组件；`statistics/adapters.py` 处理统计边界。

精确 create/modify/delete 清单见 `outputs/refactor/changes.json`，可审阅差异见 `outputs/refactor/review.diff`。没有删除已有生产文件，没有修改实验输入、已有参考数组或 workflow。`outputs/refactor/original/` 仅保存五个被修改文件的执行前版本，供审阅和按文件恢复使用。

## 物理交接

| 边界 | 输入 | 输出 | 因子责任 |
|---|---|---|---|
| Source.for_run | 显式 POT / 活时间 / 已积分运行期 | continuum cm^-2 MeV^-1；lines cm^-2 | 曝光及几何只在此施加 |
| state_at | 实际 MeV 查询网格与本次 StateParameters | (n_E,3,3) rho；独立 nu/antinu 标签 | 坐标、Hermitian、PSD、trace 校验 |
| Interaction | MeV、keV、核素、rho、TheoryPoint | cm²/keV，(n_E,) | 不含源、质量、效率 |
| RecoilYield | 源与截面 | 每核每 keV 产额 | 尚未乘核数 |
| Observation | 反冲与重建轴 | 概率或独立数值折叠结果 | 效率、分量选择一次 |
| Prediction | 每核产额、真实核数、分箱 | events/bin；(source,isotope) 最终贡献 | 核数乘一次 |
| Statistics | 同一带轴预测 | 原一维 observable | counts/PE 只除一次箱宽 |

旧 `target_flavor_counts_per_bin` 按每种核素使用整台质量、未含材料质量分数及分量接受率；新 components 已含实际核数和选择。兼容层使用选择前每核诊断恢复旧 raw，没有把新最终贡献改名冒充旧 raw。

## 实际验证

| 检查 | 实际入口/证据 | 状态 | 范围或误差 |
|---|---|---|---|
| 原始测试基线 | r0_pytest.xml + r0_fixed.xml | PASS | 100 项通过；3 项临时目录权限错误改用项目内目录后重跑通过，共 103 项 |
| 新旧独立链 | compare_baseline.py / regression_comparison.json | PASS | 11 组合，143 项逐箱比较；max abs {comparison['max_absolute_events']:.16g} events |
| 最终完整套件 | `python -m pytest -q tests --basetemp=.pytest-tmp/final-r0-r3 --junitxml=outputs/refactor/final_pytest.xml` | PASS | {tests} passed，0 failures/errors/skips |
| 合同与替换 | test_interface_contracts.py、test_component_replacement.py | PASS | 任意分量名、空/多谱线、能量依赖态、真实坐标、单位/曝光拒绝、质量/源强线性、效率零/一、A→B→A 隔离 |
| 旧 API / 三数据集 / 统计桥 | test_refactor_csi2021_regression.py | PASS | 原五个返回键、逐箱 raw 和密度、CsI2017/Ar2020、chi²与标签 |
| 旧 Fast full/pair | legacy_fast_diagnostic.json | PASS | 最大绝对差 2.14e-14；四算符、小网格诊断 |
| 旧 Fast/Slow 严格一致 | r0_legacy_fast_diagnostic.json、legacy_fast_diagnostic.json | FAIL（既有问题） | 最大约 4.94e-8 events，未放宽阈值 |
| 旧 Fast 并行构建 | parallel_fast.json | PASS | n_jobs=2，小基底、有限值与 import/序列化兼容 |
| 非项目 cwd | 绝对 PYTHONPATH 和绝对响应路径实际 import/predict | PASS | 返回 (9,)；不是 wheel 资源打包验证 |

预设计数标准为 `abs(new-ref) <= 1e-12 + 1e-10*abs(ref)`，没有事后调整。按容差归一衡量，最差项为 `{worst_case['point']}/{worst_case['grid']}/{worst['label']}`，第 {worst['worst_bin'] + 1} 箱，使用允许误差的 {worst['max_fraction_of_allowed_error']:.8g}。小截面的适配检查使用逐点精确相等，没有套用不合量级的事件绝对容差。小网格 SM 近似 chi² 基线为 {metadata['chi2_small_sm']:.15g}，直接统计适配和旧路由均复现。

同输入、同离散算法的一致性已经验证。SM medium→default 的最大逐箱相对变化约 {grid_change:.3%}；逐箱变化保存在 regression_comparison.json。本轮未认证科学收敛精度，不能把接口回归容差解释为积分误差。

## 尚未完成

R4 的组合式 Fast 编译、模型内容缓存失效和完整系数能力迁移未实现。旧 Fast 的换算常数为 `(1.973269804e-14)^2`，Slow 使用 `0.3893793721e-27`，比值为 `0.9999999995834904`，解释上述约 4.17e-10 的相对差。仅作诊断对照，不对结果施加归一化修补。已有 Fast API 仍可调用；新 predict 显式 fast 报错，auto 记录回退 Slow 的原因。

本次任务聚焦模块化与接口，不安排外部物理数据或联合统计扩展。一般 antinu 振幅及核响应外部规范审核未完成。当前统计仍为 legacy approximate statistics。安装/wheel 资源分发属于未执行的 R6 项；外置 data 的既有限制保留。没有安装或覆盖 Skill，没有把工程完成写入 Physics Gate。

## 下一步与恢复

R0–R3 范围内无待执行检查。实际模块参数、能力与依赖图见 `outputs/refactor/resolved_model.json`；源强和零效率的实际实例替换卡见 replacement_cards.json；代码指纹、输入指纹和断点见 checkpoint.json。先校验这些内容，再运行上述完整测试或 compare_baseline.py。不要运行 freeze_baseline.py 更新参考；它拒绝覆盖现存参考。

后续 R4 应先在明确保留旧行为的边界下处理已记录换算差异，再接同一物理模型和失效规则。后续接口审阅验证真实组件替换与依赖边界。当前指纹用于审阅追踪，不代表已通过 Fast 缓存物理兼容验证。
"""
    (ROOT / "docs/interface_refactor/R0_R3_REPORT.md").write_text(report, encoding="utf-8")
    added = list(dict.fromkeys(changes["added"] + ["docs/interface_refactor/R0_R3_REPORT.md"]))
    changed_hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                     for name in changes["modified"] + added if (ROOT / name).is_file()}
    task = {"task_id": "20261028-csi2021-interface-r0-r3", "work_package": ["R0", "R1", "R2", "R3"],
        "repository_commit": None, "dataset": "CsI2021", "task_kind": "refactor_preserve_behavior",
        "objective": "Validated composable CsI2021 9-bin Slow prediction with legacy raw/API/statistics preserved",
        "authorization_basis": "User requested refactoring the already copied project using the supplied package; initial delivery follows its recommended R0-R3 scope.",
        "read_first": ["Gitup01/AGENTS.md", "00_CODEX_START_HERE.md", "01_BASELINE_AUDIT.md", "02_ARCHITECTURE_AND_DECISIONS.md", "03_SOURCE_AND_EXPOSURE_CONTRACTS.md", "04_TARGET_AND_INTERACTION_CONTRACTS.md", "05_OBSERVATION_AND_PREDICTION_CONTRACTS.md", "06_PIPELINE_AND_ASSEMBLY.md", "07_FILE_CHANGE_MAP.md", "08_IMPLEMENTATION_PHASES.md", "11_VALIDATION_AND_ACCEPTANCE.md", "12_SKILL_REPLACEMENT_PROTOCOL.md", "13_TASK_AND_REVIEW_TEMPLATES.md"],
        "inputs": ["tests/reference/interface_refactor_v1/metadata.json", "tests/reference/interface_refactor_v1/baseline.npz", "data/responses/responses_all.json"],
        "create_paths": added, "modify_paths": changes["modified"], "delete_paths": [],
        "must_preserve": ["CsI2021 9 bins and historical raw", "CsI2017 and Ar2020", "physics conventions and data"],
        "blocked_inputs": [], "completion_evidence": ["final_pytest.xml", "regression_comparison.json", "resolved_model.json"]}
    checkpoint = {"record_schema": "refactor_checkpoint_v1", "task_id": task["task_id"],
        "work_package": "R0-R3", "step": "verified", "revision": 1, "base_commit": None, "current_commit": None,
        "changed_file_fingerprints": changed_hashes,
        "input_fingerprints": {"frozen_baseline_npz": comparison["reference_sha256"],
                               "nuclear_responses": metadata["hashes"]["data/responses/responses_all.json"]},
        "completed_checks": [f"{tests} pytest checks", "11 frozen regression cases", "legacy parallel Fast construction"],
        "pending_checks": [], "blockers": [],
        "outside_scope": ["R4 composable Fast", "R6 wheel/install"],
        "known_existing_failures": ["strict legacy Fast/Slow constant discrepancy"],
        "next_action": "R0-R3 complete. If extending, scope R4 conversion compatibility before compiling model kernels."}
    (out / "task_card.json").write_text(json.dumps(task, indent=2), encoding="utf-8")
    (out / "checkpoint.json").write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
    print(f"Wrote verified report: {tests} passed; regression {comparison['status']}; legacy Fast discrepancy retained")


if __name__ == "__main__":
    main()
