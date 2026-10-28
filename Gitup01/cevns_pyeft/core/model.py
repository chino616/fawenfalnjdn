from dataclasses import dataclass, asdict
from cevns_pyeft.contracts.source import SourceModel, RunExposure
from cevns_pyeft.contracts.target import TargetInventory
from cevns_pyeft.contracts.interaction import InteractionModel
from cevns_pyeft.contracts.observation import Binning, ObservationModel
from cevns_pyeft.contracts.modules import fingerprint
from cevns_pyeft.contracts.validation import plain


@dataclass(frozen=True)
class ExperimentModel:
    source: SourceModel
    run: RunExposure
    targets: TargetInventory
    interaction: InteractionModel
    observation: ObservationModel
    binning: Binning
    model_id: str = "composed_model"

    def describe(self):
        from cevns_pyeft.kernels.compiler import fast_capability
        fast = fast_capability(self)
        record = {
            "model_id": self.model_id,
            "source": self.source.describe().as_dict(),
            "run": asdict(self.run),
            "targets": {"detector_mass_kg": self.targets.detector_mass_kg,
                        "isotopes": [asdict(part) for part in self.targets.isotopes],
                        "composition": plain(self.targets.composition_record)},
            "interaction": self.interaction.describe().as_dict(),
            "observation": self.observation.describe().as_dict(),
            "binning": [{"name": axis.name, "unit": axis.unit, "edges": axis.edges.tolist(), "clock": axis.clock}
                        for axis in self.binning.axes],
            "dependency_graph": {"fluence": ["source", "run"], "recoil_yield": ["fluence", "interaction", "theory_point", "state_parameters", "numerics"],
                                 "counts": ["recoil_yield", "targets", "observation", "binning", "numerics"],
                                 "statistics": ["counts", "statistical_dataset"]},
            "capabilities": {"slow_1d": len(self.binning.axes) == 1, "fast": fast.supported,
                             "fast_conditions": fast.state_requirement, "fast_rejection_reasons": fast.reasons},
        }
        record["model_fingerprint"] = fingerprint(record)
        return record
