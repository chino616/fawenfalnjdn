"""Compare to arrays captured BEFORE the old entry point was changed."""
from pathlib import Path
import json
import numpy as np
import pytest

from cevns_pyeft.contracts import IntegrationSettings, TheoryPoint
from cevns_pyeft.core.predict import predict
from cevns_pyeft.experiments.coherent.csi2021 import make_csi2021_model
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import slow_counts_csi2021
from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import slow_counts_csi2017
from cevns_pyeft.experiments.coherent.slow_counts_ar2020 import slow_counts_ar2020
from cevns_pyeft.sources.sns import LEGACY_COMPONENT_IDS
from cevns_pyeft.statistics.adapters import to_statistical_vector
from cevns_pyeft.statistics.datasets import csi2021_dataset
from cevns_pyeft.statistics.likelihoods import chi2_csi2021
from tools.refactor.freeze_baseline import points, GRIDS

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "tests/reference/interface_refactor_v1"
RESPONSE = ROOT / "data/responses/responses_all.json"


@pytest.fixture(scope="module")
def baseline():
    with np.load(REFERENCE / "baseline.npz", allow_pickle=False) as stored:
        yield stored


CASES = [(name, grid) for name in points() for grid in GRIDS if grid != "default" or name == "sm"]


@pytest.mark.parametrize("name,grid", CASES)
def test_new_pipeline_preserves_frozen_source_isotope_bin_outputs(name, grid, baseline):
    wc, sm = points()[name]
    settings = GRIDS[grid]
    model = make_csi2021_model(RESPONSE)
    result = predict(model, parameters=TheoryPoint(wc, include_sm=sm),
                     numerics=IntegrationSettings.legacy_csi2021_v1(**settings))
    prefix = f"csi2021/{name}/{grid}"
    for flavor, component_id in LEGACY_COMPONENT_IDS.items():
        combined = np.zeros(9)
        for target in model.targets.isotopes:
            actual = result.components[(component_id, target.isotope_id)]
            old_raw = baseline[f"{prefix}/raw/{flavor}/{target.isotope_id}"]
            fraction = target.number_of_nuclei * target.nucleus_mass_kg / model.targets.detector_mass_kg
            acceptance = model.observation.selection.acceptance(component_id)
            np.testing.assert_allclose(actual, old_raw * fraction * acceptance, rtol=1e-10, atol=1e-12)
            new_raw = result.diagnostics["preselection_per_nucleus"][(component_id, target.isotope_id)] * model.targets.detector_mass_kg / target.nucleus_mass_kg
            np.testing.assert_allclose(new_raw, old_raw, rtol=1e-10, atol=1e-12)
            combined += actual
        np.testing.assert_allclose(combined, baseline[f"{prefix}/counts_per_bin/{flavor}"], rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(result.counts, baseline[f"{prefix}/counts_per_bin/total"], rtol=1e-10, atol=1e-12)


@pytest.mark.parametrize("name,grid", CASES)
def test_legacy_entry_preserves_return_keys_units_and_raw_semantics(name, grid, baseline):
    wc, sm = points()[name]
    result = slow_counts_csi2021(RESPONSE, wc, include_sm=sm, **GRIDS[grid])
    assert set(result) == {"counts_per_bin", "counts_per_npe", "target_flavor_counts_per_bin", "pe_bins", "model_note"}
    prefix = f"csi2021/{name}/{grid}"
    for kind in ("counts_per_bin", "counts_per_npe"):
        for flavor, values in result[kind].items():
            np.testing.assert_allclose(values, baseline[f"{prefix}/{kind}/{flavor}"], rtol=1e-10, atol=1e-12)
    for flavor, targets in result["target_flavor_counts_per_bin"].items():
        for target, values in targets.items():
            np.testing.assert_allclose(values, baseline[f"{prefix}/raw/{flavor}/{target}"], rtol=1e-10, atol=1e-12)


@pytest.mark.parametrize("dataset,fn,settings", [("csi2017", slow_counts_csi2017, {"n_enu": 12}), ("ar2020", slow_counts_ar2020, GRIDS["medium"])])
@pytest.mark.parametrize("name", ["sm", "multiflavor"])
def test_shared_coherent_datasets_preserve_frozen_counts(dataset, fn, settings, name, baseline):
    wc, sm = points()[name]
    result = fn(RESPONSE, wc, include_sm=sm, **settings)
    for flavor, values in result["counts_per_bin"].items():
        np.testing.assert_allclose(values, baseline[f"{dataset}/{name}/{flavor}"], rtol=1e-10, atol=1e-12)


def test_same_prediction_preserves_legacy_approximate_chi2():
    metadata = json.loads((REFERENCE / "metadata.json").read_text(encoding="utf-8"))
    result = predict(make_csi2021_model(RESPONSE), numerics=IntegrationSettings.legacy_csi2021_v1(**GRIDS["small"]))
    converted = to_statistical_vector(result, target_observable=csi2021_dataset().observable)
    assert chi2_csi2021(converted).chi2 == pytest.approx(metadata["chi2_small_sm"], rel=1e-12)


def test_existing_statistics_router_uses_same_prediction_and_preserves_labels(baseline):
    from cevns_pyeft.statistics.predictors import predict_raw_components, SOURCE_COMPONENT_LABELS
    from cevns_pyeft.statistics.observables import convert_prediction_to_dataset_observable
    result = predict_raw_components("CsI2021", responses_json=RESPONSE, **GRIDS["small"])
    for source, vector in result.components.items():
        np.testing.assert_allclose(vector.values, baseline[f"csi2021/sm/small/counts_per_bin/{source}"], rtol=1e-10, atol=1e-12)
        assert vector.metadata["source_component"] == SOURCE_COMPONENT_LABELS[source]
    metadata = json.loads((REFERENCE / "metadata.json").read_text(encoding="utf-8"))
    converted = convert_prediction_to_dataset_observable(result.total, csi2021_dataset().observable)
    assert chi2_csi2021(converted).chi2 == pytest.approx(metadata["chi2_small_sm"], rel=1e-12)
    with pytest.raises(TypeError, match="unexpected"):
        predict_raw_components("CsI2021", responses_json=RESPONSE, unconsumed=True)
