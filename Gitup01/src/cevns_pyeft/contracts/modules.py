from dataclasses import dataclass, field
from typing import Mapping
import hashlib
import json
from .validation import freeze, plain


class IncompatibleNormalizationError(ValueError):
    pass


class UnsupportedCapabilityError(ValueError):
    pass


@dataclass(frozen=True)
class ModuleDescriptor:
    contract_id: str
    model_id: str
    model_revision: str = "1"
    contract_version: str = "1"
    capabilities: tuple[str, ...] = ()
    parameters: Mapping = field(default_factory=dict)
    resources: Mapping = field(default_factory=dict)
    dependencies: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.contract_id or not self.model_id:
            raise ValueError("module contract and model IDs are required")
        object.__setattr__(self, "parameters", freeze(self.parameters))
        object.__setattr__(self, "resources", freeze(self.resources))
        object.__setattr__(self, "capabilities", tuple(self.capabilities))
        object.__setattr__(self, "dependencies", tuple(self.dependencies))

    def as_dict(self):
        return {key: plain(getattr(self, key)) for key in self.__dataclass_fields__}


def fingerprint(record):
    return hashlib.sha256(json.dumps(plain(record), sort_keys=True, allow_nan=False).encode()).hexdigest()
