"""Unchanged deterministic cases; protected numeric references live separately."""
import numpy as np

def points():
    e = np.diag([1.0, 0.0, 0.0]).astype(complex)
    multi = np.array([[1, 0.2j, 0.1], [0.15, -0.4, 0.2j], [0.05j, 0.3, 0.2]], complex)
    return {
        "sm": ({}, True),
        "np": ({(6, 1, "u"): 1e-6 * e}, False),
        "sm_np": ({(6, 1, "u"): 1e-6 * e}, True),
        "complex": ({(6, 1, "u"): (1e-6 + 2e-7j) * e,
                     (7, 1, "d"): (-3e-7 + 1e-7j) * e}, True),
        "multiflavor": ({(6, 1, "u"): 1e-6 * multi,
                         (8, 1, "d"): -1e-8 * multi}, True),
    }


GRIDS = {
    "small": dict(n_er=5, n_enu=12, n_pe_bin=4, pe_step=4.0),
    "medium": dict(n_er=11, n_enu=40, n_pe_bin=8, pe_step=3.0),
    "default": dict(n_er=21, n_enu=120, n_pe_bin=8, pe_step=3.0),
}

