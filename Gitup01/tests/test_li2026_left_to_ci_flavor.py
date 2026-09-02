import numpy as np
import pytest

from cevns_pyeft.theory.li2026.flavor import zero_flavor_matrix
from cevns_pyeft.theory.li2026.left_to_ci import left_to_ci
from cevns_pyeft.theory.li2026.operators import LI2026_OPERATOR_SPECS


KINEMATICS = {
    "E_nu": 0.05,
    "q0": 1.0e-5,
    "qabs": 0.01,
}
ENTRY = (0, 1)
LEGACY_VALUE = 1.2 - 0.7j


def _coefficient(value=LEGACY_VALUE, *, entry=ENTRY):
    matrix = zero_flavor_matrix()
    matrix[entry] = value
    return matrix


def _assert_only_entry_can_be_nonzero(matrix, entry=ENTRY):
    mask = np.ones((3, 3), dtype=bool)
    mask[entry] = False
    np.testing.assert_array_equal(matrix[mask], 0.0)


@pytest.mark.parametrize("spec", LI2026_OPERATOR_SPECS, ids=lambda spec: spec.name)
def test_all_22_left_coefficients_accept_flavor_matrices(spec):
    ci = left_to_ci({spec.key: _coefficient()}, **KINEMATICS)

    assert set(ci.p) == set(range(1, 15))
    assert set(ci.n) == set(range(1, 15))
    assert set(ci.iso) == set(range(1, 15))

    for index in range(1, 15):
        matrices = (ci.p[index], ci.n[index], *ci.iso[index])
        for matrix in matrices:
            assert matrix.shape == (3, 3)
            assert matrix.dtype == np.complex128
            _assert_only_entry_can_be_nonzero(matrix)

    assert any(
        abs(ci.p[index][ENTRY]) > 0.0 or abs(ci.n[index][ENTRY]) > 0.0
        for index in range(1, 15)
    )


def test_missing_coefficients_produce_independent_zero_matrices():
    ci = left_to_ci({}, **KINEMATICS)
    for index in range(1, 15):
        np.testing.assert_array_equal(ci.p[index], np.zeros((3, 3)))
        np.testing.assert_array_equal(ci.n[index], np.zeros((3, 3)))
        np.testing.assert_array_equal(ci.iso[index][0], np.zeros((3, 3)))
        np.testing.assert_array_equal(ci.iso[index][1], np.zeros((3, 3)))

    assert ci.p[1] is not ci.p[2]


def test_scalar_wilson_coefficient_is_not_silently_promoted():
    with pytest.raises(ValueError, match=r"shape \(3,3\)"):
        left_to_ci({(6, 1, "u"): LEGACY_VALUE}, **KINEMATICS)


def test_lnv_diagonal_is_rejected_and_lnc_diagonal_is_allowed():
    diagonal = np.eye(3, dtype=np.complex128)

    with pytest.raises(ValueError, match="vanishing diagonal"):
        left_to_ci({(7, 4, "u"): diagonal}, **KINEMATICS)

    ci = left_to_ci({(6, 1, "u"): diagonal}, **KINEMATICS)
    np.testing.assert_array_equal(ci.p[1], 2.0 * diagonal)


def test_flavor_entries_propagate_independently_through_matching():
    coefficient = zero_flavor_matrix()
    coefficient[0, 1] = 1.2 - 0.7j
    coefficient[2, 0] = -0.4 + 0.9j

    combined = left_to_ci({(6, 1, "u"): coefficient}, **KINEMATICS)
    first = left_to_ci(
        {(6, 1, "u"): _coefficient(coefficient[0, 1], entry=(0, 1))},
        **KINEMATICS,
    )
    second = left_to_ci(
        {(6, 1, "u"): _coefficient(coefficient[2, 0], entry=(2, 0))},
        **KINEMATICS,
    )

    for index in range(1, 15):
        np.testing.assert_allclose(combined.p[index], first.p[index] + second.p[index])
        np.testing.assert_allclose(combined.n[index], first.n[index] + second.n[index])


@pytest.mark.parametrize(
    "key,index,expected_p,expected_n",
    [
        ((5, 1, ""), 3, 2.7871074057940946 - 1.6258126533798885j, 0.0j),
        ((6, 1, "u"), 1, 2.4 - 1.4j, 1.2 - 0.7j),
        ((6, 1, "d"), 1, 1.2 - 0.7j, 2.4 - 1.4j),
        ((6, 2, "u"), 2, 1.00248 - 0.5847800000000001j, -0.528 + 0.308j),
        ((7, 3, "u"), 4, 0.002136 - 0.001246j, -0.001176 + 0.000686j),
        ((7, 4, "u"), 3, 0.022199999999999998 - 0.012949999999999998j, 0.02004 - 0.011689999999999999j),
        (
            (7, 5, "u"),
            10,
            0.41710686026755944 - 0.24331233515607634j,
            -0.4717068602675595 + 0.27516233515607635j,
        ),
        ((7, 6, ""), 3, -0.06048 + 0.03528j, -0.06048 + 0.03528j),
        (
            (7, 7, ""),
            10,
            -0.36719999999999997 + 0.21419999999999997j,
            -0.36719999999999997 + 0.21419999999999997j,
        ),
        ((8, 1, "u"), 13, 2.4 - 1.4j, 1.2 - 0.7j),
        ((8, 9, ""), 13, 1.2 - 0.7j, 1.2 - 0.7j),
    ],
)
def test_matrix_entries_reproduce_frozen_legacy_scalar_matching(
    key, index, expected_p, expected_n
):
    ci = left_to_ci({key: _coefficient()}, **KINEMATICS)
    assert ci.p[index][ENTRY] == pytest.approx(expected_p)
    assert ci.n[index][ENTRY] == pytest.approx(expected_n)


def test_deprecated_c10_flavor_alias_matches_quark_mass_resolved():
    coefficient = _coefficient()
    with pytest.warns(DeprecationWarning, match="quark_mass_resolved"):
        legacy = left_to_ci(
            {(7, 5, "u"): coefficient},
            c10_mass_mode="flavor",
            **KINEMATICS,
        )
    renamed = left_to_ci(
        {(7, 5, "u"): coefficient},
        c10_mass_mode="quark_mass_resolved",
        **KINEMATICS,
    )

    for index in range(1, 15):
        np.testing.assert_array_equal(legacy.p[index], renamed.p[index])
        np.testing.assert_array_equal(legacy.n[index], renamed.n[index])


def test_unknown_c10_mass_mode_is_rejected():
    with pytest.raises(ValueError, match="Unknown c10_mass_mode"):
        left_to_ci({}, c10_mass_mode="unknown", **KINEMATICS)
