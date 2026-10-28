"""Experiment-independent validation, recoil integration and assembly."""
from dataclasses import dataclass, asdict
import numpy as np
from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
from cevns_pyeft.contracts.parameters import IntegrationSettings, TheoryPoint
from cevns_pyeft.contracts.prediction import Prediction
from cevns_pyeft.contracts.validation import plain
from cevns_pyeft.rates.recoil import integrate_recoil_yield
from cevns_pyeft.rates.folding import legacy_density_fold, probability_fold


@dataclass(frozen=True)
class ValidationReport:
    fluence: object
    backend: str
    fallback_reason: str | None


def validate_compatibility(model, *, parameters, numerics, backend="slow"):
    if not isinstance(parameters, TheoryPoint) or not isinstance(numerics, IntegrationSettings):
        raise TypeError("predict requires TheoryPoint and IntegrationSettings")
    if backend not in ("slow", "fast", "auto"):
        raise ValueError("backend must be slow, fast or auto")
    if backend == "fast":
        from cevns_pyeft.kernels.compiler import fast_capability
        capability = fast_capability(model, numerics=numerics)
        if not capability.supported:
            raise UnsupportedCapabilityError("Fast: " + "; ".join(capability.reasons))
        if parameters.state.values:
            raise UnsupportedCapabilityError("Fast does not consume scanned state parameters")
    if len(model.binning.axes) != 1:
        raise UnsupportedCapabilityError("this pipeline currently supports one observed axis")
    for role in ("source", "interaction", "observation"):
        descriptor = getattr(model, role).describe()
        if descriptor.contract_id != role or descriptor.contract_version != "1":
            raise ValueError(f"{role} contract mismatch")
    if model.interaction.kinematics.process_id != "elastic_neutrino_nucleus_v1":
        raise UnsupportedCapabilityError("unsupported interaction process")
    fluence = model.source.for_run(model.run)
    if fluence.run_id != model.run.run_id:
        raise ValueError("source fluence and exposure run IDs differ")
    axis = model.binning.axes[0]
    if (axis.name, axis.unit) != (model.observation.axis_name, model.observation.axis_unit):
        raise ValueError("observation axis name or unit mismatch")
    if numerics.strategy == "legacy_csi2021_v1":
        if "sampled_density_1d" not in model.observation.describe().capabilities:
            raise UnsupportedCapabilityError("selected numerical strategy requires sampled_density_1d")
        if numerics.observed_step > np.min(np.diff(axis.edges)):
            raise ValueError("observed_step must not exceed the smallest bin width")
    elif "bin_probabilities_1d" not in model.observation.describe().capabilities:
        raise UnsupportedCapabilityError("selected numerical strategy requires bin_probabilities_1d")
    if hasattr(model.interaction, "validate"):
        model.interaction.validate(model.targets, parameters)
    if hasattr(model.observation, "validate"):
        model.observation.validate(model.binning, tuple(c.component_id for c in fluence.components))
    return ValidationReport(fluence, "fast" if backend == "fast" else "slow", "no_compiled_kernel_supplied" if backend == "auto" else None)


def predict(model, *, parameters=None, numerics=None, backend="slow", compiled=None):
    parameters = TheoryPoint() if parameters is None else parameters
    numerics = IntegrationSettings() if numerics is None else numerics
    if backend == "slow" and compiled is not None:
        raise ValueError("compiled is not consumed by the Slow backend")
    if backend == "fast" or (backend == "auto" and compiled is not None):
        from cevns_pyeft.kernels.compiler import CompiledKernel, compile_fast
        validate_compatibility(model, parameters=parameters, numerics=numerics, backend="fast")
        if compiled is None:
            compiled = compile_fast(model, numerics=numerics)
        if not isinstance(compiled, CompiledKernel):
            raise TypeError("compiled must be an interface CompiledKernel")
        return compiled.predict(model=model, parameters=parameters, numerics=numerics)
    validation = validate_compatibility(model, parameters=parameters, numerics=numerics, backend=backend)
    fluence = validation.fluence
    parts, yields, preselection, folds = {}, {}, {}, {}
    for target in model.targets.isotopes:
        maxima = [max(component.support.integration_domain_MeV[1], *(line.energy_MeV for line in component.lines))
                  if component.lines else component.support.integration_domain_MeV[1] for component in fluence.components]
        maximum = max((model.interaction.kinematics.maximum_recoil_keV(target, e) for e in maxima), default=numerics.recoil_min_keV * 2)
        recoil = np.linspace(numerics.recoil_min_keV, max(maximum, numerics.recoil_min_keV * (1 + 1e-12)), numerics.n_er)
        for component in fluence.components:
            key = (component.component_id, target.isotope_id)
            value = integrate_recoil_yield(component, target, model.interaction, parameters=parameters,
                                           numerics=numerics, recoil_keV=recoil)
            yields[key] = value
            if numerics.strategy == "legacy_csi2021_v1":
                before, diagnostic = legacy_density_fold(value, target, model.observation, model.binning, numerics)
                preselection[key] = before
                folds[key] = diagnostic
                final = before * model.observation.selection.acceptance(component.component_id)
            else:
                final = probability_fold(value, target, model.observation, model.binning)
            parts[key] = final * target.number_of_nuclei
    total = sum(parts.values(), np.zeros(model.binning.shape))
    record = model.describe()
    record["theory_point"] = {"wc_triplets": plain(parameters.wc_triplets), "include_sm": parameters.include_sm,
                              "sin2thetaW": parameters.sin2thetaW, "state_parameters": plain(parameters.state.values)}
    numerical = {**asdict(numerics), "backend": validation.backend, "requested_backend": backend,
                 "fallback_reason": validation.fallback_reason, "quadrature": "trapezoid",
                 "continuum_energy_grids_MeV": {part.component_id: np.unique(np.concatenate((
                     np.linspace(*part.support.integration_domain_MeV, numerics.n_enu),
                     part.support.breakpoints_MeV))) for part in fluence.components},
                 "recoil_grids_keV": {str(key): value.recoil_keV for key, value in yields.items()}}
    return Prediction(total, model.binning, parts,
                       {"source": fluence.normalization_record,
                        "fluence_units": {"continuum": fluence.continuum_unit, "line": fluence.line_unit},
                        "source_components": {part.component_id: {"particle_kind": part.particle_kind,
                            "support": asdict(part.support), "lines": [asdict(line) for line in part.lines]}
                            for part in fluence.components},
                        "number_of_nuclei": {t.isotope_id: t.number_of_nuclei for t in model.targets.isotopes},
                        "selection": model.observation.describe().as_dict()},
                       record, numerical,
                       {"recoil_yields": yields, "preselection_per_nucleus": preselection, "folding": folds})
