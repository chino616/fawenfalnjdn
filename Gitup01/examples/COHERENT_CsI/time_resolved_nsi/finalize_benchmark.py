"""Read back exports, pin environments and publish scoped artifact inventories."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import numpy as np
import run_benchmark as nsi


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir",type=Path,required=True)
    parser.add_argument("--finalize",action="store_true")
    args=parser.parse_args();run=args.run_dir.resolve();root=nsi.ROOT
    record=nsi.BASE/"nsi_benchmark_20261108"
    example=Path(__file__).resolve().parent
    config=read(run/"NSI_CONFIG.json");validation=read(run/"VALIDATION_RESULTS.json")
    state=read(run/"SOURCE_STATE.json")
    changed=[name for name,value in state["files"].items() if sha(root/name)!=value]
    assert not changed,changed
    claims,sources=nsi.sm.inputs(nsi.BASE)  # Rechecks every pinned direct input.
    assert sha(root/"data/responses/responses_all.json")==config["response_sha256"]
    assert sha(example/"run_benchmark.py")==config["driver_sha256"]
    for file in example.glob("*.py"): ast.parse(file.read_text(encoding="utf-8"),filename=str(file))
    with np.load(run/"benchmark.npz",allow_pickle=False) as z:
        arrays={key:z[key] for key in z.files}
    points=read(run/"points.json");ids=list(arrays["point_ids"])
    counts=arrays["signal_counts"]
    for i,point in enumerate(points):
        delta=np.zeros((4,3,3),complex)
        for iq,q in enumerate(("u","d")):
            delta[iq]=-np.sqrt(2)*config["NSI_mapping"]["GF_GeV_minus2"]*np.array(point["epsilon_"+q]).T
        np.testing.assert_allclose(arrays["coefficients_GeV_minus2"][i]-arrays["coefficients_GeV_minus2"][0],delta,rtol=1e-11,atol=1e-19)
    with (run/"events_99bins.csv").open(encoding="utf-8",newline="") as stream: rows=list(csv.DictReader(stream))
    assert len(rows)==24*99
    for row in rows:
        i=ids.index(row["point_id"]);j=int(row["pe_bin"]);k=int(row["time_bin"])
        np.testing.assert_allclose([float(row["NSI_events"]),float(row["SM_events"])],[counts[i,j,k],counts[0,j,k]],rtol=2e-14,atol=2e-12)
    with (run/"components_99bins.csv").open(encoding="utf-8",newline="") as stream: components=list(csv.DictReader(stream))
    assert len(components)==24*2*3*99
    totals=np.zeros(24)
    for row in components: totals[ids.index(row["point_id"])]+=float(row["events"])
    np.testing.assert_allclose(totals,counts.sum(axis=(1,2)),rtol=2e-14,atol=2e-10)
    index={name:i for i,name in enumerate(ids)}
    mixed=counts[index["mixed_ud_emu"]]-counts[0]
    separate=(counts[index["u_emu_plus"]]-counts[0])+.25*(counts[index["d_emu_plus"]]-counts[0])
    interference=float((mixed-separate).sum())
    assert interference<0 and float(mixed.sum())>0
    checks={"date":"2026-11-08","status":"PASS","CSV_rows":len(rows),"component_CSV_rows":len(components),
        "point_count":len(points),"original_code_files_unchanged":len(state["files"]),"direct_sources_rechecked":len(sources["sources"]),
        "total_SM_plus_NSI_Wilson_matrices_recover_epsilon_mapping":True,
        "source_table_and_primary_authenticity_are_distinct":True,
        "mixed_ud_cross_term_events":interference,
        "mixed_ud_derivation":"DeltaN(u=.1,d=-.05)-DeltaN(u=.1,d=0)-.25*DeltaN(u=0,d=.1); offdiagonal sign symmetry and quadratic coefficient reconstruction",
        "CSV_NPZ_counts_and_component_sums_agree":True,
        "plot_visual_QA":"Three PNG groups inspected; flavor legend moved above bars; no clipped labels",
        "scope":"Numerical/format/source-fingerprint checks of the authorized local-input forward benchmark, not external authorship or paper equivalence"}
    if not args.finalize:
        write(run/"EXPORT_CHECKS.json",checks)
        plot_python="F:/Work/.codex_conda_envs/codex-py311/python.exe"
        environment=dict(os.environ);environment.pop("PYTHONPATH",None);environment["PYTHONIOENCODING"]="utf-8"
        plot_versions=json.loads(subprocess.check_output([plot_python,"-B","-c",
            "import sys,json,numpy,matplotlib;print(json.dumps({'python':sys.version,'numpy':numpy.__version__,'matplotlib':matplotlib.__version__}))"],env=environment,text=True,encoding="utf-8"))
        write(run/"RUN_ENVIRONMENT.json",{"date":"2026-11-08","timezone":"Asia/Shanghai","calculation_python":sys.executable,
            "python_version":sys.version,"dependencies":{name:importlib.metadata.version(name) for name in ("numpy","scipy","uproot","PyYAML","pytest")},
            "validation_dependency_path":os.environ.get("PYTHONPATH"),"thread_settings":{"OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1"},
            "plot_python":plot_python,"plot_versions":plot_versions,"plot_environment":"PYTHONPATH cleared to preserve CPython3.11 ABI",
            "main_cwd":str(root),"legacy_time_directory":str(Path(config["NSI_mapping"]["source"]["path"]).parents[1]),
            "commands":"Exact grid/settings in per-grid report.json; complete reproducible sequence in examples/COHERENT_CsI/time_resolved_nsi/README.md",
            "runtime_test_command":"python -B -m pytest -q tests/test_component_replacement.py tests/test_rates_differential_flavor.py tests/test_nuclear_response_convention.py --junitxml=outputs/csi2021_time_nsi_20261108/runtime-tests.xml",
            "validation_command":"python -B examples/COHERENT_CsI/time_resolved_nsi/validate_benchmark.py --run-dir outputs/csi2021_time_nsi_20261108 --legacy-time-dir OLD --stage precision --finest grid_1024_1920"})
        snapshot=run/"CODE_SNAPSHOT.zip"
        if snapshot.exists():
            prior=run/"revisions/PRE_DOCUMENT_CODE_SNAPSHOT.zip"
            revision=1
            while prior.exists():
                revision+=1
                prior=run/"revisions"/(f"PRE_DOCUMENT_CODE_SNAPSHOT_{revision:02d}.zip")
            prior.write_bytes(snapshot.read_bytes())
        files=[root/name for name in state["files"]]+list(example.glob("*.py"))+list(example.glob("*.mjs"))
        with zipfile.ZipFile(snapshot,"w",zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(set(files)): archive.write(file,file.relative_to(root).as_posix())
            for row in [config["NSI_mapping"]["source"],*config["legacy_time_files"].values()]:
                file=Path(row["path"]);assert sha(file)==row["sha256"]
                archive.write(file,"read_only_legacy/"+file.relative_to(Path(config["NSI_mapping"]["source"]["path"]).parents[1]).as_posix())
    else:
        docs=read(run/"DOCUMENT_LINK_CHECKS.json");assert docs["status"]=="PASS"
        assert checks==read(run/"EXPORT_CHECKS.json")
        report=("# 本轮验收与范围\n\n2026-11-08。24个实对称u/d矢量NSI点的未拟合信号计算完成。\n\n"
            f"- 原生Slow同网格全24点通过；独立T/Eν/PE最大箱差均<0.005 events。\n"
            f"- {len(rows)}行比较CSV和{len(components)}行分量CSV回读与NPZ一致。\n"
            f"- 原{len(state['files'])}个package/SM helper文件不变，{len(sources['sources'])}个直接输入源SHA再核通过。\n"
            f"- 24项相关Runtime测试通过；{len(docs['documents'])}份文档的{docs['localLinksAndAnchors']}个本地链接/图片/锚点通过，三份报告各8个目录跳转/返回已实际执行，编号公式KaTeX及720px预览通过。\n"
            "- 三组PNG已目视检查，SVG/PNG与最终NPZ通过绘图元数据关联。\n\n"
            "512/960独立Eν误差0.00514593365未通过的原始结果保留，最终采用1024/1920；未放宽容差。来源真实性、严格论文Helm/辐射修正等价、BRN/NIN绝对归一及统计区间仍按主报告/P02保留，不将本轮局部验收称作全仓库通过。\n\n"
            "[完整报告](BENCHMARK.md) · [机器结果](VALIDATION_RESULTS.json) · [导出核对](EXPORT_CHECKS.json) · [文档检查](DOCUMENT_LINK_CHECKS.json) · [文件清单](ARTIFACT_MANIFEST.json)\n")
        (run/"REVIEW_REPORT.md").write_text(report,encoding="utf-8",newline="\n")
    modified=[root/name for name in ("examples/COHERENT_CsI/README.md","outputs/README.md",
        "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/README.md","docs/experiments/COHERENT/CsI2021/time_resolved/README.md")]
    documents=[root/"docs/experiments/COHERENT/CsI2021/time_resolved/NSI_BENCHMARK.md"]
    inventory=sorted(set([file for folder in (run,record,example) for file in folder.rglob("*") if file.is_file() and "__pycache__" not in file.parts]+modified+documents))
    self_files={run/"ARTIFACT_MANIFEST.json",run/"CHANGE_MANIFEST.json"}
    def owner(file):
        if file.is_relative_to(run):return run/"README.md"
        if file.is_relative_to(record):return record/"README.md"
        if file.is_relative_to(example):return example/"README.md"
        if file.parent.name=="time_resolved":return file.parent/"README.md"
        return file if file.name=="README.md" else file.parent/"README.md"
    entries=[{"path":file.relative_to(root).as_posix(),"operation":"modify" if file in modified else "create",
        "owner_readme":owner(file).relative_to(root).as_posix(),"sha256":sha(file),"bytes":file.stat().st_size} for file in inventory if file not in self_files]
    change={"date":"2026-11-08","authorization":"User requested NSI benchmark and explicitly selected unfitted event counts versus SM",
        "route":"validation_only","scope":"New examples, output/run records and parent navigation; no production physics or numerical resource change",
        "runtime_source_changed":False,"original_response_changed":False,"frozen_reference_changed":False,"active_registry_changed":False,
        "canonical_P08_or_statistics_freeze_inferred":False,"protection_hashes_refreshed":False,
        "backups":["backup/csi-nsi-benchmark-20261108-0"+str(i)+"/" for i in range(1,8)],"files":entries,
        "document_validation": "PASS" if args.finalize else "PENDING",
        "manifest_self_entries":["outputs/csi2021_time_nsi_20261108/CHANGE_MANIFEST.json","outputs/csi2021_time_nsi_20261108/ARTIFACT_MANIFEST.json"]}
    artifact={"date":"2026-11-08","status":"SCOPED_DELIVERY_CHECKED" if args.finalize else "PRE_DOCUMENT_CHECKS",
        "files":entries,"self_exclusions":change["manifest_self_entries"],"original_code_files_unchanged":len(state["files"]),
        "response_sha256":config["response_sha256"],"strict_paper_reproduction":False}
    if args.finalize:
        for name in ("ARTIFACT_MANIFEST.json","CHANGE_MANIFEST.json"):
            prior=run/"revisions"/("PRE_DOCUMENT_"+name)
            if prior.exists():raise FileExistsError("Do not overwrite earlier delivery revision")
            prior.write_bytes((run/name).read_bytes())
            previous={"path":prior.relative_to(root).as_posix(),"operation":"create","owner_readme":(run/"README.md").relative_to(root).as_posix(),"sha256":sha(prior),"bytes":prior.stat().st_size}
            entries.append(previous)
    write(run/"CHANGE_MANIFEST.json",change);write(run/"ARTIFACT_MANIFEST.json",artifact)
    print(json.dumps({"status":artifact["status"],"files":len(entries),"sources":len(sources["sources"]),"original_code_unchanged":len(state["files"])}))


if __name__=="__main__":main()
