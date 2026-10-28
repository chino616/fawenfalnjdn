"""Lazy public exports, preserving historical star-import names."""
from importlib import import_module
_EXPORTS = {'ArrayLike': 'source', 'ReactorComponent': 'source', 'FluxComponent': 'source', 'DATASET_ID': 'source', 'COMPONENTS': 'source', 'TOTAL_FLUX_CM2_S': 'source', 'NORMALIZATION_UNCERTAINTY_FRACTION': 'source', 'ENERGY_SUPPORT_MEV': 'source', 'MATCH_ENERGY_MEV': 'source', 'LOWEST_KOPEIKIN_NODE_MEV': 'source', 'LOW_END_POLICY': 'source', 'TIME_BASIS': 'source', 'FLUX_UNIT': 'source', 'DEFAULT_DATA_DIR': 'source', 'kopeikin_nodes': 'source', 'mueller_coefficients': 'source', 'fission_fractions': 'source', 'normalization_integral': 'source', 'differential_flux': 'source', 'total_differential_flux': 'source', 'source_state': 'source', 'load_reactor_flux': 'source'}
__all__ = list(_EXPORTS)
def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    value = getattr(import_module('.'+_EXPORTS[name],__name__),name)
    globals()[name] = value
    return value
