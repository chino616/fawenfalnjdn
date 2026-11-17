"""Two-coordinate models built from the immutable, checked 1D input snapshots.

No production loader fallback, physical input or likelihood is changed here.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ONE = ROOT/'outputs/one_d_benchmark_20261113_run1'
sys.path.append(str(ROOT/'examples/one_d_benchmark'))
sys.path.insert(0, str(ROOT))
from prediction_routes import BASIS, FrozenBilinearRoute, GaussianChannel, SolarRoute, coefficients
from cevns_pyeft.kernels.compiler import reconstruct_channels
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson

LEVELS = {'68percent': 2.30, '90percent': 4.61, '95percent': 5.99}
SNS_FLAVORS = ('ee', 'mumu', 'emu', 'etau', 'mutau', 'tautau')
CONUS_FLAVORS = ('ee', 'emu', 'etau')
SOLAR_SAMPLES = ('PandaX_paired', 'PandaX_US2', 'XENONnT', 'Solar_joint')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, obj):
    def plain(v):
        if isinstance(v, dict): return {str(k): plain(x) for k,x in v.items()}
        if isinstance(v, (list,tuple)): return [plain(x) for x in v]
        if isinstance(v, np.ndarray): return plain(v.tolist())
        if isinstance(v, np.generic): return v.item()
        if isinstance(v, Path): return str(v)
        return v
    Path(path).write_text(json.dumps(plain(obj), ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def monomials(points):
    p = np.asarray(points, float)
    x,y = p[...,0],p[...,1]
    return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y], axis=-1)


def interpolate_quadratic(fn):
    nodes = np.array([[0,0],[1,0],[-1,0],[0,1],[0,-1],[1,1]], float)
    return np.linalg.solve(monomials(nodes),np.stack([fn(*p) for p in nodes]))


def upper_rate(D, sigma, pull, level):
    denominator = 1-level*pull*pull
    if denominator<=0: raise ValueError('Gaussian-pull saturation: finite domain not established')
    return float((D+np.sqrt(level*(pull*pull*D*D+denominator*sigma*sigma)))/denominator)


def ellipsoid(coefficient, upper, level, proof):
    p = np.asarray(coefficient,float)
    Q = np.array([[p[3],p[4]/2],[p[4]/2,p[5]]])
    eigen, vectors = np.linalg.eigh(Q)
    if np.min(eigen)<=0: raise ValueError('No positive-definite rate bound; do not invent finite limits')
    center = -.5*np.linalg.solve(Q,p[1:3])
    offset = float(p[0]+p[1:3]@center+center@Q@center)
    radius2 = upper-offset
    if radius2<=0: raise ValueError('Nonpositive enclosing ellipse radius')
    matrix = vectors*np.sqrt(radius2/eigen)[None,:]*1.01
    return {'kind':'positive_rate_ellipse','center':center.tolist(),'transform':matrix.tolist(),
            'bounds':[[-1.,1.],[-1.,1.]],'Q_eigenvalues':eigen.tolist(),
            'quadratic_minimum':offset,'rate_upper':float(upper),'excluded_chi2_level':float(level),
            'positive_signal_coefficients':p.tolist(),'proof':proof,
            'axis_enclosing_bounds':np.column_stack([center-np.abs(matrix).sum(axis=1),center+np.abs(matrix).sum(axis=1)]).tolist()}


class TerrestrialPlane:
    def __init__(self, analysis, routes, flavor):
        self.analysis,self.routes,self.flavor = analysis,tuple(routes),flavor
        self.kind = 'NSI'
        self.parameters = ['epsilon_'+flavor+'_uV','epsilon_'+flavor+'_dV']
        self.key = analysis+'__NSI_'+flavor
        self.polynomials = [interpolate_quadratic(lambda u,d,r=r:self.direct_signal(r,u,d)) for r in self.routes]
        self.flat = max(float(np.max(np.abs(p[1:]))) for p in self.polynomials)<1e-10
        self.reference = [0.,0.]
        self.domain = self.make_domain()
        self.best_fit_semantics = 'flat entire real plane' if self.flat else 'all numerically recovered degenerate minima retained'

    def direct_signal(self, route, u, d):
        extra = vector_nsi_to_np_wilson(VectorNSIParameters(**{self.parameters[0]:u,self.parameters[1]:d}))
        c = coefficients(route.angle)+np.array([extra.get(k,np.zeros((3,3),complex)) for k in BASIS])
        return reconstruct_channels(route.full,c,route.rhos).sum(axis=(0,1,2))

    def signals(self, points):
        terms=monomials(points)
        out=[terms@p for p in self.polynomials]
        if any(np.min(s)<-1e-7*max(1.,float(np.max(np.abs(s)))) for s in out): raise ValueError('negative signal')
        return [np.maximum(s,0.) for s in out]

    def cost(self, points):
        p = np.asarray(points,float)
        if p.ndim==2 and len(p)>32768:
            return np.concatenate([self.cost(p[i:i+32768]) for i in range(0,len(p),32768)])
        return sum(r.channel.profile(s)[0] for r,s in zip(self.routes,self.signals(p)))

    def make_domain(self):
        if self.flat: return {'kind':'flat_real_plane','bounds':[[-1.,1.],[-1.,1.]],'meaning':'display only; allowed set is R^2'}
        level=float(self.cost(self.reference))+max(LEVELS.values())+.25
        upper=sum(r.channel.rate_upper_bound(level) for r in self.routes)
        p=sum(poly.sum(axis=1) for poly in self.polynomials)
        d=ellipsoid(p,upper,level,'If total positive signal exceeds sum of per-channel Cauchy upper bounds, at least one independently profiled channel has chi2>L. L=SMchi2+5.99+0.25, so all minima and nominal regions are inside the enclosing ellipse.')
        d['channel_upper_bounds']={r.name:r.channel.rate_upper_bound(level) for r in self.routes}
        return d

    def map(self, z):
        z=np.asarray(z,float)
        if self.flat: return z
        return np.array(self.domain['center'])+z@np.array(self.domain['transform']).T

    def inverse(self, p):
        if self.flat: return np.asarray(p,float)
        return np.linalg.solve(np.array(self.domain['transform']), (np.asarray(p)-self.domain['center']).T).T


class SolarNSIPlane:
    def __init__(self, solar, analysis):
        self.solar,self.analysis,self.kind,self.flavor = solar,analysis,'NSI','ee'
        self.indices = [0,1,2] if analysis=='Solar_joint' else [SOLAR_SAMPLES.index(analysis)]
        self.key=analysis+'__NSI_ee'
        self.parameters=['epsilon_ee_uV','epsilon_ee_dV']
        self.flat=False; self.reference=[0.,0.]
        self.domain=self.make_domain()
        self.best_fit_semantics='one fitted yield: continuous zero-cost ridge; reported point is representative' if len(self.indices)==1 else 'numerically searched joint minimum within the declared effective propagation model'

    def signals(self, points):
        p=np.asarray(points,float); shape=p.shape[:-1]; p=p.reshape(-1,2)
        out=np.empty((len(p),3))
        s=self.solar
        for i in range(0,len(p),192):
            u,d=p[i:i+192].T
            pee=s.source.pee(s.energy,u,d)
            terms=np.stack([u,d,u*u,u*d,d*d],axis=-1)
            blocks=s.sm_blocks+np.einsum('pe,sbme,pm,e->psb',pee,s.templates[:,:,1:,:],terms,s.weights,optimize=True)
            out[i:i+len(u)]=blocks[:,:,0]+s.tail_efficiency*blocks[:,:,1]
        if np.min(out)<-1e-7: raise ValueError('negative solar rate')
        return np.maximum(out,0.).reshape((*shape,3))

    def cost(self, points):
        return self.solar.profile(self.signals(points),self.indices)

    def make_domain(self):
        level=float(self.cost(self.reference))+max(LEVELS.values())+.25
        upper=sum(upper_rate(self.solar.D[i],self.solar.sigma[i],self.solar.pulls[i],level) for i in self.indices)
        p=self.solar.electron_coefficients()[self.indices].sum(axis=0)
        pmin=float(self.solar.source.probability_bounds[0])
        d=ellipsoid(p,upper/pmin,level,'Positive total rate >= Pee_min * all-electron rate for each selected sample. Sum of independent Gaussian upper bounds excludes all potentially allowed points outside this ellipse; each NSI point still recomputes propagation.')
        d.update(Pee_min=pmin,selected_samples=self.indices,signal_upper_sum=upper)
        return d

    map=TerrestrialPlane.map
    inverse=TerrestrialPlane.inverse


class SolarSMPlane:
    def __init__(self, solar, analysis, retain_pulls):
        self.solar,self.analysis,self.kind = solar,analysis,'SM'
        self.indices=[0,1,2] if analysis=='Solar_joint' else [SOLAR_SAMPLES.index(analysis)]
        self.retain_pulls=retain_pulls
        self.mode='existing_pulls_control' if retain_pulls else 'data_only'
        self.key=analysis+'__SM_angle_flux_'+self.mode
        self.parameters=['sin2thetaW','fB']; self.flat=False
        self.reference=[solar.angle,1.]
        self.domain=self.make_domain()
        self.best_fit_semantics='one fitted yield: fB=D/S(sin2thetaW) is a continuous zero-cost ridge; point is representative' if len(self.indices)==1 else 'joint weak-angle/flux fit; investigate physical boundaries and strong correlation'

    def signals(self, points):
        p=np.asarray(points,float)
        return p[...,1,None]*self.solar.weak_signals(p[...,0])

    def cost(self, points):
        return self.solar.profile(self.signals(points),self.indices,retain_pulls=self.retain_pulls)

    def make_domain(self):
        level=float(self.cost(self.reference))+max(LEVELS.values())+.25
        ref=min(self.indices,key=lambda i:self.solar.sigma[i]/self.solar.D[i])
        p=self.solar.pulls[ref] if self.retain_pulls else 0.
        upper=upper_rate(self.solar.D[ref],self.solar.sigma[ref],p,level)
        return {'kind':'solar_rate_rectangle','bounds':[[0.,1.],[0.,1.]],'reference_sample':ref,
                'relative_rate_upper':upper/self.solar.D[ref]*1.01,'excluded_chi2_level':level,
                'physical_bounds':{'sin2thetaW':[0.,1.],'fB':[0.,None]},
                'mapping':'theta=z0; fB=z1*relative_rate_upper*D_ref/S_ref(theta); no flux prior added in data_only',
                'proof':'S_ref(theta)>0 on physical weak-angle domain; larger relative rate would violate the reference sample Gaussian upper bound. The transformed rectangle includes all candidate minima/nominal regions; angle and fB=0 edges are physical.'}

    def map(self,z):
        z=np.asarray(z,float); a=z[...,0]
        rate=self.solar.weak_signals(a)[...,self.domain['reference_sample']]
        if np.any(rate<=0): raise ValueError('SM reference rate must stay positive')
        scale=self.domain['relative_rate_upper']*self.solar.D[self.domain['reference_sample']]/rate
        return np.stack([a,z[...,1]*scale],axis=-1)

    def inverse(self,p):
        p=np.asarray(p,float); a=p[...,0]
        rate=self.solar.weak_signals(a)[...,self.domain['reference_sample']]
        z=p[...,1]*rate/(self.domain['relative_rate_upper']*self.solar.D[self.domain['reference_sample']])
        return np.stack([a,z],axis=-1)


def load_models():
    sources=read(ONE/'SOURCE_MANIFEST.json')
    for p,h in sources.items():
        if sha(ROOT/p)!=h: raise ValueError('Adopted 1D source changed: '+p)
    summary_path=ROOT/'outputs/paper2601_chi2_corrected_20261111/SUMMARY.json'
    summary=read(summary_path)
    old=read(ONE/'RESULTS.json')
    routes={}
    for name in ['CsI2021','Ar2020','CONUS_plus']:
        row=summary['SM'][name]; path=ONE/'inputs'/(name+'_fixed_model.npz')
        with np.load(path,allow_pickle=False) as z:
            ch=GaussianChannel(name,z['observed'].copy(),z['sigma'].copy(),row['sigma_alpha'],
                               None if row['background'] is None else z['background'].copy(),row['sigma_beta'])
            route=FrozenBilinearRoute(name,z['full_kernel'].copy(),z['rhos'].copy(),ch,
                                     .23857 if name=='CONUS_plus' else .2387,{'authority':'immutable checked 1D snapshot'})
        np.testing.assert_allclose(route.predict(),row['signal'],atol=1e-9,rtol=1e-12)
        sources[path.relative_to(ROOT).as_posix()]=sha(path)
        routes[name]=route
    solar=SolarRoute(ROOT/'outputs/external/solar_rho_snudd/20261112_fig4_run2')
    planes=[]
    for name in ['CsI2021','Ar2020','COHERENT_CsI_Ar_mean_errors']:
        parts=[routes['CsI2021'],routes['Ar2020']] if name.startswith('COHERENT_') else [routes[name]]
        planes += [TerrestrialPlane(name,parts,f) for f in SNS_FLAVORS]
    planes += [TerrestrialPlane('CONUS_plus',[routes['CONUS_plus']],f) for f in CONUS_FLAVORS]
    planes += [SolarNSIPlane(solar,n) for n in SOLAR_SAMPLES]
    planes += [SolarSMPlane(solar,n,p) for p in [False,True] for n in SOLAR_SAMPLES]
    for f in [ONE/'RESULTS.json',ONE/'DELIVERY_MANIFEST.json',ONE/'STATISTICS_CONTRACT.md']:
        sources[f.relative_to(ROOT).as_posix()]=sha(f)
    return planes,sources,old
