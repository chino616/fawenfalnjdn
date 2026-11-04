"""Bind CsI2021 experiment-input/1 YAML/NPZ inputs to existing physics components.

No legacy dataset definition or response JSON is read by this adapter.
The allow-list identifies tested algorithms. Formula text stays audit-only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
import hashlib
import json
from pathlib import Path
from types import MappingProxyType

import numpy as np
from scipy.interpolate import interp1d

from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.contracts.parameters import IntegrationSettings
from cevns_pyeft.contracts.source import DetectorFluence, EnergySupport, FluenceLine, IncidentStateBatch, POTExposure
from cevns_pyeft.contracts.target import TargetInventory, TargetIsotope
from cevns_pyeft.experiments.definition import (
    ExperimentDefinition, ObservationDefinition, StatisticsDefinition, digest, frozen_mapping, plain,
)
from cevns_pyeft.experiments.input_package import read_arrays, strict_json, validate_document, render_physics
from cevns_pyeft.nuclear.response import ResponseW
from cevns_pyeft.sources.composable import CallableFluenceComponent
from cevns_pyeft.sources.state import NeutrinoState
from cevns_pyeft.theory.li2026.adapter import Li2026LegacyInteraction

CHANNELS = ("M", "SigmaPP", "SigmaP", "PhiPP", "PhiPT", "Delta", "MPhiPP")
SOURCE_IDS = ("prompt_numu", "delayed_nue", "delayed_numubar")
ISOTOPES = ("Cs133", "I127")


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _close(actual, expected, name):
    _require(np.isclose(actual, expected, rtol=2e-14, atol=0), "inconsistent " + name)


def _check_explanation(document, arrays, text):
    """Check the complete deterministic derived view, including all numerical tables."""
    expected = render_physics(plain(document), arrays)
    accepted = [expected]
    # Input/1 has two published prose renderings. Only these exact narrative
    # substitutions are compatible; every model, parameter and array must match.
    if document["legacy_spec"]["runtime_authority"] == "existing_python_definition":
        accepted.append(expected.replace(
            "当前运行权威：existing_python_definition。",
            "当前 Runtime 仍使用既有 Python definition；本任务没有实现 Package Loader。"
        ).replace(
            "旧 experiment.yaml 为兼容说明；运行权威见上表。新包不继承旧 fast_validated 或官方统计批准。Schema、模型绑定、消费、Runtime 和人工科学接受分别记录；技术证据声明不等于校验器重跑了相关计算。",
            "旧 experiment.yaml 为兼容说明；当前计算仍由 Python definition 驱动。新包没有继承旧 fast_validated 或官方统计批准。JSON Schema PASS 只认证合同结构与所列关系，不认证一手科学来源；Task 03 负责受控模型绑定。"
        ))
    _require(text.replace("\r\n", "\n") in accepted,
             "Physics MD differs from YAML/NPZ derived view")


def _validate(document, arrays, raw, contract):
    errors = validate_document(document)
    _require(not errors, "input contract: " + "; ".join(errors))
    package, parameters = document["package"], document["parameters"]
    _require(package["schema_version"] == contract["input_schema"], "unsupported package version")
    _require((package["dataset_id"], package["experiment_slug"]) == ("CsI2021", "COHERENT_CsI"),
             "this adapter requires the CsI2021 identity")
    _require(set(parameters) == set(contract["parameter_units"]), "missing/unknown scalar parameter")
    sources = document["provenance"]["sources"]
    for key, p in parameters.items():
        _require(p["unit"] == contract["parameter_units"][key], "wrong scalar unit: " + key)
        _require(p["value"] == p["adopted_value"], "adopted scalar differs: " + key)
        _require(isinstance(p["value"], (int, float, bool)) and np.isfinite(p["value"]),
                 "non-finite/non-scalar parameter: " + key)
        _require(p["source_refs"] and all(x in sources for x in p["source_refs"]),
                 "missing parameter provenance: " + key)
    models = document["models"]
    _require(set(models) == set(contract["model_bindings"]), "unknown/missing model_id")
    for key, binding in contract["model_bindings"].items():
        model = models[key]
        _require(model["model_id"] == key and _sha(model["mathematical_definition"].encode()) ==
                 binding["mathematics_sha256"], "unsupported model specification: " + key)
        _require(model["parameter_refs"] == binding["parameter_refs"] and
                 model["depends_on"] == binding["depends_on"], "model dependencies differ: " + key)
    interaction = document["interaction"]
    _require(interaction["basis"] == "np" and interaction["flavor_order"] == ["e", "mu", "tau"]
             and interaction["coefficient_axes"] == {"row": "final flavor", "column": "initial flavor"},
             "unsupported nuclear basis/flavor axes")
    _require(interaction["nuclear_channels"] == list(CHANNELS), "missing/unknown nuclear channel")
    _require(interaction["c10_mass_mode"] == "quark_mass_resolved", "unsupported matching convention")
    _require(document["detector"]["gamma_convention"] == "shape-rate", "unsupported Gamma convention")
    _require(document["detector"]["parameter_order"] == {
        "quenching":["q1","q2","q3","q4"], "efficiency":["a","b","c","d"], "gamma":["a0","b0"]},
        "unsupported detector parameter order")
    _require(document["prediction"]["numerical_strategy"] == "legacy_csi2021_v1"
             and document["prediction"]["model_ref"] == "legacy_csi2021_v1",
             "unsupported numerical strategy")
    from cevns_pyeft.theory.li2026.operators import LI2026_OPERATOR_SPECS
    _require(interaction["supported_operators"] == [asdict(s) | {"key": list(s.key)}
             for s in LI2026_OPERATOR_SPECS], "operator metadata differs from the bound engine")
    metadata = document["resources"]["arrays"]
    _require(set(arrays) == set(metadata) == set(contract["array_contracts"]), "NPZ key inventory differs")
    _require(_sha(raw) == document["resources"]["sha256"], "archive SHA256 mismatch")
    for key, array in arrays.items():
        m = metadata[key]
        _require({k: m[k] for k in ("unit", "axes", "shape", "dtype")} == contract["array_contracts"][key],
                 "array unit/axes/shape/dtype contract differs: " + key)
        _require(not array.dtype.hasobject and array.dtype.kind in "biufc" and np.all(np.isfinite(array))
                 and list(array.shape) == m["shape"] and str(array.dtype) == m["dtype"],
                 "unsafe/invalid array: " + key)
        _require(_sha(np.ascontiguousarray(array).tobytes()) == m["sha256_raw_c_order"],
                 "array content SHA256 mismatch: " + key)
    p = lambda key: parameters[key]["value"]
    from cevns_pyeft.foundation import constants
    from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS
    for key in parameters:
        if key.startswith("constants."):
            _close(p(key), getattr(constants, key.split(".")[1]), key + " engine pin")
        if key.startswith("lecs.") and parameters[key]["affects_fingerprint"]:
            _close(p(key), getattr(DEFAULT_LECS, key.split(".")[1]), key + " engine pin")
    _require(p("interaction.include_sm") is True, "pilot SM defaults required; explicit TheoryPoint may disable SM")
    _require(p("source.interpolation") is True, "only the declared linear tabulation is bound")
    _close(p("source.fluence_per_species"), p("source.yield_per_pot")*p("source.total_pot")/
           (4*np.pi*(100*p("source.baseline_m"))**2), "source fluence")
    _close(p("source.prompt_energy"), 1000*(p("constants.m_pi_charged")**2-p("constants.m_mu")**2)/
           (2*p("constants.m_pi_charged")), "prompt line")
    _close(p("source.integration_max"), 1000*(p("constants.m_mu")**2-p("constants.m_e")**2)/
           (2*p("constants.m_mu")), "source integration endpoint")
    grid = arrays["source_energy_MeV"]
    _require(np.array_equal(grid, np.linspace(p("source.tabulation_min"), p("source.tabulation_max"),
             int(p("source.tabulation_nodes")))), "source tabulation coordinates differ")
    for key in ("source_fluence_e", "source_fluence_mub"):
        _require(np.all(arrays[key] >= 0), "negative source fluence")
    _require(document["source"]["component_order"] == list(SOURCE_IDS), "source order differs")
    for component, initial, particle in zip(document["source"]["components"], ("mu", "e", "mu"), ("nu", "nu", "antinu")):
        _require(component["particle_kind"] == particle and component["flavor"] == initial,
                 "source particle/flavor identity differs")
        expected = np.diag([1, 0, 0] if initial == "e" else [0, 1, 0])
        _require(np.array_equal(arrays[component["rho_ref"]], expected), "pilot fixed flavor state differs")
    _require(document["target"]["isotope_order"] == list(ISOTOPES)
             and document["target"]["response_keys"] == {"Cs133": "Cs133", "I127": "I"}, "target mapping differs")
    for isotope in ISOTOPES:
        prefix = "target." + isotope + "."
        A = p(prefix+"A")
        _close(p(prefix+"mass_GeV"), A*p("constants.AMU_GEV"), prefix+"mass_GeV")
        _close(p(prefix+"mass_kg"), A*p("target.atomic_mass_kg"), prefix+"mass_kg")
        _close(p(prefix+"mass_fraction"), A/sum(p("target."+i+".A") for i in ISOTOPES), prefix+"mass_fraction")
        _close(p(prefix+"nuclei"), p("target.detector_mass")*p(prefix+"mass_fraction")/p(prefix+"mass_kg"), prefix+"nuclei")
        _require(p(prefix+"Z")+p(prefix+"N") == A and p(prefix+"isotopic_fraction") == 1, "target composition differs")
    obs = document["observable"]
    edges = arrays[obs["edges_ref"]]
    _require((obs["name"], obs["unit"], obs["bin_count"], obs["prediction_unit"], obs["statistics_unit"]) ==
             ("reconstructed PE spectrum", "PE", 9, "events/bin", "counts/PE"), "observation units/shape differ")
    _require(edges.shape == (10,) and np.all(np.diff(edges) > 0), "invalid PE edges")
    _require(np.all(arrays["statistics_uncertainty"] > 0), "non-positive statistical uncertainty")
    _require(p("statistics.sigma_alpha") > 0 and p("statistics.sigma_beta") > 0
             and p("statistics.sigma_floor") == 1e-12, "unsupported statistical scale/floor")
    _require(document["statistics"]["model_ref"] == "gaussian_two_pull_legacy_v1"
             and document["statistics"]["covariance_ref"] is None, "unsupported statistics")
    for x in ("e", "mu", "mub"):
        _require(0 <= p("detector.acceptance_"+x) <= 1, "invalid component acceptance")
    _require(p("detector.gamma_a") > 0 and p("detector.gamma_b") > 0, "invalid Gamma parameters")
    from cevns_pyeft.detectors.csi2021 import CsI2021EfficiencyParams, efficiency_csi2021
    efficiency = CsI2021EfficiencyParams(*(p("detector.efficiency_"+x) for x in "abcd"))
    values = efficiency_csi2021(np.linspace(edges[0], edges[-1], 501), params=efficiency)
    _require(np.all((values >= 0) & (values <= 1)), "efficiency outside [0,1]")


def _scope_record(document, arrays, statistics=False):
    if statistics:
        return {"statistics": plain(document["statistics"]),
                "parameters": {k: plain(v) for k, v in document["parameters"].items() if k.startswith("statistics.")},
                "arrays": {k: _sha(v.tobytes()) for k, v in arrays.items() if k.startswith("statistics_")}}
    return {"sections": {k: plain(document[k]) for k in
            ("source", "target", "interaction", "detector", "observable", "prediction")},
            "parameters": {k: plain(v) for k, v in document["parameters"].items()
                           if not k.startswith("statistics.") and v["affects_fingerprint"]},
            "models": {k: plain(v) for k, v in document["models"].items() if k != "gaussian_two_pull_legacy_v1"},
            "arrays": {k: _sha(v.tobytes()) for k, v in arrays.items() if not k.startswith("statistics_")}}


@dataclass(frozen=True)
class CsIPackage:
    directory: Path
    document: object
    arrays: object
    hashes: object
    physical_fingerprint: str
    statistical_fingerprint: str

    def value(self, key):
        return self.document["parameters"][key]["value"]

    def assert_fresh(self, scope="physical"):
        contract = Path(__file__).with_name("csi2021_package_contract.json")
        _require(_sha(contract.read_bytes()) == self.hashes["binding_contract"],
                 "package binding contract changed; reload and rebuild dependent artifacts")
        current = {name: _sha((self.directory/name).read_bytes())
                   for name in ("experiment.input.yaml", "experiment.resources.npz")}
        if "experiment.physics.md" in self.hashes:
            md_raw = (self.directory/"experiment.physics.md").read_bytes()
            if _sha(md_raw) != self.hashes["experiment.physics.md"]:
                # Explanation revisions may change exact, allow-listed prose;
                # changed numerical tables are still a package conflict.
                updated_document = strict_json((self.directory/"experiment.input.yaml").read_text("utf-8"))
                updated_raw = (self.directory/"experiment.resources.npz").read_bytes()
                updated_arrays = read_arrays(updated_raw, updated_document["resources"]["arrays"])
                _check_explanation(updated_document, updated_arrays, md_raw.decode("utf-8"))
        if all(current[k] == self.hashes[k] for k in current):
            return
        updated = read_package(self.directory, check_md=False)
        expected = self.physical_fingerprint if scope == "physical" else self.statistical_fingerprint
        actual = updated.physical_fingerprint if scope == "physical" else updated.statistical_fingerprint
        _require(actual == expected, "package " + scope + " inputs changed; reload and rebuild dependent artifacts")

    def responses(self):
        result = {}
        for isotope in ISOTOPES:
            basic = {key: self.value("target."+isotope+"."+key) for key in ("A", "Z", "N", "J", "T", "b")}
            result[isotope] = ResponseW(self.document["target"]["response_keys"][isotope], basic,
                self.value("nuclear."+isotope+".exp_factor"),
                {key: self.arrays["nuclear_"+isotope+"_"+key].tolist() for key in CHANNELS})
        return result


def read_package(directory, *, check_md=True):
    directory = Path(directory).resolve()
    yaml_raw = (directory/"experiment.input.yaml").read_bytes()
    document = strict_json(yaml_raw.decode("utf-8"))
    _require(document["resources"]["archive"] == "experiment.resources.npz"
             and document["resources"]["allow_pickle"] is False
             and document["resources"]["undeclared_external_data_allowed"] is False,
             "package requires its adjacent safe NPZ archive")
    raw = (directory/"experiment.resources.npz").read_bytes()
    arrays = read_arrays(raw, document["resources"]["arrays"])
    contract_raw = Path(__file__).with_name("csi2021_package_contract.json").read_bytes()
    contract = strict_json(contract_raw.decode("utf-8"))
    _validate(document, arrays, raw, contract)
    hashes = {"experiment.input.yaml": _sha(yaml_raw), "experiment.resources.npz": _sha(raw),
              "binding_contract": _sha(contract_raw)}
    if check_md:
        md_raw = (directory/"experiment.physics.md").read_bytes()
        _check_explanation(document, arrays, md_raw.decode("utf-8"))
        hashes["experiment.physics.md"] = _sha(md_raw)
    return CsIPackage(directory, frozen_mapping(document), frozen_mapping(arrays), frozen_mapping(hashes),
                      digest({"inputs":_scope_record(document, arrays), "binding_contract":_sha(contract_raw)}),
                      digest(_scope_record(document, arrays, True)))


@dataclass(frozen=True)
class PackedState:
    rho: np.ndarray
    particle_kind: str

    def __call__(self, energy_MeV, *, parameters):
        _require(not parameters.values, "fixed package state does not consume state parameters")
        return IncidentStateBatch(energy_MeV, self.rho, self.particle_kind, "csi2021_package_fixed_state")

    def fixed_state_for_fast(self):
        return NeutrinoState(particle_kind=self.particle_kind, rho=self.rho)


@dataclass(frozen=True)
class PackedSource:
    package: CsIPackage

    def for_run(self, run):
        p, d, a = self.package.value, self.package.document, self.package.arrays
        _require(isinstance(run, POTExposure) and run.total_pot == p("source.total_pot"),
                 "packed fluence already contains declared POT; change package to rescale")
        support = EnergySupport((p("source.integration_min"), p("source.integration_max")),
            (p("source.tabulation_min"), p("source.tabulation_max")),
            interpolation_id="linear_packed_200_nodes", convention_id="legacy_sns_56MeV_node_mask_muon_DAR_quadrature")
        parts = []
        for component in d["source"]["components"]:
            continuum = (lambda x: np.zeros_like(x)) if component["continuum_ref"] is None else interp1d(
                a["source_energy_MeV"], a[component["continuum_ref"]], bounds_error=False, fill_value=0.)
            lines = (FluenceLine("pion_DAR", p("source.prompt_energy"), p("source.fluence_per_species")),) if component["line_model_ref"] else ()
            parts.append(CallableFluenceComponent(component["component_id"], component["particle_kind"],
                support, continuum, PackedState(a[component["rho_ref"]], component["particle_kind"]), lines))
        return DetectorFluence(tuple(parts), run.run_id,
            {"geometry_included": True, "POT_included": True, "fluence_per_species_cm^-2": p("source.fluence_per_species"),
             "source": "declared NPZ arrays", "physical_endpoint_audited": False})

    def describe(self):
        self.package.assert_fresh()
        return ModuleDescriptor("source", "csi2021_packed_fluence", capabilities=("slow_1d", "fixed_state"),
            parameters={"physical_input_fingerprint": self.package.physical_fingerprint})


@dataclass(frozen=True)
class PackedInteraction(Li2026LegacyInteraction):
    packed_responses: object = field(default_factory=dict)
    physical_input_fingerprint: str = ""

    def __post_init__(self):
        # ResponseW's existing reader requires nested lists. Definition snapshots
        # freeze constructor lists into tuples, so restore its documented representation.
        responses = {key: ResponseW(value.name, plain(value.basic), value.exp_factor, plain(value.responses))
                     for key, value in self.packed_responses.items()}
        object.__setattr__(self, "_responses", MappingProxyType(responses))
        object.__setattr__(self, "_sha256", self.physical_input_fingerprint)

    def describe(self):
        actual = {key:{"A":value.basic["A"], "b":value.basic["b"], "exp_factor":value.exp_factor,
                       "responses":plain(value.responses)} for key,value in self._responses.items()}
        return replace(super().describe(), resources={"nuclear_array_dependency": self.physical_input_fingerprint,
                       "actual_response_fingerprint":digest(actual)})


@dataclass(frozen=True)
class PackageExecutor:
    package: CsIPackage

    def describe_execution(self, model):
        return {"strategy": "legacy_csi2021_v1", "input_mode": "package_only",
                "physical_input_fingerprint": self.package.physical_fingerprint}

    def settings(self, settings):
        return IntegrationSettings(n_er=settings["n_er"], n_enu=settings["n_enu"],
            n_observed_bin=settings["n_pe_bin"], observed_step=settings["pe_step"],
            recoil_min_keV=settings["recoil_min_keV"], strategy="legacy_csi2021_v1")

    def __call__(self, experiment, point, backend, settings, kernel):
        from cevns_pyeft.core.predict import predict
        self.package.assert_fresh()
        result = predict(experiment.model, parameters=point, numerics=self.settings(settings),
                         backend=backend, compiled=kernel)
        return result, {"detector": result}, None, {"strategy": "legacy_csi2021_v1", "input_mode": "package_only",
            "package_hashes": plain(self.package.hashes), "full_response_channels": list(CHANNELS)}

    def compile(self, experiment, settings):
        from cevns_pyeft.kernels.compiler import compile_fast
        self.package.assert_fresh()
        return compile_fast(experiment.model, numerics=self.settings(settings))


@dataclass(frozen=True)
class PackagePhysics:
    physical_input_fingerprint: str
    implementation_modules: tuple = (
        "cevns_pyeft.experiments.coherent.csi2021_package", "cevns_pyeft.experiments.input_package",
        "cevns_pyeft.core.predict", "cevns_pyeft.rates.recoil", "cevns_pyeft.rates.folding",
        "cevns_pyeft.rates.differential", "cevns_pyeft.nuclear.response",
        "cevns_pyeft.theory.li2026.adapter", "cevns_pyeft.theory.li2026.amplitude",
        "cevns_pyeft.theory.li2026.left_to_ci", "cevns_pyeft.theory.li2026.responses",
        "cevns_pyeft.theory.li2026.coefficients", "cevns_pyeft.detectors.csi2021",
    )


@dataclass(frozen=True)
class PackagePreparation:
    package: CsIPackage

    def __call__(self, definition, resources):
        from cevns_pyeft.core.model import ExperimentModel
        from cevns_pyeft.contracts.observation import Axis, Binning
        from cevns_pyeft.detectors.csi2021 import (
            CsIGammaResponse, CsI2021Efficiency, CsI2021EfficiencyParams, CsI2021Observation,
        )
        from cevns_pyeft.detectors.selection import LegacyComponentAcceptance
        p, a = self.package.value, self.package.arrays
        targets = tuple(TargetIsotope(i, p("target."+i+".mass_GeV"), p("target."+i+".mass_kg"),
                        p("target."+i+".nuclei"), "legacy_A_times_amu") for i in ISOTOPES)
        inventory = TargetInventory(targets, p("target.detector_mass"), {"basis": "Cs:I=1:1 number ratio"})
        acceptance = dict(zip(SOURCE_IDS, [p("detector.acceptance_"+x) for x in ("mu", "e", "mub")]))
        response = CsIGammaResponse(tuple(p("detector.quenching_q"+str(i)) for i in range(1, 5)),
                                   p("detector.gamma_a"), p("detector.gamma_b"))
        efficiency = CsI2021Efficiency(CsI2021EfficiencyParams(*(p("detector.efficiency_"+x) for x in "abcd")))
        observation = CsI2021Observation(LegacyComponentAcceptance(acceptance), response, efficiency)
        interaction = PackedInteraction("package_array_authority", {"Cs133": "Cs133", "I127": "I"},
            packed_responses=self.package.responses(), physical_input_fingerprint=self.package.physical_fingerprint)
        model = ExperimentModel(PackedSource(self.package), POTExposure(p("source.total_pot"), definition.dataset_id),
            inventory, interaction, observation, Binning((Axis(definition.observation.name, "PE", a["observable_pe_edges"]),)),
            model_id="csi2021_package_legacy_9bin_v1")
        return model, PackageExecutor(self.package)


def evaluate_package(experiment, prediction):
    from cevns_pyeft.statistics.profiling import profile_gaussian_two_pull
    experiment.executor.package.assert_fresh("statistics")
    s = experiment.definition.statistics
    values = prediction.counts/np.diff(experiment.definition.observation.edges)
    return profile_gaussian_two_pull(values, s.observed, s.background, s.uncertainty,
                                     sigma_alpha=s.signal_sigma, sigma_beta=s.background_sigma)


def load_package_experiment(directory, *, check_md=True):
    """Use the public catalog/loader with the selected independent package."""
    from cevns_pyeft.experiments.catalog import ExperimentCatalog
    from cevns_pyeft.experiments.loader import ResourceCatalog, load_experiment
    package = read_package(directory, check_md=check_md)
    p, d, a = package.value, package.document, package.arrays
    settings = {"n_er": p("numerics.n_er"), "n_enu": p("numerics.n_enu"),
                "n_pe_bin": p("numerics.n_observed_bin"), "pe_step": p("numerics.observed_step"),
                "recoil_min_keV": p("numerics.recoil_min_keV")}
    stat = StatisticsDefinition(__name__+":evaluate_package", p("statistics.sigma_alpha"), p("statistics.sigma_beta"),
        observed=tuple(a["statistics_observed"]), background=tuple(a["statistics_background"]),
        uncertainty=tuple(a["statistics_uncertainty"]), kind="gaussian_two_pull", observable_unit="counts/PE",
        status="legacy approximate; residual/background semantics unresolved")
    definition = ExperimentDefinition("CsI2021", "COHERENT_CsI", d["package"]["analysis_revision"],
        ("package_POT_integrated",), PackagePhysics(package.physical_fingerprint),
        ObservationDefinition("reconstructed PE spectrum", "PE", tuple(a["observable_pe_edges"])),
        (), {"slow": settings, "fast": settings}, PackagePreparation(package), statistics=stat,
        reproduction_sin2thetaW=p("interaction.sin2thetaW"),
        capabilities={"slow": "package-only legacy scope", "fast": "interface_kernel_v1",
                      "statistics": "legacy approximate Gaussian", "official_likelihood": "BLOCKED"})
    catalog = ExperimentCatalog(builtins=False).register("CsI2021", definition)
    return load_experiment("CsI2021", registry=catalog, resources=ResourceCatalog(package.directory))

