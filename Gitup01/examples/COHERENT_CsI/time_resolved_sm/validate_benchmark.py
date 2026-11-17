"""Validate an explicit SM forward run; do not advance scientific gates."""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path
import sys
import time

import numpy as np
from scipy.integrate import quad

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from examples.COHERENT_CsI.time_resolved_common import sm_support as driver
from cevns_pyeft.contracts.parameters import IntegrationSettings, TheoryPoint
from cevns_pyeft.core.predict import predict
from cevns_pyeft.rates.folding import linear_fold_weights
from cevns_pyeft.rates.recoil import integrate_recoil_yield


def read_grid(folder):
    with np.load(folder / "prediction.npz", allow_pickle=False) as source:
        arrays = {key: source[key] for key in source.files}
    return arrays, json.loads((folder / "report.json").read_text(encoding="utf-8"))


def comparison(a, b, threshold=.005):
    difference = np.asarray(b) - np.asarray(a)
    worst = np.unravel_index(np.abs(difference).argmax(), difference.shape)
    maximum = float(np.max(np.abs(difference)))
    return {"max_bin_absolute_difference_events": maximum, "total_difference_events": float(difference.sum()),
        "worst_bin": list(map(int, worst)), "threshold_events": threshold, "status": "PASS" if maximum < threshold else "FAIL"}


def assemble_energy(model, arrays, numerical, *, stored_yields):
    """Independent order of existing linear folding, for nonnegative pure SM.

    Uses the package's own linear_fold_weights and recoil integrator. It does
    not implement another cross section or another detector response.
    """
    fluence = model.source.for_run(model.run)
    result = np.zeros((2, 3, 9))
    model = replace(model, interaction=driver.CheckedSMInteraction(model.interaction))
    point = TheoryPoint({}, include_sm=True, sin2thetaW=arrays["_sin2thetaW"])
    for it, target in enumerate(model.targets.isotopes):
        key = target.isotope_id + "_" + fluence.components[0].component_id + "_T_keVnr"
        if stored_yields or len(arrays[key]) == numerical.n_er:
            recoil = arrays[key]
        else:
            maximum = model.interaction.kinematics.maximum_recoil_keV(target, fluence.components[0].support.integration_domain_MeV[1])
            recoil = np.linspace(numerical.recoil_min_keV, maximum, numerical.n_er)
        matrix = linear_fold_weights(target, model.observation, model.binning, numerical, recoil, fluence.components[0].component_id)
        for ic, component in enumerate(fluence.components):
            if stored_yields:
                yield_ = arrays[target.isotope_id + "_" + component.component_id + "_yield_per_keV_per_nucleus"]
            else:
                yield_ = integrate_recoil_yield(component, target, model.interaction, parameters=point,
                    numerics=numerical, recoil_keV=recoil).values_per_keV
            result[it, ic] = yield_ @ matrix * target.number_of_nuclei
    return result


def background_templates(onboarding, arrays, acceptance):
    result = {}
    audit = []
    for name in ("brn", "nin"):
        pe_table = np.loadtxt(onboarding / "sources/official" / (name + "PE.txt"))
        time_table = np.loadtxt(onboarding / "sources/official" / (name + "Trec.txt"))
        np.testing.assert_allclose(np.diff(pe_table[:, 0]), 1.0, rtol=0, atol=1e-13)
        np.testing.assert_allclose(np.diff(time_table[:, 0]), .01, rtol=0, atol=1e-13)
        cdf = acceptance.TimeMassCDF(time_table[:, 1], np.r_[time_table[:, 0] - .005, time_table[-1, 0] + .005])
        selected = (pe_table[:, 0] >= arrays["pe_edges"][0]) & (pe_table[:, 0] < arrays["pe_edges"][-1])
        energy = np.histogram(pe_table[selected, 0], bins=arrays["pe_edges"], weights=pe_table[selected, 1])[0]
        raw = energy[:, None] * cdf.integral(arrays["time_edges_us"])[None, :]
        probability = raw / pe_table[:, 1].sum()
        result[name.upper() + "_raw_template"] = raw
        result[name.upper() + "_full_PE_probability_candidate"] = probability
        audit.append({"component": name.upper(), "raw_PE_table_sum": float(pe_table[:, 1].sum()),
            "raw_template_selected_events": float(raw.sum()), "probability_candidate_selected_events": float(probability.sum()),
            "published_prior_events": 18.4 if name == "brn" else 5.6,
            "prior_used_to_rescale": False, "status": "UNRESOLVED_NORMALIZATION_DIAGNOSTIC"})
    return result, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--legacy-time-dir", type=Path, default=driver.LOCAL_TIME, help="Local adopted time/mapping modules; optional explicit compatibility override")
    parser.add_argument("--onboarding", type=Path, default=driver.ROOT / "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved")
    parser.add_argument("--finest", default="grid_512_960")
    args = parser.parse_args()
    run = args.run_dir.resolve()
    onboarding = args.onboarding.resolve()
    claims, register = driver.inputs(onboarding)
    arrays, report = read_grid(run / args.finest)
    numerical = IntegrationSettings(**report["numeric_settings"])
    sin2 = float(claims["C_SIN2_PAPER"]["value"])
    arrays["_sin2thetaW"] = sin2
    acceptance, profile = driver.time_modules(args.legacy_time_dir.resolve())
    source_time = driver.time_source(onboarding, profile)
    time_efficiency = acceptance.CsITimeEfficiency(*claims["C_TIME_EFF"]["value"])
    model = driver.build_model(claims)
    checks = []

    def passed(name, **details):
        checks.append({"name": name, "status": "PASS", **details})
        print(json.dumps({"check": name, "status": "PASS"}), flush=True)

    assert arrays["target_component_counts"].shape == (2, 3, 9, 11)
    assert np.isfinite(arrays["target_component_counts"]).all() and np.all(arrays["target_component_counts"] >= 0)
    np.testing.assert_allclose(arrays["target_component_counts"].sum(axis=(0, 1)), arrays["signal_counts"], atol=2e-12, rtol=1e-14)
    np.testing.assert_allclose(arrays["signal_counts"].sum(axis=1),
        (arrays["energy_before_time"] * arrays["time_weights"].sum(axis=1)[None, :, None]).sum(axis=(0, 1)), atol=2e-12, rtol=1e-14)
    passed("finite_nonnegative_components_axes_and_projection_closure", shape=[2, 3, 9, 11])

    eta = float(claims["C_ETA"]["value"])
    fluence = model.source.for_run(model.run)
    integrals = [quad(lambda e: float(component.continuum(np.array([e]))[0]), *component.support.integration_domain_MeV,
                     epsabs=1, epsrel=1e-12)[0] + sum(line.fluence_per_cm2 for line in component.lines) for component in fluence.components]
    np.testing.assert_allclose(np.array(integrals) / eta, 1.0, rtol=3e-14, atol=0)
    native_counts = [target.number_of_nuclei for target in model.targets.isotopes]
    np.testing.assert_allclose(native_counts[0], native_counts[1], rtol=2e-15)
    passed("source_each_flavor_integrates_to_eta_and_equal_CsI_nucleus_numbers", eta_cm_minus2=eta,
           integrated_fluence_per_flavor=integrals, number_of_nuclei=native_counts)

    references = []
    for shift in (-.25, 0.0, .25):
        converted = acceptance.build_time_weights(source_time, arrays["time_edges_us"], efficiency=time_efficiency,
            shift_us=shift, template_normalization="reference_window", energy_fluence_scope="full_support", reference_window_us=[0, 6])
        full = acceptance.build_time_weights(source_time, arrays["time_edges_us"], efficiency=time_efficiency,
            shift_us=shift, template_normalization="full_support", energy_fluence_scope="full_support", reference_window_us=[0, 6])
        np.testing.assert_allclose(converted.effective_weights, full.effective_weights, rtol=2e-14, atol=1e-16)
        references.append(converted.reference_fractions)
    np.testing.assert_array_equal(references[0], references[1])
    np.testing.assert_array_equal(references[1], references[2])
    passed("time_representation_conversion_and_fixed_shift_denominator", shifts_us=[-.25, 0, .25], reference_fractions=references[1])

    original_response = model.observation.response
    gamma_norms = []
    for recoil in (2., 5., 15., 40., 70.):
        density = lambda x: float(original_response.density(x, recoil, target=model.targets.isotopes[0]))
        norm = quad(density, 0, np.inf, epsabs=2e-10, epsrel=2e-10, limit=300)[0]
        gamma_norms.append(norm)
    np.testing.assert_allclose(gamma_norms, 1, rtol=1e-8, atol=1e-10)
    observed_nodes = np.arange(0, 60 + .5 * numerical.observed_step, numerical.observed_step)
    efficiency_values = model.observation.efficiency(observed_nodes)
    assert np.all((efficiency_values >= 0) & (efficiency_values <= 1))
    for name, value in arrays.items():
        if name.endswith("_T_keVnr"):
            assert value.min() >= 2 and value.max() <= 70
    passed("P06_gamma_normalization_efficiency_range_and_QF_domain", recoil_tests_keVnr=[2, 5, 15, 40, 70], gamma_integrals=gamma_norms)

    equivalence = json.loads((run / "NATIVE_SM_EQUIVALENCE.json").read_text(encoding="utf-8"))
    assert equivalence["status"] == "PASS"
    passed("native_direct_against_checked_SM_and_exact_response_node_reuse", evidence="NATIVE_SM_EQUIVALENCE.json", **equivalence)

    grids = []
    previous = None
    for name in ("grid_128_240", "grid_256_480", args.finest):
        grid, metadata = read_grid(run / name)
        row = {"name": name, "settings": metadata["numeric_settings"], "total_events": float(grid["signal_counts"].sum())}
        if previous is not None:
            row["refinement"] = comparison(previous["signal_counts"], grid["signal_counts"])
        grids.append(row)
        previous = grid
    assert grids[-1]["refinement"]["status"] == "PASS"
    passed("simultaneous_grid_refinement_SM_point_only", grids=grids, acceptance_events=.005)

    print("Checking independent integration axes with the existing recoil and folding routines", flush=True)
    reordered = assemble_energy(model, arrays, numerical, stored_yields=True)
    np.testing.assert_allclose(reordered, arrays["energy_before_time"], rtol=2e-13, atol=2e-11)
    passed("existing_linear_fold_order_matches_authoritative_common_Slow", max_energy_bin_error=float(np.max(np.abs(reordered-arrays["energy_before_time"]))))
    axis_checks = []
    for name, settings, stored in [
        ("recoil", replace(numerical, n_er=numerical.n_er // 2), False),
        ("neutrino_energy", replace(numerical, n_enu=numerical.n_enu // 2), False),
        ("observed_PE", replace(numerical, n_observed_bin=numerical.n_observed_bin // 2, observed_step=numerical.observed_step * 2), True),
    ]:
        print(json.dumps({"axis_check_started": name, "settings": asdict(settings)}), flush=True)
        started = time.perf_counter()
        energy = assemble_energy(model, arrays, settings, stored_yields=stored)
        changed = (energy[..., None] * arrays["time_weights"][:, None, :]).sum(axis=(0, 1))
        record = {"axis": name, "coarsened_settings": asdict(settings), **comparison(changed, arrays["signal_counts"]),
                  "elapsed_s": time.perf_counter() - started}
        axis_checks.append(record)
        print(json.dumps(record), flush=True)
    assert all(row["status"] == "PASS" for row in axis_checks), axis_checks
    passed("independent_recoil_energy_and_PE_refinements", axes=axis_checks)

    pilot, pilot_report = read_grid(run / "pilot")
    scaled = driver.build_model(claims, mass_factor=2.0, fluence_factor=3.0)
    pilot_settings = IntegrationSettings(**pilot_report["numeric_settings"])
    scaled = replace(scaled, interaction=driver.CheckedSMInteraction(scaled.interaction))
    scaled_prediction = predict(scaled, parameters=TheoryPoint({}, sin2thetaW=sin2), numerics=pilot_settings)
    original_energy = pilot["energy_before_time"].sum(axis=(0, 1))
    np.testing.assert_allclose(scaled_prediction.counts, 6 * original_energy, rtol=3e-13, atol=2e-10)
    passed("actual_common_Slow_mass_times_fluence_scaling", mass_factor=2, fluence_factor=3,
           max_energy_bin_error=float(np.max(np.abs(scaled_prediction.counts-6*original_energy))))

    backgrounds, audit = background_templates(onboarding, arrays, acceptance)
    arrays.update(backgrounds)
    arrays["expected_raw_template_diagnostic"] = arrays["signal_counts"] + arrays["SS_derived"] + arrays["BRN_raw_template"] + arrays["NIN_raw_template"]
    arrays["signal_excess_raw_template_diagnostic"] = arrays["C_raw"] - arrays["SS_derived"] - arrays["BRN_raw_template"] - arrays["NIN_raw_template"]
    assert int(arrays["C_raw"].sum()) == 1578 and int(arrays["AC_raw"].sum()) == 1295
    passed("official_event_histograms_and_unscaled_background_diagnostics", C_raw_total=1578, AC_raw_total=1295,
           SS_total=float(arrays["SS_derived"].sum()), backgrounds=audit)

    snapshot = json.loads((run / "SOURCE_STATE_BEFORE_VALIDATION.json").read_text(encoding="utf-8"))
    changed = [name for name, fingerprint in snapshot["files"].items() if driver.sha(driver.ROOT / name) != fingerprint]
    assert not changed, changed
    passed("source_files_unchanged_during_final_calculation_and_validation", code_files=len(snapshot["files"]))

    arrays.pop("_sin2thetaW")
    np.savez_compressed(run / "benchmark.npz", **arrays)
    keys = ["signal_counts", "C_raw", "AC_raw", "SS_derived", "BRN_raw_template", "NIN_raw_template", "expected_raw_template_diagnostic",
            "full_fluence_signal_counts", "BRN_full_PE_probability_candidate", "NIN_full_PE_probability_candidate"]
    csv = ["PE_low,PE_high,time_low_us,time_high_us," + ",".join(keys)]
    for i in range(9):
        for j in range(11):
            row = [arrays["pe_edges"][i], arrays["pe_edges"][i+1], arrays["time_edges_us"][j], arrays["time_edges_us"][j+1]]
            row.extend(arrays[key][i, j] for key in keys)
            csv.append(",".join(format(float(value), ".17g") for value in row))
    (run / "events_99bins.csv").write_text("\n".join(csv) + "\n", encoding="utf-8", newline="\n")
    for axis, edge_name, reduce_axis in [("PE", "pe_edges", 1), ("time", "time_edges_us", 0)]:
        table = [axis + "_low," + axis + "_high," + ",".join(keys)]
        projected = {key: arrays[key].sum(axis=reduce_axis) for key in keys}
        for i in range(len(arrays[edge_name])-1):
            row = [arrays[edge_name][i], arrays[edge_name][i+1]] + [projected[key][i] for key in keys]
            table.append(",".join(format(float(value), ".17g") for value in row))
        (run / (axis + "_projection.csv")).write_text("\n".join(table) + "\n", encoding="utf-8", newline="\n")
    result = {"date": "2026-11-07", "timezone": "Asia/Shanghai", "status": "PASS_SM_FORWARD_NUMERICAL_CHECKS",
        "scope": "One nominal SM point, both isotopes, three DAR flavors,99 bins; no BSM domain or statistical fit acceptance",
        "strict_paper_reproduction": "NOT_CERTIFIED", "human_authoritative_Slow_freeze": "NOT_REVIEWED",
        "SM_total_events": float(arrays["signal_counts"].sum()),
        "full_fluence_SM_total_events": float(arrays["full_fluence_signal_counts"].sum()),
        "checks": checks, "background_normalization": "UNRESOLVED; never rescaled to published priors",
        "native_SM_contains_vector_and_axial_terms": True, "paper_radiative_coupling_and_radius_nuisance_equivalence": "NOT_CERTIFIED",
        "native_equivalence_evidence_sha256": driver.sha(run / "NATIVE_SM_EQUIVALENCE.json"),
        "final_grid_report_sha256": driver.sha(run / args.finest / "report.json"), "input_source_count": len(register["sources"])}
    driver.write_json(run / "VALIDATION_RESULTS.json", result)
    driver.write_json(run / "CONTRACT_TEST_PLAN.json", {"requested_by": "User2026-11-07:SM benchmark and event-count figures",
        "route": "validation_only", "P06_P07_methods": [row["name"] for row in checks], "bin_error_threshold_events": .005,
        "optional_unrequested": ["P08 Fast freeze", "P09 nuisance fit", "strict official likelihood reproduction"]})
    print(json.dumps({"status": result["status"], "SM_total_events": result["SM_total_events"], "checks": len(checks)}), flush=True)


if __name__ == "__main__":
    main()
