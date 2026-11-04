"""Regression for the explicit CsI2021 pilot-package binding."""
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT/"data/experiments/COHERENT_CsI/CsI2021"


def test_pilot_package_has_explicit_runtime_binding():
    from cevns_pyeft.experiments.coherent.csi2021_package import read_package, load_package_experiment
    package = read_package(PACKAGE)
    assert len(package.arrays) == 23
    experiment = load_package_experiment(PACKAGE)
    assert experiment.dataset_id == "CsI2021"
    assert experiment.model.interaction.response_keys == {"Cs133": "Cs133", "I127": "I"}
    assert experiment.model.binning.shape == (9,)
    assert len(experiment.model.targets.isotopes) == 2
    assert package.document["package"]["human_physics_approval"] == "NOT_REVIEWED"


def test_package_small_grid_uses_all_source_isotope_components():
    from cevns_pyeft.experiments.coherent.csi2021_package import load_package_experiment
    from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment
    experiment = load_package_experiment(PACKAGE)
    prediction = predict_experiment(experiment, numerics={"n_er": 5, "n_enu": 12, "n_pe_bin": 3})
    assert len(prediction.combined_prediction.components) == 6
    assert np.isclose(prediction.counts.sum(), 381.8912488750059, rtol=1e-12)
    fit = evaluate_experiment(experiment, prediction)
    assert np.isclose(fit.chi2, 10.777108968658267, rtol=1e-11)

import copy
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import replace
import pytest


def copy_package(tmp_path):
    location = tmp_path/"package"
    location.mkdir()
    for name in ["experiment.input.yaml", "experiment.resources.npz", "experiment.physics.md"]:
        shutil.copyfile(PACKAGE/name, location/name)
    return location


def rewrite_package(location, transform_document=None, transform_arrays=None, render=True):
    from cevns_pyeft.experiments.input_package import render_physics
    path = location/"experiment.input.yaml"
    data = json.loads(path.read_text("utf-8"))
    with np.load(location/"experiment.resources.npz", allow_pickle=False) as stored:
        arrays = {key: np.array(stored[key]) for key in stored.files}
    if transform_document:
        transform_document(data)
    if transform_arrays:
        transform_arrays(arrays)
        np.savez_compressed(location/"experiment.resources.npz", **arrays)
        data["resources"]["sha256"] = hashlib.sha256((location/"experiment.resources.npz").read_bytes()).hexdigest()
        for key, array in arrays.items():
            if key in data["resources"]["arrays"]:
                meta = data["resources"]["arrays"][key]
                meta.update(shape=list(array.shape), dtype=str(array.dtype),
                            sha256_raw_c_order=hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest())
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
    if render:
        (location/"experiment.physics.md").write_text(render_physics(data, arrays), "utf-8")


@pytest.mark.parametrize("mutation", [
    "basis", "flavor_axis", "unknown_operator", "unknown_model", "wrong_unit", "wrong_axis",
    "bad_archive_hash", "missing_parameter", "negative_gamma", "bad_acceptance",
    "missing_component", "component_order", "gamma_convention", "numerical_strategy",
])
def test_invalid_package_contract_is_rejected(tmp_path, mutation):
    from cevns_pyeft.experiments.coherent.csi2021_package import read_package
    location = copy_package(tmp_path)
    def change(d):
        if mutation == "basis": d["interaction"]["basis"] = "iso"
        elif mutation == "flavor_axis": d["interaction"]["coefficient_axes"]["row"] = "initial flavor"
        elif mutation == "unknown_operator": d["interaction"]["supported_operators"][0]["key"] = [9, 99, "x"]
        elif mutation == "unknown_model": d["models"]["evil"] = d["models"].pop("legacy_csi_gamma")
        elif mutation == "wrong_unit": d["parameters"]["detector.gamma_a"]["unit"] = "GeV"
        elif mutation == "wrong_axis": d["resources"]["arrays"]["nuclear_Cs133_M"]["axes"][0]["values"] = ["n", "p"]
        elif mutation == "bad_archive_hash": d["resources"]["sha256"] = "0"*64
        elif mutation == "missing_parameter": del d["parameters"]["lecs.L1"]
        elif mutation == "negative_gamma":
            d["parameters"]["detector.gamma_a"]["value"] = -1.
            d["parameters"]["detector.gamma_a"]["adopted_value"] = -1.
        elif mutation == "bad_acceptance":
            d["parameters"]["detector.acceptance_mu"]["value"] = 1.2
            d["parameters"]["detector.acceptance_mu"]["adopted_value"] = 1.2
        elif mutation == "missing_component": d["source"]["components"].pop()
        elif mutation == "component_order": d["source"]["components"].reverse()
        elif mutation == "gamma_convention": d["detector"]["gamma_convention"] = "shape-scale"
        elif mutation == "numerical_strategy": d["prediction"]["numerical_strategy"] = "bin_probability_v1"
    rewrite_package(location, transform_document=change, render=False)
    with pytest.raises((ValueError, KeyError, TypeError)):
        read_package(location, check_md=False)


@pytest.mark.parametrize("mutation", ["extra", "missing", "dtype", "negative_sigma", "reverse_edges", "object"])
def test_npz_corruption_is_rejected(tmp_path, mutation):
    from cevns_pyeft.experiments.coherent.csi2021_package import read_package
    location = copy_package(tmp_path)
    def change(a):
        if mutation == "extra": a["surprise"] = np.ones(2)
        elif mutation == "missing": del a["nuclear_I127_M"]
        elif mutation == "dtype": a["nuclear_Cs133_M"] = a["nuclear_Cs133_M"].astype("float32")
        elif mutation == "negative_sigma": a["statistics_uncertainty"][0] = -1.
        elif mutation == "reverse_edges": a["observable_pe_edges"] = a["observable_pe_edges"][::-1]
        elif mutation == "object": a["nuclear_Cs133_M"] = np.array([object()], dtype=object)
    rewrite_package(location, transform_arrays=change, render=False)
    with pytest.raises((ValueError, KeyError, TypeError)):
        read_package(location, check_md=False)


def test_physics_markdown_drift_is_rejected(tmp_path):
    from cevns_pyeft.experiments.coherent.csi2021_package import read_package
    location = copy_package(tmp_path)
    path = location/"experiment.physics.md"
    path.write_text(path.read_text("utf-8")+"\nExtra scalar 42\n", "utf-8")
    with pytest.raises(ValueError, match="Physics MD"):
        read_package(location)


def test_current_renderer_and_published_input1_prose_are_compatible(tmp_path):
    from cevns_pyeft.experiments.coherent.csi2021_package import read_package
    from cevns_pyeft.experiments.input_package import render_physics
    from cevns_pyeft.experiments.definition import plain
    location = copy_package(tmp_path)
    original = read_package(location)
    path = location/"experiment.physics.md"
    path.write_text(render_physics(plain(original.document), original.arrays), "utf-8")
    current = read_package(location)
    assert original.physical_fingerprint == current.physical_fingerprint
    # Changes to actual parameter tables remain an input conflict.
    path.write_text(path.read_text("utf-8").replace("0.0554628", "0.0554629"), "utf-8")
    with pytest.raises(ValueError, match="Physics MD"):
        read_package(location)


def test_explanation_edit_after_load_rejects_the_existing_snapshot(tmp_path):
    from cevns_pyeft.experiments.coherent.csi2021_package import load_package_experiment
    location = copy_package(tmp_path)
    experiment = load_package_experiment(location)
    path = location/"experiment.physics.md"
    path.write_text(path.read_text("utf-8")+"\nUnapproved parameter 42\n", "utf-8")
    with pytest.raises(ValueError, match="Physics MD"):
        experiment.executor.package.assert_fresh()


def test_source_and_statistics_have_separate_physical_fingerprints(tmp_path):
    from cevns_pyeft.experiments.coherent.csi2021_package import read_package, load_package_experiment
    location = copy_package(tmp_path)
    original = read_package(location)
    first = load_package_experiment(location)
    rewrite_package(location, transform_arrays=lambda a: a["statistics_observed"].__iadd__(.05))
    updated = read_package(location)
    second = load_package_experiment(location)
    assert original.physical_fingerprint == updated.physical_fingerprint
    assert original.statistical_fingerprint != updated.statistical_fingerprint
    assert first.physics_fingerprint == second.physics_fingerprint
    assert first.analysis_fingerprint != second.analysis_fingerprint
    original.assert_fresh("physical")
    with pytest.raises(ValueError, match="statistics"):
        original.assert_fresh("statistics")


def test_input_change_invalidates_an_existing_runtime_snapshot(tmp_path):
    from cevns_pyeft.experiments.coherent.csi2021_package import load_package_experiment
    from cevns_pyeft.experiments.runtime import predict_experiment
    location = copy_package(tmp_path)
    experiment = load_package_experiment(location)
    def change(d):
        for item in ["value", "adopted_value"]:
            d["parameters"]["detector.gamma_b"][item] += .01
    rewrite_package(location, transform_document=change)
    with pytest.raises(ValueError, match="physical inputs changed"):
        predict_experiment(experiment, numerics={"n_er":3, "n_enu":6, "n_pe_bin":3})


def test_external_cwd_three_files_only_without_legacy_fallback(tmp_path):
    location = copy_package(tmp_path)
    script = tmp_path/"probe.py"
    code = r'''import pathlib,sys,json
sys.path.insert(0, sys.argv[1])
root=pathlib.Path(sys.argv[1]).resolve()
package=pathlib.Path(sys.argv[2]).resolve()
def audit(event,args):
    if event == "import" and str(args[0]).endswith("csi2021_definition"):
        raise RuntimeError("legacy definition import forbidden")
    if event == "open" and isinstance(args[0],(str,bytes)):
        path=pathlib.Path(args[0]).resolve()
        if path.is_relative_to(root/"data") and not path.is_relative_to(package):
            raise RuntimeError("legacy data fallback forbidden: "+str(path))
sys.addaudithook(audit)
from cevns_pyeft.experiments.coherent.csi2021_package import load_package_experiment
from cevns_pyeft.experiments.runtime import predict_experiment,evaluate_experiment
exp=load_package_experiment(package)
p=predict_experiment(exp,numerics={"n_er":5,"n_enu":12,"n_pe_bin":3})
f=evaluate_experiment(exp,p)
assert "cevns_pyeft.experiments.coherent.csi2021_definition" not in sys.modules
print(json.dumps({"events":float(p.counts.sum()),"chi2":f.chi2,"components":len(p.combined_prediction.components)}))
'''
    script.write_text(code, "utf-8")
    process = subprocess.run([sys.executable, "-B", str(script), str(ROOT), str(location)],
                             cwd=tmp_path, text=True, capture_output=True, encoding="utf-8")
    assert process.returncode == 0, process.stderr
    result = json.loads(process.stdout)
    assert result["components"] == 6
    assert np.isclose(result["events"], 381.8912488750059, rtol=1e-12)


def test_packaged_state_and_operator_boundaries():
    from cevns_pyeft.experiments.coherent.csi2021_package import load_package_experiment
    from cevns_pyeft.contracts.parameters import TheoryPoint
    from cevns_pyeft.theory.li2026.operators import canonicalize_wilson_coefficients
    experiment = load_package_experiment(PACKAGE)
    model = experiment.model
    for component in model.source.for_run(model.run).components:
        fixed = component.fixed_state_for_fast()
        assert not fixed.is_energy_dependent
        for target in model.targets.isotopes:
            E = np.array([30.])
            state = component.state_at(E, parameters=TheoryPoint().state)
            for T in [0., 1., model.interaction.kinematics.maximum_recoil_keV(target, 30.)]:
                cross = model.interaction.dsigma_dT(target=target, energy_MeV=E,
                    recoil_keV=T, incident_state=state, parameters=TheoryPoint())
                assert cross.unit == "cm^2/keV" and cross.values_cm2_per_keV.shape == (1,)
            for T in [-1., np.nan, np.inf]:
                with pytest.raises(ValueError):
                    model.interaction.dsigma_dT(target=target, energy_MeV=E,
                        recoil_keV=T, incident_state=state, parameters=TheoryPoint())
    with pytest.raises((ValueError,KeyError)):
        canonicalize_wilson_coefficients(wc_triplets={(9,99,"x"):np.eye(3)})
    with pytest.raises(ValueError):
        canonicalize_wilson_coefficients(wc_triplets={(5,1,""):np.eye(3)})


def test_unused_snapshot_does_not_change_physical_or_analysis_identity(tmp_path):
    from cevns_pyeft.experiments.coherent.csi2021_package import load_package_experiment
    location = copy_package(tmp_path)
    first = load_package_experiment(location)
    def change(d):
        for item in ["value", "adopted_value"]:
            d["parameters"]["lecs.L9"][item] += .1
    rewrite_package(location, transform_document=change)
    second = load_package_experiment(location)
    assert first.physics_fingerprint == second.physics_fingerprint
    assert first.analysis_fingerprint == second.analysis_fingerprint


def test_response_replacement_changes_actual_coefficient_dependencies():
    from cevns_pyeft.experiments.coherent.csi2021_package import load_package_experiment
    experiment = load_package_experiment(PACKAGE)
    interaction = experiment.model.interaction
    response = interaction.packed_responses["Cs133"]
    changed_response = replace(response, exp_factor=response.exp_factor*.99)
    changed = replace(interaction, packed_responses={**interaction.packed_responses, "Cs133":changed_response})
    assert interaction.describe() != changed.describe()



