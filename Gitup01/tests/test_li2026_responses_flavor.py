import math

import numpy as np
import pytest

from cevns_pyeft.foundation import constants as constants
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.theory.li2026.flavor import dagger, zero_flavor_matrix
from cevns_pyeft.theory.li2026.left_to_ci import left_to_ci
from cevns_pyeft.theory.li2026.responses import (
    NR_SECTOR,
    RKinematics,
    _assert_same_sector,
    _ord,
    compute_R_matrices,
    responses_R,
)


ACTIVE_NR = (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14)
LNC_NR = {1, 2, 5, 6, 7, 11, 13, 14}
LNV_NR = {3, 4, 8, 9, 10, 12}
KIN = RKinematics(Enu=0.05, qabs=0.01, m_A=67.95, m_N=0.938)


def _embedded(value, *, row=0, column=1):
    matrix = zero_flavor_matrix()
    matrix[row, column] = value
    return matrix


def _matrix_ci_basis(indices=ACTIVE_NR):
    result = {}
    for index in indices:
        tau0 = zero_flavor_matrix()
        tau1 = zero_flavor_matrix()
        tau0[0, 1] = 0.1 * index + 0.03j * (index + 1)
        tau0[0, 2] = -0.02 * index + 0.01j
        tau1[0, 1] = -0.04 * (index + 2) + 0.02j * index
        tau1[0, 2] = 0.015 * index - 0.025j
        result[index] = (tau0, tau1)
    return result


def test_ord_is_matrix_dagger_product_and_sums_final_flavor():
    coefficient = np.array(
        [[0.0, 2.0, 0.0], [1.0, 3.0, 0.0], [0.0, 4.0, 0.0]],
        dtype=np.complex128,
    )
    expected = dagger(coefficient) @ coefficient

    np.testing.assert_array_equal(_ord(coefficient, coefficient), expected)
    assert expected[1, 1] == pytest.approx(29.0)


def test_nr_sector_metadata_is_complete_and_forbids_cross_interference():
    assert set(NR_SECTOR) == set(range(1, 15))
    assert {index for index, sector in NR_SECTOR.items() if sector == "LNC"} == LNC_NR
    assert {index for index, sector in NR_SECTOR.items() if sector == "LNV"} == LNV_NR

    _assert_same_sector(1, 13)
    _assert_same_sector(3, 8)
    with pytest.raises(RuntimeError, match="LNC-LNV interference is forbidden"):
        _assert_same_sector(1, 3)


def test_responses_and_isospin_tensors_have_canonical_flavor_first_shapes():
    ci_basis = _matrix_ci_basis()
    response = responses_R(ci_basis, KIN, tau=0, taup=1)
    assert set(response) == {
        "M",
        "SigmaPP",
        "SigmaP",
        "PhiPP",
        "PhiPT",
        "Delta",
        "MPhiPP",
        "SigmaPDelta",
    }
    assert all(matrix.shape == (3, 3) for matrix in response.values())

    tensors = compute_R_matrices(
        ci_basis,
        E_nu=KIN.Enu,
        qabs=KIN.qabs,
        mA=KIN.m_A,
        mN=KIN.m_N,
    )
    assert all(tensor.shape == (3, 3, 2, 2) for tensor in tensors.values())
    for response_key, tensor_key in {
        "M": "MM",
        "SigmaPP": "SSPP",
        "SigmaP": "SSP",
        "PhiPP": "PhiPP",
        "PhiPT": "PhiPT",
        "Delta": "DD",
        "MPhiPP": "MPhiPP",
        "SigmaPDelta": "SigmaPDelta",
    }.items():
        np.testing.assert_array_equal(tensors[tensor_key][:, :, 0, 1], response[response_key])


def test_lnc_and_lnv_response_sectors_add_without_cross_terms():
    all_coefficients = _matrix_ci_basis()
    lnc_coefficients = {i: value for i, value in all_coefficients.items() if i in LNC_NR}
    lnv_coefficients = {i: value for i, value in all_coefficients.items() if i in LNV_NR}

    for tau in (0, 1):
        for taup in (0, 1):
            total = responses_R(all_coefficients, KIN, tau=tau, taup=taup)
            lnc = responses_R(lnc_coefficients, KIN, tau=tau, taup=taup)
            lnv = responses_R(lnv_coefficients, KIN, tau=tau, taup=taup)
            for channel in total:
                np.testing.assert_allclose(total[channel], lnc[channel] + lnv[channel])


@pytest.mark.parametrize(
    "channel,expected",
    [
        ("M", -0.0003691468798395277 + 0.0002904839158367293j),
        ("SigmaPP", -0.00021015661445299982 + 0.00016998230631544767j),
        ("SigmaP", -0.00018862524765406817 + 0.00015144761721976507j),
        ("PhiPP", -0.002767959264164828 + 0.002359965268579839j),
        ("PhiPT", -0.001370139632082414 + 0.0011681826342899194j),
        ("Delta", -0.0006160910228108905 + 0.0005070126122148639j),
        ("MPhiPP", 0.00012894383341570297 - 0.00006273752298112089j),
        ("SigmaPDelta", 0.0j),
    ],
)
def test_flavor_entry_reproduces_frozen_scalar_response_formula(channel, expected):
    ci_basis = {
        index: (
            _embedded(complex(0.1 * index, 0.03 * (index + 1))),
            _embedded(complex(-0.04 * (index + 2), 0.02 * index)),
        )
        for index in ACTIVE_NR
    }
    response = responses_R(ci_basis, KIN, tau=0, taup=1)[channel]

    assert response[1, 1] == pytest.approx(expected)
    mask = np.ones((3, 3), dtype=bool)
    mask[1, 1] = False
    np.testing.assert_array_equal(response[mask], 0.0)


def test_physical_nuclear_contraction_is_hermitian():
    response_db = ResponseDB("data/responses/responses_all.json").get("Ge73")
    energy = 0.005
    recoil = 0.5e-6
    mass_a = 73.0 * float(constants.AMU_GEV)
    qabs2 = 2.0 * mass_a * recoil
    qabs = math.sqrt(qabs2)
    q2 = recoil * recoil - qabs2

    lnc = zero_flavor_matrix()
    lnc[0, 1] = 1.0e-6 + 2.0e-7j
    lnc[0, 2] = -4.0e-7 + 1.0e-7j
    lnv = zero_flavor_matrix()
    lnv[0, 1] = 2.0e-7 - 3.0e-7j
    lnv[0, 2] = 5.0e-7j

    ci = left_to_ci(
        {
            (6, 1, "u"): lnc,
            (7, 3, "u"): lnv,
            (7, 4, "u"): 2.0 * lnv,
        },
        E_nu=energy,
        q0=recoil,
        q2=q2,
        qabs=qabs,
        qabs2=qabs2,
        mA=mass_a,
    )
    response_tensors = compute_R_matrices(
        ci.iso,
        E_nu=energy,
        qabs=qabs,
        qabs2=qabs2,
        mA=mass_a,
        mN=0.938,
        basis="iso",
    )
    y = (0.5 * qabs * float(response_db.get_basic("b"))) ** 2
    channel_map = {
        "MM": "M",
        "SSPP": "SigmaPP",
        "SSP": "SigmaP",
        "PhiPP": "PhiPP",
        "PhiPT": "PhiPT",
        "DD": "Delta",
        "MPhiPP": "MPhiPP",
    }

    total = zero_flavor_matrix()
    for response_key, nuclear_key in channel_map.items():
        nuclear = np.asarray(response_db.W_iso(nuclear_key, y), dtype=float)
        total += np.einsum(
            "abij,ij->ab", response_tensors[response_key], nuclear, optimize=True
        )

    np.testing.assert_allclose(total, total.conj().T, atol=1.0e-20, rtol=1.0e-12)
