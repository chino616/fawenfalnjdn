"""Versioned, content-bound rho packets shared across two Python processes."""
from pathlib import Path
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PIN = '11622ded104994959a649d85e263c2d9f933ea74'
SCHEMA = 'solar_rho_snudd/1'
CARD = ROOT / 'extensions/solar_rho_snudd/snudd.input.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf8')


def energy_grid(energy):
    a = np.asarray(energy, dtype='<f8')
    if a.ndim != 1 or not len(a) or not np.all(np.isfinite(a)) or np.any(a <= 0) or np.any(np.diff(a) <= 0):
        raise ValueError('strictly increasing positive finite E_MeV required')
    return a


def identity(energy, u, d, card_sha):
    a = energy_grid(energy)
    if not np.all(np.isfinite([u, d])):
        raise ValueError('finite real ee-uV/dV required')
    return {'schema': SCHEMA, 'card_sha256': card_sha, 'energy_sha256': hashlib.sha256(a.tobytes()).hexdigest(),
            'energy_shape': list(a.shape), 'epsilon_hex': [float(u or 0.).hex(), float(d or 0.).hex()],
            'source': '8B', 'particle': 'nu', 'basis': ['e', 'mu', 'tau'], 'mode': 'solar_day_only'}


def packet_key(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate_rho(energy, rho):
    a = energy_grid(energy)
    rho = np.asarray(rho, dtype='<c16')
    if rho.shape != (len(a), 3, 3) or not np.all(np.isfinite(rho)):
        raise ValueError('finite rho_flavour[N_E,3,3] required')
    hermitian = float(np.max(abs(rho-rho.conj().swapaxes(-1, -2))))
    trace_error = float(np.max(abs(np.trace(rho, axis1=-2, axis2=-1)-1)))
    if hermitian > 1e-10 or trace_error > 1e-10:
        raise ValueError('rho violates Hermitian/trace-one contract; no repair allowed')
    eigmin = float(np.linalg.eigvalsh(rho).min())
    pee = rho[:, 0, 0].real
    if eigmin < -1e-10 or np.any(pee < -1e-10) or np.any(pee > 1+1e-10):
        raise ValueError('rho is not PSD/probabilistic; no clipping allowed')
    return rho, {'hermitian_max': hermitian, 'trace_error_max': trace_error, 'minimum_eigenvalue': eigmin,
                 'pee_range': [float(pee.min()), float(pee.max())], 'unit': '1'}


def load_packet(directory, expected):
    directory = Path(directory)
    manifest = read(directory / 'manifest.json')
    if manifest['input_identity'] != expected or manifest['software_commit'] != PIN:
        raise ValueError('wrong NSI/energy/physics/software rho packet')
    if sha(directory / 'rho.npz') != manifest['rho_npz_sha256']:
        raise ValueError('corrupt rho packet content')
    with np.load(directory / 'rho.npz', allow_pickle=False) as a:
        energy, rho, pee = a['E_MeV'].copy(), a['rho_flavour'].copy(), a['pee'].copy()
    rho, _ = validate_rho(energy, rho)
    if hashlib.sha256(energy.astype('<f8').tobytes()).hexdigest() != expected['energy_sha256'] or list(energy.shape) != expected['energy_shape']:
        raise ValueError('rho packet energy coordinates changed')
    if not np.array_equal(pee, rho[:, 0, 0].real):
        raise ValueError('pee must equal the full stored rho_ee')
    return energy, rho, manifest
