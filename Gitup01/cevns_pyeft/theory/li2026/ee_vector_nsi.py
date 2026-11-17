"""Real electron-flavor vector NSI, paper2601 Eq.(95), shared nuclear amplitude.

Only the coefficient contraction/vectorization is new. Nuclear W, LEFT matching,
particle R, normalization and units are all delegated to the existing adapter.
The other two flavors have identical SM cross sections in this declared subspace.
"""
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
import numpy as np
from cevns_pyeft.contracts import TheoryPoint, StateParameters
from cevns_pyeft.contracts.interaction import DifferentialCrossSection, ElasticKinematics
from cevns_pyeft.contracts.modules import ModuleDescriptor, UnsupportedCapabilityError
from cevns_pyeft.foundation.constants import G_F
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson
from .adapter import Li2026LegacyInteraction

BASIS=((6,1,'u'),(6,1,'d'),(6,2,'u'),(6,2,'d'))
MONOMIALS=('1','eu','ed','eu^2','eu*ed','ed^2')


def nsi_point(eu=0., ed=0., *, sin2thetaW=.23857):
    if not np.all(np.isfinite([eu,ed])):raise ValueError('finite real NSI parameters required')
    return TheoryPoint(vector_nsi_to_np_wilson(VectorNSIParameters(epsilon_ee_uV=float(eu),epsilon_ee_dV=float(ed))),
        include_sm=True,sin2thetaW=sin2thetaW,
        state=StateParameters({'epsilon_ee_uV':float(eu),'epsilon_ee_dV':float(ed)}))


def couplings(point):
    if not point.include_sm:raise UnsupportedCapabilityError('declared model is SM + real ee vector NSI')
    allowed={(6,1,'u'),(6,1,'d')};values=[]
    if set(point.wc_triplets)-allowed:raise UnsupportedCapabilityError('only real ee vector u,d NSI supported')
    for key in [(6,1,'u'),(6,1,'d')]:
        matrix=np.asarray(point.wc_triplets.get(key,np.zeros((3,3))),complex)
        if matrix.shape!=(3,3) or not np.all(np.isfinite(matrix)):raise ValueError('finite 3x3 flavor matrix required')
        rest=matrix.copy();rest[0,0]=0
        if np.any(rest!=0) or matrix[0,0].imag!=0:raise UnsupportedCapabilityError('mu/tau, off-diagonal or complex NSI outside declared scope')
        values.append(float(-matrix[0,0].real/(np.sqrt(2)*G_F)))
    return tuple(values)


def monomials(eu,ed):
    eu,ed=np.broadcast_arrays(eu,ed)
    return np.stack([np.ones_like(eu),eu,ed,eu*eu,eu*ed,ed*ed],axis=-1)


@dataclass(frozen=True)
class ElectronVectorNSI:
    responses_json: str | Path
    isotope_keys: tuple
    kinematics: ElasticKinematics=field(default_factory=ElasticKinematics,init=False)
    _legacy: object=field(init=False,repr=False,compare=False)
    _coefficients: object=field(init=False,repr=False,compare=False)

    def __post_init__(self):
        legacy=Li2026LegacyInteraction(self.responses_json,{k:k for k in self.isotope_keys})
        object.__setattr__(self,'_legacy',legacy)
        object.__setattr__(self,'responses_json',legacy.responses_json)
        @lru_cache(maxsize=32768)
        def coefficients(target,recoil,angle):
            emin=self.kinematics.minimum_energy_MeV(target,recoil)*1e-3
            e0=max(.020,1.1*emin);h=e0/2;energy=np.array([e0,e0+h,e0+2*h])*1000
            # Differential coefficients reuse shared left_to_ci and R:W.
            H=legacy.coefficient_dsigma(target=target,energy_MeV=energy,recoil_keV=recoil,basis_keys=BASIS).sum(axis=1).real
            vectors=np.zeros((3,4))
            vectors[0]=legacy.coefficient_values(TheoryPoint(sin2thetaW=angle),BASIS)[:,0,0].real
            vectors[1,0]=vectors[2,1]=-np.sqrt(2)*G_F  # Eq.95, GeV^-2
            H=np.einsum('ai,eij,bj->eab',vectors,H,vectors)
            values=np.stack([H[:,0,0],2*H[:,0,1],2*H[:,0,2],H[:,1,1],2*H[:,1,2],H[:,2,2]],axis=-1)
            values*=((energy*1e-3)**2)[:,None]
            f0,f1,f2=values;q=(f2-2*f1+f0)/2
            coefficient=np.array([f0,f1-f0-q,q]);coefficient.setflags(write=False)
            return e0,h,coefficient
        object.__setattr__(self,'_coefficients',coefficients)

    def validate(self,targets,parameters):
        couplings(parameters);self._legacy.validate(targets,parameters)

    def spectral_coefficients(self,target,energy_MeV,recoil_keV,angle=.23857):
        """dσ_e/dT coefficients [1,eu,ed,eu²,eu ed,ed²], cm²/keV.

        E²*dσ is exactly quadratic for these four dimension-6 vector/axial
        operators. This is algebraic vectorization, not a fitted rate surrogate.
        """
        energy=np.asarray(energy_MeV,float);recoil=float(recoil_keV)
        if energy.ndim!=1 or np.any(energy<=0) or not np.isfinite(recoil) or recoil<0:
            raise ValueError('positive 1D energies and finite nonnegative recoil required')
        e0,h,c=self._coefficients(target,recoil,float(angle));x=(energy*1e-3-e0)/h
        out=(c[0]+x[:,None]*(c[1]+x[:,None]*c[2]))/((energy*1e-3)**2)[:,None]
        out[energy<self.kinematics.minimum_energy_MeV(target,recoil)]=0.
        return out

    def dsigma_dT(self,*,target,energy_MeV,recoil_keV,incident_state,parameters):
        from types import SimpleNamespace
        self.validate(SimpleNamespace(isotopes=(target,)),parameters)
        incident_state.require_coordinates(energy_MeV,'nu');eu,ed=couplings(parameters)
        coefficients=self.spectral_coefficients(target,energy_MeV,recoil_keV,parameters.sin2thetaW)
        # rho_ee is physical Pee; the mu/tau split is unobservable here because
        # both have precisely the same SM cross section. Never replace Pee by1/3.
        correction=coefficients[:,1:]@monomials(eu,ed)[1:]
        values=coefficients[:,0]+incident_state.rho[...,0,0].real*correction
        bound=512*np.finfo(float).eps*(abs(coefficients[:,0])+abs(correction))
        values=np.where(abs(values)<=bound,0.,values)
        if np.any(values<0):raise ValueError('negative NSI cross section beyond floating cancellation')
        return DifferentialCrossSection(energy_MeV,values,float(recoil_keV),'li2026_ee_vector_nsi')

    def describe(self):
        return ModuleDescriptor('interaction','li2026_ee_vector_nsi',capabilities=('slow_elastic','real_ee_vector_nsi'),
            parameters={'basis':BASIS,'monomials':MONOMIALS,'mapping':'C61q_NSI=-sqrt(2)*G_F*epsilon_ee_qV, paper2601 Eq95',
                        'delegated':self._legacy.describe().as_dict(),'extra_KN_or_spin_factor':False,
                        'external_nuclear_author_source_certification':'UNRESOLVED'},
            resources={'path':str(self.responses_json),'sha256':self._legacy._sha256})
