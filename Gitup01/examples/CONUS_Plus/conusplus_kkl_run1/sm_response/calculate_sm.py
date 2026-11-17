"""CONUS+ SM calculation through the project's existing direct Slow pipeline.

Run via the parent run_benchmark.py with --method sm and a fresh output.
Inputs are explicit Gitup01 resources; the original execution source is archived.
No fitted normalization is used.
"""
from __future__ import annotations
from pathlib import Path as _LayoutPath
import sys as _layout_sys
_layout_sys.path.insert(0, str(_LayoutPath(__file__).resolve().parents[1]))
from conusplus_paths import Layout
LAYOUT = Layout('sm')
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
from scipy.optimize import brentq
from scipy.special import ndtr
HERE = Path(__file__).resolve().parent
SNAPSHOT = LAYOUT.path('snapshot')
sys.path.insert(0, str(SNAPSHOT))
from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.contracts.observation import Axis, Binning, BinProbabilities
from cevns_pyeft.contracts.parameters import IntegrationSettings, TheoryPoint
from cevns_pyeft.contracts.source import EnergySupport, IncidentStateBatch, LiveTimeExposure
from cevns_pyeft.contracts.target import TargetInventory, TargetIsotope
from cevns_pyeft.core.model import ExperimentModel
from cevns_pyeft.core.predict import predict
from cevns_pyeft.experiments.package_components import ArrayContinuum
from cevns_pyeft.foundation.constants import AMU_GEV
from cevns_pyeft.sources.composable import CallableFluenceComponent, DifferentialFluxSource
from cevns_pyeft.theory.li2026.adapter import Li2026LegacyInteraction
DATA = SNAPSHOT / 'data/experiments/CONUS_Plus/conusplus_kkl_run1'
OUTPUT = LAYOUT.path('outputs')
ISOTOPES = ('Ge70', 'Ge72', 'Ge73', 'Ge74', 'Ge76')
CONFIG = json.loads((DATA / 'input_choices.json').read_text(encoding='utf-8'))
EDGES = np.arange(160.0, 351.0, 10.0)
POINT = TheoryPoint(include_sm=True, sin2thetaW=CONFIG['constants']['sin2thetaW_reference'])

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def json_value(value):
    if isinstance(value, dict) or hasattr(value, 'items'):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    if isinstance(value, np.ndarray):
        return json_value(value.tolist())
    if isinstance(value, np.generic):
        return json_value(value.item())
    if isinstance(value, complex):
        return {'real': value.real, 'imag': value.imag}
    if isinstance(value, Path):
        return str(value)
    return value

def write_json(path, record):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(json_value(record), ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

@dataclass(frozen=True)
class GeLindhardGaussian:
    """Paper Eqs. (29)-(31), with reconstructed-bin acceptance and lost tails."""
    k: float = CONFIG['detector_lindhard_k']
    z: int = 32
    sigma0_eVee: float = CONFIG['detector_sigma0_eVee']
    fano: float = CONFIG['detector_fano']
    pair_energy_eVee: float = CONFIG['detector_pair_energy_eVee']
    axis_name: str = 'ionization_energy'
    axis_unit: str = 'eVee'

    def mean_eVee(self, recoil_keV):
        recoil = np.asarray(recoil_keV, dtype=float)
        if np.any(recoil < 0) or not np.all(np.isfinite(recoil)):
            raise ValueError('recoil must be finite and nonnegative')
        epsilon = 11.5 * self.z ** (-7.0 / 3.0) * recoil
        g = 3.0 * epsilon ** 0.15 + 0.7 * epsilon ** 0.6 + epsilon
        return 1000.0 * recoil * self.k * g / (1.0 + self.k * g)

    def sigma_eVee(self, recoil_keV):
        return np.sqrt(self.sigma0_eVee ** 2 + self.fano * self.pair_energy_eVee * self.mean_eVee(recoil_keV))

    def bin_probabilities(self, *, target, recoil_keV, binning, component_id):
        mean = self.mean_eVee(recoil_keV)[:, None]
        sigma = self.sigma_eVee(recoil_keV)[:, None]
        edges = binning.axes[0].edges
        lower = (edges[:-1] - mean) / sigma
        upper = (edges[1:] - mean) / sigma
        values = np.where(lower > 0, ndtr(-lower) - ndtr(-upper), ndtr(upper) - ndtr(lower))
        return BinProbabilities(recoil_keV, binning, values, ('reconstructed_analysis_window', 'paper_unity_efficiency'))

    def describe(self):
        return ModuleDescriptor('observation', 'conusplus_lindhard_gaussian_candidate_v1', capabilities=('bin_probabilities_1d',), parameters={'k': self.k, 'Z': self.z, 'sigma0_eVee': self.sigma0_eVee, 'Fano': self.fano, 'eta_eVee': self.pair_energy_eVee, 'normalization': 'full real Gaussian, ROI losses retained', 'efficiency': 'one in reconstructed analysis bins', 'source_locator': '2501.17843v3 PDF p.9, Eqs.(29)-(31)'}, dependencies=('recoil_keV', 'observed_bin_edges'))

def reactor_state(energy_MeV, *, parameters):
    if parameters.values:
        raise ValueError('This SM calculation has a fixed incident state')
    return IncidentStateBatch(energy_MeV, np.diag([1.0, 0.0, 0.0]), 'antinu', 'reactor_electron_antineutrino_fixed_v1')

def build_model(*, mass_scale=1.0, flux_scale=1.0, live_scale=1.0):
    flux = np.genfromtxt(DATA / 'reactor_flux_default.csv', delimiter=',', names=True, encoding='utf-8')
    low_nodes = np.genfromtxt(DATA / 'kopeikin_low_energy_transcribed.csv', delimiter=',', names=True, encoding='utf-8')
    breaks = tuple(sorted(set(low_nodes['energy_MeV'].tolist() + [2.0, 8.0])))
    support = EnergySupport((0.0, 10.0), (0.0, 10.0), breakpoints_MeV=breaks, interpolation_id='linear_tabulated_flux', convention_id='onboarding_v3')
    component = CallableFluenceComponent('reactor_antinu_e', 'antinu', support, ArrayContinuum(flux['energy_MeV'], flux['flux_cm_minus2_s_minus1_MeV_minus1'] * flux_scale), reactor_state)
    source = DifferentialFluxSource((component,), ModuleDescriptor('source', 'conusplus_tabulated_detector_flux_candidate_v1', capabilities=('slow_1d',), parameters={'flux_cm2_s': CONFIG['flux_total_cm2_s'] * flux_scale, 'source_locator': 'onboarding v3 PROVENANCE_MAP.json, reactor_flux_default.csv'}, resources={'flux_sha256': sha256(DATA / 'reactor_flux_default.csv')}))
    detector_mass = CONFIG['effective_detector_mass_kg'] * mass_scale
    mean_mass_u = sum((CONFIG['target_number_fractions'][name] * CONFIG['target_atomic_masses_u'][name] for name in ISOTOPES))
    total_nuclei = detector_mass / (mean_mass_u * CONFIG['constants']['atomic_mass_kg'])
    targets = TargetInventory(tuple((TargetIsotope(name, int(name[2:]) * AMU_GEV, CONFIG['target_atomic_masses_u'][name] * CONFIG['constants']['atomic_mass_kg'], total_nuclei * CONFIG['target_number_fractions'][name], 'kinematics_A_times_amu_inventory_NIST_atomic_mass') for name in ISOTOPES)), detector_mass, {'number_fractions': CONFIG['target_number_fractions'], 'atomic_masses_u': CONFIG['target_atomic_masses_u'], 'mass_accounting': 'atomic mass for nuclei per kg, A*amu for kinematics'})
    seconds = CONFIG['exposure_kg_day'] / CONFIG['effective_detector_mass_kg'] * CONFIG['constants']['seconds_per_day'] * live_scale
    return ExperimentModel(source, LiveTimeExposure(seconds, 'conusplus_kkl_run1_effective_1kg'), targets, Li2026LegacyInteraction(SNAPSHOT / 'data/responses/responses_all.json', {name: name for name in ISOTOPES}), GeLindhardGaussian(), Binning((Axis('ionization_energy', 'eVee', EDGES),)), 'conusplus_sm_response_isolated_v1')

def settings(n_er, n_enu, recoil_min=None):
    response = GeLindhardGaussian()
    cutoff = brentq(lambda t: float(response.mean_eVee(t)) - response.pair_energy_eVee, 1e-08, 1.0, xtol=1e-14)
    return IntegrationSettings(n_er=n_er, n_enu=n_enu, strategy='bin_probability_v1', recoil_min_keV=cutoff if recoil_min is None else recoil_min, observed_step=1.0)

def calculate_case(case):
    name, n_er, n_enu = case
    started = time.perf_counter()
    model = build_model()
    numerics = settings(n_er, n_enu)
    result = predict(model, parameters=POINT, numerics=numerics, backend='slow')
    arrays = {'counts': result.counts, 'edges_eVee': EDGES}
    for isotope in ISOTOPES:
        key = ('reactor_antinu_e', isotope)
        recoil = result.diagnostics['recoil_yields'][key]
        arrays['counts_' + isotope] = result.components[key]
        arrays['recoil_keV_' + isotope] = recoil.recoil_keV
        arrays['yield_per_nucleus_per_keV_' + isotope] = recoil.values_per_keV
    np.savez_compressed(OUTPUT / (name + '.npz'), **arrays)
    record = {'case': name, 'seconds': time.perf_counter() - started, 'counts': result.counts, 'total_events': float(result.counts.sum()), 'parameter_point': {'include_sm': True, 'wc_triplets': {}, 'sin2thetaW': POINT.sin2thetaW}, 'backend': 'slow', 'executor': 'cevns_pyeft.core.predict.predict', 'model': result.model_record, 'numerics': result.numerical_record, 'normalization': result.normalization_record, 'provenance_status': 'PROJECT_DERIVED_LOCAL_RESPONSE_PRIMARY_CHAIN_PENDING', 'source_map': '../snapshot/data/experiments/CONUS_Plus/conusplus_kkl_run1/PROVENANCE_MAP.json'}
    write_json(OUTPUT / (name + '.json'), record)
    return {'case': name, 'total_events': record['total_events'], 'seconds': record['seconds']}

def main():
    LAYOUT.require_writable_run()
    LAYOUT.verify_inputs()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=('base', 'energy_refined', 'recoil_refined', 'fine', 'energy_641', 'fine_641', 'all'), default='all')
    args = parser.parse_args()
    cases = [('base', 81, 161), ('energy_refined', 81, 321), ('recoil_refined', 161, 161), ('fine', 161, 321), ('energy_641', 81, 641), ('fine_641', 161, 641)]
    cases = [case for case in cases if args.case in ('all', case[0])]
    pending = [case for case in cases if not (OUTPUT / (case[0] + '.json')).exists()]
    if not pending:
        print('All selected cases already exist. Use validate_results.py for verification.', flush=True)
        return
    print('Direct Slow cases ' + repr(pending), flush=True)
    with ProcessPoolExecutor(max_workers=3) as executor:
        jobs = {executor.submit(calculate_case, case): case for case in pending}
        for job in as_completed(jobs):
            print(json.dumps(job.result()), flush=True)
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
