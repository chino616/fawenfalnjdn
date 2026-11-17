"""Fresh full-basis forward models, isolated from registered experiments.

Uses readable mainline resources/records and shared numerical owners. Ground
restorations must reproduce adopted dim-6 projections at the same grids.
Solar full22 is explicitly a fixed-SM-propagation control, not arbitrary-LEFT
matter propagation. No formal input package or runtime code is changed.
"""
from __future__ import annotations
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import re
import sys
import time
from types import SimpleNamespace
import numpy as np
from numpy.polynomial.chebyshev import chebvander

from common import ROOT, read, sha
from model_adapters import BASIS, Ground, REFERENCE, SOLAR, SOLAR_SAMPLES
from cevns_pyeft.contracts import IntegrationSettings, TheoryPoint
from cevns_pyeft.contracts.observation import Axis, Binning
from cevns_pyeft.contracts.source import POTExposure
from cevns_pyeft.contracts.target import TargetInventory, TargetIsotope
from cevns_pyeft.core.model import ExperimentModel
from cevns_pyeft.detectors.csi2021 import CsI2021Observation, CsI2021Efficiency, CsI2021EfficiencyParams, CsIGammaResponse
from cevns_pyeft.detectors.selection import LegacyComponentAcceptance
from cevns_pyeft.detectors.coherent import ObservedGaussianObservation
from cevns_pyeft.experiments.package_profiles import ArrayEfficiency
from cevns_pyeft.foundation.constants import AMU_GEV
from cevns_pyeft.rates.folding import linear_fold_weights, trapezoid_weights
from cevns_pyeft.rates.legacy_observables import observed_gaussian_fold
from cevns_pyeft.sources.sns import SNSLegacySource
from cevns_pyeft.theory.li2026.adapter import Li2026LegacyInteraction
from cevns_pyeft.theory.li2026.operators import LI2026_OPERATOR_SPECS

KEYS = tuple(spec.key for spec in LI2026_OPERATOR_SPECS)


def flavor_tensor(key):
    """Explicit channel convention, not a flavor-universal scalar injection.

    LNC: ee. LNV: e<->mu, antisymmetric for dipole/tensor, symmetric for scalar.
    Each nonzero entry has magnitude |c|. No sqrt(2) normalization rescaling.
    """
    spec = next(s for s in LI2026_OPERATOR_SPECS if s.key == tuple(key))
    f = np.zeros((3, 3), complex)
    if spec.lepton_number == "LNC":
        f[0, 0] = 1.
    else:
        f[1, 0] = 1.
        f[0, 1] = -1. if key[0] == 5 or key[1] == 3 else 1.
    return f


def md_parameters(path):
    text = Path(path).read_text(encoding="utf-8")
    entries = {}
    for match in re.finditer(r"^\| \[`([^`]+)`\]\([^)]*\) \| ([^|]+) \|", text, re.M):
        value = match[2].strip()
        try:
            entries[match[1]] = json.loads(value)
        except (ValueError, TypeError):
            pass
    return entries, text


def build_csi():
    record = read(f"{REFERENCE}/CsI2021_kernel_record.json")["dependencies"]
    params, text = md_parameters(ROOT/"data/experiments/COHERENT_CsI/CsI2021/experiment.physics.md")
    axis = re.search(r"完整边界为 ([\d., ]+) PE", text)
    if axis is None:
        raise ValueError("explicit readable CsI bin-edge evidence missing")
    edges = np.array([float(x) for x in axis[1].split(",")])
    expected = record["axes"][0]["edges"]["sha256"]
    if sha_array(edges) != expected:
        raise ValueError("readable CsI edge declaration differs from adopted fingerprint")
    targets = tuple(TargetIsotope(**item) for item in record["targets"]["isotopes"])
    inventory = TargetInventory(targets, sum(t.nucleus_mass_kg*t.number_of_nuclei for t in targets))
    p = record["source"]["parameters"]
    source = SNSLegacySource(baseline_m=p["baseline_m"], yield_per_pot=p["yield_per_pot"],
                             num_points=params["source.tabulation_nodes"])
    run = POTExposure(record["run"]["total_pot"], "CsI2021")
    obs = record["observation"]["parameters"]
    response = obs["response"]
    observation = CsI2021Observation(LegacyComponentAcceptance(obs["acceptance"]),
        CsIGammaResponse(tuple(response["quenching"]), response["gamma_a"], response["gamma_b"]),
        CsI2021Efficiency(CsI2021EfficiencyParams(**obs["efficiency"]["parameters"])))
    interaction = Li2026LegacyInteraction(ROOT/"data/responses/responses_all.json", {"Cs133": "Cs133", "I127": "I"})
    model = ExperimentModel(source, run, inventory, interaction, observation,
                            Binning((Axis(observation.axis_name, "PE", edges),)), "cutoff_csi_readable_record_restoration")
    # Regenerate actual source numbers and verify their saved raw-array hashes.
    energy = np.linspace(params["source.tabulation_min"], params["source.tabulation_max"], params["source.tabulation_nodes"])
    fluence = model.source.for_run(model.run)
    from cevns_pyeft.experiments.coherent.sns import SNSDataset, build_neutrino_empirical_flux_sns
    config = SNSDataset("CsI2021", 0, p["baseline_m"], run.total_pot, p["yield_per_pot"], energy[0], energy[-1],
                        params["source.mask_min"], params["source.mask_max"])
    raw = build_neutrino_empirical_flux_sns(config, num_points=len(energy))
    for key, values in (("source_energy_MeV", energy), ("source_fluence_e", raw["measured"]["e"](energy)),
                        ("source_fluence_mub", raw["measured"]["mub"](energy))):
        if sha_array(np.asarray(values, float)) != record["source"]["resources"][key]:
            raise ValueError("restored SNS raw array hash differs: "+key)
    return model


def sha_array(values):
    import hashlib
    return hashlib.sha256(np.ascontiguousarray(values).tobytes()).hexdigest()


def build_ar():
    p, _ = md_parameters(ROOT/"data/experiments/COHERENT_Ar/Ar2020/experiment.physics.md")
    table = ROOT/"data/experiments/COHERENT_Ar/Ar2020/detector/CENNS10AnlAEfficiency.txt"
    # Exact historical numeric expression spelling; no coordinate reinterpretation.
    data = np.array([[float(t.replace("*10^", "e")) for t in line.split()] for line in table.read_text().splitlines() if line.strip()])
    efficiency = ArrayEfficiency(data[:, 0], data[:, 2], 0., None)
    target = TargetIsotope("Ar40", p["target.Ar40.mass_GeV"], p["target.Ar40.mass_kg"], p["target.Ar40.nuclei"])
    model = ExperimentModel(SNSLegacySource(baseline_m=p["source.baseline_m"], yield_per_pot=p["source.yield_per_pot"], num_points=p["source.tabulation_nodes"]),
        POTExposure(p["source.total_pot"], "Ar2020"), TargetInventory((target,), p["target.detector_mass"]),
        Li2026LegacyInteraction(ROOT/"data/responses/responses_all.json", {"Ar40": "Ar40"}),
        ObservedGaussianObservation(p["detector.mean_linear"], p["detector.mean_quadratic"], p["detector.sigma_coefficient"], efficiency),
        Binning((Axis("reconstructed PE spectrum", "PE", np.array(read(f"{REFERENCE}/Ar2020_kernel_record.json")["pe_bins"])),)),
        "cutoff_ar_readable_legacy_column1_control")
    return model


def build_conus():
    directory = ROOT/"examples/CONUS_Plus/conusplus_kkl_run1/nsi_response"
    sys.path.insert(0, str(directory))
    # The selected model factory only reads existing project resources.
    spec = importlib.util.spec_from_file_location("cutoff_conus_model", directory/"nsi_model.py")
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    return module.model(), module.sm.settings


def energy_polynomial(interaction, target, recoil, maximum, keys=KEYS, *, verify=True):
    """Exact E^2 H(E) degree<=4 for the active shared response polynomials.

    Five defining nodes; an independent native probe at every recoil; no fitting
    of event rates. This keeps all nuclear channels and interference terms.
    """
    minimum = interaction.kinematics.minimum_energy_MeV(target, float(recoil))
    low, high = max(1.001*minimum, 1e-4), max(maximum, 1.5*minimum)
    center, radius = (low+high)/2, (high-low)/2
    nodes = np.cos(np.pi*(np.arange(5)+.5)/5)
    energy = center+radius*nodes
    native = interaction.coefficient_dsigma(target=target, energy_MeV=energy, recoil_keV=float(recoil), basis_keys=keys)
    weighted = native*(energy[:, None, None, None]*1e-3)**2
    coefficients = np.linalg.solve(chebvander(nodes, 4), weighted.reshape(5, -1)).reshape(weighted.shape)
    error = 0.
    if verify:
        probe = np.array([-.347, .713])
        e = center+radius*probe
        direct = interaction.coefficient_dsigma(target=target, energy_MeV=e, recoil_keV=float(recoil), basis_keys=keys)*(e[:, None, None, None]*1e-3)**2
        predicted = np.einsum("ep,p...->e...", chebvander(probe, 4), coefficients)
        scale = np.maximum(np.max(abs(weighted), axis=0), np.max(abs(direct), axis=0))
        active = scale > 0
        error = float(np.max(abs(predicted-direct)[:, active]/scale[active])) if np.any(active) else 0.
        if error > 2e-8:
            raise ValueError(f"E-polynomial native holdout failed at T={recoil}: {error}")
    return coefficients, center, radius, error


def moments(energy, weights, center, radius):
    return np.einsum("e,ep->p", weights/(energy*1e-3)**2, chebvander((energy-center)/radius, 4))


def compile_ground(model, name, *, n_er, n_enu, n_observed=256, step=.0625, verify=True):
    source = model.source.for_run(model.run)
    components = source.components
    maximum = max(max([c.support.integration_domain_MeV[1]]+[l.energy_MeV for l in c.lines]) for c in components)
    full = np.zeros((len(model.targets.isotopes), len(components), 8, len(KEYS), len(KEYS), model.binning.shape[0]), complex)
    errors = []
    for ti, target in enumerate(model.targets.isotopes):
        endpoint = model.interaction.kinematics.maximum_recoil_keV(target, maximum)
        lower = .1
        if name == "CONUS_plus":
            from scipy.optimize import brentq
            lower = brentq(lambda t: float(model.observation.mean_eVee(t))-model.observation.pair_energy_eVee, 1e-8, 1.)
        recoil = np.linspace(lower, endpoint, n_er)
        if name == "CsI2021_9PE":
            ns = IntegrationSettings(n_er=n_er, n_enu=n_enu, n_observed_bin=n_observed, observed_step=step,
                                     recoil_min_keV=lower, strategy="legacy_csi2021_v1")
            folds = [linear_fold_weights(target, model.observation, model.binning, ns, recoil, c.component_id) for c in components]
        elif name == "Ar2020_average":
            fold = observed_gaussian_fold(recoil, trapezoid_weights(recoil), model.binning.axes[0].edges,
                                          model.observation.efficiency, model.observation, n_observed)
            folds = [fold]*len(components)
        else:
            ns = IntegrationSettings(n_er=n_er, n_enu=n_enu, recoil_min_keV=lower, strategy="bin_probability_v1")
            folds = [linear_fold_weights(target, model.observation, model.binning, ns, recoil, c.component_id) for c in components]
        for ri, t in enumerate(recoil):
            coefficients, center, radius, error = energy_polynomial(model.interaction, target, float(t), maximum, verify=verify)
            errors.append(error)
            minimum = model.interaction.kinematics.minimum_energy_MeV(target, float(t))
            for si, component in enumerate(components):
                breaks = component.support.breakpoints_MeV if name == "CONUS_plus" else ()
                energy = np.unique(np.r_[np.linspace(*component.support.integration_domain_MeV, n_enu), breaks])
                energy = energy[(energy >= minimum) & (energy > 0)]
                m = np.zeros(5)
                if len(energy) > 1:
                    m += moments(energy, trapezoid_weights(energy)*component.continuum(energy), center, radius)
                for line in component.lines:
                    if line.energy_MeV >= minimum:
                        m += moments(np.array([line.energy_MeV]), np.array([line.fluence_per_cm2]), center, radius)
                integrated = np.einsum("p,p...->...", m, coefficients)
                full[ti, si] += integrated[..., None]*folds[si][ri]*target.number_of_nuclei
        print("FORWARD", name, target.isotope_id, n_er, "max_E_holdout", max(errors), flush=True)
    full = .5*(full+full.swapaxes(3, 4).conj())
    return full, {"n_er": n_er, "n_enu": n_enu, "n_observed": n_observed, "step": step,
                  "native_energy_holdout_max_relative": max(errors), "native_energy_holdout_count": 2*len(errors),
                  "energy_representation": "exact degree4 E^2 operator coefficients;5 defining+2 native holdout nodes per recoil"}


def compile_solar(solar, *, n_er=801, verify=True):
    from cevns_pyeft.experiments.solar_singlebin import load_singlebin
    energy, energy_weights = solar.energy, solar.weights
    rho = solar.source.rho(energy, 0., 0.)
    np.testing.assert_allclose(rho[:, 0, 0].real, solar.source.pee(energy, 0., 0.), atol=2e-15, rtol=0)
    probs = np.array([np.ones(len(energy)), rho[:, 0, 0].real, (rho[:, 0, 0]+rho[:, 1, 1]).real])
    polynomial = np.zeros((3, len(KEYS), 3))
    # Actual binning/model data come from the readable mainline singlebin loader.
    records = []
    for sample_index, sample in enumerate(SOLAR_SAMPLES):
        model = load_singlebin(sample, root=ROOT).model
        interaction = Li2026LegacyInteraction(ROOT/"data/responses/responses_all.json", {t.isotope_id: t.isotope_id for t in model.targets.isotopes})
        lower, upper = model.observation.requested_bounds
        split = model.observation.verified_upper
        recoil = np.unique(np.r_[np.linspace(lower, upper, n_er), model.observation.energy[
            (model.observation.energy > lower) & (model.observation.energy < upper)], split])
        rw = np.zeros_like(recoil)
        known = recoil <= split
        rw[known] = trapezoid_weights(recoil[known])*model.observation.known_acceptance(recoil[known])
        if not model.observation.complete:
            tail = recoil >= split
            rw[tail] += trapezoid_weights(recoil[tail])*solar.tail_efficiency
        component = model.source.components_per_second[0]
        flux_weights = energy_weights*component.continuum(energy)*model.seconds_per_year
        matrices = np.zeros((3, len(KEYS), len(KEYS)), complex)
        error_max = 0.
        for target in model.targets.isotopes:
            for j, t in enumerate(recoil):
                if rw[j] == 0:
                    continue
                coefficients, center, radius, error = energy_polynomial(interaction, target, float(t), float(energy.max()), verify=verify)
                error_max = max(error_max, error)
                mask = energy >= interaction.kinematics.minimum_energy_MeV(target, float(t))
                for state in range(3):
                    m = moments(energy[mask], flux_weights[mask]*probs[state, mask], center, radius)
                    matrices[state] += np.einsum("p,phij->ij", m, coefficients)*rw[j]*target.number_of_nuclei*model.exposure_tyr
            print("SOLAR22", sample, target.isotope_id, "recoils", len(recoil), flush=True)
        from cevns_pyeft.rates.differential import _sm_left_dim6
        sm = np.array([_sm_left_dim6(True, .23857).get(key, np.zeros((3, 3)))[0, 0] for key in KEYS])
        n0 = float(np.real(sm.conj() @ matrices[0] @ sm))
        for i, key in enumerate(KEYS):
            lnv = LI2026_OPERATOR_SPECS[i].lepton_number == "LNV"
            linear = 0. if lnv else 2*float(np.real(matrices[1][i] @ sm))
            quadratic = float(np.real(matrices[2 if lnv else 1, i, i]))
            polynomial[sample_index, i] = (n0, linear, quadratic)
        records.append({"sample": sample, "n_er": n_er, "recoil_nodes": len(recoil),
                        "native_energy_holdout_max_relative": error_max, "SM_events": n0,
                        "adopted_SM_events": float(solar.sm[sample_index]), "relative_SM_difference": n0/solar.sm[sample_index]-1})
    return polynomial, records
