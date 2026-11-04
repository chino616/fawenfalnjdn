"""Load observation implementations when requested by an actual calculation."""
from importlib import import_module

_EXPORTS = {
    "CsI2021Observation": "csi2021",
    "CsI2021Efficiency": "csi2021",
    "CsI2021EfficiencyParams": "csi2021",
    "CsIGammaResponse": "csi2021",
    "ConstantEfficiency": "csi2021",
    "LegacyComponentAcceptance": "selection",
}
__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    value = getattr(import_module("."+_EXPORTS[name], __name__), name)
    globals()[name] = value
    return value
