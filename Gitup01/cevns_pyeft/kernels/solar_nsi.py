"""Energy-resolved solar ee-NSI kernel, with state recomputed at every point.

K[isotope, known_or_unselected_tail, polynomial_monomial, E] integrates only
target/recoil/detector/source magnitude. Pee(E;eu,ed) is NOT compiled away.
This is a separate representation from the constant-rho generic interface kernel.
"""
from dataclasses import dataclass
import json
import numpy as np
from cevns_pyeft.experiments.definition import plain,digest
from cevns_pyeft.experiments.solar_nsi import check_point,make_prediction,tail_epsilon
from cevns_pyeft.theory.li2026.ee_vector_nsi import monomials


def fold_identity(experiment,numerics,weak_angle):
    """Only inputs of the state-independent energy kernel, not its Pee provider."""
    m=experiment.model;o=m.observation
    modules={k:v for k,v in experiment.record['implementation'].items() if k!='cevns_pyeft.sources.solar_msw'}
    return digest({'source_magnitude':plain(m.source.components_per_second[0].continuum_function),
        'support':plain(m.source.components_per_second[0].support),'targets':plain(m.targets),
        'interaction':m.interaction.describe().as_dict(),'energy':o.energy,'efficiency':o.efficiency,
        'bounds':o.requested_bounds,'exposure_tyr':m.exposure_tyr,'seconds_per_year':m.seconds_per_year,
        'numerics':dict(numerics),'weak_angle':weak_angle,'implementations':modules})


def trap_weights(x):
    w=np.zeros_like(x);w[:-1]+=np.diff(x)/2;w[1:]+=np.diff(x)/2
    return w


@dataclass(frozen=True)
class SolarNSIKernel:
    energy:np.ndarray
    energy_weights:np.ndarray
    values:np.ndarray
    isotope_keys:tuple
    record:dict

    def blocks(self,pee,eu,ed):
        # shape parameter_batch + (isotope, known/tail). Polynomial coefficients
        # may be signed; positivity is required only after physical contraction.
        coefficients=monomials(eu,ed)
        sm=np.einsum('ibe,e->ib',self.values[:,:,0,:],self.energy_weights)
        correction=np.einsum('...e,ibme,...m,e->...ib',pee,self.values[:,:,1:,:],coefficients[...,1:],self.energy_weights,optimize=True)
        output=sm+correction
        tolerance=1e-10*np.maximum(1.,np.max(abs(output),axis=(-1,-2),keepdims=True))
        if np.any(output < -tolerance):raise ValueError('negative energy-resolved physical rate')
        return np.maximum(output,0.)

    def integrated_electron_coefficients(self,epsilon_tail):
        return np.einsum('ibme,e,b->m',self.values,self.energy_weights,np.array([1.,epsilon_tail]))

    def validate(self,experiment,numerics,point):
        if self.record['physics_fingerprint']!=experiment.physics_fingerprint or self.record['sin2thetaW']!=point.sin2thetaW:
            raise ValueError('stale/wrong NSI kernel physical definition or weak angle')
        if dict(numerics)!=self.record['numerics']:raise ValueError('kernel numerical grid differs from Runtime request')

    def rebind_state(self,experiment):
        """Explicit reuse only after checking every state-independent dependency.

        Enables the fixed-SM-propagation and solar-composition controls without
        pretending that a fixed-state generic kernel can handle variable Pee.
        """
        from dataclasses import replace
        numerics=self.record['numerics'];angle=self.record['sin2thetaW']
        if fold_identity(experiment,numerics,angle)!=self.record['fold_dependency_digest']:
            raise ValueError('cannot rebind changed cross section/source magnitude/target/efficiency/exposure')
        record={**self.record,'physics_fingerprint':experiment.physics_fingerprint,
            'rebound_from_physics_fingerprint':self.record['physics_fingerprint'],
            'physical_dependencies':plain(experiment.record),'rebind_scope':'state provider only; every fold input digest unchanged'}
        return replace(self,record=record)

    def predict(self,experiment,point,numerics):
        self.validate(experiment,numerics,point);m=experiment.model;eu,ed=check_point(m,point)
        pee=m.state_model.pee(self.energy,eu,ed);values=self.blocks(pee,eu,ed)
        known={};tails={};parts={}
        for i,isotope in enumerate(self.isotope_keys):
            key=('solar_B8',isotope);known[key]=float(values[i,0]);tails[key]=float(values[i,1])
            parts[key]=np.array([values[i,0]+tail_epsilon(m)*values[i,1]])
        return make_prediction(m,parts,known,tails,point,numerics,backend='energy_resolved_ee_vector_nsi_v1')

    def save(self,path):
        np.savez_compressed(path,energy=self.energy,energy_weights=self.energy_weights,values=self.values,
            isotope_keys=np.array(self.isotope_keys),record_json=np.array(json.dumps(plain(self.record),sort_keys=True)),
            array_digest=np.array(digest({'energy':self.energy,'weights':self.energy_weights,'values':self.values,'isotopes':self.isotope_keys})))

    @classmethod
    def load(cls,path):
        with np.load(path,allow_pickle=False) as a:
            energy=a['energy'].copy();weights=a['energy_weights'].copy();values=a['values'].copy();keys=tuple(a['isotope_keys'].tolist());record=json.loads(str(a['record_json']))
            if record['representation']!='energy_resolved_ee_vector_nsi_v1' or str(a['array_digest'])!=digest({'energy':energy,'weights':weights,'values':values,'isotopes':keys}):
                raise ValueError('wrong representation or corrupted NSI kernel arrays')
        for a in [energy,weights,values]:a.setflags(write=False)
        return cls(energy,weights,values,keys,record)


def compile_kernel(experiment,numerics,weak_angle):
    from cevns_pyeft.experiments.runtime import validate_snapshot
    validate_snapshot(experiment);m=experiment.model;o=m.observation
    x,w=np.polynomial.legendre.leggauss(numerics['n_enu'])
    support=m.source.components_per_second[0].support.integration_domain_MeV
    energy=(support[0]+support[1])/2+(support[1]-support[0])/2*x;ew=w*(support[1]-support[0])/2
    spectrum=m.source.components_per_second[0].continuum(energy)*m.seconds_per_year
    lo,hi=o.requested_bounds;split=o.verified_upper
    recoil=np.unique(np.r_[np.linspace(lo,hi,numerics['n_er']),o.energy[(o.energy>lo)&(o.energy<hi)],split])
    weights=np.zeros((2,len(recoil)))
    known=recoil<=split;weights[0,known]=trap_weights(recoil[known])*o.known_acceptance(recoil[known])
    if not o.complete:
        mask=recoil>=split;weights[1,mask]=trap_weights(recoil[mask])
    values=np.zeros((len(m.targets.isotopes),2,6,len(energy)))
    for i,target in enumerate(m.targets.isotopes):
        scale=target.number_of_nuclei*m.exposure_tyr
        for j,t in enumerate(recoil):
            ds=m.interaction.spectral_coefficients(target,energy,float(t),weak_angle).T
            values[i]+=weights[:,j,None,None]*ds[None,:,:]*spectrum[None,None,:]*scale
    record={'representation':'energy_resolved_ee_vector_nsi_v1','physics_fingerprint':experiment.physics_fingerprint,
        'numerics':dict(numerics),'sin2thetaW':weak_angle,'axes':['isotope','known_or_unselected_tail','1,eu,ed,eu²,eu*ed,ed²','E_MeV'],
        'state_treatment':'recompute Pee(E;eu,ed) at every point; not a fixed-state EFT quadratic rate',
        'physical_dependencies':plain(experiment.record),'recoil_nodes':len(recoil),'source_magnitude':'per-year fluence, fixed flux5.46e6, no parameter rescaling',
        'fold_dependency_digest':fold_identity(experiment,numerics,weak_angle)}
    for a in [energy,ew,values]:a.setflags(write=False)
    return SolarNSIKernel(energy,ew,values,tuple(t.isotope_id for t in m.targets.isotopes),record)
