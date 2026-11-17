"""Bind a light-vector interaction through the existing component override API.

The formal solar packages remain immutable SM input authorities. A prepared
NSI/NGI benchmark records its explicit vector component, its source-code hash,
and a distinct physics fingerprint in standard Runtime assembly metadata.
"""
from cevns_pyeft.experiments.catalog import ExperimentCatalog
from cevns_pyeft.experiments.loader import load_experiment
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.solar_b8 import SolarModel
from cevns_pyeft.theory.light_vector import LightVectorKN


def with_solar_light_vector(experiment, *, mass_MeV, coupling, scenario='universal'):
    if not isinstance(experiment.model, SolarModel):
        raise TypeError('this adapter requires a package-backed solar-B8 model')
    interaction = LightVectorKN(experiment.model.interaction, mass_MeV, coupling, scenario)
    catalog = ExperimentCatalog(builtins=False).register(experiment.dataset_id, experiment.definition)
    return load_experiment(experiment.dataset_id, definition=experiment.definition,
        resources=experiment.resource_catalog, registry=catalog, components={'interaction': interaction})


def load_solar_light_vector(package, *, mass_MeV, coupling, scenario='universal'):
    return with_solar_light_vector(load_experiment_package(package),
        mass_MeV=mass_MeV, coupling=coupling, scenario=scenario)
