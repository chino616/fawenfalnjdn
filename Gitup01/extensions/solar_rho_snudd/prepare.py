"""Record the inspected fixed installation and explicit source choices.

Writes this extension's card only; original project data and physics stay read-only.
Run --write after export_rho --inspect; default --check verifies deterministic input.
"""
from pathlib import Path
import argparse
import subprocess
import numpy as np
from .protocol import ROOT, PIN, CARD, read, save, sha

EVIDENCE = ROOT / 'outputs/external/solar_rho_snudd/20261112_run1/source_evidence'


def expected_card():
    install = read(EVIDENCE / 'INSTALLATION.json')
    old = read(ROOT / 'data/benchmarks/solar_b8_nsi_2601_19883/nsi.input.json')
    osc = dict(install['upstream_default_oscillation'])
    osc.update(theta_12=old['oscillation']['theta12_rad'], theta_13=old['oscillation']['theta13_rad'],
               delta_m12=old['oscillation']['dm21_eV2']*1e-18)
    url = 'https://github.com/SNuDD/SNuDD/blob/' + PIN + '/'
    raw = ROOT / '.externals/SNuDD/snudd/data/flux_distributions/8B_dist.txt'
    values = np.loadtxt(raw)
    return {'schema': 'external_snudd_source/1', 'version': '3.4', 'date': '2026-11-12', 'commit': PIN,
        'scope': 'real ee-only uV/dV, solar day-only effective two-flavor propagation; other project physics unchanged',
        'versions': install['versions'], 'upstream_files': install['upstream_files'],
        'producer_files': {p: sha(ROOT / p) for p in ['extensions/solar_rho_snudd/export_rho.py', 'extensions/solar_rho_snudd/protocol.py']},
        'oscillation_actual_GeV_rad': osc, 'oscillation_upstream_default_GeV_rad': install['upstream_default_oscillation'],
        'oscillation_choices': {'theta12_theta13_dm21': 'match v3.3 PEANUTS-selected project input exactly',
             'theta23_delta_dm31': 'explicit SNuDD pinned defaults; mu/tau distribution unobservable for current ee-only diagonal scattering; dm31 used only in validity diagnostic'},
        'baseline_card': 'data/benchmarks/solar_b8_nsi_2601_19883/nsi.input.json',
        'baseline_card_sha256': sha(ROOT / 'data/benchmarks/solar_b8_nsi_2601_19883/nsi.input.json'),
        'density_coefficients': install['density_coefficients'], 'radial_integration': install['radial_integration'],
        'production_file': {'path': str(raw.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha(raw), 'shape': list(values.shape),
                            'ranges': [values.min(axis=0).tolist(), values.max(axis=0).tolist()], 'first_row': values[0].tolist(), 'last_row': values[-1].tolist()},
        'normalization': {'rho_unit': '1', 'rho_trace': 1, 'flux_stays_cm2_s': 5460000.,
                          'spectrum': 'read-only Bahcall829 rows from project singlebin; no SNuDD spectrum/targets/detector/rate called'},
        'verification': {'direct_software': 'pinned checkout and every tracked package-file hash verified',
                         'paper_to_software': 'source comments/headers identify upstream papers; formulas and raw array verified as software inputs, no independent paper digitization certification',
                         'adiabaticity': 'independent ee-only finite-difference diagnostic; physical validity beyond two-flavor model not certified',
                         'upstream_gamma_check': 'not called: gamma_min returns(value,label), gamma_check compares tuple with scalar in this pin'},
        'references': {
            'software': {'citation': 'AMARAL D W P, CERDEÑO D, CHEEK A, COSTA V, FOLDENAUER P. SNuDD: Solar Neutrinos for Direct Detection[EB/OL]. arXiv:2607.22817v1, 2026.',
                         'url': 'https://arxiv.org/abs/2607.22817v1', 'direct_url': url + 'snudd/nsi/nsi_probabilities.py',
                         'locator': 'SolarDensityMatrixCalculator.density_mass/density; ProbabilityCalculator._cos_matter_average; direct adopted software, effective two-flavor and mass-decohered flavor reconstruction'},
            'nsi_mapping': {'citation': 'SNuDD Collaboration. GeneralNSI model source[CP/OL]. Fixed Git commit '+PIN+', accessed2026-11-12.',
                            'url': url+'snudd/models.py', 'locator': 'GeneralNSI.xi_p/xi_n/xi_u/xi_d/xi_e; model eps_matrix multiplies each xi, phi=0'},
            'density': {'citation': 'BAHCALL J N, SERENELLI A M, BASU S. 10,000 Standard Solar Models: a Monte Carlo Simulation[J]. Astrophysical Journal Supplement, 2006,165:400-431. DOI:10.1086/504043. arXiv:astro-ph/0511337.',
                        'url': 'https://arxiv.org/abs/astro-ph/0511337', 'direct_url': url+'snudd/nsi/solar_profiles.py',
                        'locator': 'log10_electron_density, log10_neutron_electron_density; e1..e5,n1,n2; adopted software fits, not B16 arrays'},
            'production': {'citation': 'LOPES I, TURCK-CHIÈZE S. Solar neutrino physics oscillations: Sensitivity to the electronic density in the Sun\u2019s core[J]. Astrophysical Journal,2013,765:14. DOI:10.1088/0004-637X/765/1/14. arXiv:1302.2791.',
                           'url': 'https://arxiv.org/abs/1302.2791v1', 'direct_url': url+'snudd/data/flux_distributions/8B_dist.txt',
                           'locator': 'raw two-column file header identifies1302.2791; flux_dists.interpolate_dist linear, outside0; native distribution normalized in dr over0-.35 by propagation code'},
            'remaining_oscillation': {'citation': 'ESTEBAN I, GONZALEZ-GARCIA M C, MALTONI M, et al. NuFit-6.0: Updated global analysis of three-flavor neutrino oscillations[J]. JHEP,2024,12:216. DOI:10.1007/JHEP12(2024)216. arXiv:2410.05380.',
                                     'url': 'https://arxiv.org/abs/2410.05380', 'direct_url': url+'snudd/nsi/oscillation.py',
                                     'locator': 'osc_params_best; explicit theta23=43.3deg,delta=212deg,dm31=2.513e-3eV² retained; theta12/13/dm21 overridden from v3.3 project card'},
        }}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    expected = expected_card()
    if args.write:
        save(CARD, expected)
        freeze = subprocess.check_output([str(ROOT / '.venvs/snudd/Scripts/python.exe'), '-m', 'pip', 'freeze', '--all'], text=True)
        (CARD.parent / 'requirements.lock.txt').write_text(freeze, encoding='utf8')
    elif read(CARD) != expected:
        raise ValueError('extension source card is stale')
    print('PASS: pinned external source card ' + ('recorded' if args.write else 'checked'))


if __name__ == '__main__':
    main()
