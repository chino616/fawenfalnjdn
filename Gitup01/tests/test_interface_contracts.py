"""Behavioral contracts and independent toy-source integrals (not experiment data)."""
from dataclasses import replace
import numpy as np
import pytest

from cevns_pyeft.contracts import (Axis, Binning, BinProbabilities, DetectorFluence, EnergySupport,
    FluenceLine, IncidentStateBatch, IntegrationSettings, IntegratedRunReference, LiveTimeExposure,
    POTExposure, StateParameters, TargetInventory, TargetIsotope, TheoryPoint)
from cevns_pyeft.contracts.interaction import DifferentialCrossSection, ElasticKinematics
from cevns_pyeft.contracts.modules import IncompatibleNormalizationError, ModuleDescriptor, UnsupportedCapabilityError
from cevns_pyeft.core.model import ExperimentModel
from cevns_pyeft.core.predict import predict, validate_compatibility
from cevns_pyeft.detectors.csi2021 import CsI2021Observation, ConstantEfficiency
from cevns_pyeft.detectors.selection import LegacyComponentAcceptance
from cevns_pyeft.experiments.coherent.csi2021 import make_csi2021_model
from cevns_pyeft.rates.recoil import integrate_recoil_yield
from cevns_pyeft.sources.composable import CallableFluenceComponent, DifferentialFluxSource, IntegratedFluenceSource
from cevns_pyeft.sources.sns import SNSLegacySource
from cevns_pyeft.targets import csi_target_inventory, inventory_from_number_fractions


def state_provider(energy_MeV, *, parameters):
    fraction = np.asarray(energy_MeV) / 10 * parameters.values.get("fraction_scale", 1)
    rho = np.zeros((len(energy_MeV), 3, 3), complex)
    rho[:, 0, 0], rho[:, 1, 1] = fraction, 1 - fraction
    return IncidentStateBatch(energy_MeV, rho, "nu", "test_energy_state", ("fraction_scale",))


class ToyInteraction:
    """Test fixture with a constant cross-section scale times electron density."""
    kinematics = ElasticKinematics()

    def describe(self):
        return ModuleDescriptor("interaction", "test_fixture_density_cross_section")

    def dsigma_dT(self, *, target, energy_MeV, recoil_keV, incident_state, parameters):
        return DifferentialCrossSection(energy_MeV, incident_state.rho[:, 0, 0].real, recoil_keV, "test_fixture")


def toy_component(*, lines=True, provider=state_provider):
    return CallableFluenceComponent("arbitrary_test_beam", "nu", EnergySupport((1, 3)),
        lambda e: np.full_like(e, 2.0), provider,
        (FluenceLine("lower", 0.5, 1.0), FluenceLine("upper", 4.0, 2.0)) if lines else ())


TARGET = TargetIsotope("test_isotope", 1.0, 1.0, 2.0)


@pytest.mark.parametrize("lines,expected", [(True, 1.65), (False, 0.8)])
def test_arbitrary_components_empty_and_multiple_lines_have_independent_integral(lines, expected):
    result = integrate_recoil_yield(toy_component(lines=lines), TARGET, ToyInteraction(),
        parameters=TheoryPoint(), numerics=IntegrationSettings(n_enu=9), recoil_keV=np.array([0.1, 0.2]))
    # Integral 2*(E/10)dE from 1 to 3 is .8; the two delta lines add .05 and .8.
    np.testing.assert_allclose(result.values_per_keV, expected, rtol=1e-14)
    scaled = integrate_recoil_yield(toy_component(lines=lines), TARGET, ToyInteraction(),
        parameters=TheoryPoint(state=StateParameters({"fraction_scale": 0.5})),
        numerics=IntegrationSettings(n_enu=9), recoil_keV=np.array([0.1, 0.2]))
    np.testing.assert_allclose(scaled.values_per_keV, expected * .5, rtol=1e-14)


def test_state_grid_values_are_checked_and_copied():
    energy = np.array([1.0, 2.0])
    state = state_provider(energy, parameters=StateParameters())
    energy[0] = .5
    with pytest.raises(ValueError, match="coordinates"):
        state.require_coordinates(energy, "nu")
    with pytest.raises(ValueError):
        state.rho[0, 0, 0] = 0
    def wrong_grid(energy_MeV, *, parameters):
        return state_provider(energy_MeV + 0.01, parameters=parameters)
    with pytest.raises(ValueError, match="coordinates"):
        integrate_recoil_yield(toy_component(provider=wrong_grid), TARGET, ToyInteraction(),
            parameters=TheoryPoint(), numerics=IntegrationSettings(), recoil_keV=np.array([.1, .2]))


def test_flux_times_livetime_and_integrated_fluence_agree_and_cannot_mix():
    descriptor = ModuleDescriptor("source", "test_fixture_detector_flux")
    flux = DifferentialFluxSource((toy_component(),), descriptor)
    fluence = flux.for_run(LiveTimeExposure(7, "fixture"))
    source = IntegratedFluenceSource(fluence, descriptor)
    energy = np.array([1., 2.])
    np.testing.assert_array_equal(source.for_run(IntegratedRunReference("fixture")).components[0].continuum(energy), [14, 14])
    assert fluence.components[0].lines[1].fluence_per_cm2 == 14
    for run in (POTExposure(3, "fixture"), LiveTimeExposure(7, "fixture"), IntegratedRunReference("other")):
        with pytest.raises(IncompatibleNormalizationError):
            source.for_run(run)
    with pytest.raises(IncompatibleNormalizationError):
        flux.for_run(POTExposure(3))
    with pytest.raises(IncompatibleNormalizationError):
        SNSLegacySource().for_run(LiveTimeExposure(7, "fixture"))


def test_source_rejects_wrong_units_and_duplicate_ids():
    with pytest.raises(ValueError, match="requires"):
        DetectorFluence((toy_component(),), "test", continuum_unit="GeV^-1")
    with pytest.raises(ValueError, match="unique"):
        DetectorFluence((toy_component(), toy_component()), "test")
    with pytest.raises(ValueError):
        FluenceLine("bad", 1, -1)
    with pytest.raises(ValueError, match="continuum"):
        integrate_recoil_yield(replace(toy_component(), continuum_function=lambda e: -np.ones_like(e)), TARGET,
            ToyInteraction(), parameters=TheoryPoint(), numerics=IntegrationSettings(), recoil_keV=np.array([.1, .2]))


def test_targets_number_fractions_and_explicit_mass_fractions_agree():
    inventory = csi_target_inventory()
    cs, iodine = inventory.isotopes
    assert cs.number_of_nuclei == pytest.approx(iodine.number_of_nuclei, rel=1e-15)
    from_number = inventory_from_number_fractions(14.57, inventory.isotopes, [.5, .5])
    for a, b in zip(inventory.isotopes, from_number.isotopes):
        assert a.number_of_nuclei == pytest.approx(b.number_of_nuclei, rel=1e-15)
    with pytest.raises(ValueError, match="mass"):
        TargetInventory((cs,), 14.57)


def test_probability_units_selection_and_adjacent_bin_closure():
    selection = LegacyComponentAcceptance({"test": .8})
    observation = CsI2021Observation(selection, efficiency=ConstantEfficiency(1))
    axis = Axis(observation.axis_name, observation.axis_unit, [0, 10, 20, 60])
    bins = Binning((axis,))
    recoil = np.array([2., 7., 15.])
    values = observation.bin_probabilities(target=TARGET, recoil_keV=recoil, binning=bins, component_id="test")
    combined = observation.bin_probabilities(target=TARGET, recoil_keV=recoil,
        binning=Binning((replace(axis, edges=[0, 60]),)), component_id="test")
    np.testing.assert_allclose(values.values.sum(axis=1), combined.values[:, 0], rtol=1e-9, atol=1e-11)
    with pytest.raises(ValueError, match="at most one"):
        BinProbabilities(recoil, bins, np.full((3, 3), .5))
    with pytest.raises(ValueError, match="more than once"):
        BinProbabilities(recoil, bins, np.full((3, 3), .1), ("gate", "gate"))
    with pytest.raises(ValueError, match="no acceptance"):
        observation.bin_probabilities(target=TARGET, recoil_keV=recoil, binning=bins, component_id="unknown")
    with pytest.raises(ValueError, match="clock"):
        Axis("time", "us", [0, 1, 2])


def test_generic_full_pipeline_uses_probability_objects_and_arbitrary_component_names():
    class ToyObservation:
        axis_name, axis_unit = "test observable", "test-unit"

        def describe(self):
            return ModuleDescriptor("observation", "test_fixture_fixed_probability", capabilities=("bin_probabilities_1d",))

        def bin_probabilities(self, *, target, recoil_keV, binning, component_id):
            return BinProbabilities(recoil_keV, binning, np.tile([.2, .3], (len(recoil_keV), 1)))

    component = toy_component()
    fluence = DetectorFluence((component,), "test")
    model = ExperimentModel(IntegratedFluenceSource(fluence, ModuleDescriptor("source", "test_fixture")),
        IntegratedRunReference("test"), TargetInventory((TARGET,), 2.), ToyInteraction(), ToyObservation(),
        Binning((Axis("test observable", "test-unit", [0, 1, 2]),)))
    numerics = IntegrationSettings(n_er=5, n_enu=9, strategy="bin_probability_v1")
    result = predict(model, numerics=numerics)
    recoil = result.diagnostics["recoil_yields"][(component.component_id, TARGET.isotope_id)]
    expected = np.trapezoid(recoil.values_per_keV, recoil.recoil_keV) * 2 * np.array([.2, .3])
    np.testing.assert_allclose(result.counts, expected, rtol=1e-14)
    assert tuple(result.components) == (("arbitrary_test_beam", "test_isotope"),)


def test_invalid_backends_units_and_unconsumed_configuration_are_rejected():
    model = make_csi2021_model("data/responses/responses_all.json")
    with pytest.raises(UnsupportedCapabilityError, match="Fast"):
        validate_compatibility(replace(model, interaction=ToyInteraction()), parameters=TheoryPoint(), numerics=IntegrationSettings(), backend="fast")
    assert validate_compatibility(model, parameters=TheoryPoint(), numerics=IntegrationSettings(), backend="fast").backend == "fast"
    report = validate_compatibility(model, parameters=TheoryPoint(), numerics=IntegrationSettings(), backend="auto")
    assert report.backend == "slow" and report.fallback_reason
    with pytest.raises(ValueError, match="unit mismatch"):
        predict(replace(model, binning=Binning((replace(model.binning.axes[0], unit="keV"),))))
    with pytest.raises(TypeError):
        make_csi2021_model("data/responses/responses_all.json", unused_parameter=1)
    with pytest.raises(ValueError, match="does not consume"):
        predict(model, parameters=TheoryPoint(state=StateParameters({"unconsumed": 1})),
            numerics=IntegrationSettings(n_er=3, n_enu=6))


def test_generic_modules_do_not_import_concrete_experiments_or_workflow():
    import ast
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / "src/cevns_pyeft"
    files = list((root / "contracts").glob("*.py")) + [root / name for name in (
        "rates/recoil.py", "rates/folding.py", "core/model.py", "core/predict.py")]
    for path in files:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            modules = [node.module or ""] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            assert not any("experiments" in name or "workflows" in name for name in modules), path


def test_neutral_import_does_not_eagerly_load_experiments_and_engine_still_works(tmp_path):
    import os
    from pathlib import Path
    import subprocess
    import sys
    root = Path(__file__).resolve().parents[1]
    script = """import sys
from cevns_pyeft.core.predict import predict
from cevns_pyeft.core.model import ExperimentModel
assert not any(name.startswith('cevns_pyeft.experiments') for name in sys.modules)
from cevns_pyeft.core import engine
assert callable(engine.slow_counts_csi2021)
"""
    result = subprocess.run([sys.executable, "-c", script], cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(root / "src")}, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
