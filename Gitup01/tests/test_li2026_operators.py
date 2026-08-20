import numpy as np
import pytest

from cevns_pyeft.kernels.basis import li2026_left_basis
from cevns_pyeft.theory.li2026.operators import (
    LI2026_OPERATOR_SPECS,
    OPERATOR_SPECS_BY_KEY,
    OperatorSpec,
    get_operator_spec,
    validate_operator_coefficient,
)


def test_metadata_covers_exactly_the_active_22_operator_basis():
    basis_keys = [element.triplet for element in li2026_left_basis()]
    metadata_keys = [spec.key for spec in LI2026_OPERATOR_SPECS]
    assert len(metadata_keys) == 22
    assert len(set(metadata_keys)) == 22
    assert metadata_keys == basis_keys
    assert set(OPERATOR_SPECS_BY_KEY) == set(basis_keys)


def test_operator_dimensions_units_and_sector_counts():
    assert all(spec.dimension == spec.key[0] for spec in LI2026_OPERATOR_SPECS)
    assert all(spec.unit_power_GeV == 4 - spec.dimension for spec in LI2026_OPERATOR_SPECS)
    assert sum(spec.lepton_number == "LNC" for spec in LI2026_OPERATOR_SPECS) == 13
    assert sum(spec.lepton_number == "LNV" for spec in LI2026_OPERATOR_SPECS) == 9
    assert all(
        spec.lnv_diagonal_must_vanish == (spec.lepton_number == "LNV")
        for spec in LI2026_OPERATOR_SPECS
    )


def test_operator_spec_rejects_inconsistent_unit_metadata():
    with pytest.raises(ValueError, match="GeV power"):
        OperatorSpec(
            key=(6, 1, "u"),
            name="bad",
            dimension=6,
            lepton_number="LNC",
            unit_power_GeV=-3,
        )


def test_lookup_rejects_unknown_operator():
    assert get_operator_spec((6, 1, "u")).name == "C6u1"
    with pytest.raises(KeyError, match="Unknown Li2026"):
        get_operator_spec((9, 1, "u"))


def test_lnv_coefficients_require_zero_diagonal_but_lnc_do_not():
    off_diagonal = np.zeros((3, 3), dtype=complex)
    off_diagonal[0, 1] = 2.0 + 3.0j
    np.testing.assert_array_equal(
        validate_operator_coefficient((7, 4, "u"), off_diagonal), off_diagonal
    )

    with pytest.raises(ValueError, match="vanishing diagonal"):
        validate_operator_coefficient((7, 4, "u"), np.eye(3))

    np.testing.assert_array_equal(
        validate_operator_coefficient((6, 1, "u"), np.eye(3)), np.eye(3)
    )
