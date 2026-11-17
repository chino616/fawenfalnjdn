"""Compute the actual solar ee-vector NSI joint region in mainline Runtime.

Preserves previous SM/multibin/audit outputs. Primary uses two-flavor NSI MSW and
an explicitly named X constant-tail assumption; zero/unit/profiled-tail and fixed
SM propagation are separate controls. All contours subtract their own jointly
minimized chi2 over a certified full-plane search domain, never the SM value.
"""
from pathlib import Path
import argparse,hashlib,json,sys,time
import numpy as np
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from cevns_pyeft.experiments.definition import plain
from cevns_pyeft.experiments.solar_nsi import load_solar_nsi,INPUT_DIRECTORY
from cevns_pyeft.experiments.runtime import compile_experiment,predict_experiment,evaluate_experiment
from cevns_pyeft.statistics.solar_nsi import SolarNSIJoint
from cevns_pyeft.theory.li2026.ee_vector_nsi import nsi_point,monomials

SAMPLES=('PandaX_paired','PandaX_US2','XENONnT')


def save(path,value):path.write_text(json.dumps(plain(value),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def crossings(function,x,minimum):
    y=np.linspace(-1,1,1601);values=np.asarray(function(np.full_like(y,x),y))-minimum-4.61
    roots=[]
    for a,b,fa,fb in zip(y[:-1],y[1:],values[:-1],values[1:]):
        if fa*fb<0:roots.append(float(brentq(lambda t:float(function(x,t))-minimum-4.61,a,b,xtol=2e-11)))
    return roots


def reference_crossings(polygons,x):
    crossings=[]
    for polygon in polygons:
        for p,q in zip(polygon,np.vstack([polygon[1:],polygon[:1]])):
            if min(p[0],q[0])<=x<max(p[0],q[0]):crossings.append(float(p[1]+(x-p[0])*(q[1]-p[1])/(q[0]-p[0])))
    return sorted(set(round(a,9) for a in crossings if -1-1e-7<=a<=1+1e-7))


def simultaneous_pull_check(model,u,d):
    signals=model.signals(u,d);A=np.vstack([np.diag(signals/model.sigma),np.diag(1/model.pull)])
    rhs=np.r_[(model.D-signals)/model.sigma,np.zeros(3)]
    alpha=np.linalg.lstsq(A,rhs,rcond=None)[0];chi=float(np.sum((A@alpha-rhs)**2))
    direct=float(model.chi2(u,d))
    if abs(chi-direct)>1e-11:raise ValueError('independent simultaneous pull solver disagrees')
    return {'point':[u,d],'analytic':direct,'simultaneous_lstsq':chi,'absolute_difference':abs(chi-direct)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'outputs/solar_b8_nsi/20261112_fig4_run1')
    parser.add_argument('--grid',type=int,default=601)
    args=parser.parse_args();out=args.output.resolve()
    if not out.is_relative_to(ROOT/'outputs/solar_b8_nsi'):raise ValueError('use independent solar_b8_nsi output root')
    out.mkdir(parents=True,exist_ok=True)
    if (out/'NSI_RESULTS.json').exists():raise FileExistsError('create-only final results; choose a new run')
    (out/'kernels').mkdir(exist_ok=False)
    (out/'source').mkdir(exist_ok=False)
    experiments=[];kernels=[];convergence=[];shared=None
    points=[(0.,0.),(.3,-.1),(-.4,.6),(-17.3,15.7)]
    for sample in SAMPLES:
        e=load_solar_nsi(sample,root=ROOT,interaction=shared);shared=e.model.interaction
        print('Building',sample,'energy-resolved kernels',flush=True)
        checks=[];saved=[]
        for label,n_er,n_enu in [('recoil_base',401,96),('recoil_fine',801,96),('energy_fine',801,144)]:
            t=time.perf_counter();k=compile_experiment(e,numerics={'n_er':n_er,'n_enu':n_enu})
            predictions=[predict_experiment(e,parameters=nsi_point(u,d),backend='fast',kernel=k,numerics=k.record['numerics']).counts[0] for u,d in points]
            saved.append((k,predictions));print(sample,label,'events',predictions,'seconds',round(time.perf_counter()-t,2),flush=True)
        for left,right,axis in [(0,1,'recoil'),(1,2,'neutrino_energy')]:
            a=np.array(saved[left][1]);b=np.array(saved[right][1]);tol=np.maximum(3e-4,.002*abs(b));diff=abs(a-b)
            checks.append({'axis':axis,'points':points,'differences_events':diff.tolist(),'tolerance':tol.tolist(),'passed':bool(np.all(diff<=tol))})
        if not all(row['passed'] for row in checks):save(out/'CONVERGENCE_FAILURE.json',checks);raise ValueError('kernel convergence failed')
        k=saved[-1][0];k.save(out/'kernels'/f'{sample}.npz')
        destination=out/sample;destination.mkdir();save(destination/'PREPARED_MODEL.json',e.describe())
        slow_checks=[]
        for u,d in [points[0],points[1],points[-1]]:
            p=nsi_point(u,d);fast=predict_experiment(e,parameters=p,backend='fast',kernel=k,numerics=k.record['numerics'])
            slow=predict_experiment(e,parameters=p,numerics={'n_er':801,'n_enu':480})
            difference=abs(fast.counts-slow.counts);tolerance=np.maximum(3e-4,.002*abs(slow.counts))
            if not np.all(difference<=tolerance):raise ValueError('Slow and parameter-dependent-state kernel disagree')
            slow_checks.append({'point':[u,d],'fast':fast.counts.tolist(),'slow':slow.counts.tolist(),'difference':difference.tolist(),'tolerance':tolerance.tolist()})
            print(sample,'Slow verified',u,d,fast.counts.tolist(),slow.counts.tolist(),flush=True)
        convergence.append({'sample':sample,'independent_grids':checks,'direct_slow_checks':slow_checks})
        experiments.append(e);kernels.append(k)
    model=SolarNSIJoint(tuple(experiments),tuple(kernels))
    save(out/'FORWARD_VALIDATION.json',convergence)
    minimums={}
    for mode in ['flat_sensitivity','zero','unit','profile_bounds']:
        print('Joint minimization',mode,flush=True);minimums[mode]=model.minimize(mode)
        save(out/'MINIMUMS.json',minimums);print(mode,minimums[mode]['minimum'],flush=True)
    fixed_experiments=tuple(load_solar_nsi(s,root=ROOT,propagation='sm_fixed',interaction=shared) for s in SAMPLES)
    fixed_kernels=tuple(k.rebind_state(e) for k,e in zip(kernels,fixed_experiments))
    fixed=SolarNSIJoint(fixed_experiments,fixed_kernels);minimums['fixed_SM_propagation']=fixed.minimize()
    alternative_experiments=tuple(load_solar_nsi(s,root=ROOT,composition='agss09',interaction=shared) for s in SAMPLES)
    alternative_kernels=tuple(k.rebind_state(e) for k,e in zip(kernels,alternative_experiments))
    alternative=SolarNSIJoint(alternative_experiments,alternative_kernels);minimums['alternative_AGSS09_profile']=alternative.minimize()
    save(out/'MINIMUMS.json',minimums)
    # One pass through parameter-dependent Pee yields all X-tail sensitivity
    # surfaces; the probabilities are not recomputed four times needlessly.
    line=np.linspace(-1,1,args.grid);xx,yy=np.meshgrid(line,line,indexing='xy');u=xx.ravel();d=yy.ravel()
    block=np.empty((len(u),3,2))
    for i in range(0,len(u),192):
        block[i:i+192]=model.blocks(u[i:i+192],d[i:i+192])
        if i%(192*250)==0:print('Scanned',i,'/',len(u),'points',flush=True)
    surfaces={}
    for mode in ['flat_sensitivity','zero','unit','profile_bounds']:
        if mode=='profile_bounds':signals=np.clip(model.D,block[:,:,0],block.sum(axis=-1))
        else:signals=block[:,:,0]+{'flat_sensitivity':model.epsilon_tail,'zero':0.,'unit':1.}[mode]*block[:,:,1]
        chi=np.sum((model.D-signals)**2/(model.sigma**2+model.pull**2*signals**2),axis=-1).reshape(xx.shape)
        surfaces[mode]=chi-minimums[mode]['minimum']['chi2']
    surfaces['fixed_SM_propagation']=fixed.batch_grid(xx,yy)-minimums['fixed_SM_propagation']['minimum']['chi2']
    np.savez_compressed(out/'solar_NSI_surfaces.npz',epsilon_ee_uV=line,epsilon_ee_dV=line,
        signal_known=block[:,:,0].reshape((*xx.shape,3)),signal_unselected_tail=block[:,:,1].reshape((*xx.shape,3)),
        **{'delta_chi2_'+key:value for key,value in surfaces.items()})
    reference=json.loads((out/'source_evidence/paper_fig4_green_reference.json').read_text(encoding='utf8'))
    polygons=[np.array(p) for p in reference['polygons']]
    slice_rows=[]
    for x in [-.75,-.5,0.,.5,.75]:
        row={'epsilon_ee_uV':x,'paper_green_reference':reference_crossings(polygons,x)}
        for mode in ['flat_sensitivity','zero','unit','profile_bounds']:
            row[mode]=crossings(lambda u,d,mode=mode:model.chi2(u,d,mode),x,minimums[mode]['minimum']['chi2'])
        row['fixed_SM_propagation']=crossings(fixed.chi2,x,minimums['fixed_SM_propagation']['minimum']['chi2'])
        row['alternative_AGSS09_profile']=crossings(alternative.chi2,x,minimums['alternative_AGSS09_profile']['minimum']['chi2'])
        slice_rows.append(row)
    save(out/'SLICE_BOUNDARIES.json',slice_rows)
    from matplotlib.path import Path as Polygon
    points2=np.column_stack([u,d]);paper_mask=np.any(np.stack([Polygon(p).contains_points(points2).reshape(xx.shape) for p in polygons]),axis=0)
    own=surfaces['flat_sensitivity']<=4.61
    comparison={'paper_is_reference_only':True,'grid_size':args.grid,'intersection_over_union':float(np.sum(own&paper_mask)/np.sum(own|paper_mask)),
        'computed_allowed_fraction':float(own.mean()),'paper_allowed_fraction':float(paper_mask.mean()),
        'counterexample':{'point':[0.,.178],'computed':model.detail(0.,.178),'paper_membership':any(Polygon(p).contains_point((0.,.178)) for p in polygons),
                         'delta_chi2':float(model.chi2(0.,.178)-minimums['flat_sensitivity']['minimum']['chi2'])},
        'status':'COMPUTED_PHYSICAL_EE_NSI_REGION_DIFFERS_FROM_PAPER_GRAPHIC; NO_TUNING_TO_REFERENCE'}
    save(out/'PAPER_COMPARISON.json',comparison)
    # Dense radial integration and native-radius sum provide independent source
    # quadrature controls, including the far-away true joint parameter minimum.
    radial_checks=[]
    for u0,d0 in [(0,0),(.3,-.1),(0,.178),tuple(minimums['flat_sensitivity']['minimum'][k] for k in ['epsilon_ee_uV','epsilon_ee_dV'])]:
        a=model.signals(u0,d0);b=model.signals(u0,d0,radial_order=16)
        radial_checks.append({'point':[u0,d0],'order8':a.tolist(),'order16':b.tolist(),'relative':(abs(a-b)/np.maximum(abs(b),1e-30)).tolist()})
        if not np.all(abs(a-b)<=np.maximum(3e-4,.002*abs(b))):raise ValueError('radial quadrature convergence failed')
    checks=[simultaneous_pull_check(model,*p) for p in [(0,0),(0,.178),(.3,-.1)]]
    # Standard Runtime and the batched joint evaluator must bind the same signals
    # and three independent pulls. This never compares a point to a reference fit.
    runtime_checks=[]
    for u0,d0 in [(0,0),(.3,-.1)]:
        evaluations=[]
        for e,k in zip(experiments,kernels):
            p=predict_experiment(e,parameters=nsi_point(u0,d0),backend='fast',kernel=k,numerics=k.record['numerics']);evaluation=evaluate_experiment(e,p)
            evaluations.append(evaluation.chi2)
        difference=abs(sum(evaluations)-model.chi2(u0,d0))
        if difference>1e-10:raise ValueError('Runtime and joint inference disagree')
        runtime_checks.append({'point':[u0,d0],'sample_chi2':evaluations,'joint':float(model.chi2(u0,d0)),'absolute_difference':float(difference)})
    # Optional diagnostic only: all-electron scattering also describes universal
    # vector NSI detection. It is NOT substituted for electron-flavor NSI.
    all_electron=np.stack([k.integrated_electron_coefficients(model.epsilon_tail) for k in kernels])@monomials(0.,.178)
    universal_control=float(np.sum((model.D-all_electron)**2/(model.sigma**2+model.pull**2*all_electron**2)))
    result={'date':'2026-11-12','analysis':'actual solar ee-vector NSI, paper2601 singlebin method','SM':model.detail(0.,0.),
        'primary_minimum':minimums['flat_sensitivity'],'controls':{k:v for k,v in minimums.items() if k!='flat_sensitivity'},
        'delta_chi2_threshold':4.61,'DOF':2,'primary_tail':'flat_sensitivity','primary_propagation':'nsi_msw',
        'statistical_data':{'D':model.D,'sigma_stat':model.sigma,'pull_sigmas':model.pull,'independent':True},
        'radial_convergence':radial_checks,'independent_pull_checks':checks,'Runtime_joint_checks':runtime_checks,
        'paper_comparison':comparison,'not_adopted_universal_detection_diagnostic':{'point':[0.,.178],'all_flavors_NSI_signal':all_electron,'chi2':universal_control,'meaning':'different physical model; not a claim about what paper authors implemented'},
        'limits':['two-flavor adiabatic model, theta13_m=vacuum, no Earth regeneration','X tail is explicit project assumption; zero/unit and bounded profile controls kept separate',
                  'B16 structure is pinned secondary transcription; neutron density uses baryon mass1u approximation','paper exact oscillation/profile/SM input card not published; project choice explicitly sourced',
                  'seven directly adopted nuclear tables; Xe124/126 missing, no renormalization; external nuclear author release unverified'],
        'status':'MAINLINE_NSI_COMPUTED; EXACT_PAPER_GREEN_REPRODUCTION_NOT_ESTABLISHED','scientific_acceptance':'NOT_REVIEWED',
        'inputs':{'nsi_card':str(ROOT/INPUT_DIRECTORY/'nsi.input.json'),'sha256':sha(ROOT/INPUT_DIRECTORY/'nsi.input.json')},'runner_sha256':sha(Path(__file__))}
    save(out/'NSI_RESULTS.json',result)
    plot(out,line,surfaces,polygons,model,comparison)
    for module in experiments[0].record['implementation']:
        import importlib.util
        source=Path(importlib.util.find_spec(module).origin);destination=out/'source'/source.relative_to(ROOT)
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(source.read_bytes())
    save(out/'SOURCE_FINGERPRINTS.json',{module:hash_ for module,hash_ in experiments[0].record['implementation'].items()})
    print('COMPUTED solar NSI; primary minimum',result['primary_minimum']['minimum'],'paper IoU',comparison['intersection_over_union'],flush=True)


def plot(out,line,surfaces,polygons,model,comparison):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    fig,ax=plt.subplots(figsize=(7.1,6.4),constrained_layout=True)
    ax.contourf(line,line,surfaces['flat_sensitivity'],levels=[-1,4.61],colors=['#5eae69'],alpha=.65)
    ax.contour(line,line,surfaces['flat_sensitivity'],levels=[4.61],colors=['#176b2d'],linewidths=1.8)
    for p in polygons:ax.plot(p[:,0],p[:,1],color='#4a4a4a',ls='--',lw=1.1)
    ax.plot(0,0,'k+',ms=9);ax.plot(0,.178,'o',color='#b53235',ms=5)
    ax.set(xlim=(-1,1),ylim=(-1,1),xlabel=r'$\epsilon_{ee}^{uV}$',ylabel=r'$\epsilon_{ee}^{dV}$',
           title='Solar joint NSI: calculated physical electron-flavor model\n90% criterion: joint minimum subtracted, '+r'$\Delta\chi^2\leq4.61$')
    ax.set_aspect('equal');ax.grid(alpha=.15)
    ax.legend(handles=[Patch(facecolor='#5eae69',alpha=.65,label='Calculated: NSI MSW + ee scattering'),
        Line2D([],[],color='#4a4a4a',ls='--',label='Paper Fig.4 green boundary (reference only)'),
        Line2D([],[],marker='o',ls='',color='#b53235',label='Point (0, 0.178): computed allowed, paper excluded')],fontsize=8,loc='lower left')
    fig.savefig(out/'solar_Fig4_computed_vs_paper.png',dpi=190);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11.6,5.2),constrained_layout=True)
    colors={'flat_sensitivity':'#176b2d','zero':'#1c72b0','unit':'#c47b28','profile_bounds':'#7f4ca3','fixed_SM_propagation':'#ba3838'}
    for mode,color in colors.items():
        axes[0].contour(line,line,surfaces[mode],levels=[4.61],colors=[color],linewidths=1.3)
    axes[0].set(xlim=(-1,1),ylim=(-1,1),xlabel=r'$\epsilon_{ee}^{uV}$',ylabel=r'$\epsilon_{ee}^{dV}$',title='Independent treatment controls (own joint minima)')
    axes[0].legend(handles=[Line2D([],[],color=c,label=m.replace('_',' ')) for m,c in colors.items()],fontsize=7,loc='lower left');axes[0].set_aspect('equal')
    y=np.linspace(-.25,.65,1200)
    for mode,color in colors.items():
        minimum=json.loads((out/'MINIMUMS.json').read_text(encoding='utf8'))[mode]['minimum']['chi2']
        if mode=='fixed_SM_propagation':
            from dataclasses import replace
            state=model.state;model.state=replace(state,propagation='sm_fixed');values=model.chi2(np.zeros_like(y),y);model.state=state
        else:values=model.chi2(np.zeros_like(y),y,mode)
        axes[1].plot(y,values-minimum,color=color,label=mode.replace('_',' '),lw=1.3)
    axes[1].axhline(4.61,color='k',ls=':',lw=1);axes[1].set(xlabel=r'$\epsilon_{ee}^{dV}$ at $\epsilon_{ee}^{uV}=0$',ylabel=r'$\Delta\chi^2$ (2D minimum)',ylim=(0,10),title='Actual chi-square slices, not paper traces');axes[1].grid(alpha=.2)
    fig.savefig(out/'solar_NSI_controls.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4.7),constrained_layout=True);energy=np.linspace(.1,16.56,400)
    for u in [-.5,-.03,0,.03,.5]:ax.plot(energy,model.state.pee(energy,u,0),label=rf'$\epsilon_{{ee}}^{{uV}}={u:g}$')
    ax.set(xlabel=r'$E_\nu$ [MeV]',ylabel=r'$\langle P_{ee}\rangle$',ylim=(.27,.68),title='Production-averaged NSI MSW probabilities\nB16-GS98, paper2409 Appendix B approximation');ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.savefig(out/'solar_Pee_NSI.png',dpi=180);plt.close(fig)


if __name__=='__main__':main()
