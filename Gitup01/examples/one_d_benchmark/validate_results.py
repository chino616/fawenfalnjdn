"""Independent analytic flux, native differential and full/pair checks."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT))
from prediction_routes import BASIS, coefficients, load_routes, read, sha
from run_analysis import write
from cevns_pyeft.contracts import IncidentStateBatch, TheoryPoint
from cevns_pyeft.experiments.solar_singlebin import load_singlebin
from cevns_pyeft.kernels.compiler import reconstruct_channels
from cevns_pyeft.theory.li2026.ee_vector_nsi import ElectronVectorNSI


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    out = parser.parse_args().output.resolve()
    data = read(out/"RESULTS.json")
    routes, solar, sources = load_routes(out)
    checks = []
    for name, route in routes.items():
        for par, x in [("sin2thetaW", .14), ("sin2thetaW", .31), ("epsilon_ee_uV", -.12),
                       ("epsilon_mumu_dV", .36), ("epsilon_emu_uV", -.17)]:
            c = coefficients(x if par == "sin2thetaW" else route.angle, None if par == "sin2thetaW" else par, x)
            full = reconstruct_channels(route.full, c, route.rhos)
            pair = reconstruct_channels(route.full, c, route.rhos, representation="pair")
            error = float(np.max(abs(full-pair)))
            if error > 1e-8: raise ValueError("full/pair reconstruction differs")
            checks.append({"analysis": name, "parameter": par, "value": x, "max_channel_bin_difference": error})
    fluxchecks = []
    for name, indices in {"PandaX_paired": [0], "PandaX_US2": [1], "XENONnT": [2], "Solar_joint": [0, 1, 2]}.items():
        s, d, w = solar.SM[indices], solar.D[indices], 1/solar.sigma[indices]**2
        fhat = float((w*s*d).sum()/(w*s*s).sum())
        error = float(1/np.sqrt((w*s*s).sum()))
        row = data["scans"][name+"__fB_data_only"]
        minerror = abs(row["best_fit"]-fhat)
        enderror = max(abs(row["intervals"]["68percent"][0][0]-max(0., fhat-error)),
                       abs(row["intervals"]["68percent"][0][1]-(fhat+error)))
        if max(minerror, enderror) > 1e-7: raise ValueError("analytic free-flux fit differs")
        fluxchecks.append({"analysis": name, "analytic_best_fB": fhat, "analytic_sigma_fB": error,
                           "best_point_error": minerror, "interval_endpoint_error": enderror})
    base = load_singlebin("PandaX_US2", root=ROOT)
    interaction = ElectronVectorNSI(ROOT/"data/responses/responses_all.json", tuple(t.isotope_id for t in base.model.targets.isotopes))
    direct = []
    for target in [base.model.targets.isotopes[0], base.model.targets.isotopes[-1]]:
        for t in [.35, 1.3, 2.5]:
            energy = np.array([7., 12., 16.])
            table = interaction.spectral_coefficients(target, energy, t, solar.angle)
            for angle in [.12, .31, .49]:
                u, d = -4*(angle-solar.angle)/3, 2*(angle-solar.angle)/3
                from_coeff = table@np.array([1., u, d, u*u, u*d, d*d])
                brute = base.model.interaction._legacy.dsigma_dT(target=target, energy_MeV=energy,
                    recoil_keV=t, incident_state=IncidentStateBatch(energy, np.diag([1., 0., 0.]), "nu", "validation"),
                    parameters=TheoryPoint(sin2thetaW=angle)).values_cm2_per_keV
                error = float(np.max(abs(from_coeff-brute))/max(float(np.max(abs(brute))), 1e-100))
                if error > 2e-9: raise ValueError("new full native differential holdout differs")
                direct.append({"isotope": target.isotope_id, "recoil_keV": t, "sin2thetaW": angle,
                               "max_relative_error": error, "reference": "raw Li2026LegacyInteraction.dsigma_dT, all supplied energies; no energy polynomial on reference side"})
    curvechecks = []
    for key, row in data["scans"].items():
        with np.load(out/"scans"/(key+".npz"), allow_pickle=False) as z:
            np.testing.assert_allclose(z["chi2"]-row["chi2_min"], z["delta_chi2"], rtol=0, atol=2e-12)
            if np.min(z["delta_chi2"]) < -1e-7: raise ValueError("negative delta chi2 exceeds roundoff")
        maxroot = max([abs(x["residual"]) for x in row["root_checks"]], default=0.)
        if maxroot > 2e-7: raise ValueError("confidence endpoint not a chi2 crossing")
        curvechecks.append({"key": key, "roots_checked": len(row["root_checks"]), "max_root_residual": maxroot})
    tablefile = ROOT/"data/benchmarks/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/benchmark/tableII_1sigma.csv"
    with tablefile.open(encoding="utf-8-sig") as f: rows = list(csv.DictReader(f))
    reference_intervals = {}
    for row in rows:
        reference_intervals.setdefault(row["coupling"], []).append([float(row["lower"]), float(row["upper"])])
    comparison = []
    for par, ref in reference_intervals.items():
        own = data["scans"]["CONUS_plus__"+par]["intervals"]["68percent"]
        if len(own) != len(ref): raise ValueError("CONUS interval branch count differs")
        difference = float(np.max(abs(np.array(own)-np.array(ref))))
        comparison.append({"analysis": "CONUS_plus", "parameter": par, "own_68percent": own, "paper_TableII_1sigma": ref,
                           "max_endpoint_difference": difference, "source": "2501.17843v3 PDF p13 TableII; rounded published endpoints"})
    weak = data["scans"]["CONUS_plus__sin2thetaW"]
    reference = {"CONUS_NSI": comparison, "CONUS_weak_angle": {"own_best": weak["best_fit"], "own_68percent": weak["intervals"]["68percent"],
                 "paper_best": .247, "paper_68percent": [.195, .299], "source": "2501.17843v3 PDF p11 Eq34", "model_equivalence": "not certified; conditional numerical agreement"},
                 "COHERENT_weak_angle_context": {"paper_best": .237, "paper_sigma": .029, "source": "2211.11905v2 PDF p16 Eq41", "same_likelihood": False,
                 "reason": "paper uses time and shape-nuisance likelihood; current nine-bin+Ar energy Gaussian is a different approximation"},
                 "solar_context": {"source": "2411.11749v1 PDF pp7-8 Eqs18-23 and Fig2", "same_likelihood": False,
                 "reason": "published multibin US2/XENON analysis differs from current three-singlebin Gaussian and current source/response; no author chi2 grid acquired"}}
    write(out/"REFERENCE_COMPARISON.json", reference)
    supplemental = {"status": "PASS_SCOPED_INDEPENDENT_ANALYTIC_AND_NATIVE_CHECKS", "full_pair_holdouts": checks,
                    "analytic_free_flux_checks": fluxchecks, "raw_native_weak_angle_differential_holdouts": direct,
                    "confidence_crossing_checks": curvechecks, "source_files_unchanged": len(sources),
                    "not_claimed": ["fresh native final-grid Slow run for inaccessible CsI/Ar packages", "official likelihood reproduction", "Wilks coverage proved by toys"]}
    write(out/"qa/INDEPENDENT_CHECKS.json", supplemental)
    source_manifest = read(out/"SOURCE_MANIFEST.json")
    for path in HERE.glob("*.py"): source_manifest[path.relative_to(ROOT).as_posix()] = sha(path)
    source_manifest[tablefile.relative_to(ROOT).as_posix()] = sha(tablefile)
    write(out/"SOURCE_MANIFEST.json", source_manifest)
    print("Independent checks passed:", len(checks), "full/pair;", len(direct), "native differential;", len(curvechecks), "curves")


if __name__ == "__main__":
    main()
