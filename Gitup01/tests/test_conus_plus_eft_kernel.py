import numpy as np

from cevns_pyeft.experiments.conus_plus.eft_kernel import (
    EFTCoordinate,
    build_quadratic_kernel,
    reactor_visible_coordinates,
    validate_quadratic_kernel,
)


def test_reactor_visible_basis_has_explicit_real_imag_coordinates():
    coordinates = reactor_visible_coordinates()
    assert len(coordinates) == 114
    assert coordinates[0].initial_flavor == "e"
    assert {coordinate.component for coordinate in coordinates} == {"real", "imag"}


def test_quadratic_kernel_reconstructs_held_out_spectrum():
    coordinates = (
        EFTCoordinate("x", (6, 1, "u"), "e", "e", "real", 1.0),
        EFTCoordinate("y", (6, 1, "u"), "e", "e", "real", 1.0),
    )

    def direct(wc):
        x = float(np.real(wc.get((6, 1, "u"), np.zeros((3, 3)))[0, 0]))
        return np.array([1.0 + x + 2.0 * x * x, 2.0 - 0.5 * x + x * x])

    kernel = build_quadratic_kernel(direct, coordinates, steps=0.1)

    def direct_point(point):
        x = float(np.sum(point))
        return np.array([1.0 + x + 2.0 * x * x, 2.0 - 0.5 * x + x * x])

    result = validate_quadratic_kernel(
        kernel,
        direct_point,
        ([0.07, -0.03], [0.2, 0.1]),
        atol=1.0e-12,
        rtol=1.0e-12,
    )
    assert result["points"] == 2
    assert result["max_abs"] < 1.0e-12
