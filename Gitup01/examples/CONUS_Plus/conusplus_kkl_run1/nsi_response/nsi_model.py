"""NSI adapter over the verified SM experiment and existing project APIs."""
from pathlib import Path as _LayoutPath
import sys as _layout_sys
_layout_sys.path.insert(0, str(_LayoutPath(__file__).resolve().parents[1]))
from conusplus_paths import Layout
LAYOUT = Layout('nsi')
from dataclasses import dataclass, replace
from pathlib import Path
import sys
import numpy as np
import sm_model as sm
from cevns_pyeft.contracts.parameters import TheoryPoint
from cevns_pyeft.sources.state import NeutrinoState
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson
HERE = Path(__file__).resolve().parent
BASIS = ((6, 1, 'u'), (6, 1, 'd'), (6, 2, 'u'), (6, 2, 'd'))
COUPLINGS = ('epsilon_ee_uV', 'epsilon_ee_dV', 'epsilon_emu_uV', 'epsilon_emu_dV', 'epsilon_etau_uV', 'epsilon_etau_dV')

@dataclass(frozen=True)
class ReactorFixedState:
    """Expose the existing constant reactor state to the interface compiler."""

    def __call__(self, energy_MeV, *, parameters):
        return sm.reactor_state(energy_MeV, parameters=parameters)

    def fixed_state_for_fast(self):
        return NeutrinoState(particle_kind='antinu', rho=np.diag([1.0, 0.0, 0.0]))

def model():
    baseline = sm.build_model()
    components = tuple((replace(component, state_provider=ReactorFixedState()) for component in baseline.source.components_per_second))
    return replace(baseline, source=replace(baseline.source, components_per_second=components), model_id='conusplus_vector_nsi_response_candidate_v1')

def point(**couplings):
    unknown = set(couplings) - set(COUPLINGS)
    if unknown:
        raise ValueError('Unsupported NSI coordinate(s): ' + repr(sorted(unknown)))
    if any((not np.isfinite(value) for value in couplings.values())):
        raise ValueError('NSI coordinates must be finite')
    for name in ('epsilon_ee_uV', 'epsilon_ee_dV'):
        if name in couplings and abs(np.imag(couplings[name])) > 0:
            raise ValueError('Diagonal Hermitian NSI coordinates must be real')
    coefficients = vector_nsi_to_np_wilson(VectorNSIParameters(**couplings))
    return TheoryPoint(wc_triplets=coefficients, include_sm=True, sin2thetaW=sm.POINT.sin2thetaW)

def verify_snapshot():
    return LAYOUT.verify_inputs()
