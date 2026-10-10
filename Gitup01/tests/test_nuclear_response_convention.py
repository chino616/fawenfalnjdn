import numpy as np
import pytest

from cevns_pyeft.nuclear.response import ResponseDB


RESPONSES = ResponseDB("data/responses/responses_all.json")


@pytest.mark.parametrize("nucleus", ["Cs133", "I", "Ar40"])
def test_m_response_zero_momentum_selects_np_ordering_and_positive_cross_term(nucleus):
    """The coherent M response at q=0 diagnoses the external p/n ordering.

    With the JSON-declared (p,n) basis, W_M(0) must have proton-proton,
    proton-neutron and neutron-neutron entries close to [[Z^2, ZN],
    [ZN, N^2]].  This test locks the ordering and p-n cross-term sign used by
    the Li2026 contraction path.  Exact response-table normalization remains a
    separate source-table audit item.
    """

    response = RESPONSES.get(nucleus)
    z = float(response.get_basic("Z"))
    n = float(response.get_basic("N"))

    got = np.asarray(response.W_np("M", 0.0), dtype=float)
    expected_pn = np.array([[z * z, z * n], [z * n, n * n]], dtype=float)
    expected_np = np.array([[n * n, z * n], [z * n, z * z]], dtype=float)

    assert got[0, 0] > 0.0
    assert got[0, 1] > 0.0
    assert got[1, 0] > 0.0
    assert got[1, 1] > 0.0
    np.testing.assert_allclose(got, got.T, rtol=0.0, atol=0.0)
    assert np.linalg.norm(got - expected_pn) < np.linalg.norm(got - expected_np)


def test_iodine_m_response_zero_momentum_normalization_is_not_silently_promoted():
    """Freeze the current iodine residual until the source table is audited."""

    response = RESPONSES.get("I")
    z = float(response.get_basic("Z"))
    n = float(response.get_basic("N"))
    got = np.asarray(response.W_np("M", 0.0), dtype=float)
    expected = np.array([[z * z, z * n], [z * n, n * n]], dtype=float)
    residual = got - expected

    assert abs(residual[1, 1]) == pytest.approx(0.038805631525118835)
    assert abs(residual[1, 1]) > 1.0e-2


def test_response_json_declares_np_pn_matrix_basis():
    metadata = RESPONSES.meta

    assert metadata["basis"] == "np"
    assert "2x2 matrix in (p,n)" in metadata["note"]
