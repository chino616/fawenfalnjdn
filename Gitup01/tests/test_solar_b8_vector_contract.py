"""Independent charge, interference, decoupling and Runtime identity checks."""
from dataclasses import replace
from pathlib import Path
import numpy as np
import pytest
from cevns_pyeft.contracts import TheoryPoint, IncidentStateBatch, TargetIsotope
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.runtime import predict_experiment
from cevns_pyeft.experiments.solar_vector import with_solar_light_vector
from cevns_pyeft.theory.light_vector import LightVectorKN

ROOT = Path(__file__).resolve().parents[1]
X = ROOT / 'data/experiments/XENONnT/XENONnT_2024_SolarB8'
P = ROOT / 'data/experiments/PandaX4T/PandaX4T_2024_US2'


@pytest.fixture(scope='module')
def base():
    return load_experiment_package(X)


def dsigma(interaction, target, *, t=1.0, sm=True, angle=.23857):
    energy = np.array([8., 12., 16.])
    rho = IncidentStateBatch(energy, np.eye(3) / 3, 'nu', 'test')
    return interaction.dsigma_dT(target=target, energy_MeV=energy, recoil_keV=t,
        incident_state=rho, parameters=TheoryPoint(include_sm=sm, sin2thetaW=angle)).values_cm2_per_keV


def test_zero_coupling_exactly_returns_same_sm(base):
    sm = base.model.interaction; target = base.model.targets.isotopes[0]
    vector = LightVectorKN(sm, 10., 0.)
    np.testing.assert_array_equal(dsigma(vector, target), dsigma(sm, target))
    np.testing.assert_array_equal(dsigma(vector, target, sm=False), np.zeros(3))


def test_absolute_published_charge_shift_and_interference_sign(base):
    sm = base.model.interaction; target = base.model.targets.isotopes[4]
    a = sm.mass_numbers[4]; z = sm.proton_number; n = a - z
    q = (.5 - 2 * .23857) * z - .5 * n
    delta = 3 * a * (2e-5) ** 2 / (2 ** .5 * sm.fermi_GeV_minus2 *
        (.010 ** 2 + 2 * target.kinematic_mass_GeV * 1e-6))
    universal = LightVectorKN(sm, 10., 2e-5)
    bl = LightVectorKN(sm, 10., 2e-5, 'b_minus_l')
    np.testing.assert_allclose(dsigma(universal, target) / dsigma(sm, target), (1 + delta / q) ** 2, rtol=3e-15)
    np.testing.assert_allclose(dsigma(bl, target) / dsigma(sm, target), (1 - delta / (3 * q)) ** 2, rtol=3e-15)
    assert np.all(dsigma(universal, target) < dsigma(sm, target))
    assert np.all(dsigma(bl, target) > dsigma(sm, target))


def test_np_only_has_g_fourth_power_and_mass_decouples(base):
    sm = base.model.interaction; target = base.model.targets.isotopes[0]
    first = LightVectorKN(sm, 10., 1e-5)
    doubled = replace(first, coupling=2e-5)
    np.testing.assert_allclose(dsigma(doubled, target, sm=False), 16 * dsigma(first, target, sm=False), rtol=2e-15)
    heavy = replace(first, mass_MeV=1e8)
    np.testing.assert_allclose(dsigma(heavy, target), dsigma(sm, target), rtol=3e-14)


def test_interference_is_signed_and_charge_cancellation_is_not_clipped(base):
    sm = base.model.interaction; target = base.model.targets.isotopes[4]
    proto = LightVectorKN(sm, 10., 1.)
    q = proto.weak_charge(target, .23857)
    cancel = replace(proto, coupling=float(np.sqrt(-q / proto.charge_shift(target, 1.))))
    total = dsigma(cancel, target); pure_np = dsigma(cancel, target, sm=False); standard = dsigma(sm, target)
    assert np.all(total < 1e-28 * standard)
    np.testing.assert_allclose(pure_np, standard, rtol=5e-15)
    np.testing.assert_allclose(total - standard - pure_np, -2 * standard, rtol=5e-15)
    assert np.all(dsigma(replace(cancel, coupling=2 * cancel.coupling), target) > standard)


def test_vector_flavor_universality_and_elastic_support(base):
    sm = base.model.interaction; target = base.model.targets.isotopes[0]
    vector = LightVectorKN(sm, 10., 2e-5)
    energy = np.array([10.]); point = TheoryPoint(sin2thetaW=.23857)
    values = []
    for flavor in range(3):
        rho = IncidentStateBatch(energy, np.diag(np.eye(3)[flavor]), 'nu', 'flavor_test')
        values.append(vector.dsigma_dT(target=target, energy_MeV=energy, recoil_keV=.8, incident_state=rho, parameters=point).values_cm2_per_keV)
    np.testing.assert_array_equal(values[0], values[1]); np.testing.assert_array_equal(values[1], values[2])
    t = vector.kinematics.maximum_recoil_keV(target, 10.)
    rho = IncidentStateBatch(energy, np.eye(3) / 3, 'nu', 'endpoint')
    above = vector.dsigma_dT(target=target, energy_MeV=energy, recoil_keV=t * 1.001, incident_state=rho, parameters=point)
    np.testing.assert_array_equal(above.values_cm2_per_keV, [0.])


def test_zero_sm_charge_is_finite_without_dividing_by_zero(base):
    sm = replace(base.model.interaction, proton_number=1, mass_numbers=(1,), isotope_ids=('H1',))
    target = TargetIsotope('H1', .938, 1.67e-27, 1., 'algebraic test target')
    vector = LightVectorKN(sm, 10., 1e-5)
    assert np.all(np.isfinite(dsigma(vector, target, angle=.25)))
    assert np.all(dsigma(vector, target, angle=.25) > 0)


@pytest.mark.parametrize('mass,g,scenario', [(0,1e-5,'universal'),(-1,1e-5,'universal'),(10,-1,'universal'),(10,np.nan,'universal'),(10,1e-5,'other')])
def test_invalid_model_parameters_rejected(base, mass, g, scenario):
    with pytest.raises(ValueError):
        LightVectorKN(base.model.interaction, mass, g, scenario)


def test_component_override_changes_fingerprint_and_preserves_response(base):
    a = with_solar_light_vector(base, mass_MeV=10., coupling=2e-5)
    b = with_solar_light_vector(base, mass_MeV=10., coupling=2e-5, scenario='b_minus_l')
    assert len({base.physics_fingerprint, a.physics_fingerprint, b.physics_fingerprint}) == 3
    np.testing.assert_array_equal(a.model.observation[0].probability, base.model.observation[0].probability)
    assert a.describe()['actual_assembly']['implementations']['interaction']['module'] == 'cevns_pyeft.theory.light_vector'
    first = predict_experiment(a, numerics={'n_er':31, 'n_enu':24})
    second = predict_experiment(b, numerics={'n_er':31, 'n_enu':24})
    assert np.all(first.counts >= 0) and np.all(second.counts > first.counts)
    np.testing.assert_allclose(sum(p.counts for p in first.detector_predictions.values()), first.counts, rtol=1e-14)


def test_pandax_stays_a_true_recoil_projection():
    p = load_experiment_package(P)
    a = with_solar_light_vector(p, mass_MeV=10., coupling=2e-5)
    assert a.definition.observation.unit == 'keVnr'
    assert a.definition.capabilities['electron_spectrum'] == 'BLOCKED missing US2 response'
