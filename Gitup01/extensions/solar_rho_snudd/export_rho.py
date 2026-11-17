"""Only this module imports SNuDD, only inside its isolated interpreter.

Source onboarding: GeneralNSI model mapping; SolarDensityMatrixCalculator for
day-only propagation; explicit OscillationParameters; original full rho retained.
No CEvNS-pyEFT imports, target, cross section, detector, flux magnitude or events.
"""
from pathlib import Path
import argparse
import importlib.metadata as metadata
import platform
import subprocess
import numpy as np
from .protocol import ROOT, PIN, CARD, read, save, sha, identity, validate_rho


def model_parameters(u, d):
    # GeneralNSI.eps_matrix * xi_p/n reproduces proton/neutron coefficients.
    if not np.all(np.isfinite([u, d])):
        raise ValueError('finite real epsilon required')
    p, n = 2*u+d, u+2*d
    scale = float(np.hypot(p, n)/np.sqrt(5))
    return np.diag([scale, 0., 0.]), float(np.arctan2(n, p)) if scale else 0., 0.


def imports():
    import snudd
    from snudd import config
    from snudd.models import GeneralNSI
    from snudd.nsi import oscillation as osc, solar_profiles as profiles, flux_dists
    from snudd.nsi.nsi_probabilities import SolarDensityMatrixCalculator
    package = Path(snudd.__file__).resolve().parent
    expected = ROOT / '.externals/SNuDD/snudd'
    if package != expected:
        raise ValueError('worker must import the pinned independent SNuDD checkout')
    return config, GeneralNSI, osc, profiles, flux_dists, SolarDensityMatrixCalculator


def inspect_install(destination):
    config, _, osc, profiles, flux_dists, _ = imports()
    destination.mkdir(parents=True, exist_ok=True)
    commit = subprocess.check_output(['git', '-C', str(ROOT / '.externals/SNuDD'), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != PIN:
        raise ValueError('unreviewed SNuDD version')
    x = np.linspace(0., .35, 1000)
    ne = 10**profiles.log10_electron_density(x)
    nn = ne*profiles.neutron_electron_fraction(x)
    distribution = flux_dists.dist_dict['8B'](x)
    np.savetxt(destination / 'snudd_profile_diagnostic.txt', np.column_stack([x, ne, nn, distribution]), fmt='%.16g',
               header='r_Rsun ne_mol_cm3 nn_mol_cm3 B8_raw_dr_profile\nDirect SNuDD fitted densities and distribution; diagnostic, not the B16 input.')
    files = subprocess.check_output(['git', '-C', str(ROOT / '.externals/SNuDD'), 'ls-files'], text=True).splitlines()
    original = {p: sha(ROOT / '.externals/SNuDD' / p) for p in files if p.startswith('snudd/') or p in ['LICENSE', 'README.md', 'pyproject.toml']}
    result = {'commit': commit, 'python': platform.python_version(), 'package_root': str(ROOT / '.externals/SNuDD/snudd'),
              'versions': {name: metadata.version(name) for name in ['snudd', 'numpy', 'scipy', 'pandas', 'packaging']},
              'upstream_files': original, 'upstream_default_oscillation': vars(osc.osc_params_best),
              'density_coefficients': {k: getattr(profiles, k) for k in ['e1', 'e2', 'e3', 'e4', 'e5', 'n1', 'n2']},
              'radial_integration': {'lo': 0., 'hi': .35, 'nodes': 1000, 'rule': 'trapezoid in dr, normalized original production profile'},
              'profile_diagnostic_sha256': sha(destination / 'snudd_profile_diagnostic.txt'),
              'constants': {'G_F_GeV_minus2': config.G_F, 'fm_conv': config.fm_conv, 'R_SUN_m': profiles.R_SUN},
              'imported_main_project': False}
    save(destination / 'INSTALLATION.json', result)


def adiabatic_diagnostic(energy, u, d, params, config, profiles):
    # Independent ee-only two-level test. Do not call upstream gamma_check:
    # this pinned release compares gamma_min's (value,label) tuple to a scalar.
    # Finite-difference dtheta_m/dr covers the full solar path and input E grid.
    x = np.linspace(0., 1., 4001)
    ne = profiles.electron_density(x)
    veff = np.sqrt(2)*config.G_F*ne*(1+(2*u+d)+profiles.neutron_electron_fraction(x)*(u+2*d))
    a = np.cos(params.theta_13)**2*veff
    da = np.gradient(a, x)/(profiles.R_SUN*profiles.M2PERGEV)
    delta = params.delta_m12/(2*(energy*1e-3))[:, None]
    diagonal = delta*np.cos(2*params.theta_12)-a
    offdiag = delta*np.sin(2*params.theta_12)
    splitting = np.hypot(diagonal, offdiag)
    derivative = offdiag*da/(2*splitting**2)
    with np.errstate(divide='ignore', invalid='ignore'):
        gamma = splitting/(2*abs(derivative))
    minimum = float(np.nanmin(gamma))
    ratio = float(np.max(2*(energy*1e-3)[:, None]*abs(veff)/abs(params.delta_m31)))
    return {'method': 'ee-only two-level splitting/(2|dtheta_m/dr|), independent finite difference',
            'r_nodes': len(x), 'r_domain': [0., 1.], 'minimum_gamma': minimum if np.isfinite(minimum) else None,
            'gamma_ge_100': bool(minimum >= 100), 'max_abs_2EV_over_dm31': ratio,
            'meaning': 'adiabatic diagnostic only; two-flavor reduction / large-NSI validity not certified'}


def export(request):
    config, GeneralNSI, osc, _, _, Calculator = imports()
    card = read(CARD)
    for p, h in card['upstream_files'].items():
        if sha(ROOT / '.externals/SNuDD' / p) != h:
            raise ValueError('pinned upstream content changed: '+p)
    versions = {k: metadata.version(k) for k in card['versions']}
    if versions != card['versions']:
        raise ValueError('isolated dependency versions changed')
    params = osc.OscillationParameters(**card['oscillation_actual_GeV_rad'])
    energy = np.asarray(request['E_MeV'], float)
    for item in request['points']:
        u, d = item['epsilon']
        wanted = identity(energy, u, d, sha(CARD))
        if wanted != item['input_identity']:
            raise ValueError('request identity does not match parameters/grid/card')
        matrix, eta, phi = model_parameters(u, d)
        model = GeneralNSI(matrix, eta, phi)
        # Day-only: this class never constructs/calls an Earth propagator.
        rho = np.asarray(Calculator(model, osc_params=params, adiabatic_check=False).density(energy*1e-3, '8B'))
        rho, checks = validate_rho(energy, rho)
        destination = Path(item['destination']).resolve()
        if not destination.is_relative_to(ROOT / 'outputs/external/solar_rho_snudd'):
            raise ValueError('rho output must stay inside the explicit external output root')
        destination.mkdir(parents=True, exist_ok=True)
        if (destination / 'manifest.json').exists():
            raise FileExistsError('do not overwrite an existing rho packet')
        np.savez_compressed(destination / 'rho.npz', E_MeV=energy, rho_flavour=rho, pee=rho[:, 0, 0].real)
        save(destination / 'manifest.json', {'input_identity': wanted, 'software_commit': PIN, 'worker': 'isolated SNuDD process',
             'versions': versions, 'rho_npz_sha256': sha(destination / 'rho.npz'), 'rho_shape': list(rho.shape),
             'physical_checks': checks, 'model': {'epsilon_ee_uV': u, 'epsilon_ee_dV': d, 'eta': eta, 'phi': phi,
             'eps_matrix': matrix.tolist()}, 'oscillation_actual_GeV_rad': vars(params),
             'adiabatic_diagnostic': adiabatic_diagnostic(energy, u, d, params, config, imports()[3])})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inspect', type=Path)
    p.add_argument('--request', type=Path)
    args = p.parse_args()
    if bool(args.inspect) == bool(args.request):
        p.error('choose exactly one --inspect or --request')
    if args.inspect:
        inspect_install(args.inspect)
    else:
        export(read(args.request))


if __name__ == '__main__':
    main()
