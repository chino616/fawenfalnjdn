"""Export final interface-refactor evidence and a per-file review without Git."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import xml.etree.ElementTree as ET

PROJECT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = PROJECT/"outputs/refactor_r4"
    fast = json.loads((out/"fast_slow_comparison.json").read_text())
    wheel = json.loads((out/"wheel_smoke.json").read_text())
    cards = json.loads((out/"replacement_cards.json").read_text())
    suites = list(ET.parse(out/"final_pytest.xml").getroot().iter("testsuite"))
    tests = sum(int(s.attrib["tests"]) for s in suites)
    assert not any(int(s.attrib.get(k,0)) for s in suites for k in ("failures","errors","skipped"))
    assert tests and fast["status"]==wheel["status"]=="PASS" and all(c["status"]=="PASS" for c in cards)
    before = json.loads((out/"start_hashes.json").read_text())
    data_changes = [p for p,h in before.items() if p.startswith("data/") and sha(PROJECT/p)!=h]
    old_reference_changes = [p for p,h in before.items() if p.startswith("tests/reference/") and sha(PROJECT/p)!=h]
    assert not data_changes and not old_reference_changes
    modified, added, diff = [], [], []
    originals = out/"original"
    for original in sorted(originals.rglob("*")):
        if not original.is_file(): continue
        name = original.relative_to(originals).as_posix()
        current = PROJECT/name
        assert current.is_file()
        if current.read_bytes()==original.read_bytes(): continue
        modified.append(name)
        diff.extend(difflib.unified_diff(original.read_text(encoding="utf-8").splitlines(keepends=True),current.read_text(encoding="utf-8").splitlines(keepends=True),fromfile="before_R4/"+name,tofile="after_R4/"+name))
    for folder in ("src","tests"):
        for p in sorted((PROJECT/folder).rglob("*")):
            name=p.relative_to(PROJECT).as_posix()
            if p.is_file() and p.suffix in (".py",".json",".npz") and "__pycache__" not in p.parts and name not in before:
                added.append(name)
                if p.suffix==".py":
                    diff.extend(difflib.unified_diff([],p.read_text(encoding="utf-8").splitlines(keepends=True),fromfile="/dev/null",tofile="after_R4/"+name))
    uncovered=[p for p,h in before.items() if p.startswith("src/") and sha(PROJECT/p)!=h and p not in modified]
    assert not uncovered, uncovered
    packet=PROJECT.parent/"重构/CEvNS_pyEFT_interface_refactor_v1/CEvNS_pyEFT_interface_refactor_v1"
    files=sorted(p for p in packet.glob("*.md") if p.name!="15_PACKAGE_MANIFEST.md")
    links=0
    for p in files:
        text=p.read_text(encoding="utf-8")
        assert "ROOT" not in text and "uproot" not in text
        for target in re.findall(r"\]\(([^)]+)\)",text):
            if "://" in target or target.startswith("#"): continue
            assert (p.parent/target.split("#")[0]).is_file(), (p.name,target)
            links+=1
    rows="\n".join(f"| [{p.name}]({p.name}) | {p.stat().st_size} | `{sha(p)}` |" for p in files)
    (packet/"15_PACKAGE_MANIFEST.md").write_text(f"""# 文档包清单与质量检查

范围修订：2026-10-28（Asia/Shanghai），版本 1.1。按用户要求，任务聚焦模块化、接口、Fast 缓存和发行验证；第09文档替换为模块接口审阅，R5 同步改为接口审阅与替换验证。

共 {len(files)+1} 份 Markdown；{links} 个文档内相对链接目标全部存在。此项只证明文档一致性，实际软件状态见 Gitup01/docs/interface_refactor/R4_R6_REPORT.md 和测试日志。01 中的源码事实及哈希仍锚定原始提交，不冒充当前实现。

| 文件 | 字节数 | SHA256 |
|---|---:|---|
{rows}
""",encoding="utf-8")
    worst_case,worst=max(((c,e) for c in fast["cases"] for e in c["comparisons"]),key=lambda p:p[1]["fraction_of_allowed_error"])
    artifact=next((out/"dist").glob("*.whl"))
    utilities=["tools/refactor/validate_interface_fast.py","tools/refactor/check_wheel.py","tools/refactor/report_r4.py",
               "docs/interface_refactor/FAST_AND_CACHE.md","docs/interface_refactor/R4_R6_REPORT.md"]
    added=list(dict.fromkeys(added+utilities))
    changes={"modified":modified,"added":added,"deleted_production_files":[],"experiment_data_changes":data_changes,
             "old_reference_changes":old_reference_changes,"instruction_packet":{p.name:sha(p) for p in packet.glob("*.md")},
             "documentation_scope_changes":["docs/interface_refactor/R0_R3_REPORT.md","tools/refactor/write_report.py",
                                             "outputs/refactor/checkpoint.json"],
             "review_scope":"R3 verified code to current production code; instruction scope amended as requested"}
    (out/"changes.json").write_text(json.dumps(changes,indent=2),encoding="utf-8")
    (out/"review.diff").write_text("".join(diff),encoding="utf-8")
    table="\n".join(f"| `{p}` | 修改 |" for p in modified)
    report=f"""# R4–R6 模块化与接口实施结果

日期：2026-10-28（Asia/Shanghai）。状态：IMPLEMENTED / VERIFIED，按用户最新范围完成 Fast、缓存、模块审阅及发行验证。外部数据接入已从任务中移除；说明包第09文档及 R5 已改为模块接口审阅，不作为缺资料待办。

## 实际行为

`make_csi2021_model → compile_fast(model,numerics) → CompiledKernel.predict(TheoryPoint)` 读取同一组装模型的源、运行期、真实核数、截面、观测、选择和分箱。通用编译器不选择具体实验或识别固定源标签。`predict(...,backend="fast",compiled=kernel)` 使用相同接口返回带轴 Prediction；旧 Slow API 和统计桥保留。

当前支持范围：CsI2021 一维 9 箱的 Li2026 `operator_bilinear_v1`，22 个活跃算符，固定且不随扫描改变的入射态。R0–R3 的一般 Slow 状态查询继续可用。能量依赖态、扫描相关态参数、未知系数能力会明确拒绝 Fast。没有把支持字段当作物理能力证明。

## 唯一公式归属与兼容边界

Li2026 响应多项式统一位于 `theory/li2026/responses.py::_response_polynomials`。Slow 使用味矩阵双线性项，Fast 使用算符外积，二者调用同一组多项式。`coefficients.py` 只负责匹配、核响应收缩及系数表示；旧 builder 的公式副本已移除，旧函数转发到该 owner。

新 Fast 使用 Slow 相同的单位换算 `GEV_INV2_TO_CM2`，没有全局归一化补偿。旧 Fast API 为兼容既有模板保留历史换算常数与数组语义。三个既有数据集的旧 full/diag/pair 数组全部与本轮修改前参考逐项完全一致。旧 Fast/Slow 约 4.17e-10 的相对换算差异仅在显式 legacy 路径保留；新模型链已通过严格一致性检查。

`legacy_csi2021_v1` 的线性折叠仅在总系数响应通过正半定检查后执行。单通道允许有符号贡献，不逐通道截断。核数、运行期及选择只施加一次。结果记录核指纹、实际参数、后端与舍入截断诊断。

## 缓存合同

独立 schema 为 `interface_kernel_v1`，轴顺序为 target/source/channel/operator_i/operator_j/observed_bin。保存 full、diag/pair、数组 dtype/shape 内容哈希和完整依赖记录，加载禁用 pickle。复数 pair 约定冻结为 `pair_im=-Im(H_ij)`。

内容键包括实际连续谱/谱线、源支撑和插值、曝光、核数、核响应资源内容、观测折叠、分箱、数值设置及相关实现内容。相同内容换路径可复用；同一路径改内容、效率、质量、曝光、选择、分箱或网格变化会拒用过时核。构造后核响应文件改变时须重建 interaction 快照。旧模板不补假的新指纹自动升级。

Wilson 扫描值及通过 SM 系数注入的 sin²θW 不编入 H；固定 rho 外置于重建，实际 rho 与参数写入 Prediction。统计数据、背景或误差改变无需重建物理核，实际 chi² 仍使用更新后的数据。

## 实际验证

| 检查 | 结果与证据 |
|---|---|
| 完整套件 | {tests} passed，0 failures/errors/skips；`outputs/refactor_r4/final_pytest.xml` |
| 新 Fast/Slow | 11 组参数/网格组合，全部 22 算符；逐源、逐核素、逐箱比较；max abs {fast['maximum_absolute_events']:.16g} events |
| full/pair 及文件往返 | 最大绝对差 {max(c['pair_and_reload_max_absolute'] for c in fast['cases']):.16g} events；保存/加载结果一致 |
| 单点单通道 | 22 算符的复味矩阵、固定相干 rho，逐通道与 Slow owner 比较，LNC/LNV 不干涉检查通过 |
| 扩展参数点 | SM、NP-only、SM+NP、复相位、多味及合法 LNV 非对角点，小/中网格验证通过 |
| 已有三数据集 | Slow 冻结参考继续通过；旧 Fast 的 15 组数组逐项完全相等 |
| 失效/完整性 | 同路径效率与核响应改动、参数/网格/分箱变化、损坏数组、旧格式均被拒绝 |
| 真正的插槽替换 | 源强×2、效率为零：先拒用原核，再重建并与 Slow 比较；原模型不变；replacement_cards.json |
| 发行导入 | wheel 构建成功；隔离 Python 在项目外从 wheel 导入，显式读取外置核响应，Slow/Fast 与存储往返通过 |
| 缓存可迁移 | 源码端生成的核在 wheel 端通过相同内容指纹加载及重建；wheel_smoke.json |

预设标准仍为 `abs(new-ref) <= 1e-12 + 1e-10*abs(ref)`，未更改既有数组或放宽容差。按容差归一的最差项为 `{worst_case['point']}/{worst_case['grid']}/{worst['source']}/{worst['isotope']}`，第 {worst['worst_bin']} 箱，使用允许误差的 {worst['fraction_of_allowed_error']:.9g}。逐箱工程一致性不代表新的科学收敛认证。

默认网格编译耗时约 {fast['compilation']['default']['seconds']:.3f} 秒；本次重建（含内容核验）约 0.013–0.026 秒/点。这些是本机本次记录，不是通用性能保证。详细输入、时长及误差见 fast_slow_comparison.json。

验证使用 `F:/Work/.codex_conda_envs/codex-py311/python.exe`，未安装或更新环境包。NumPy 最低版本明确为 2.0，与已使用的 `trapezoid` API 一致。首次 wheel 构建遇到系统临时目录权限问题，改用项目内临时目录、禁用索引及依赖安装后通过。

## 文件与发行产物

| 已有文件 | 动作 |
|---|---|
{table}

新增的生产职责集中于 `theory/li2026/coefficients.py`、`kernels/compiler.py`、`kernels/fingerprint.py`、`kernels/interface_storage.py`。保存前原文件与范围审阅差异位于 outputs/refactor_r4/original 和 review.diff；精确清单见 changes.json。没有修改实验输入或既有参考数组，没有改变工作流 Gate，没有创建项目副本。

用户文档：[组合式接口](README.md)、[Fast 与缓存](FAST_AND_CACHE.md)。说明包 17 份文档的范围、文件名、相对链接及 SHA256 清单已同步。能力和依赖图来自实际模型实例，见 resolved_model.json。

Wheel：`outputs/refactor_r4/dist/{artifact.name}`，SHA256 `{sha(artifact)}`。外置 data 仍由调用方明确传入，不宣称已打入 wheel。发行验证是隔离 wheel 导入与资源读取，没有向指定 Conda 环境执行安装。

## 恢复与边界

当前范围无待执行检查或资料阻塞。checkpoint.json 绑定当前源码与输入指纹；后续修改应先核对指纹，再运行相应测试。R0–R3 报告和参考继续作为历史阶段证据，不把其当作当前所有能力的描述。

可复现命令：

```powershell
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -m pytest -q tests --basetemp=.pytest-tmp/review-r4
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' tools/refactor/validate_interface_fast.py
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' tools/refactor/check_wheel.py
```

一般反中微子振幅及核响应外部物理审核仍沿用既有限制；当前统计仍是 legacy approximate statistics。这些不是本轮模块化工作中擅自修正或新增的物理模型。未安装或覆盖 Skill。
"""
    (PROJECT/"docs/interface_refactor/R4_R6_REPORT.md").write_text(report,encoding="utf-8")
    for p in (PROJECT/"docs/interface_refactor").glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)",p.read_text(encoding="utf-8")):
            if "://" not in target and not target.startswith("#"):
                assert (p.parent/target.split("#")[0]).is_file(),(p,target)
    scope={"objective":"modularity, explicit interfaces, common-model Fast and content cache",
           "stages_completed":["R4","R5 interface review (amended)","R6 offline distribution validation"],
           "user_scope_amendment":"external-data ingestion work package removed; no missing-data follow-up",
           "pending_checks":[],"blockers":[]}
    hashes={p.relative_to(PROJECT).as_posix():sha(p) for folder in ("src","tests","tools/refactor","docs/interface_refactor")
            for p in sorted((PROJECT/folder).rglob("*")) if p.is_file() and p.suffix in (".py",".md",".npz",".json") and "__pycache__" not in p.parts}
    hashes.update({name:sha(PROJECT/name) for name in ("README.md","pyproject.toml","requirements.txt")})
    checkpoint={"record_schema":"refactor_checkpoint_v1","task_id":"20261028-modular-interface-r4-r6","revision":1,
                "status":"VERIFIED","git_revision":None,"scope":scope,"file_fingerprints":hashes,
                "input_fingerprints":{p:h for p,h in before.items() if p.startswith(("data/","tests/reference/"))},
                "instruction_packet_fingerprints":changes["instruction_packet"],
                "distribution":{"path":artifact.relative_to(PROJECT).as_posix(),"sha256":sha(artifact)},
                "compiled_kernel_fingerprints":{key:value["fingerprint"] for key,value in fast["compilation"].items()},
                "completion_evidence":["final_pytest.xml","fast_slow_comparison.json","wheel_smoke.json","replacement_cards.json"],
                "next_action":"Current authorized modularity/interface scope is complete."}
    (out/"checkpoint.json").write_text(json.dumps(checkpoint,indent=2),encoding="utf-8")
    (out/"task_card.json").write_text(json.dumps(scope,indent=2),encoding="utf-8")
    print(f"Verified report: {tests} tests; Fast/Slow {fast['maximum_absolute_events']:.6g}; data/ref changes 0; links {links}")


if __name__=="__main__":
    main()
