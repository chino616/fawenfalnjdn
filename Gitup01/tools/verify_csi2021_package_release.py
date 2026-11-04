"""Validate the package adapter in a wheel and in isolated lifecycle transactions."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n","utf-8")


def run(command,cwd,log,environment=None):
    process=subprocess.run(command,cwd=cwd,env=environment,capture_output=True,text=True,encoding="utf-8")
    log.write_text(process.stdout+"\n"+process.stderr,"utf-8")
    if process.returncode:
        raise RuntimeError(f"{command!r} failed ({process.returncode}). See {log}")
    return process.stdout


def wheel_check(output,package):
    stage=output/"build_source"
    stage.mkdir()
    shutil.copytree(ROOT/"cevns_pyeft",stage/"cevns_pyeft",ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    for name in ["pyproject.toml","README.md"]:shutil.copyfile(ROOT/name,stage/name)
    wheels=output/"wheels"
    wheels.mkdir()
    temporary=output/"build_temp"
    temporary.mkdir()
    environment={**os.environ,"TEMP":str(temporary),"TMP":str(temporary),
                 "PYTHONDONTWRITEBYTECODE":"1","OPENBLAS_NUM_THREADS":"1"}
    run([sys.executable,"-B","-m","pip","wheel",str(stage),"--no-build-isolation","--no-deps",
         "--no-index","--no-cache-dir","--wheel-dir",str(wheels)],output,output/"wheel_build.log",environment)
    wheel=next(wheels.glob("*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        names=archive.namelist()
        for needed in ["cevns_pyeft/experiments/input_package.schema.json",
                       "cevns_pyeft/experiments/coherent/csi2021_package_contract.json",
                       "cevns_pyeft/experiments/coherent/csi2021_package.py"]:
            assert needed in names,needed
    installed=output/"installed_wheel"
    run([sys.executable,"-B","-m","pip","install","--no-index","--no-deps","--no-cache-dir",
         "--target",str(installed),str(wheel)],output,output/"wheel_install.log",environment)
    case=output/"external_case"
    case.mkdir()
    inputs=case/"input"
    inputs.mkdir()
    for name in ["experiment.input.yaml","experiment.resources.npz","experiment.physics.md"]:
        shutil.copyfile(package/name,inputs/name)
    probe=case/"probe.py"
    code=r'''from pathlib import Path
import sys,json,importlib.abc
installed=Path(sys.argv[1]).resolve()
inputs=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(installed))
class BlockLegacy(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname.endswith("csi2021_definition"):
   raise ImportError("legacy dataset definition forbidden in package-only release check")
sys.meta_path.insert(0,BlockLegacy())
import cevns_pyeft
assert Path(cevns_pyeft.__file__).resolve().is_relative_to(installed)
from cevns_pyeft.experiments.coherent.csi2021_package import load_package_experiment
from cevns_pyeft.experiments.runtime import predict_experiment,evaluate_experiment,compile_experiment
from cevns_pyeft.kernels.interface_storage import save_compiled_kernel,load_compiled_kernel
import numpy as np
e=load_package_experiment(inputs)
settings={"n_er":5,"n_enu":12,"n_pe_bin":3}
p=predict_experiment(e,numerics=settings)
f=evaluate_experiment(e,p)
kernel=compile_experiment(e,numerics=settings)
save_compiled_kernel(Path.cwd()/"candidate_full22_kernel.npz",kernel)
loaded=load_compiled_kernel(Path.cwd()/"candidate_full22_kernel.npz",model=e.model)
fast=predict_experiment(e,numerics=settings,backend="fast",kernel=loaded)
np.testing.assert_allclose(fast.counts,p.counts,rtol=1e-11,atol=1e-12)
result={"status":"PASS","module":str(Path(cevns_pyeft.__file__).resolve()),
"events":float(p.counts.sum()),"chi2_legacy_approximate":f.chi2,"alpha":f.alpha,"beta":f.beta,
"component_count":len(p.combined_prediction.components),"compiled_basis_count":len(kernel.basis_keys),
"kernel_shape":list(kernel.full_kernel.shape),"max_abs_slow_fast":float(np.max(np.abs(fast.counts-p.counts))),
"kernel_role":"engineering small-grid candidate; formal P08 acceptance remains separate",
"legacy_definition_loaded":any(m.endswith("csi2021_definition") for m in sys.modules)}
assert not result["legacy_definition_loaded"]
(Path.cwd()/"result.json").write_text(json.dumps(result,indent=2),"utf-8")
print(json.dumps(result))
'''
    probe.write_text(code,"utf-8")
    run([sys.executable,"-I","-B",str(probe),str(installed),str(inputs)],case,output/"wheel_probe.log",environment)
    result=json.loads((case/"result.json").read_text("utf-8"))
    result.update(wheel=str(wheel),wheel_sha256=hashlib.sha256(wheel.read_bytes()).hexdigest())
    write(output/"wheel_result.json",result)
    return result


def snapshot(root):
    areas=["cevns_pyeft","data","configs"]
    values={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for area in areas for p in (root/area).rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    values["README.md"]=hashlib.sha256((root/"README.md").read_bytes()).hexdigest()
    return values


def lifecycle_check(output):
    from cevns_pyeft.experiments import management as manager
    root=output/"managed_copy"
    root.mkdir()
    for name in ["cevns_pyeft","data","configs"]:
        shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    (root/"README.md").write_text("# Isolated management verification\n\n"
        "[CsI definition](cevns_pyeft/experiments/coherent/csi2021_definition.py)\n"
        "[Ar definition](cevns_pyeft/experiments/coherent/ar2020_definition.py)\n","utf-8")
    assert manager.audit(root)["status"]=="PASS"
    before=snapshot(root)
    baseline=manager._probe(root)
    exported=manager.export_package(root,"CsI2021",output/"CsI2021_transfer.zip")
    with zipfile.ZipFile(exported["package"]) as archive:
        names=archive.namelist()
        assert any("experiment.input.yaml" in n for n in names)
        assert any("experiment.resources.npz" in n for n in names)
        assert any("csi2021_package.py" in n for n in names)
    removal=manager.apply_plan(manager.make_plan(root,"uninstall","CsI2021"))
    assert removal["status"]=="COMMITTED"
    assert not (root/"data/experiments/COHERENT_CsI/CsI2021/experiment.input.yaml").exists()
    assert manager.describe(root,"CsI2021")["installed"] is False
    assert (root/"data/responses/responses_all.json").is_file()
    installed=manager.apply_plan(manager.make_plan(root,"install",package=exported["package"],activate=True))
    assert installed["status"]=="COMMITTED"
    restored=manager._probe(root)
    for key in baseline:
        np = __import__("numpy")
        np.testing.assert_allclose(restored[key]["counts"],baseline[key]["counts"],rtol=1e-12,atol=1e-12)
    rollback_install=manager.rollback(root,installed["transaction_id"])
    rollback_remove=manager.rollback(root,removal["transaction_id"])
    assert rollback_install["status"]==rollback_remove["status"]=="ROLLED_BACK"
    assert snapshot(root)==before
    result={"status":"PASS","audit":manager.audit(root),"actual_fresh_process_baseline":baseline,
        "restored_fresh_process_results":restored,"uninstall":removal["transaction_id"],
        "reinstall":installed["transaction_id"],"rollback_install":rollback_install["status"],
        "rollback_remove":rollback_remove["status"],"all_original_file_hashes_restored":True,
        "three_formal_inputs_transferred":True,"canonical_repository_lifecycle_untouched":True}
    write(output/"lifecycle_result.json",result)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--package",type=Path,default=ROOT/"data/experiments/COHERENT_CsI/CsI2021")
    parser.add_argument("--mode",choices=["wheel","lifecycle"],required=True)
    args=parser.parse_args()
    output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    if args.mode=="wheel":result=wheel_check(output,args.package.resolve())
    else:result=lifecycle_check(output)
    print(json.dumps({"mode":args.mode,"status":result["status"],"output":str(output)}))


if __name__=="__main__":
    main()

