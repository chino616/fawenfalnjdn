"""Explicit assembly of the protected CsI2021 one-dimensional model."""
from cevns_pyeft.contracts.observation import Axis, Binning
from cevns_pyeft.contracts.source import POTExposure
from cevns_pyeft.core.model import ExperimentModel
from cevns_pyeft.detectors.csi2021 import CsI2021Observation, PE_BINS_9, DEFAULT_ACCEPTANCE
from cevns_pyeft.detectors.selection import LegacyComponentAcceptance
from cevns_pyeft.sources.sns import SNSLegacySource, LEGACY_COMPONENT_IDS
from cevns_pyeft.targets.materials import csi_target_inventory
from cevns_pyeft.theory.li2026.adapter import Li2026LegacyInteraction


def make_csi2021_model(responses_json, *, detector_mass_kg=14.57, baseline_m=19.3,
                       yield_per_pot=0.0848, total_pot=3.198e23, c10_mass_mode="quark_mass_resolved"):
    observation = CsI2021Observation(LegacyComponentAcceptance(
        {LEGACY_COMPONENT_IDS[key]: value for key, value in DEFAULT_ACCEPTANCE.items()}))
    return ExperimentModel(
        source=SNSLegacySource(baseline_m=baseline_m, yield_per_pot=yield_per_pot),
        run=POTExposure(total_pot=total_pot, run_id="CsI2021"),
        targets=csi_target_inventory(detector_mass_kg),
        interaction=Li2026LegacyInteraction(responses_json, c10_mass_mode=c10_mass_mode),
        observation=observation,
        binning=Binning((Axis(observation.axis_name, observation.axis_unit, PE_BINS_9),)),
        model_id="csi2021_legacy_9bin_v1",
    )
