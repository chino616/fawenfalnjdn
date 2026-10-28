"""The existing SNS tabulation exposed as detector fluence, without target mass."""
from dataclasses import dataclass
from types import MappingProxyType
import numpy as np
from cevns_pyeft.contracts.modules import IncompatibleNormalizationError, ModuleDescriptor
from cevns_pyeft.contracts.source import DetectorFluence, EnergySupport, FluenceLine, IncidentStateBatch, POTExposure
from cevns_pyeft.contracts.validation import positive
from cevns_pyeft.experiments.coherent.sns import SNSDataset, build_neutrino_empirical_flux_sns, sns_component_state
from cevns_pyeft.rates.differential import emax_muon_dar_mev
from .composable import CallableFluenceComponent

LEGACY_COMPONENT_IDS = MappingProxyType({"mu": "prompt_numu", "e": "delayed_nue", "mub": "delayed_numubar"})


@dataclass(frozen=True)
class ConstantSNSState:
    flavor: str

    def fixed_state_for_fast(self):
        return sns_component_state(self.flavor)

    def __call__(self, energy_MeV, *, parameters):
        if parameters.values:
            raise ValueError("constant legacy SNS state does not consume state parameters")
        state = sns_component_state(self.flavor)
        return IncidentStateBatch(energy_MeV, state.rho, state.particle_kind, "sns_pure_flavor_legacy_v1")


@dataclass(frozen=True)
class SNSLegacySource:
    from cevns_pyeft.experiments.coherent.csi2021_definition import DEFINITION as _D
    baseline_m: float = _D.physical.run.baseline_m
    yield_per_pot: float = _D.physical.run.yield_per_pot
    energy_tabulation: tuple = _D.physical.run.energy_tabulation
    node_support: tuple = _D.physical.run.node_support
    num_points: int = _D.physical.run.num_points
    interpolation: bool = _D.physical.run.interpolation

    def __post_init__(self):
        positive(self.baseline_m, "baseline_m")
        positive(self.yield_per_pot, "yield_per_pot", zero=True)

    def for_run(self, run):
        if not isinstance(run, POTExposure):
            raise IncompatibleNormalizationError("SNSLegacySource requires POTExposure")
        config = SNSDataset(run.run_id, 0.0, self.baseline_m, run.total_pot, self.yield_per_pot,
                            *self.energy_tabulation, *self.node_support)
        flux = build_neutrino_empirical_flux_sns(config, num_points=self.num_points, use_interpolation=self.interpolation)
        support = EnergySupport((0.0, emax_muon_dar_mev()), self.energy_tabulation,
                                interpolation_id=f"linear_{self.num_points}_nodes_{self.energy_tabulation}",
                                convention_id="legacy_sns_56MeV_node_mask_muon_DAR_quadrature")
        components = []
        for flavor in ("mu", "e", "mub"):
            line_energy, weight = flux["measured"]["muLine"]
            lines = (FluenceLine("pion_DAR", line_energy, weight),) if flavor == "mu" else ()
            continuum = (lambda energy: np.zeros_like(energy)) if flavor == "mu" else flux["measured"][flavor]
            components.append(CallableFluenceComponent(LEGACY_COMPONENT_IDS[flavor],
                              "antinu" if flavor == "mub" else "nu", support,
                              continuum, ConstantSNSState(flavor), lines))
        return DetectorFluence(tuple(components), run.run_id,
                               {"geometry_included": True, "baseline_m": self.baseline_m,
                                "total_pot": run.total_pot, "yield_per_pot": self.yield_per_pot,
                                "fluence_per_species_cm^-2": flux["basic"]["NTimeIntegratedFlux_cm^-2"],
                                "input_unit": "per_POT", "output_unit": "cm^-2 MeV^-1",
                                "node_mask_MeV": self.node_support, "physical_endpoint_audited": False})

    def describe(self):
        return ModuleDescriptor("source", "sns_legacy", capabilities=("slow_1d", "fixed_state"),
                                parameters={"baseline_m": self.baseline_m, "yield_per_pot": self.yield_per_pot,
                                            "tabulation_nodes": self.num_points, "tabulation_MeV": self.energy_tabulation, "node_mask_MeV": self.node_support, "interpolation": self.interpolation})
