"""Independent native Slow and native flavor-amplitude checks for new forwards."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import ROOT, write_json
from forward22 import build_csi, build_ar, build_conus, compile_ground, KEYS, flavor_tensor
from model_adapters import Ground, load_ground
from cevns_pyeft.contracts import TheoryPoint, IntegrationSettings
from cevns_pyeft.core.predict import predict
from cevns_pyeft.rates.legacy_observables import predict_legacy_observable
from cevns_pyeft.rates.differential import differential_cross_section_nn
from cevns_pyeft.nuclear.response import ResponseDB


def validate(output):
    output = Path(output).resolve()
    if not output.is_relative_to((ROOT/"outputs/cutoff_scales").resolve()) or not output.is_dir():
        raise ValueError("validation must be written in this Part's model run")
    destination = output/"NATIVE_SLOW_VALIDATION.json"
    if destination.exists():
        raise FileExistsError("independent validation is create-only")
    old, _ = load_ground()
    rows = []
    for name, factory in (("CsI2021_9PE", build_csi), ("Ar2020_average", build_ar), ("CONUS_plus", lambda: build_conus()[0])):
        model = factory()
        full, _ = compile_ground(model, name, n_er=11, n_enu=24, n_observed=8, step=2.)
        route = Ground(name, full, old[name].rhos, old[name].channel, old[name].angle, KEYS)
        for key in ((5,1,""), (6,2,"u"), (7,4,"u"), (8,1,"u")):
            flavor = flavor_tensor(key)
            p = route.polynomial(key, flavor)
            coefficient = np.sqrt(max(p[0].sum(), 1)/p[2].sum()) if p[2].sum() > 0 else 1e-5
            point = TheoryPoint({key: coefficient*flavor}, include_sm=True, sin2thetaW=route.angle)
            try:
                if name == "Ar2020_average":
                    slow = predict_legacy_observable(model, point, {"n_er":11,"n_enu":24,"n_pe_bin":8,"recoil_min_keV":.1}, "observed_gaussian_legacy_v1").counts
                else:
                    lower = .1
                    if name == "CONUS_plus":
                        from scipy.optimize import brentq
                        lower = brentq(lambda t:float(model.observation.mean_eVee(t))-model.observation.pair_energy_eVee,1e-8,1.)
                    ns=IntegrationSettings(n_er=11,n_enu=24,n_observed_bin=8,observed_step=2.,recoil_min_keV=lower,
                                           strategy="bin_probability_v1" if name=="CONUS_plus" else "legacy_csi2021_v1")
                    slow = predict(model, parameters=point, numerics=ns, backend="slow").counts
            except RuntimeError as exc:
                if "positive semidefinite" not in str(exc):
                    raise
                rows.append({"analysis":name,"operator":list(key),"coefficient":coefficient,
                             "status":"NATIVE_AMPLITUDE_PSD_REJECTED", "error":str(exc),
                             "scope":"unresolved pointwise amplitude validity; not bypassed, clipped or counted as a passing Slow check"})
                print("NATIVE_PSD_REJECTED",name,key,flush=True)
                continue
            fast = route.predict(key, coefficient, flavor=flavor)
            error=float(np.max(abs(slow-fast))/max(float(slow.sum()),1.))
            if error > 2e-8:
                raise ValueError(f"native Slow/full22 mismatch: {name} {key} {error}")
            rows.append({"analysis":name,"operator":list(key),"coefficient":coefficient,"status":"PASS",
                         "native_Slow_total_events":float(slow.sum()),"full22_total_events":float(fast.sum()),
                         "max_bin_difference_over_total":error,"grid":{"n_er":11,"n_enu":24,"n_observed":8},
                         "scope":"identical coarse grid: arithmetic equivalence, not convergence acceptance"})
            print("SLOW_CHECK",name,key,error,flush=True)
    # Flavor-level native amplitude cross-check, including every new operator on Xe.
    db=ResponseDB(ROOT/"data/responses/responses_all.json")
    from cevns_pyeft.theory.li2026.coefficients import differential_coefficients
    from cevns_pyeft.foundation.constants import AMU_GEV
    from types import SimpleNamespace
    checks=[]
    for isotope in ("Xe129","Xe131"):
        response=db.get(isotope);target=SimpleNamespace(kinematic_mass_GeV=response.basic['A']*AMU_GEV)
        recoil=1.23
        from cevns_pyeft.contracts.interaction import ElasticKinematics
        minimum=ElasticKinematics().minimum_energy_MeV(target,recoil)
        energy=np.array([1.15*minimum,1.9*minimum])
        h=differential_coefficients(response,target,energy,recoil,KEYS,c10_mass_mode="quark_mass_resolved").sum(axis=1)
        for i,key in enumerate(KEYS):
            f=flavor_tensor(key);rho=np.diag([.4,.35,.25])
            expected=h[:,i,i].real*float(np.trace(rho@f.conj().T@f).real)
            direct=differential_cross_section_nn(response,recoil,energy,rho=rho,particle_kind="nu",wc_triplets={key:f},include_sm=False).dsigma_cm2_per_keV
            denominator=max(float(np.max(abs(expected))),1e-300)
            error=float(np.max(abs(expected-direct))/denominator)
            if error > 3e-10:
                raise ValueError(f"native Xe flavor amplitude mismatch {isotope} {key}: {error}")
            checks.append({"isotope":isotope,"operator":list(key),"relative_native_amplitude_difference":error})
    rejected=[row for row in rows if row['status']!='PASS']
    write_json(destination,{"status":"PARTIAL_NATIVE_SLOW_VALIDATION" if rejected else "PASS_NATIVE_SLOW_AND_FLAVOR_CHECKS",
                            "ground_Slow_checks":rows,"Xe_all_operator_native_checks":checks,"unresolved_native_PSD_points":rejected,
                            "limits":"coarse-grid equivalence plus native cross-section algebra; convergence reported separately; no new official-likelihood claim"})
    print("VALIDATED",len(rows),"native Slow predictions and",len(checks),"Xe native flavor amplitudes",flush=True)


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",type=Path,required=True);validate(p.parse_args().output)
