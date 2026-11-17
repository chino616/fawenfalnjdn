"""Render/check latest-analysis navigation; never register or activate a dataset.

The JSON index owns links and descriptions of processing methods. Scientific
numbers, input choices and approvals remain in the linked original records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs/experiments/latest_analysis_index.json"
START, END = "<!-- latest-analyses:start -->", "<!-- latest-analyses:end -->"


def load_index(root=ROOT):
    return json.loads((Path(root) / "docs/experiments/latest_analysis_index.json").read_text(encoding="utf-8"))


def file_link(label, target, source, root=ROOT):
    target = (Path(root) / target).resolve()
    return f"[{label}](<{os.path.relpath(target, Path(source).parent).replace(chr(92), '/')}>)"


def readme_section(root, source):
    root, source = Path(root), Path(source)
    index = load_index(root)
    relative = source.relative_to(root).as_posix()
    rows = [row for row in index["analyses"] if relative in row.get("readmes", [])]
    if not rows:
        return ""
    text = [START, "", "## 当前最新分析与处理方式", "",
            file_link("五条实验最新入口", "docs/experiments/LATEST_EXPERIMENTS.md", source, root), "",
            "| 分析 | 方法/版本 | 输入 | 结果与核对范围 |", "|---|---|---|---|"]
    for row in rows:
        text.append("| " + " | ".join([
            row["title"], file_link(row["version"] + "；处理方式", row["methods_file"], source, root),
            file_link("当前输入", row["input"], source, root),
            " / ".join(file_link(result["label"], result["path"], source, root) for result in row["results"]),
        ]) + " |")
    text.extend(["", "来源/审核状态、计算完成状态与默认Runtime注册分别记录；链接不授予新的科学批准。", "", END])
    return "\n".join(text) + "\n"


def render_methods(row, source, root=ROOT):
    lines = ["# " + row["title"] + "：当前处理方式", "",
             f"版本：**{row['version']}**；analysis_id：`{row['analysis_id']}`。", "",
             row["purpose"], "", "| 层次 | 本分析采用的处理 |", "|---|---|"]
    lines += [f"| {key} | {value} |" for key, value in row["processing"].items()]
    lines.extend(["", "## 文件与运行入口", ""])
    for label, key in (("Onboarding/物理说明", "onboarding"), ("当前输入", "input"),
                       ("复算/验证入口", "entry"), ("来源/证据", "evidence")):
        lines.append("- " + file_link(label, row[key], source, root))
    lines.extend("- " + file_link(item["label"], item["path"], source, root) for item in row["results"])
    lines.extend(["", "## 当前范围与限制", "", *["- " + x for x in row["limitations"]], "",
                  file_link("返回最新实验总入口", "docs/experiments/LATEST_EXPERIMENTS.md", source, root), ""])
    return "\n".join(lines)


def render_main(index, source, root=ROOT):
    lines = ["# 当前五条实验主线：最新版本与处理方式", "",
             "2026-11-11。此入口只列用户选定实验的当前版本。不同分析方法的输入、代码与结果分别链接；旧版本保留在原历史位置。", "",
             file_link("对应文件夹构造", "docs/experiments/LATEST_FOLDER_LAYOUT.md", source, root), "",
             "| 实验/分析 | 当前版本 | 方法说明 | Onboarding/输入 | 结果 |",
             "|---|---|---|---|---|"]
    for row in index["analyses"]:
        lines.append("| " + " | ".join([row["title"], row["version"],
            file_link("METHODS.md", row["methods_file"], source, root),
            file_link("说明", row["onboarding"], source, root) + " / " + file_link("输入", row["input"], source, root),
            " / ".join(file_link(x["label"], x["path"], source, root) for x in row["results"]),
        ]) + " |")
    lines.extend(["", "## 方法之间的区别", "",
        "| 分析 | 观测与探测器处理 | 统计/结果性质 |", "|---|---|---|"])
    for row in index["analyses"]:
        lines.append(f"| {row['title']} | {row['processing']['观测与响应']} | {row['processing']['统计与能力']} |")
    lines.extend(["", "## Gitup01内的归属", "",
        "- docs/experiments：当前说明、METHODS和可点击阅读入口。",
        "- data/experiments、data/benchmarks：原物理输入和明确分析专属的数值基准。",
        "- examples：调用公共引擎的复算/验证脚本；CsI-time已采用本地时间模块。",
        "- outputs：最新计算的数值、图、缓存与验证；同次运行内的网格比较是收敛证据。",
        "- workflows/.../runs：来源、决定、合同与阶段记录；不作为Runtime代码依赖。", "",
        "CONUS+最新SM/NSI已在Gitup01内按上述职责集中；历史输入实现仅保存一份压缩证据，计算入口使用本地显式资源。",
        "数值、DRAFT/PARTIAL、NOT_REVIEWED及Ar单位冲突等限制保持原记录；目录迁入不自动激活新Runtime dataset。", "",
        file_link("本次整理与验证", "outputs/latest_layout_20261111/README.md", source, root), ""])
    return "\n".join(lines)


def render_layout():
    return """# 当前五条实验对应的文件夹构造

这是本次整理后的最新版本视图。每个METHODS.md说明观测轴、响应、核结构、统计方式、结果性质及限制；完整源码与历史材料不在此树重复展开。

```text
Gitup01/
├─ docs/experiments/
│  ├─ LATEST_EXPERIMENTS.md             最新实验总入口
│  ├─ latest_analysis_index.json        同一入口的机器索引
│  ├─ LATEST_FOLDER_LAYOUT.md           本文件
│  ├─ PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/
│  │  ├─ SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md
│  │  ├─ PandaX4T.singlebin.physics.v3.2.1.md
│  │  ├─ XENONnT.singlebin.physics.v3.2.1.md
│  │  └─ METHODS.md
│  ├─ COHERENT/
│  │  ├─ CsI2021/time_resolved/          时间分析：onboarding、SM/NSI报告、METHODS
│  │  ├─ CsI2017/                       25箱说明与METHODS
│  │  └─ Ar2020/                        12箱说明与METHODS
│  └─ CONUS_Plus/datasets/conusplus_kkl_run1/
│     ├─ experiment.physics.md          当前v3 onboarding
│     ├─ experiment.physics.summary.md
│     ├─ METHODS.md                     SM和NSI的处理区别
│     └─ benchmarks/
│        ├─ sm_response_20261106/SM_BENCHMARK.md
│        └─ nsi_response_20261106/NSI_BENCHMARK.md
├─ data/
│  ├─ experiments/
│  │  ├─ COHERENT_CsI/CsI2017/          YAML、NPZ、Physics MD；确定性25箱
│  │  ├─ COHERENT_CsI/CsI2021/time_resolved/
│  │  │  ├─ analysis_inputs.npz         当前99箱、时间边缘和分析数组
│  │  │  ├─ nuclear_response_CsI.npz    核表切片，仅供来源核对
│  │  │  └─ README.md
│  │  ├─ COHERENT_Ar/Ar2020/            YAML、NPZ、Physics MD；专用12箱折叠
│  │  └─ CONUS_Plus/conusplus_kkl_run1/ Flux、Ge库存、观测及来源映射
│  ├─ benchmarks/
│  │  ├─ solar_b8_singlebin_2601_19883/ 三样本独立card、接受度、拟合信号
│  │  ├─ COHERENT_CsI/CsI2021_time/nsi_20261108/points.json
│  │  └─ CONUS_Plus/conusplus_kkl_run1/
│  │     ├─ sm_response_20261106/        SM论文图线基准
│  │     └─ nsi_response_20261106/       NSI区间/轮廓基准与统计准备
│  └─ responses/responses_all.json      共用原核响应
├─ examples/
│  ├─ COHERENT_CsI/
│  │  ├─ time_resolved_common/          本地时间模块、纯NSI映射、ORIGIN.json
│  │  ├─ time_resolved_sm/              SM前向、验证、绘图
│  │  └─ time_resolved_nsi/             24点NSI前向、验证、绘图
│  └─ CONUS_Plus/conusplus_kkl_run1/
│     ├─ run_benchmark.py               --method sm 或 --method nsi
│     ├─ conusplus_paths.py             本地路径、输入指纹、新输出保护
│     ├─ LOCAL_INPUTS.json
│     ├─ sm_response/                  唯一SM装配及计算/核对/报告
│     └─ nsi_response/                 复用SM装配的NSI映射、核、拟合与报告
├─ tools/
│  ├─ latest_experiments.py             生成/检查最新入口、METHODS及README导航
│  └─ run_solar_b8_singlebin_benchmark.py
├─ outputs/
│  ├─ solar_b8_singlebin/20261111_response_run2/
│  ├─ csi2021_time_sm_20261107/
│  ├─ csi2021_time_nsi_20261108/
│  ├─ csi2021_time_sm_data_comparison_20261109/
│  ├─ COHERENT_CsI/CsI2017/sm_legacy_25bin_20261111/SM_RESULT.json
│  ├─ COHERENT_Ar/Ar2020/sm_legacy_12bin_20261111/SM_RESULT.json
│  ├─ CONUS_Plus/conusplus_kkl_run1/
│  │  ├─ sm_response_20261106/           最新SM数值、图、收敛证据
│  │  ├─ nsi_response_20261106/          最新NSI数值、图、核与验证
│  │  └─ provenance/response_20261106_source.zip
│  └─ latest_layout_20261111/           本次迁移、回滚映射和实际验证
├─ workflows/cevns-pyeft/runs/
│  ├─ COHERENT_CsI/CsI2021/time_resolved/来源、证据、合同及原数组证据
│  └─ CONUS_Plus/conusplus_kkl_run1/
│     ├─ P00/P01/P02/P03等来源与合同
│     └─ benchmarks/
│        ├─ sm_response_20261106/       SM原执行/阶段记录
│        └─ nsi_response_20261106/      NSI原执行/阶段记录
└─ cevns_pyeft/                         共用引擎；现有dataset注册保持原状
```

CsI2017与Ar2020的当前数值是已执行的指定回归网格核对，不被目录名称提升为默认网格收敛结论。CONUS+与CsI-time的原科学来源/审核限制继续保留。

[返回最新入口](LATEST_EXPERIMENTS.md) · [本次整理与验证](../../outputs/latest_layout_20261111/README.md)
"""


def generated(root=ROOT):
    root = Path(root)
    index = load_index(root)
    result = {root / "docs/experiments/LATEST_EXPERIMENTS.md": render_main(index, root / "docs/experiments/LATEST_EXPERIMENTS.md", root)}
    result[root / "docs/experiments/LATEST_FOLDER_LAYOUT.md"] = render_layout()
    for row in index["analyses"]:
        source = root / row["methods_file"]
        result[source] = render_methods(row, source, root)
    for relative in sorted({name for row in index["analyses"] for name in row.get("readmes", [])}):
        path = root / relative
        original = path.read_text(encoding="utf-8-sig")
        section = readme_section(root, path)
        if START in original:
            if original.count(START) != 1 or original.count(END) != 1:
                raise ValueError("Invalid latest-analysis markers: " + relative)
            original = re.sub(re.escape(START) + r"[\s\S]*?" + re.escape(END) + r"\n?", section, original)
        else:
            original = original.rstrip() + "\n\n" + section
        result[path] = original
    return result


def check(root=ROOT):
    root = Path(root).resolve()
    index = load_index(root)
    errors, ids = [], set()
    for row in index["analyses"]:
        if row["analysis_id"] in ids:
            errors.append("duplicate analysis: " + row["analysis_id"])
        ids.add(row["analysis_id"])
        references = [row[key] for key in ("methods_file", "onboarding", "input", "entry", "evidence")]
        references.extend(x["path"] for x in row["results"])
        references.extend(row.get("readmes", []))
        if row.get("input_origin"):
            references.append(row["input_origin"])
        for name in references:
            path = (root / name).resolve()
            if not path.is_relative_to(root) or not path.exists():
                errors.append("missing or outside Gitup01: " + name)
        if len(row["processing"]) < 4 or not row["limitations"]:
            errors.append("method distinction/limitations incomplete: " + row["analysis_id"])
        if row.get("input_origin"):
            adopted, origin = root / row["input"], root / row["input_origin"]
            if adopted.is_file() and origin.is_file() and hashlib.sha256(adopted.read_bytes()).digest() != hashlib.sha256(origin.read_bytes()).digest():
                errors.append("adopted input differs from its source evidence: " + row["analysis_id"])
    for path, expected in generated(root).items():
        if not path.is_file() or path.read_text(encoding="utf-8-sig") != expected:
            errors.append("generated navigation differs: " + path.relative_to(root).as_posix())
    return {"status": "FAIL" if errors else "PASS", "analyses": len(ids), "errors": errors,
            "scope": "latest navigation and method distinctions, not scientific approval"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        # Save exact pre-edit copies; this index never changes a physical input.
        backup = ROOT / "backup/latest-index-20261111-run01"
        for path, text in generated().items():
            if path.exists() and path.read_text(encoding="utf-8-sig") == text:
                continue
            if path.exists():
                target = backup / path.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_bytes(path.read_bytes())
                    with (ROOT / "backup/BACKUP_MANIFEST.md").open("a", encoding="utf-8") as h:
                        h.write(f"\n- 2026-11-11 latest-index: `{path.relative_to(ROOT).as_posix()}` → "
                                f"`{target.relative_to(ROOT).as_posix()}`; SHA256 `{hashlib.sha256(path.read_bytes()).hexdigest()}`.\n")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    result = check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result["status"] != "PASS"


if __name__ == "__main__":
    raise SystemExit(main())
