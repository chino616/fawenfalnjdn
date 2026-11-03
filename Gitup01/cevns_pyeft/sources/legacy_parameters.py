"""Default SNS source component parameters, without a dataset import."""
from dataclasses import dataclass

@dataclass(frozen=True)
class SNSComponentDefaults:
    baseline_m: float = 19.3
    yield_per_pot: float = .0848
    energy_tabulation: tuple = (.001, 300.)
    node_support: tuple = (.001, 56.)
    num_points: int = 200
    interpolation: bool = True

SNS_COMPONENT_DEFAULTS = SNSComponentDefaults()
