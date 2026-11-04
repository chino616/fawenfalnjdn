"""Historical factory backed by the canonical YAML/NPZ package."""
from dataclasses import replace
from pathlib import Path
from .csi2021_definition import DEFINITION


def make_csi2021_model(responses_json=None, *, detector_mass_kg=None, baseline_m=None,
        yield_per_pot=None, total_pot=None, c10_mass_mode=None):
    # The old standard response path is an inert compatibility argument. No I/O.
    # A distinct external response override must use explicit component injection.
    if responses_json is not None and Path(responses_json).name != "responses_all.json":
        raise ValueError("external response overrides use explicit interaction components; package resources are authoritative")
    from cevns_pyeft.experiments.loader import load_experiment
    physical = DEFINITION.physical
    run = physical.run
    run = replace(run, baseline_m=run.baseline_m if baseline_m is None else baseline_m,
        yield_per_pot=run.yield_per_pot if yield_per_pot is None else yield_per_pot,
        total_pot=run.total_pot if total_pot is None else total_pot)
    physical = replace(physical, run=run,
        mass_kg=physical.mass_kg if detector_mass_kg is None else detector_mass_kg,
        c10_mass_mode=physical.c10_mass_mode if c10_mass_mode is None else c10_mass_mode)
    return load_experiment(DEFINITION.dataset_id, definition=replace(DEFINITION, physical=physical)).model
