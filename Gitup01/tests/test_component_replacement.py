from dataclasses import replace
import numpy as np
import pytest

from cevns_pyeft.contracts import IntegrationSettings, TheoryPoint, StateParameters
from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.core.predict import predict
from cevns_pyeft.detectors.csi2021 import ConstantEfficiency
from cevns_pyeft.experiments.coherent.csi2021 import make_csi2021_model
from cevns_pyeft.experiments.coherent.sns import build_neutrino_empirical_flux_sns, SNS_DATASETS, loadNeutrinoEmpiricalFluxSNS
from cevns_pyeft.rates.differential import differential_cross_section_nn, p_smearing_csi
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.sources.composable import ScaledSource
from cevns_pyeft.sources.sns import LEGACY_COMPONENT_IDS
from cevns_pyeft.statistics.adapters import to_statistical_vector
from cevns_pyeft.statistics.datasets import csi2021_dataset
from cevns_pyeft.targets import csi_target_inventory

NUMERICS = IntegrationSettings(n_er=5, n_enu=12, n_observed_bin=4, observed_step=4)
RESPONSES = "data/responses/responses_all.json"


class EquivalentSourceAdapter:
    def __init__(self, original):
        self.original = original

    def for_run(self, run):
        return self.original.for_run(run)

    def describe(self):
        return ModuleDescriptor("source", "equivalent_source_adapter", parameters={"original": self.original.describe().as_dict()})


def test_real_source_slot_replacement_scaling_and_instance_isolation():
    model = make_csi2021_model(RESPONSES)
    first = predict(model, numerics=NUMERICS)
    equivalent = predict(replace(model, source=EquivalentSourceAdapter(model.source)), numerics=NUMERICS)
    doubled = predict(replace(model, source=ScaledSource(model.source, 2)), numerics=NUMERICS)
    repeated = predict(model, numerics=NUMERICS)
    np.testing.assert_array_equal(first.counts, equivalent.counts)
    np.testing.assert_array_equal(first.counts, repeated.counts)
    for key, value in first.components.items():
        np.testing.assert_allclose(doubled.components[key], value * 2, rtol=1e-14, atol=1e-14)
    assert first.model_record["model_fingerprint"] != doubled.model_record["model_fingerprint"]
    assert all(not value.flags.writeable for value in first.components.values())


def test_only_target_mass_changes_counts_not_per_nucleus_yield():
    model = make_csi2021_model(RESPONSES)
    first = predict(model, numerics=NUMERICS)
    doubled = predict(replace(model, targets=csi_target_inventory(29.14)), numerics=NUMERICS)
    np.testing.assert_allclose(doubled.counts, first.counts * 2, rtol=1e-14)
    for key in first.components:
        np.testing.assert_array_equal(first.diagnostics["recoil_yields"][key].values_per_keV,
                                      doubled.diagnostics["recoil_yields"][key].values_per_keV)


def test_observation_efficiency_replacement_and_selection_are_applied_once():
    model = make_csi2021_model(RESPONSES)
    identity_model = replace(model, observation=replace(model.observation, efficiency=ConstantEfficiency(1)))
    identity = predict(identity_model, numerics=NUMERICS)
    half = predict(replace(identity_model, observation=replace(identity_model.observation, efficiency=ConstantEfficiency(.5))), numerics=NUMERICS)
    zero = predict(replace(identity_model, observation=replace(identity_model.observation, efficiency=ConstantEfficiency(0))), numerics=NUMERICS)
    np.testing.assert_array_equal(zero.counts, np.zeros(9))
    np.testing.assert_allclose(half.counts, identity.counts * .5, rtol=1e-14)
    for (source, isotope), values in identity.components.items():
        before = identity.diagnostics["preselection_per_nucleus"][(source, isotope)]
        target = next(t for t in model.targets.isotopes if t.isotope_id == isotope)
        expected = before * target.number_of_nuclei * model.observation.selection.acceptance(source)
        np.testing.assert_allclose(values, expected, rtol=1e-14)
    np.testing.assert_array_equal(predict(identity_model, numerics=NUMERICS).counts, identity.counts)


def test_sns_parameters_are_actually_consumed_and_legacy_loader_is_equal():
    old = loadNeutrinoEmpiricalFluxSNS("CsI2021")
    explicit = build_neutrino_empirical_flux_sns(SNS_DATASETS["CsI2021"])
    grid = np.linspace(.1, 55, 25)
    model = make_csi2021_model(RESPONSES)
    fluence = model.source.for_run(model.run)
    by_id = {part.component_id: part for part in fluence.components}
    for flavor in ("e", "mub"):
        np.testing.assert_array_equal(old["measured"][flavor](grid), explicit["measured"][flavor](grid))
        np.testing.assert_array_equal(old["measured"][flavor](grid), by_id[LEGACY_COMPONENT_IDS[flavor]].continuum(grid))
    twice_distance = replace(model.source, baseline_m=38.6).for_run(model.run)
    for first, quarter in zip(fluence.components, twice_distance.components):
        np.testing.assert_allclose(quarter.continuum(grid), first.continuum(grid) * .25, rtol=1e-14)
    assert by_id["prompt_numu"].lines[0].fluence_per_cm2 == old["measured"]["muLine"][1]


@pytest.mark.parametrize("name,flavor", [("Cs133", "e"), ("I127", "mub")])
def test_interaction_adapter_matches_existing_cross_section_and_response(name, flavor):
    model = make_csi2021_model(RESPONSES)
    target = next(t for t in model.targets.isotopes if t.isotope_id == name)
    source = next(c for c in model.source.for_run(model.run).components if c.component_id == LEGACY_COMPONENT_IDS[flavor])
    energy = np.array([20., 30., 40.])
    state = source.state_at(energy, parameters=StateParameters())
    matrix = np.array([[1e-6, .2e-6j, 0], [0, .4e-6, 0], [0, 0, 0]])
    point = TheoryPoint({(6, 1, "u"): matrix})
    result = model.interaction.dsigma_dT(target=target, energy_MeV=energy, recoil_keV=2,
                                        incident_state=state, parameters=point)
    response = ResponseDB(RESPONSES).get({"Cs133": "Cs133", "I127": "I"}[name])
    old = differential_cross_section_nn(response, 2, energy, rho=state.rho, particle_kind=state.particle_kind,
                                        wc_triplets=point.wc_triplets, include_sm=True, sin2thetaW=.2387)
    np.testing.assert_array_equal(result.values_cm2_per_keV, old.dsigma_cm2_per_keV)
    assert np.max(result.values_cm2_per_keV) > 0
    np.testing.assert_array_equal(model.observation.response.density(energy, 2, target=target), p_smearing_csi(energy, 2))


def test_statistics_adapter_converts_bin_width_only_once():
    model = make_csi2021_model(RESPONSES)
    result = predict(model, numerics=NUMERICS)
    dataset = csi2021_dataset()
    raw = to_statistical_vector(result)
    converted = to_statistical_vector(result, target_observable=dataset.observable)
    np.testing.assert_array_equal(raw.values, result.counts)
    np.testing.assert_allclose(converted.values, result.counts / np.diff(result.axes[0].edges), rtol=1e-15)
    wrong = replace(dataset.observable, bin_edges=dataset.observable.bin_edges + 1)
    with pytest.raises(ValueError, match="edges"):
        to_statistical_vector(result, target_observable=wrong)
    for label, component in (("mu", "prompt_numu"), ("e", "delayed_nue"), ("mub", "delayed_numubar")):
        values = to_statistical_vector(result, component_id=component).values
        expected = sum(value for (source, _), value in result.components.items() if source == component)
        np.testing.assert_array_equal(values, expected)
