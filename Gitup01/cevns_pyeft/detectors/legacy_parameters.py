"""Deprecated default-value view of the canonical CsI2021 input package.

Reusable detector algorithms accept explicit parameters and never import this
module on the package-only path. This module owns no experimental numbers.
"""
from dataclasses import dataclass, field


def _package():
    from cevns_pyeft.foundation.paths import resource_root
    from cevns_pyeft.experiments.input_package import strict_json
    return strict_json((resource_root()/"data/experiments/COHERENT_CsI/CsI2021/experiment.input.yaml").read_text(encoding="utf-8"))


def _value(key):
    return _package()["parameters"][key]["value"]


@dataclass(frozen=True)
class CsIResponseDefaults:
    quenching: tuple = field(default_factory=lambda: tuple(_value(f"detector.quenching_q{i}") for i in range(1,5)))
    gamma_a: float = field(default_factory=lambda: _value("detector.gamma_a"))
    gamma_b: float = field(default_factory=lambda: _value("detector.gamma_b"))
    efficiency: tuple = field(default_factory=lambda: tuple(_value("detector.efficiency_"+key) for key in "abcd"))


def __getattr__(name):
    if name == "CSI_RESPONSE_DEFAULTS":
        return CsIResponseDefaults()
    if name == "CSI_COMPONENT_ACCEPTANCE":
        return tuple((c["legacy_label"], _value("detector.acceptance_"+c["legacy_label"])) for c in _package()["source"]["components"])
    if name == "CSI_PE_EDGES":
        from cevns_pyeft.foundation.paths import resource_root
        from cevns_pyeft.experiments.package_loader import read_package
        data, arrays = read_package(resource_root()/"data/experiments/COHERENT_CsI/CsI2021")
        return tuple(arrays[data["observable"]["edges_ref"]])
    raise AttributeError(name)


__all__ = ["CsIResponseDefaults", "CSI_RESPONSE_DEFAULTS", "CSI_PE_EDGES", "CSI_COMPONENT_ACCEPTANCE"]
