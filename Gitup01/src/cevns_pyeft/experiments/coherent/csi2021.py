"""Compatible factory backed by the authoritative dataset definition."""
from dataclasses import replace
from .csi2021_definition import DEFINITION

def make_csi2021_model(responses_json, *, detector_mass_kg=DEFINITION.physical.mass_kg,
        baseline_m=DEFINITION.physical.run.baseline_m,
        yield_per_pot=DEFINITION.physical.run.yield_per_pot,
        total_pot=DEFINITION.physical.run.total_pot,
        c10_mass_mode=DEFINITION.physical.c10_mass_mode):
    from .execution import assemble_csi2021
    physical=DEFINITION.physical
    physical=replace(physical,run=replace(physical.run,baseline_m=baseline_m,
        yield_per_pot=yield_per_pot,total_pot=total_pot),mass_kg=detector_mass_kg,c10_mass_mode=c10_mass_mode)
    return assemble_csi2021(replace(DEFINITION,physical=physical),responses_json)
