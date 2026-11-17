"""Host-side state provider: file protocol only, no import of SNuDD.

Energy lookup is exact. A packet may supply any strictly matching subset; no
interpolation, extrapolation, projection repair or assumption of fixed SM rho.
Full raw rho stays in packets; only the ee-equivalent projection enters v3.3.
"""
from dataclasses import dataclass, field
from pathlib import Path
from collections import OrderedDict
import subprocess
import tempfile
import numpy as np
from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.sources.solar_msw import SolarDiagonalState
from .protocol import ROOT, CARD, read, save, sha, identity, packet_key, energy_grid, load_packet


@dataclass(frozen=True)
class ExternalSolarState:
    cache_root: Path
    card_sha256: str
    propagation: str = 'snudd_day_twoflavor'
    _packets: list = field(default_factory=list, init=False, repr=False, compare=False)
    _loaded: object = field(default_factory=OrderedDict, init=False, repr=False, compare=False)

    @property
    def probability_bounds(self):
        osc = read(CARD)['oscillation_actual_GeV_rad']
        s12, s13 = np.sin(osc['theta_12'])**2, np.sin(osc['theta_13'])**2
        return s13**2+(1-s13)**2*min(s12, 1-s12), s13**2+(1-s13)**2*max(s12, 1-s12)

    def verify(self):
        if sha(CARD) != self.card_sha256:
            raise ValueError('external input card changed; reload definition')
        for name, h in read(CARD)['producer_files'].items():
            if sha(ROOT / name) != h:
                raise ValueError('external rho producer changed: '+name)

    def _find_subset(self, energy, u, d):
        tag = (float(u or 0.).hex(), float(d or 0.).hex())
        for oldtag, directory in self._packets:
            if oldtag != tag:
                continue
            if not (directory / 'manifest.json').exists():
                continue
            stamp = tuple((directory / n).stat().st_mtime_ns for n in ['manifest.json', 'rho.npz'])
            cached = self._loaded.get(directory)
            if cached is not None and cached[0] == stamp:
                _, oldenergy, rho, manifest = cached
            else:
                manifest = read(directory / 'manifest.json')
                oldenergy, rho, _ = load_packet(directory, manifest['input_identity'])
                self._loaded[directory] = (stamp, oldenergy, rho, manifest)
                if len(self._loaded) > 32:
                    self._loaded.popitem(last=False)
            if manifest['input_identity']['card_sha256'] != self.card_sha256:
                raise ValueError('stale source packet')
            ix = np.searchsorted(oldenergy, energy)
            if np.all(ix < len(oldenergy)) and np.array_equal(oldenergy[ix], energy):
                return rho[ix]
        return None

    def prefetch(self, energy, points):
        self.verify()
        energy = energy_grid(energy)
        cache = Path(self.cache_root).resolve()
        if not cache.is_relative_to(ROOT / 'outputs/external/solar_rho_snudd'):
            raise ValueError('use the independent external cache root')
        missing = []
        for u, d in points:
            if self._find_subset(energy, u, d) is not None:
                continue
            wanted = identity(energy, u, d, self.card_sha256)
            destination = cache / packet_key(wanted)
            if not (destination / 'manifest.json').exists():
                missing.append({'epsilon': [float(u), float(d)], 'input_identity': wanted, 'destination': str(destination)})
            elif load_packet(destination, wanted):
                pass
            tag = (float(u or 0.).hex(), float(d or 0.).hex())
            if (tag, destination) not in self._packets:
                self._packets.append((tag, destination))
        if missing:
            cache.mkdir(parents=True, exist_ok=True)
            # One isolated process per missing batch, never per recoil integration.
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', dir=cache, delete=False, encoding='utf8') as temp:
                request = Path(temp.name)
            save(request, {'E_MeV': energy.tolist(), 'points': missing})
            try:
                result = subprocess.run([str(ROOT / '.venvs/snudd/Scripts/python.exe'), '-B', '-m',
                    'extensions.solar_rho_snudd.export_rho', '--request', str(request)], cwd=ROOT, capture_output=True, text=True, timeout=60)
                if result.returncode:
                    raise RuntimeError('isolated SNuDD export failed: '+result.stdout+result.stderr)
            finally:
                request.unlink(missing_ok=True)
            for item in missing:
                load_packet(item['destination'], item['input_identity'])

    def full_rho(self, energy, u, d):
        self.verify()
        energy = energy_grid(energy)
        rho = self._find_subset(energy, u, d)
        if rho is None:
            self.prefetch(energy, [(u, d)])
            rho = self._find_subset(energy, u, d)
        if rho is None:
            raise RuntimeError('external source did not supply exact coordinates')
        return rho

    def pee(self, energy, eu=0., ed=0., *, radial_order=None):
        if radial_order is not None:
            raise ValueError('SNuDD radial integration is fixed upstream; radial_order is not consumed')
        u, d = np.broadcast_arrays(np.asarray(eu, float), np.asarray(ed, float))
        if not np.all(np.isfinite(u)) or not np.all(np.isfinite(d)):
            raise ValueError('finite real NSI required')
        self.prefetch(energy, zip(u.ravel(), d.ravel()))
        values = [self.full_rho(energy, a, b)[:, 0, 0].real for a, b in zip(u.ravel(), d.ravel())]
        return np.asarray(values).reshape((*u.shape, len(energy)))

    def __call__(self, energy_MeV, *, parameters):
        if set(parameters.values) != {'epsilon_ee_uV', 'epsilon_ee_dV'}:
            raise ValueError('bind the same ee-only source/scattering parameters')
        p = self.pee(energy_MeV, parameters.values['epsilon_ee_uV'], parameters.values['epsilon_ee_dV'])
        rho = np.zeros((len(p), 3, 3))
        rho[:, 0, 0], rho[:, 1, 1], rho[:, 2, 2] = p, (1-p)/2, (1-p)/2
        return SolarDiagonalState(energy_MeV, rho, 'nu', 'snudd_ee_scattering_equivalent_projection',
                                  ('epsilon_ee_uV', 'epsilon_ee_dV'))

    def describe(self):
        self.verify()
        card = read(CARD)
        return ModuleDescriptor('state', 'external_snudd_day_ee_only', model_revision='3.4',
            capabilities=('energy_dependent', 'parameter_dependent_ee_only'),
            parameters={'propagation': self.propagation, 'commit': card['commit'], 'oscillation': card['oscillation_actual_GeV_rad'],
                        'solar_profiles': 'SNuDD own analytic densities and96-row8B distribution, not B16',
                        'projection': 'full rho retained; diag(Pee,(1-Pee)/2,(1-Pee)/2) is rate-equivalent only for declared diagonal ee-only K'},
            resources={'input_card_sha256': self.card_sha256})
