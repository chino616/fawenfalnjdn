"""Unchanged real-symmetric epsilon-to-Wilson conversion, extracted from the adopted mapping.
Only these pure functions are used; old kernels and old fit outputs are not imported.
"""
import numpy as np
from cevns_pyeft.foundation.constants import G_F

def _matrix(value):
    if value is None:
        return np.zeros((3, 3))
    a = np.asarray(value)
    if a.shape != (3, 3) or np.iscomplexobj(a) or (not np.isfinite(a).all()):
        raise ValueError('Vector NSI must be finite real 3x3 matrices')
    a = np.asarray(a, float)
    if not np.allclose(a, a.T, rtol=0, atol=1e-14):
        raise ValueError('Real NSI matrices must be symmetric (Hermitian)')
    return a

def vector_nsi_wilson(epsilon_u=None, epsilon_d=None):
    """C61q[final,initial]=-sqrt(2) G_F epsilon_q.T, GeV^-2."""
    return {(6, 1, q): -np.sqrt(2) * G_F * _matrix(a).T for q, a in (('u', epsilon_u), ('d', epsilon_d))}
