"""Lazy public exports, preserving historical star-import names."""
from importlib import import_module
_EXPORTS = {'SNSDataset': 'sns', 'SNS_DATASETS': 'sns', 'SourceSpecies': 'sns', 'sns_component_state': 'sns', 'loadNeutrinoEmpiricalFluxSNS': 'sns', 'build_neutrino_empirical_flux_sns': 'sns', 'load_neutrino_empirical_flux_sns': 'sns', 'loadNeutrinoFlux': 'sns', 'CSI2017_PE_PER_KEV': 'slow_counts_csi2017', 'CSI2017_BINS_25': 'slow_counts_csi2017', 'CSI2017_WIDTHS_25': 'slow_counts_csi2017', 'CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH': 'slow_counts_csi2017', 'slow_counts_csi2017': 'slow_counts_csi2017', 'ArrayLike': 'slow_counts_csi2021', 'CsI2021EfficiencyParams': 'slow_counts_csi2021', 'efficiency_csi2021': 'slow_counts_csi2021', 'EfficiencyModel': 'slow_counts_csi2021', 'efficiency': 'slow_counts_csi2021', 'PE_BINS_9': 'slow_counts_csi2021', 'PE_WIDTHS_9': 'slow_counts_csi2021', 'DEFAULT_ACCEPTANCE': 'slow_counts_csi2021', 'A_TARGET': 'slow_counts_csi2021', 'combine_equal_stoichiometry': 'slow_counts_csi2021', 'slow_counts_csi2021': 'slow_counts_csi2021', 'AR_BINS_12': 'slow_counts_ar2020', 'AR_WIDTHS_12': 'slow_counts_ar2020', 'AR_DEFAULT_EFFICIENCY_RELATIVE_PATH': 'slow_counts_ar2020', 'AR_D': 'slow_counts_ar2020', 'AR_B': 'slow_counts_ar2020', 'AR_DMIN': 'slow_counts_ar2020', 'AR_DMAX': 'slow_counts_ar2020', 'slow_counts_ar2020': 'slow_counts_ar2020', 'build_fast_kernel_csi2017': 'fast_kernel_csi2017', 'build_fast_kernel_csi2021': 'fast_kernel_csi2021', 'build_fast_kernel_ar2020': 'fast_kernel_ar2020'}
__all__ = list(_EXPORTS)
def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    value = getattr(import_module('.'+_EXPORTS[name],__name__),name)
    globals()[name] = value
    return value
