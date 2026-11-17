"""Independent native-Slow, NSI flavor-flow and numerical precision checks."""
from __future__ import annotations

import argparse
from dataclasses import replace, asdict
import json
from pathlib import Path
import time

import numpy as np
import run_benchmark as nsi
from cevns_pyeft.core.predict import predict
from cevns_pyeft.contracts.parameters import IntegrationSettings
from cevns_pyeft.kernels.compiler import compile_fast


def load(folder):
    with np.load(folder / "prediction.npz", allow_pickle=False) as source:
        arrays = {key: source[key] for key in source.files}
    return arrays, json.loads((folder / "report.json").read_text(encoding="utf-8"))


def max_difference(a, b):
    delta = np.asarray(b)-np.asarray(a)
    index = np.unravel_index(np.abs(delta).argmax(), delta.shape)
    maximum = float(np.max(np.abs(delta)))
    return {"max_bin_difference_events": maximum, "worst_index": list(map(int,index)),
        "threshold_events": .005, "status": "PASS" if maximum < .005 else "FAIL"}


def evaluate(kernel, model, points, mapping, sin2, time_weights):
    rhos = np.asarray([component.fixed_state_for_fast().rho for component in model.source.for_run(model.run).components])
    energy = np.array([nsi.cached_evaluate(kernel, model, nsi.point_parameters(point,mapping,sin2),rhos)[0] for point in points])
    return energy[...,None]*time_weights[None,None,:,None,:]


def native_checks(run, legacy):
    pilot, metadata = load(run / "pilot")
    points = json.loads((run / "pilot/points.json").read_text(encoding="utf-8"))
    mapping = nsi.legacy_mapping(legacy)
    model, claims, _, tables = nsi.frame(nsi.BASE,legacy)
    numerical = IntegrationSettings(**metadata["numerical_settings"])
    samples = np.arange(0,60+.5*numerical.observed_step,numerical.observed_step)
    # Same exact native P06 node values, already independently tested in SM.
    model = replace(model, observation=replace(model.observation,
        response=nsi.sm.ExactSampledGammaResponse(model.observation.response,samples)))
    native = []
    records = []
    for i,point in enumerate(points):
        started=time.perf_counter()
        prediction=predict(model,parameters=nsi.point_parameters(point,mapping,claims["C_SIN2_PAPER"]["value"]),numerics=numerical,backend="slow")
        energy=np.array([[prediction.components[(c,t)] for c in nsi.SOURCE_IDS] for t in nsi.TARGETS])
        parts=tables["reference_window"].apply(energy,counts_include_time_acceptance=False)
        reference=pilot["target_component_counts"][i]
        np.testing.assert_allclose(parts,reference,rtol=5e-11,atol=2e-9)
        native.append(parts)
        row={"id":point["id"],"max_target_component_bin_error":float(np.max(np.abs(parts-reference))),
            "status":"PASS","elapsed_s":time.perf_counter()-started}
        records.append(row);print(json.dumps(row),flush=True)
    u=np.array(points[16]["epsilon_u"])
    for point in points:
        for q in ("u","d"):
            epsilon=np.array(point["epsilon_"+q])
            actual=mapping.vector_nsi_wilson(np.array(point["epsilon_u"]),np.array(point["epsilon_d"]))[(6,1,q)]
            np.testing.assert_array_equal(actual,-np.sqrt(2)*nsi.G_F*epsilon.T)
            np.testing.assert_array_equal(epsilon,epsilon.T)
    bad=np.zeros((3,3));bad[0,1]=.1
    rejected=[]
    for name, bad_matrix in [("non_Hermitian",bad),("complex_phase",1j*np.eye(3)),("nonfinite",np.full((3,3),np.nan))]:
        try:mapping.vector_nsi_wilson(bad_matrix)
        except ValueError:rejected.append(name)
        else:raise AssertionError("Unsupported NSI input accepted: "+name)
    result={"date":"2026-11-08","status":"PASS","scope":"All24 declared real symmetric NSI points, same native full-energy Slow and same physical inputs at16/40 pilot grid",
        "pilot_precision_is_scientifically_frozen":False,"max_native_bin_error":max(row["max_target_component_bin_error"] for row in records),
        "records":records,"mapping_formula":"C61q=-sqrt(2) G_F epsilon_q.T, GeV^-2","unsupported_inputs_rejected":rejected,
        "driver_sha256":nsi.sm.sha(nsi.__file__),"validator_sha256":nsi.sm.sha(__file__)}
    nsi.sm.write_json(run/"NATIVE_SLOW_CHECKS.json",result)
    np.savez_compressed(run/"native_slow_checks.npz",native=np.array(native),compiled=pilot["target_component_counts"],differences=np.array(native)-pilot["target_component_counts"])
    return result


def precision_checks(run,legacy,finest):
    arrays,metadata=load(run/finest)
    points=json.loads((run/finest/"points.json").read_text(encoding="utf-8"))
    mapping=nsi.legacy_mapping(legacy)
    original,claims,register,tables=nsi.frame(nsi.BASE,legacy)
    model=replace(original,interaction=nsi.CheckedCoefficientEnergy(original.interaction))
    sin2=claims["C_SIN2_PAPER"]["value"]
    numerical=IntegrationSettings(**metadata["numerical_settings"])
    native=json.loads((run/"NATIVE_SLOW_CHECKS.json").read_text(encoding="utf-8"))
    equivalence=json.loads((run/"COEFFICIENT_ENERGY_EQUIVALENCE.json").read_text(encoding="utf-8"))
    assert native["status"]==equivalence["status"]=="PASS"
    checks=[]
    def passed(name,**details):
        checks.append({"name":name,"status":"PASS",**details});print(json.dumps({"check":name,"status":"PASS"}),flush=True)
    parts=arrays["target_component_counts"]
    assert parts.shape==(len(points),2,3,9,11)
    assert np.isfinite(parts).all() and np.all(parts>=0)
    np.testing.assert_allclose(parts.sum(axis=(1,2)),arrays["signal_counts"],rtol=2e-14,atol=2e-11)
    passed("nonnegative_counts_source_target_axes_and_projection_closure",shape=list(parts.shape))
    with np.load(nsi.SM_RUN/"grid_512_960/prediction.npz",allow_pickle=False) as sm:
        if numerical.n_er==512 and numerical.n_enu==960:
            np.testing.assert_allclose(parts[0],sm["target_component_counts"],rtol=5e-12,atol=2e-10)
            sm_error=float(np.max(np.abs(parts[0]-sm["target_component_counts"])))
        else:
            sm_error=float(np.max(np.abs(parts[0]-sm["target_component_counts"])))
            assert sm_error<.005
    passed("zero_NSI_recovers_previous_SM",max_bin_error=sm_error,previous_SM_total=353.46560868634367,current_SM_total=float(parts[0].sum()))
    index={point["id"]:i for i,point in enumerate(points)}
    base=parts[index["SM"]]
    for name, unaffected in [("d_ee_plus",[0,2]),("d_mumu_plus",[1]),("d_etau",[0,2]),("d_mutau",[1]),("tau_diagonal_control",[0,1,2])]:
        np.testing.assert_allclose(parts[index[name]][:,unaffected],base[:,unaffected],rtol=2e-12,atol=2e-10)
    for plus,minus in [("u_emu_plus","u_emu_minus"),("d_emu_plus","d_emu_minus")]:
        np.testing.assert_allclose(parts[index[plus]],parts[index[minus]],rtol=2e-12,atol=2e-10)
        assert np.all(parts[index[plus]]>=base-2e-10)
    for source in range(3):
        assert float((parts[index["d_emu_plus"]]-base)[:,source].sum())>0
    passed("diagonal_interference_flavor_flow_tau_control_and_FC_sign_symmetry")
    assert parts[index["d_ee_plus"]].sum()<base.sum()<parts[index["d_ee_minus"]].sum()
    assert parts[index["d_mumu_plus"]].sum()<base.sum()<parts[index["d_mumu_minus"]].sum()
    e_only=parts[index["d_etau"]]-base
    assert e_only[:,1].sum()>0 and np.max(abs(e_only[:,[0,2]]))<2e-10
    passed("published_vector_NSI_interference_sign_and_incoherent_final_flavor_behavior")
    previous_folder="grid_256_480_checked" if numerical.n_er==512 else "grid_512_960"
    previous,previous_meta=load(run/previous_folder)
    refine=max_difference(previous["signal_counts"],arrays["signal_counts"])
    component_refine=max_difference(previous["target_component_counts"],parts)
    assert refine["status"]==component_refine["status"]=="PASS",(refine,component_refine)
    passed("all24_NSI_points_grid_refinement",previous_grid=previous_folder,current_grid=finest,total=refine,components=component_refine)
    axis_records=[]
    for name,setting in [("recoil",replace(numerical,n_er=numerical.n_er//2)),
            ("neutrino_energy",replace(numerical,n_enu=numerical.n_enu//2)),
            ("PE",replace(numerical,n_observed_bin=numerical.n_observed_bin//2,observed_step=numerical.observed_step*2))]:
        folder=run/(finest+"_axis_"+name)
        if (folder/"counts.npz").exists():
            with np.load(folder/"counts.npz",allow_pickle=False) as cached:changed=cached["parts"]
        else:
            print(json.dumps({"axis_started":name,"settings":asdict(setting)}),flush=True)
            kernel=compile_fast(model,numerics=setting,basis_keys=nsi.BASIS)
            changed=evaluate(kernel,model,points,mapping,sin2,tables["reference_window"].effective_weights)
            folder.mkdir(exist_ok=True);np.savez_compressed(folder/"counts.npz",parts=changed)
            nsi.sm.write_json(folder/"settings.json",asdict(setting))
        total=max_difference(changed.sum(axis=(1,2)),arrays["signal_counts"])
        detail={"axis":name,"coarse_settings":asdict(setting),"total":total,"components":max_difference(changed,parts)}
        axis_records.append(detail);print(json.dumps(detail),flush=True)
    assert all(row["total"]["status"]==row["components"]["status"]=="PASS" for row in axis_records),axis_records
    passed("independent_recoil_energy_PE_precision_all24_points",axes=axis_records)
    passed("native_Slow_and_checked_energy_kernel_equivalence",native_max_error=native["max_native_bin_error"],coefficient_checks=equivalence)
    state=json.loads((run/"SOURCE_STATE.json").read_text(encoding="utf-8"))
    changed=[name for name,value in state["files"].items() if nsi.sm.sha(nsi.ROOT/name)!=value]
    assert not changed,changed
    passed("original_physics_sources_SM_helper_and_resources_unchanged",code_files=len(state["files"]),primary_sources=len(register["sources"]),response_sha256=metadata["response_sha256"])
    result={"date":"2026-11-08","timezone":"Asia/Shanghai","status":"PASS_DECLARED_NSI_FORWARD_POINTS","point_count":len(points),
        "finest_grid":finest,"settings":asdict(numerical),"bin_error_threshold_events":.005,"checks":checks,
        "SM_events":float(base.sum()),"external_paper_reproduction":"NOT_CERTIFIED","likelihood_or_confidence_regions_computed":False,
        "canonical_P08_Fast_freeze":"NOT_REVIEWED","scope":"Declared real symmetric u/d contact vector NSI points; unmodified native SM vector/axial baseline and local nuclear responses"}
    nsi.sm.write_json(run/"VALIDATION_RESULTS.json",result)
    np.savez_compressed(run/"benchmark.npz",**arrays)
    nsi.sm.write_json(run/"points.json",points)
    nsi.sm.write_json(run/"CONTRACT_TEST_PLAN.json",{"requested_scope":"Forward NSI event counts versus SM, as selected by user",
        "point_count":len(points),"methods":[row["name"] for row in checks],"threshold_events":.005,
        "excluded_claims":["paper best fit","statistical exclusion","canonical Fast approval","general complex or non-vector EFT"]})
    print(json.dumps({"status":result["status"],"points":len(points),"SM_events":result["SM_events"],"checks":len(checks)}),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir",type=Path,required=True)
    parser.add_argument("--legacy-time-dir", type=Path, default=nsi.sm.LOCAL_TIME, help="Local adopted time/mapping modules; optional explicit compatibility override")
    parser.add_argument("--stage",choices=["native","precision"],required=True)
    parser.add_argument("--finest",default="grid_512_960")
    args=parser.parse_args()
    if args.stage=="native":native_checks(args.run_dir.resolve(),args.legacy_time_dir.resolve())
    else:precision_checks(args.run_dir.resolve(),args.legacy_time_dir.resolve(),args.finest)


if __name__=="__main__":main()
