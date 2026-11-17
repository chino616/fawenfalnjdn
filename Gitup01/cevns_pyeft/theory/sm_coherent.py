"""Tree-level SM CEvNS, arXiv:2411.11749v1 Eqs. (1)--(3).

DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions
from the first CEvNS data at direct detection experiments. JCAP 05 (2025) 012,
doi:10.1088/1475-7516/2025/05/012. The actual benchmark is the arXiv v1.
Klein--Nystrand nuclear structure is independent of the EFT polynomial tables.
All numerical constants are explicit package inputs, not mutable module defaults.
"""
from dataclasses import dataclass, field
import numpy as np
from cevns_pyeft.contracts.interaction import ElasticKinematics, DifferentialCrossSection
from cevns_pyeft.contracts.modules import ModuleDescriptor, UnsupportedCapabilityError


def klein_nystrand_squared(recoil_keV, mass_GeV, A, *, radius_fm, skin_fm, hbarc_GeV_fm):
    t=np.asarray(recoil_keV,dtype=float)
    if np.any(~np.isfinite(t)) or np.any(t<0) or min(mass_GeV,A,radius_fm,skin_fm,hbarc_GeV_fm)<=0:
        raise ValueError('invalid Klein-Nystrand input')
    q=np.sqrt(2*mass_GeV*t*1e-6)/hbarc_GeV_fm
    x=q*radius_fm*float(A)**(1/3)
    f=np.empty_like(x)
    small=abs(x)<1e-3
    f[small]=1-x[small]**2/10+x[small]**4/280-x[small]**6/15120
    f[~small]=3*(np.sin(x[~small])-x[~small]*np.cos(x[~small]))/x[~small]**3
    return (f/(1+(q*skin_fm)**2))**2


@dataclass(frozen=True)
class StandardModelKN:
    fermi_GeV_minus2: float
    inverse_GeV2_to_cm2: float
    hbarc_GeV_fm: float
    radius_fm: float
    skin_fm: float
    proton_number: int
    mass_numbers: tuple
    isotope_ids: tuple
    kinematics: ElasticKinematics=field(default_factory=ElasticKinematics)

    def describe(self):
        return ModuleDescriptor('interaction','coherent_sm_kn_v1',capabilities=('slow_1d','flavor_universal_SM'),
            parameters={'G_F':self.fermi_GeV_minus2,'GeV^-2_to_cm2':self.inverse_GeV2_to_cm2,
                        'hbarc_GeV_fm':self.hbarc_GeV_fm,'radius_coefficient_fm':self.radius_fm,'skin_fm':self.skin_fm,
                        'Z':self.proton_number,'A':self.mass_numbers,'isotope_ids':self.isotope_ids,
                        'kinematic_factor':'1-m*T/(2*E^2)-T/E','reference':'2411.11749v1 PDF p3 Eqs.(1)-(3)'})

    def validate(self,targets,parameters):
        if parameters.wc_triplets or parameters.state.values:
            raise UnsupportedCapabilityError('SM benchmark has no BSM or incident-state scan')
        if any(target.isotope_id not in self.isotope_ids for target in targets.isotopes):
            raise ValueError('isotope is absent from this explicit SM target map')

    def dsigma_dT(self,*,target,energy_MeV,recoil_keV,incident_state,parameters):
        energy=np.asarray(energy_MeV,dtype=float)
        incident_state.require_coordinates(energy,'nu')
        if parameters.wc_triplets:raise UnsupportedCapabilityError('pure SM only')
        a=float(self.mass_numbers[self.isotope_ids.index(target.isotope_id)])
        e=energy*1e-3;t=float(recoil_keV)*1e-6;m=target.kinematic_mass_GeV
        qv=.5*((1-4*parameters.sin2thetaW)*self.proton_number-(a-self.proton_number))
        factor=1-m*t/(2*e**2)-t/e
        ff=float(klein_nystrand_squared(recoil_keV,m,a,radius_fm=self.radius_fm,skin_fm=self.skin_fm,hbarc_GeV_fm=self.hbarc_GeV_fm))
        values=self.fermi_GeV_minus2**2*m/np.pi*qv*qv*ff*np.maximum(factor,0)*self.inverse_GeV2_to_cm2*1e-6
        values=np.where(energy>=self.kinematics.minimum_energy_MeV(target,recoil_keV),values,0.)
        if not parameters.include_sm:values=np.zeros_like(energy)
        return DifferentialCrossSection(energy,values,float(recoil_keV),'coherent_sm_kn_v1')
