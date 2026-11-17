"""Non-executable compatibility helpers retained after entry cleanup.

No calculate(), main() or CLI; not a new accepted physics implementation.
Existing NSI and historical validation consumers reuse unchanged helpers.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import time
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LOCAL_TIME = ROOT / "examples/COHERENT_CsI/time_resolved_common"
LOCAL_ANALYSIS_DATA = ROOT / "data/experiments/COHERENT_CsI/CsI2021/time_resolved"

from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.contracts.interaction import DifferentialCrossSection
from cevns_pyeft.contracts.observation import Axis, Binning
from cevns_pyeft.contracts.parameters import IntegrationSettings, TheoryPoint
from cevns_pyeft.contracts.source import DetectorFluence, EnergySupport, FluenceLine, IntegratedRunReference, IncidentStateBatch
from cevns_pyeft.contracts.validation import plain
from cevns_pyeft.core.model import ExperimentModel
from cevns_pyeft.core.predict import predict
from cevns_pyeft.detectors.csi2021 import CsI2021Efficiency, CsI2021EfficiencyParams, CsI2021Observation, CsIGammaResponse
from cevns_pyeft.detectors.selection import LegacyComponentAcceptance
from cevns_pyeft.sources.composable import CallableFluenceComponent, IntegratedFluenceSource
from cevns_pyeft.sources.sns import ConstantSNSState, LEGACY_COMPONENT_IDS
from cevns_pyeft.targets.materials import csi_target_inventory
from cevns_pyeft.theory.li2026.adapter import Li2026LegacyInteraction


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(plain(value), ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                          encoding="utf-8", newline="\n")


def inputs(onboarding):
    register = json.loads((onboarding / "P00_SOURCE_REGISTER.yaml").read_text(encoding="utf-8"))
    ledger = json.loads((onboarding / "P01_EVIDENCE_LEDGER.yaml").read_text(encoding="utf-8"))
    claims = {row["claim_id"]: row for row in ledger["claims"]}
    for source in register["sources"]:
        if sha(ROOT / source["uri_or_path"]) != source["sha256"]:
            raise ValueError("Source fingerprint mismatch: " + source["source_id"])
    return claims, register


def local_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def time_modules(folder):
    return (local_module(folder / "time_acceptance.py", "_csi_sm_time_acceptance"),
            local_module(folder / "time_profile.py", "_csi_sm_time_profile"))


def analysis_input_file(onboarding):
    """Use the local current resource and verify its unchanged adopted source."""
    evidence = onboarding / "data/analysis_inputs.npz"
    default = ROOT / "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved"
    if onboarding.resolve() != default.resolve():
        return evidence
    adopted = LOCAL_ANALYSIS_DATA / "analysis_inputs.npz"
    if sha(adopted) != sha(evidence):
        raise ValueError("Current time-analysis input differs from its adopted evidence; review resource version")
    return adopted


def time_source(onboarding, profile_module):
    array_path = analysis_input_file(onboarding)
    with np.load(array_path, allow_pickle=False) as data:
        profiles = {name: profile_module.BinnedTimeProfile(name, data["ROOT_time_edges_us"], data[name + "_time_mass"])
                    for name in ("mu", "e", "mub", "ebar")}
    return SimpleNamespace(components=("mu", "e", "mub"), profile=profiles.__getitem__,
        provenance={"raw_sha256": sha(onboarding / "sources/official/snsFlux2D.root"),
                    "cache_sha256": sha(array_path)})


class CheckedSMInteraction:
    """Reuse the previous audit's checked E^2*dSigma/dT quadratic evaluation.

    Every recoil/state is checked against five current native evaluations;
    three determine the polynomial and two independently check it. This is
    restricted to pure SM and constant incident state. It builds no EFT cache.
    Failed checks fall back to the original full energy-array call.
    """
    coefficient_contract = None

    def __init__(self, original):
        self.original = original
        self.statistics = {"checked_calls": 0, "fallback_calls": 0, "max_holdout_relative_error": 0.0}

    def __getattr__(self, name):
        return getattr(self.original, name)

    def dsigma_dT(self, *, target, energy_MeV, recoil_keV, incident_state, parameters):
        energy = np.asarray(energy_MeV)
        arguments = dict(target=target, recoil_keV=recoil_keV, parameters=parameters)
        rho = incident_state.rho
        constant = rho.ndim == 2 or np.array_equal(rho, np.broadcast_to(rho[0], rho.shape))
        if energy.size < 6 or not parameters.include_sm or parameters.wc_triplets or not constant:
            return self.original.dsigma_dT(energy_MeV=energy, incident_state=incident_state, **arguments)
        lo, hi = float(energy.min()), float(energy.max())
        if hi - lo < 1e-8:
            return self.original.dsigma_dT(energy_MeV=energy, incident_state=incident_state, **arguments)
        probes = lo + (hi - lo) * np.array([.10, .31, .52, .73, .94])
        probe_state = IncidentStateBatch(probes, rho if rho.ndim == 2 else rho[0],
            incident_state.particle_kind, incident_state.state_model_id)
        measured = self.original.dsigma_dT(energy_MeV=probes, incident_state=probe_state, **arguments).values_cm2_per_keV
        scale = max(float(np.max(np.abs(measured * probes**2))), 1e-300)
        coefficients = np.polynomial.polynomial.polyfit(probes[[0, 2, 4]] / hi,
            measured[[0, 2, 4]] * probes[[0, 2, 4]]**2 / scale, 2)
        checked = np.polynomial.polynomial.polyval(probes / hi, coefficients) * scale / probes**2
        relative = float(np.max(np.abs(checked - measured)) / max(float(np.max(np.abs(measured))), 1e-300))
        values = np.polynomial.polynomial.polyval(energy / hi, coefficients) * scale / energy**2
        if not np.allclose(checked, measured, rtol=2e-10, atol=2e-12 * float(np.max(np.abs(measured)))) or np.any(values < 0):
            self.statistics["fallback_calls"] += 1
            return self.original.dsigma_dT(energy_MeV=energy, incident_state=incident_state, **arguments)
        self.statistics["checked_calls"] += 1
        self.statistics["max_holdout_relative_error"] = max(self.statistics["max_holdout_relative_error"], relative)
        return DifferentialCrossSection(energy, values, float(recoil_keV), "native_SM_checked_energy_evaluation")

    def describe(self):
        return ModuleDescriptor("interaction", "native_SM_checked_energy_evaluation", capabilities=("slow_elastic",),
            parameters={"original": self.original.describe().as_dict(), "three_fit_two_holdout_probes": True,
                "pure_SM_only": True, "EFT_cache": False})


class ExactSampledGammaResponse:
    """Reuse exact native density values at the common Slow engine's PE nodes.

    This caches only P06 conditional response evaluations, without source,
    cross section, selection, event counts or added interpolation.
    """
    def __init__(self, original, samples):
        self.original = original
        self.samples = np.array(samples)
        self.step = float(self.samples[1] - self.samples[0])
        self.rows = {}
        self.lookup_count = 0

    def density(self, observed, recoil_keV, *, target):
        if np.ndim(observed) == 0:
            index = int(round((float(observed) - self.samples[0]) / self.step))
            if 0 <= index < len(self.samples) and abs(float(observed) - self.samples[index]) < 1e-12:
                key = float(recoil_keV)
                if key not in self.rows:
                    self.rows[key] = self.original.density(self.samples, key, target=target)
                self.lookup_count += 1
                return float(self.rows[key][index])
        return self.original.density(observed, recoil_keV, target=target)

    def describe(self):
        return {**self.original.describe(), "numerical_evaluation": "exact_requested_PE_nodes_reused", "extra_interpolation": False}


def build_model(claims, *, mass_factor=1.0, fluence_factor=1.0, energy_fluence_scope="reference_window"):
    """Supply published Eq.29 spectra to existing explicit-fluence contracts."""
    value = lambda key: claims[key]["value"]
    eta = float(value("C_ETA")) * fluence_factor
    muon_mass = float(value("C_MMU"))
    endpoint = float(value("C_ENDPOINT"))
    line_energy = float(value("C_LINE"))
    support = EnergySupport((0.0, endpoint), physical_domain_MeV=(0.0, endpoint),
        convention_id="2211.11905v2_Eq29_DAR_m_mu_over_2")

    def electron_spectrum(energy):
        e = np.asarray(energy)
        return np.where((e >= 0) & (e <= endpoint), eta * 192 * e**2 / muon_mass**3 * (.5 - e / muon_mass), 0.0)

    def antimuon_spectrum(energy):
        e = np.asarray(energy)
        return np.where((e >= 0) & (e <= endpoint), eta * 64 * e**2 / muon_mass**3 * (.75 - e / muon_mass), 0.0)

    continua = {"mu": lambda e: np.zeros_like(e), "e": electron_spectrum, "mub": antimuon_spectrum}
    components = tuple(CallableFluenceComponent(LEGACY_COMPONENT_IDS[name], "antinu" if name == "mub" else "nu",
        support, continua[name], ConstantSNSState(name),
        (FluenceLine("pion_DAR", line_energy, eta),) if name == "mu" else ()) for name in ("mu", "e", "mub"))
    run = IntegratedRunReference("CsI2021_time_SM_20261107")
    normalization = {"equation": "2211.11905v2 Eq29", "eta_cm^-2": eta, "POT": value("C_POT"),
        "yield_per_flavor_per_POT": value("C_YIELD"), "baseline_m": value("C_L"),
        "fluence_scope": ("reference_window_0_6us_same_numerical_eta" if energy_fluence_scope == "reference_window"
                          else "full_support_same_numerical_eta"), "additional_livetime_factor": False,
        "fluence_scale_for_validation": fluence_factor}
    source = IntegratedFluenceSource(DetectorFluence(components, run.run_id, normalization),
        ModuleDescriptor("source", "csi2021_paper_DAR_nominal", capabilities=("slow_1d", "fixed_state"), parameters=normalization))
    params = CsI2021EfficiencyParams(*value("C_EFF"))
    gamma = value("C_GAMMA")
    observation = CsI2021Observation(
        LegacyComponentAcceptance({identifier: 1.0 for identifier in LEGACY_COMPONENT_IDS.values()}, "before_time_selection"),
        CsIGammaResponse(tuple(value("C_QF")), gamma["a_numerator"], gamma["b_slope"]), CsI2021Efficiency(params))
    response = ROOT / value("C_RESOURCE_BINDING")["path"]
    return ExperimentModel(source, run, csi_target_inventory(float(value("C_MASS")) * mass_factor),
        Li2026LegacyInteraction(response), observation,
        Binning((Axis(observation.axis_name, "PE", np.array(value("C_PE"))),)), "CsI2021_time_SM_paper_inputs_local_RESPONSE")

