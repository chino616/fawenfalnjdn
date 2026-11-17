"""Isolated export of the exact source arrays used by the pinned SNuDD model.

The full scan consumes numbers only. No change to the upstream radial grid,
production interpolation, normalization, model, or oscillation parameters.
"""
from pathlib import Path
import argparse
import numpy as np
from .protocol import ROOT, CARD, PIN, read, save, sha
from .export_rho import imports


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / 'outputs/external/solar_rho_snudd'):
        raise ValueError('independent external output root required')
    if (out / 'manifest.json').exists():
        raise FileExistsError('source export is create-only')
    out.mkdir(parents=True, exist_ok=True)
    card = read(CARD)
    config, _, osc, profiles, flux_dists, _ = imports()
    for name, h in card['upstream_files'].items():
        if sha(ROOT / '.externals/SNuDD' / name) != h:
            raise ValueError('pinned source changed: '+name)
    params = osc.OscillationParameters(**card['oscillation_actual_GeV_rad'])
    x = np.linspace(0., .35, 1000)  # exact upstream _cos_matter_average grid
    distribution = flux_dists.dist_dict['8B'](x)
    norm = config.trapezoid(distribution, x)
    weights = np.zeros_like(x)
    weights[:-1] += np.diff(x)/2
    weights[1:] += np.diff(x)/2
    weights *= distribution/norm
    potential = np.sqrt(2)*config.G_F*profiles.electron_density(x)
    # q=cos2theta12 - E_MeV*alpha*(1+epsilon_p+Y*epsilon_n).
    alpha = 2e-3*params.c13**2*potential/params.delta_m12
    np.savez_compressed(out / 'source.npz', r_Rsun=x, radial_weights=weights,
        alpha_per_MeV=alpha, neutron_electron_ratio=profiles.neutron_electron_fraction(x),
        cos2theta12=np.array(params.c12_2), sin2theta12=np.array(params.s12_2),
        c13_squared=np.array(params.c13**2), s13_squared=np.array(params.s13**2), U_PMNS=osc.UPMNS(params))
    save(out / 'manifest.json', {'schema': 'snudd_ee_exact_source_arrays/1', 'software_commit': PIN,
        'input_card_sha256': sha(CARD), 'source_npz_sha256': sha(out / 'source.npz'),
        'upstream_files': card['upstream_files'], 'producer_sha256': sha(Path(__file__)),
        'representation': 'exact ee-only algebraic specialization; same1000 nodes, linear production, trapezoid normalized in dr',
        'radial_nodes': len(x), 'strictly_nonzero_weight_nodes': int(np.count_nonzero(weights)),
        'radial_weight_sum': float(weights.sum()), 'oscillation_actual_GeV_rad': vars(params),
        'full_rho_reconstruction': 'U diag(c13²*(1+average_cos2m)/2,c13²*(1-average_cos2m)/2,s13²) Udagger',
        'flavor_order': ['e', 'mu', 'tau'], 'no_energy_or_parameter_interpolation': True})
    print('Exported exact SNuDD source arrays:', out)


if __name__ == '__main__':
    main()
