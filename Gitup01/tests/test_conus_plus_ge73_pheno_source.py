from __future__ import annotations

import math

import numpy as np

from cevns_pyeft.experiments.conus.source import (
    PHI0_CM2_S,
    kopeikin_spectrum_shape,
    load_conus_plus_ge73_reactor_flux,
    load_reactor_flux_tables,
    mueller_spectrum_shape,
    release_reactor_spectrum_shape,
)
from cevns_pyeft.experiments.registry import get_experiment_spec


def test_mueller_and_kopeikin_tables_match_document():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    tables = load_reactor_flux_tables(spec)

    assert set(tables.mueller) == {"U235", "U238", "Pu239", "Pu241"}
    assert tables.mueller["U235"]["fission_fraction"] == 0.56
    assert tables.mueller["U238"]["a0"] == 4.833e-1
    assert tables.mueller["Pu239"]["a1"] == -7.432
    assert tables.mueller["Pu241"]["a5"] == -1.896e-3

    assert tables.kopeikin_energy_mev.shape == (32,)
    assert tables.kopeikin_rho.shape == (32,)
    assert np.all(np.diff(tables.kopeikin_energy_mev) > 0.0)
    assert tables.kopeikin_energy_mev[0] == 0.010
    assert tables.kopeikin_rho[0] == 0.0774
    assert tables.kopeikin_energy_mev[-1] == 2.000
    assert tables.kopeikin_rho[-1] == 1.3


def test_release_flux_support_nonnegative_and_continuous():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    tables = load_reactor_flux_tables(spec)
    shape = release_reactor_spectrum_shape

    assert shape(-1.0, tables) == 0.0
    assert shape(0.0, tables) == 0.0
    assert shape(0.009999, tables) == 0.0
    assert shape(10.0001, tables) == 0.0

    grid = np.r_[np.linspace(0.01, 2.0, 200), np.linspace(2.0, 10.0, 500)]
    assert np.all(np.asarray(shape(grid, tables)) >= 0.0)

    left = float(shape(np.nextafter(2.0, 0.0), tables))
    right = float(mueller_spectrum_shape(2.0, tables))
    assert math.isclose(left, right, rel_tol=1.0e-10, abs_tol=1.0e-10)


def test_flux_normalization_scalar_array_and_components():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    payload = load_conus_plus_ge73_reactor_flux(spec)
    flux = payload["measured"]["nuebar"]
    norm = payload["basic"]["normalization_integral"]
    assert norm > 0.0

    grid = np.unique(np.r_[payload["tables"]["kopeikin_energy_mev"], np.linspace(2.0, 10.0, 20001)])
    integral = float(np.trapezoid(np.asarray(flux(grid), dtype=float), grid))
    assert math.isclose(integral, PHI0_CM2_S, rel_tol=5.0e-6)

    points = np.array([-0.1, 0.0, 0.009, 0.01, 1.0, 2.0, 9.5, 10.1])
    arr = np.asarray(flux(points), dtype=float)
    scalar = np.asarray([flux(float(x)) for x in points], dtype=float)
    assert np.allclose(arr, scalar, rtol=0.0, atol=0.0)


def test_matching_diagnostics_match_phase0_inventory():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    tables = load_reactor_flux_tables(spec)
    rho_mueller_2 = float(mueller_spectrum_shape(2.0, tables))
    rho_kop_2 = float(kopeikin_spectrum_shape(2.0, tables))
    assert math.isclose(rho_mueller_2, 1.2580795, rel_tol=5.0e-7)
    assert math.isclose(rho_mueller_2 / rho_kop_2, 0.9677535, rel_tol=5.0e-7)
