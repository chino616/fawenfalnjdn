from dataclasses import dataclass
from typing import Mapping
import numpy as np
from cevns_pyeft.contracts.validation import freeze


@dataclass(frozen=True)
class LegacyComponentAcceptance:
    values: Mapping[str, float]
    selection_id: str = "legacy_component_acceptance"

    def __post_init__(self):
        if not self.selection_id or any(not np.isfinite(value) or not 0 <= value <= 1 for value in self.values.values()):
            raise ValueError("selection requires an ID and probabilities in [0,1]")
        object.__setattr__(self, "values", freeze(self.values))

    def acceptance(self, component_id):
        if component_id not in self.values:
            raise ValueError(f"selection has no acceptance for component {component_id!r}")
        return float(self.values[component_id])
