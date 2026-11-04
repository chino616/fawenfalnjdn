"""Reproduce the CsI2021 package-driven P04-P10 numerical audit.

Run with absolute --package/--output paths from any working directory.
Each saved prediction carries its current physical/code/numerical identity.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
bootstrap = argparse.ArgumentParser(add_help=False)
bootstrap.add_argument("--implementation-root", type=Path, default=ROOT)
IMPLEMENTATION_ROOT = bootstrap.parse_known_args()[0].implementation_root.resolve()
sys.path.insert(0, str(IMPLEMENTATION_ROOT))
import numpy as np
from scipy.integrate import quad
from cevns_pyeft.experiments.coherent.csi2021_package import (
    load_package_experiment, read_package, CHANNELS, SOURCE_IDS, ISOTOPES,
)
from cevns_pyeft.experiments.definition import digest, plain
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment
from cevns_pyeft.contracts.parameters import TheoryPoint


def write_json(path, value):
    def encode(item):
        if isinstance(item, np.ndarray): return item.tolist()
        if isinstance(item, np.generic): return item.item()
        if isinstance(item, Path): return str(item)
        raise TypeError(type(item).__name__)
    temporary = path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(plain(value), ensure_ascii=False, indent=2, allow_nan=False, default=encode)+"\n", "utf-8")
    temporary.replace(path)


def component_array(prediction):
    return np.array([[prediction.components[(s, i)] for i in ISOTOPES] for s in SOURCE_IDS])


def phase04(experiment, package, output):
    from cevns_pyeft.nuclear.response import ResponseDB
    database = ResponseDB(ROOT/"data/responses/responses_all.json")  # Explicit comparison only.
    rows = []
    for isotope, response in package.responses().items():
        original = database.get(package.document["target"]["response_keys"][isotope])
        for channel in CHANNELS:
            for y in (0., .1, .5, 1.):
                packed = np.array(response.W_np(channel, y))
                reference = np.array(original.W_np(channel, y))
                error = float(np.max(np.abs(packed-reference)))
                assert np.allclose(packed, reference, rtol=1e-14, atol=1e-12)
                rows.append({"isotope":isotope,"channel":channel,"y":y,"max_abs":error,"W":packed})
    iodine = package.responses()["I127"]
    nn = iodine.W_np("M", 0)[1][1]
    n = package.value("target.I127.N")
    result = {"machine_gate":"PASS","scope":"all 14 NPZ nuclear arrays and 22 internal operator contracts",
        "comparisons":rows,"max_response_difference":max(r["max_abs"] for r in rows),
        "operator_metadata":package.document["interaction"]["supported_operators"],
        "I127_M_nn_zero":{"actual":nn,"N_squared":n*n,"residual":nn-n*n,"status":"retained original table"},
        "typed_output":"PackedInteraction._responses[isotope]: ResponseW",
        "full_response_channels":list(CHANNELS),"engine_zero_channel":"SigmaPDelta",
        "external_nuclear_source_audit":"MISSING","general_antineutrino_EFT":"BLOCKED"}
    write_json(output/"P04_results.json",result)
    return result


def phase05(experiment, package, output):
    from cevns_pyeft.theory.li2026.amplitude import flavor_kernel_onebody_li2026
    from cevns_pyeft.rates.differential import _sm_left_dim6
    rows=[]
    for target in experiment.model.targets.isotopes:
        mass=target.kinematic_mass_GeV
        for component in experiment.model.source.for_run(experiment.model.run).components:
            E=np.array([30.])
            state=component.state_at(E,parameters=TheoryPoint().state)
            endpoint=experiment.model.interaction.kinematics.maximum_recoil_keV(target,30.)
            minimum=experiment.model.interaction.kinematics.minimum_energy_MeV(target,endpoint)
            assert np.isclose(minimum,30.,rtol=1e-13)
            values=[]
            for T in [0.,1.,endpoint,endpoint*(1+1e-5)]:
                cross=experiment.model.interaction.dsigma_dT(target=target,energy_MeV=E,
                    recoil_keV=T,incident_state=state,parameters=TheoryPoint())
                assert cross.unit=="cm^2/keV" and np.all(np.isfinite(cross.values_cm2_per_keV))
                values.append(float(cross.values_cm2_per_keV[0]))
            assert values[-1]==0.
            response=package.responses()[target.isotope_id]
            kernel=flavor_kernel_onebody_li2026(response,E_nu_GeV=.030,ER_keV=1.,
                                               left_hat=_sm_left_dim6(True,package.value("interaction.sin2thetaW")))
            assert kernel.q0==1e-6
            assert np.isclose(kernel.qabs2,2*mass*1e-6)
            assert np.isclose(kernel.q2,kernel.q0**2-kernel.qabs2)
            expected_y=kernel.qabs2*package.value("target."+target.isotope_id+".b")**2/4
            assert np.isclose(kernel.y,expected_y)
            contraction=np.einsum("...ij,ji->...",state.rho,kernel.kernel).real
            independent=float(contraction.item())*mass/(8*np.pi*.030**2)*package.value("constants.GEV_INV2_TO_CM2")*1e-6
            assert np.isclose(values[1],independent,rtol=1e-13)
            rows.append({"isotope":target.isotope_id,"source":component.component_id,
                "particle_kind":component.particle_kind,"Tmax_keV_at_30MeV":endpoint,"Emin_MeV":minimum,
                "cross_sections_at_0_1_endpoint_outside":values,"q0_GeV":kernel.q0,"qabs2_GeV2":kernel.qabs2,
                "signed_q2_GeV2":kernel.q2,"y":kernel.y,"independent_units_result":independent})
    result={"machine_gate":"PASS","unit":"cm^2/keV","points":rows,
            "mass_convention":"package A*AMU_GEV, explicitly checked against fixed engine constant",
            "particle_treatment":"legacy_shared_kernel; general antinu audit remains open",
            "actual_integration":"positive E grid nodes satisfying E>=Emin; trapezoid; prompt lines evaluated separately"}
    write_json(output/"P05_results.json",result)
    return result


def phase06(experiment,package,output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    obs=experiment.model.observation
    target=experiment.model.targets.isotopes[0]
    recoils=np.array([1.,5.,10.,30.])
    rows=[]
    for T in recoils:
        integral,error=quad(lambda x:float(obs.response.density(x,float(T),target=target)),0,np.inf,
                            epsabs=1e-10,epsrel=1e-10,limit=300)
        assert abs(integral-1)<1e-8
        probability=obs.bin_probabilities(target=target,recoil_keV=np.array([T]),
            binning=experiment.model.binning,component_id=SOURCE_IDS[0])
        assert np.all(probability.values>=0) and probability.values.sum()<=1+1e-12
        rows.append({"recoil_keV":T,"density_integral_positive_PE":integral,"quad_error_estimate":error,
                     "accepted_window_probability":float(probability.values.sum()),
                     "bin_probabilities":probability.values[0],"included_selections":probability.included_selections})
    pe=np.linspace(.001,100,800)
    fig,axes=plt.subplots(1,2,figsize=(10,3.8),layout="constrained")
    for T in recoils: axes[0].plot(pe,obs.response.density(pe,float(T),target=target),label=f"{T:g} keVnr")
    axes[0].set(xlabel="Reconstructed PE",ylabel="Density / PE",title="CsI Gamma response")
    axes[0].legend(frameon=False)
    axes[1].plot(pe,obs.efficiency(pe),color="#286a9b")
    axes[1].set(xlabel="Reconstructed PE",ylabel="Efficiency",ylim=(0,1),title="Energy efficiency")
    for suffix in ["png","pdf"]:fig.savefig(output/f"P06_response.{suffix}",dpi=170)
    plt.close(fig)
    result={"machine_gate":"PASS","density_unit":"PE^-1","bin_probability_unit":"1",
        "actual_runtime_representation":"sampled_density; selection applied after legacy_density_fold",
        "alternative_probability_diagnostic":"bin_probabilities includes energy efficiency and component acceptance",
        "analysis_window":[float(x) for x in experiment.model.binning.axes[0].edges[[0,-1]]],
        "rows":rows,"official_calibration_domain":"MISSING; sampled range only"}
    write_json(output/"P06_results.json",result)
    return result


PROFILES={
"small":{"n_er":5,"n_enu":12,"n_pe_bin":3,"pe_step":3.},
"default":{"n_er":21,"n_enu":120,"n_pe_bin":8,"pe_step":3.},
"energy":{"n_er":21,"n_enu":240,"n_pe_bin":8,"pe_step":3.},
"recoil":{"n_er":41,"n_enu":240,"n_pe_bin":8,"pe_step":3.},
"observed":{"n_er":41,"n_enu":240,"n_pe_bin":16,"pe_step":1.5},
"fine":{"n_er":81,"n_enu":480,"n_pe_bin":32,"pe_step":.75},
"fine_energy":{"n_er":81,"n_enu":960,"n_pe_bin":32,"pe_step":.75},
"fine_recoil":{"n_er":161,"n_enu":480,"n_pe_bin":32,"pe_step":.75},
"fine_observed":{"n_er":81,"n_enu":480,"n_pe_bin":64,"pe_step":.375},
"finer":{"n_er":161,"n_enu":960,"n_pe_bin":64,"pe_step":.375},
}


def saved_prediction(experiment,package,output,name,settings,parameters=None):
    point=TheoryPoint(sin2thetaW=package.value("interaction.sin2thetaW")) if parameters is None else parameters
    folder=output/"predictions"
    folder.mkdir(exist_ok=True)
    meta_path,array_path=folder/(name+".json"),folder/(name+".npz")
    point_key={str(k):np.asarray(v).tolist() for k,v in point.wc_triplets.items()}
    # Complex points are fingerprinted by the shared canonical representation.
    from cevns_pyeft.kernels.fingerprint import digest as content_digest
    identity=content_digest({"physics":experiment.physics_fingerprint,"numerics":settings,
                             "point":{str(k):v for k,v in point.wc_triplets.items()},
                             "include_sm":point.include_sm,"sin2thetaW":point.sin2thetaW})
    if meta_path.exists() and array_path.exists():
        existing=json.loads(meta_path.read_text("utf-8"))
        if existing["identity"]==identity and existing["array_sha256"]==hashlib.sha256(array_path.read_bytes()).hexdigest():
            print(f"Reuse {name}",flush=True)
            with np.load(array_path,allow_pickle=False) as stored:return np.array(stored["components"]),existing
    start=time.perf_counter()
    prediction=predict_experiment(experiment,parameters=point,numerics=settings)
    components=component_array(prediction.combined_prediction)
    assert np.all(np.isfinite(components)) and np.all(components>=0)
    assert np.allclose(components.sum(axis=(0,1)),prediction.counts,rtol=1e-13)
    np.savez_compressed(array_path,components=components,counts=prediction.counts,
        edges=experiment.model.binning.axes[0].edges,source_ids=SOURCE_IDS,isotope_ids=ISOTOPES)
    fit=evaluate_experiment(experiment,prediction)
    meta={"identity":identity,"physics_fingerprint":experiment.physics_fingerprint,
        "thread_settings":{k:os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS")},
        "package_hashes":package.hashes,"profile":settings,"seconds":time.perf_counter()-start,
        "array_sha256":hashlib.sha256(array_path.read_bytes()).hexdigest(),"shape":list(components.shape),
        "unit":"events/bin","total":float(prediction.counts.sum()),
        "chi2_legacy_approximate":fit.chi2,"alpha":fit.alpha,"beta":fit.beta,
        "actual_numerical_record":prediction.combined_prediction.numerical_record}
    write_json(meta_path,meta)
    print(f"{name}: {meta['total']:.10f} events; {meta['seconds']:.2f}s",flush=True)
    return components,meta


def phase07(experiment,package,output):
    results={}
    for name,settings in PROFILES.items():
        results[name]=saved_prediction(experiment,package,output,name,settings)
    reference=results["finer"][0]
    comparisons={}
    for name,(values,metadata) in results.items():
        difference=np.abs(values-reference)
        comparisons[name]={"max_abs_component_bin":float(difference.max()),
            "max_rel_component_bin":float(np.max(difference/np.maximum(reference,1e-12))),
            "max_abs_total_bin":float(np.max(np.abs(values.sum(axis=(0,1))-reference.sum(axis=(0,1))))),
            "components_pass_0p5percent_0p01events":bool(np.all(difference<=.01+.005*np.abs(reference)))}
    from cevns_pyeft.experiments.loader import load_experiment,ResourceCatalog
    legacy=load_experiment("CsI2021",resources=ResourceCatalog(ROOT))
    legacy_checks={}
    for name in ["small","default"]:
        original=predict_experiment(legacy,numerics=PROFILES[name]).combined_prediction
        difference=np.abs(component_array(original)-results[name][0])
        assert np.allclose(component_array(original),results[name][0],rtol=1e-11,atol=1e-10)
        legacy_checks[name]={"max_abs_source_isotope_bin":float(difference.max()),"total":float(original.counts.sum())}
    # Independent axis refinements are compared at a common base.
    fine=results["fine"][0]
    axis_checks={}
    for name in ["fine_energy","fine_recoil","fine_observed"]:
        delta=np.abs(fine-results[name][0])
        axis_checks[name]={"max_abs":float(delta.max()),"max_rel":float((delta/np.maximum(results[name][0],1e-12)).max()),
                          "pass":bool(np.all(delta<=.01+.005*np.abs(results[name][0])))}
    converged=all(row["pass"] for row in axis_checks.values()) and comparisons["fine"]["components_pass_0p5percent_0p01events"]
    result={"machine_gate":"PASS" if converged else "BLOCKED","convergence_passed":converged,
        "profiles":{k:v[1] for k,v in results.items()},"convergence_comparisons":comparisons,
        "independent_axis_checks":axis_checks,"legacy_same_grid":legacy_checks,
        "tolerances":{"relative":.005,"absolute_events_per_component_bin":.01},
        "reference_profile":"finer","reference_file":"predictions/finer.npz" if converged else None,
        "human_reference_acceptance":"NOT_REVIEWED","evidence_level":"internal convergence plus same-grid legacy regression",
        "cutoff_keV":package.value("numerics.recoil_min_keV"),"parameter_scope":"SM point",
        "external_paper_forward":"MISSING"}
    write_json(output/"P07_results.json",result)
    return result


def phase08(experiment,package,output):
    """Engineering equivalence evidence, with formal Slow-acceptance status explicit."""
    from cevns_pyeft.kernels.interface_storage import load_compiled_kernel
    from cevns_pyeft.theory.li2026.operators import LI2026_OPERATOR_SPECS
    candidate=output/"wheel_validation_01/external_case/candidate_full22_kernel.npz"
    settings=PROFILES["small"]
    numerics=experiment.executor.settings({**experiment.definition.numerical_profiles["slow"],**settings})
    kernel=load_compiled_kernel(candidate,model=experiment.model,numerics=numerics)
    assert len(kernel.basis_keys)==22
    points=[("SM",TheoryPoint())]
    combined={}
    for index,spec in enumerate(LI2026_OPERATOR_SPECS):
        rng=np.random.default_rng(20261104+index)
        matrix=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
        if spec.lepton_number=="LNV":np.fill_diagonal(matrix,0)
        else:matrix=(matrix+matrix.conj().T)/2
        matrix*={5:1e-10,6:2e-7,7:1e-6,8:1e-5}[spec.dimension]
        points.append((spec.name,TheoryPoint({spec.key:matrix})))
        combined[spec.key]=matrix
    points.extend([("mixed_with_SM",TheoryPoint(combined)),("mixed_without_SM",TheoryPoint(combined,include_sm=False))])
    rows=[]
    slow_values=[];fast_values=[];coefficients=[]
    started=time.perf_counter()
    for name,point in points:
        slow=predict_experiment(experiment,parameters=point,numerics=settings).combined_prediction
        fast=kernel.predict(parameters=point)
        pair=kernel.predict(parameters=point,representation="pair")
        a,b=component_array(slow),component_array(fast)
        error=np.abs(a-b)
        assert np.allclose(a,b,rtol=1e-10,atol=1e-12)
        assert np.allclose(component_array(pair),b,rtol=1e-12,atol=1e-12)
        rows.append({"point":name,"include_sm":point.include_sm,"max_abs_source_isotope_bin":float(error.max()),
                     "max_rel_source_isotope_bin":float((error/np.maximum(abs(a),1e-15)).max())})
        slow_values.append(a);fast_values.append(b)
        coefficients.append(experiment.model.interaction.coefficient_values(point,kernel.basis_keys))
    np.savez_compressed(output/"P08_candidate_comparisons.npz",
        slow=np.array(slow_values),fast=np.array(fast_values),coefficients=np.array(coefficients),
        point_names=np.array([n for n,p in points]),sources=SOURCE_IDS,isotopes=ISOTOPES,
        edges=experiment.model.binning.axes[0].edges)
    result={"machine_gate":"BLOCKED","engineering_equivalence_status":"PASS",
        "formal_blocker":"P07 current-version human Slow freeze is NOT_REVIEWED; no formal P08 acceptance inferred",
        "scope":"22 internal operators, fixed states, all seven supplied nuclear response channels plus the identically zero SigmaPDelta",
        "candidate_kernel":str(candidate.relative_to(output)),"profile":settings,"basis_keys":kernel.basis_keys,
        "kernel_shape":list(kernel.full_kernel.shape),"comparisons":rows,"evaluation_seconds_total":time.perf_counter()-started,
        "coefficient_axes":"operator, final flavor, initial flavor",
        "cross_section_particle_treatment":"legacy_shared_kernel",
        "cumulative_fast":{"plan_status":"NOT_REQUESTED","machine_gate":"NOT_RUN"},
        "general_energy_dependent_state":"unsupported by this compiler",
        "evidence_level":"same-grid engineering equivalence; parameter-wide numerical convergence is separate"}
    write_json(output/"P08_results.json",result)
    return result


def reference_prediction(experiment,output):
    from cevns_pyeft.contracts.prediction import Prediction
    from cevns_pyeft.experiments.runtime import ExperimentPrediction
    p07=json.loads((output/"P07_results.json").read_text("utf-8"))
    name=p07["reference_profile"] if p07["convergence_passed"] else "default"
    metadata=json.loads((output/"predictions"/(name+".json")).read_text("utf-8"))
    array_file=output/"predictions"/(name+".npz")
    assert metadata["physics_fingerprint"]==experiment.physics_fingerprint,"saved prediction is stale"
    assert metadata["array_sha256"]==hashlib.sha256(array_file.read_bytes()).hexdigest(),"saved reference corruption"
    with np.load(array_file,allow_pickle=False) as stored:
        values=np.array(stored["components"]);counts=np.array(stored["counts"])
        np.testing.assert_array_equal(stored["edges"],experiment.model.binning.axes[0].edges)
    components={(s,i):values[a,b] for a,s in enumerate(SOURCE_IDS) for b,i in enumerate(ISOTOPES)}
    prediction=Prediction(counts,experiment.model.binning,components,
        {"route":"verified saved direct integration","input_hashes":dict(experiment.executor.package.hashes)},
        experiment.model.describe(),metadata["actual_numerical_record"])
    return ExperimentPrediction(experiment.dataset_id,experiment.definition.analysis_revision,
        experiment.analysis_fingerprint,experiment.physics_fingerprint,prediction,{"detector":prediction},"slow",
        {"reference_file":str(array_file),"reference_sha256":metadata["array_sha256"]}),name


def phase09(experiment,package,output):
    from cevns_pyeft.statistics.profiling import profile_gaussian_two_pull
    prediction,name=reference_prediction(experiment,output)
    fit=evaluate_experiment(experiment,prediction)
    widths=np.diff(experiment.definition.observation.edges)
    signal=prediction.counts/widths
    stat=experiment.definition.statistics
    data=np.array(stat.observed);background=np.array(stat.background);error=np.array(stat.uncertainty)
    X=np.column_stack([signal,background])
    weight=1/np.maximum(error,package.value("statistics.sigma_floor"))**2
    prior=np.array([stat.signal_sigma,stat.background_sigma])
    pulls=np.linalg.solve(X.T@(weight[:,None]*X)+np.diag(1/prior**2),X.T@(weight*(data-signal-background)))
    independent=np.sum(weight*(data-signal-background-X@pulls)**2)+np.sum((pulls/prior)**2)
    assert np.allclose([fit.chi2,fit.alpha,fit.beta],[independent,*pulls],rtol=1e-12,atol=1e-12)
    toy=profile_gaussian_two_pull(signal,signal+background,background,error,
                                 sigma_alpha=stat.signal_sigma,sigma_beta=stat.background_sigma)
    assert toy.chi2<1e-20
    np.savetxt(output/"P09_observables.csv",np.column_stack([signal,data,background,error]),
               delimiter=",",header="signal_counts_per_PE,observed_counts_per_PE,background_counts_per_PE,sigma_counts_per_PE",
               comments="")
    result={"machine_gate":"PASS","capability":"legacy approximate Gaussian evaluation only",
        "prediction_backend":"Slow","prediction_profile":name,"chi2":fit.chi2,"alpha":fit.alpha,"beta":fit.beta,
        "success":fit.success,"message":fit.message,"chi2_data":fit.chi2_data,"chi2_nuisance":fit.chi2_nuisance,
        "independent_chi2":float(independent),"asimov_chi2":toy.chi2,
        "bin_width_conversion_count":1,"input_hashes":package.hashes,
        "background_subtraction_semantics":"CONFLICT retained from package",
        "official_likelihood":"BLOCKED","confidence_intervals":"NOT_RUN",
        "profile_bounds":"unbounded analytic Gaussian pulls",
        "sigma_floor":package.value("statistics.sigma_floor"),"covariance_used":False}
    write_json(output/"P09_results.json",result)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--implementation-root", type=Path, default=ROOT,
                        help="Pin imports to an audited source tree or installed wheel")
    parser.add_argument("--package",type=Path,default=ROOT/"data/experiments/COHERENT_CsI/CsI2021")
    parser.add_argument("--output",type=Path,default=ROOT/"outputs/csi2021_package_execution_20261104")
    parser.add_argument("--phases",nargs="+",choices=["P04","P05","P06","P07","P08","P09"],default=["P04","P05","P06","P07"])
    parser.add_argument("--profile",choices=list(PROFILES),help="Calculate one independent Slow quadrature profile")
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    package=read_package(args.package)
    experiment=load_package_experiment(args.package)
    if args.profile:
        saved_prediction(experiment,package,args.output,args.profile,PROFILES[args.profile])
        return
    for phase in args.phases:
        print(f"Begin {phase}",flush=True)
        result=globals()["phase"+phase[1:]](experiment,package,args.output)
        print(f"{phase}: {result['machine_gate']}",flush=True)


if __name__=="__main__":
    main()

