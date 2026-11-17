"""Solar ee-vector NSI propagation, 2409.04703v2 Appendix B Eqs.(B4)-(B9).

Owns flavor state only; no cross section, detector, nuclei or exposure here.
Profile columns and oscillation numbers are explicit numerical inputs with
provenance in the separate solar-NSI card. The chosen two-flavor adiabatic model
keeps theta13_m=theta13 and neglects Earth regeneration, as that appendix does.
"""
from dataclasses import dataclass
import hashlib
import numpy as np
from cevns_pyeft.contracts import IncidentStateBatch
from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.foundation.constants import G_F, HBARC_GEV_FM
from cevns_pyeft.contracts.validation import coordinates,readonly


@dataclass(frozen=True)
class SolarDiagonalState(IncidentStateBatch):
    """Same state contract, vectorial validation specialized to diagonal rho.

    For diagonal matrices nonnegative diagonal entries are exactly the PSD
    condition. Every energy still gets finite/Hermitian/trace/PSD checks, without
    millions of Python calls into the general eigensystem validator.
    """
    def __post_init__(self):
        energy=coordinates(self.energy_MeV,'state energy')
        rho=readonly(self.rho,dtype=complex)
        if self.particle_kind!='nu' or np.any(energy<=0) or rho.shape!=(len(energy),3,3):
            raise ValueError('solar diagonal state requires positive nu energies and matching Nx3x3 rho')
        diagonal=np.diagonal(rho,axis1=-2,axis2=-1)
        diagonal_only=np.zeros_like(rho);diagonal_only[:,np.arange(3),np.arange(3)]=diagonal
        if np.any(abs(rho-diagonal_only)>1e-10) or np.any(abs(diagonal.imag)>1e-10):
            raise ValueError('solar state must be diagonal Hermitian')
        if np.any(diagonal.real < -1e-10) or not np.allclose(diagonal.real.sum(axis=-1),1.,atol=1e-10,rtol=0):
            raise ValueError('solar density is not PSD/trace one')
        object.__setattr__(self,'energy_MeV',energy);object.__setattr__(self,'rho',rho)
        object.__setattr__(self,'parameter_dependencies',tuple(self.parameter_dependencies))


@dataclass(frozen=True)
class SolarMSW:
    profile: np.ndarray
    theta12: float
    theta13: float
    dm21: float
    propagation: str='nsi_msw'
    radial_order: int=8

    def __post_init__(self):
        p=np.asarray(self.profile,float)
        if p.ndim!=2 or p.shape[1]!=4 or np.any(np.diff(p[:,0])<=0) or not np.all(np.isfinite(p)) or np.any(p[:,1:]<0):
            raise ValueError('expected increasing r, nonnegative ne,nn,production profile')
        if self.propagation not in ('nsi_msw','sm_fixed'):raise ValueError('select explicit propagation model')
        if not 0<self.theta12<np.pi/2 or not 0<self.theta13<np.pi/2 or not self.dm21>0:
            raise ValueError('finite physical mixing angles and positive dm21 required')
        if not isinstance(self.radial_order,int) or self.radial_order<2:raise ValueError('radial order>=2')
        p=p.copy();p.setflags(write=False);object.__setattr__(self,'profile',p)

    @property
    def probability_bounds(self):
        s12=np.sin(self.theta12)**2;c13=np.cos(self.theta13)**2;s13=np.sin(self.theta13)**2
        return s13*s13+c13*c13*min(s12,1-s12),s13*s13+c13*c13*max(s12,1-s12)

    def radial_quadrature(self):
        p=self.profile;edges=np.r_[p[0,0],[r for r in [.02,.05,.1,.2,.4] if p[0,0]<r<p[-1,0]],p[-1,0]]
        x,w=np.polynomial.legendre.leggauss(self.radial_order)
        r=np.concatenate([.5*(b+a)+.5*(b-a)*x for a,b in zip(edges[:-1],edges[1:])])
        weight=np.concatenate([.5*(b-a)*w for a,b in zip(edges[:-1],edges[1:])])
        ne,nn,production=[np.interp(r,p[:,0],p[:,i]) for i in [1,2,3]]
        weight*=production;weight/=weight.sum()
        return r,ne,nn,weight

    def pee(self,energy_MeV,eu=0.,ed=0.,*,radial_order=None):
        energy=np.asarray(energy_MeV,float);eu,ed=np.broadcast_arrays(np.asarray(eu,float),np.asarray(ed,float))
        if energy.ndim!=1 or not np.all(np.isfinite(energy)) or np.any(energy<0) or not np.all(np.isfinite(eu)) or not np.all(np.isfinite(ed)):
            raise ValueError('finite nonnegative 1D energy and real NSI parameters required')
        if radial_order is not None:
            from dataclasses import replace
            return replace(self,radial_order=radial_order).pee(energy,eu,ed)
        _,ne,nn,weight=self.radial_quadrature()
        if self.propagation=='sm_fixed':eu=np.zeros_like(eu);ed=np.zeros_like(ed)
        # sqrt2 Gf * density: mol/cm³ -> cm^-3 -> eV³; Gf GeV^-2 -> eV^-2.
        hbarc_eV_cm=HBARC_GEV_FM*1e-4
        factor=np.sqrt(2)*G_F*1e-18*6.02214076e23*hbarc_eV_cm**3
        potential=factor*(ne+eu[...,None]*(2*ne+nn)+ed[...,None]*(ne+2*nn))
        c13=np.cos(self.theta13)**2;s13=np.sin(self.theta13)**2
        A=2*energy.reshape((1,)*eu.ndim+(-1,1))*1e6*c13*potential[...,None,:]
        diagonal=self.dm21*np.cos(2*self.theta12)-A
        offdiag=self.dm21*np.sin(2*self.theta12)
        cos2m=diagonal/np.hypot(diagonal,offdiag)
        average=np.sum(cos2m*weight,axis=-1)
        return .5*c13*c13*(1+np.cos(2*self.theta12)*average)+s13*s13

    def __call__(self,energy_MeV,*,parameters):
        keys={'epsilon_ee_uV','epsilon_ee_dV'}
        if set(parameters.values)-keys:raise ValueError('unknown solar state parameter')
        eu=parameters.values.get('epsilon_ee_uV',0.);ed=parameters.values.get('epsilon_ee_dV',0.)
        p=self.pee(energy_MeV,eu,ed)
        if p.ndim!=1:raise ValueError('state_at requires one parameter point')
        rho=np.zeros((len(p),3,3));rho[:,0,0]=p;rho[:,1,1]=rho[:,2,2]=(1-p)/2
        return SolarDiagonalState(energy_MeV,rho,'nu','physical_Pee__mu_tau_equivalent',
            ('epsilon_ee_uV','epsilon_ee_dV') if self.propagation=='nsi_msw' else ())

    def describe(self):
        return ModuleDescriptor('state','solar_ee_vector_msw',capabilities=('energy_dependent','parameter_dependent_ee_only'),
            parameters={'theta12_rad':self.theta12,'theta13_rad':self.theta13,'dm21_eV2':self.dm21,
                'propagation':self.propagation,'radial_order_per_panel':self.radial_order,
                'equations':'2409.04703v2 p10 B4-B9; theta13_m=vacuum, no Earth matter',
                'mu_tau_split':'equivalent only in this ee-vector subspace; not a prediction of separate Pmu/Ptau',
                'Pee_bounds':self.probability_bounds},
            resources={'profile_array_sha256':hashlib.sha256(self.profile.tobytes()).hexdigest()})
