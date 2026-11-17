"""Run solar SM with actual nuclear Response (current default, D0004).

--legacy-kn explicitly selects the historical 2026-11-07 KN calculation.
The old functions remain available for reference and plotting utilities.
"""
from pathlib import Path
import argparse,hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.runtime import predict_experiment
from cevns_pyeft.experiments.definition import plain

FAMILIES=[('XENONnT','XENONnT_2024_SolarB8'),('PandaX4T','PandaX4T_2024_US2')]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(plain(obj),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')


def run_one(family,dataset,output,resume=False):
    directory=ROOT/'data/experiments'/family/dataset
    destination=output/dataset
    experiment=load_experiment_package(directory)
    if destination.exists() and resume:
        from types import SimpleNamespace
        saved=json.loads((destination/'SM_RESULT.json').read_text(encoding='utf8'))
        if saved['physics_fingerprint']!=experiment.physics_fingerprint:raise ValueError('saved physical inputs/implementation changed; use a new output run')
        proxy=SimpleNamespace(counts=np.array(saved['counts']),detector_predictions={key:SimpleNamespace(counts=np.array(values)) for key,values in saved['per_run'].items()})
        if family=='XENONnT':plot_xenon(experiment,proxy,directory,destination,saved)
        else:plot_pandax(experiment,proxy,directory,destination,saved)
        (destination/'README.md').write_text(f'# {dataset}: SM forward benchmark\n\n2026-11-07. Restored plotting from the same verified numerical result.\n\n[Result and convergence](SM_RESULT.json) · [Numerical arrays](sm_prediction.npz) · [Actual Runtime inputs](PREPARED_MODEL.json) · [Figure](events.png)\n',encoding='utf8')
        print(dataset,'reused verified numerical result',saved['total_events'],flush=True)
        return saved
    destination.mkdir(parents=True,exist_ok=False)
    results=[];predictions=[]
    settings=[('base',201,120),('recoil_refined',401,120),('recoil_fine',801,120),('energy_refined',801,480)]
    for label,n_er,n_enu in settings:
        started=time.perf_counter()
        result=predict_experiment(experiment,backend='slow',numerics={'n_er':n_er,'n_enu':n_enu})
        predictions.append(result)
        record={'label':label,'n_er':n_er,'n_enu':n_enu,'counts':result.counts.tolist(),'total_events':float(result.counts.sum()),'seconds':time.perf_counter()-started}
        results.append(record)
        print(dataset,label,'events',record['total_events'],'seconds',round(record['seconds'],2),flush=True)
    final=predictions[-1]
    checks=[]
    for left,right,axis in [(1,2,'recoil'),(2,3,'neutrino_energy')]:
        a,b=predictions[left].counts,predictions[right].counts
        tolerance=np.maximum(2e-4,.002*abs(b))
        checks.append({'axis':axis,'from':settings[left][0],'to':settings[right][0],
                       'absolute_difference':abs(b-a).tolist(),'relative_difference':(abs(b-a)/np.maximum(abs(b),1e-30)).tolist(),
                       'tolerance_events':tolerance.tolist(),'passed':bool(np.all(abs(b-a)<=tolerance))})
    if not all(row['passed'] for row in checks):
        # Refine only the dimension that failed the declared numerical criterion.
        current_er,current_enu=settings[-1][1:]
        refine_recoil=not next(row for row in checks if row['axis']=='recoil')['passed']
        refine_energy=not next(row for row in checks if row['axis']=='neutrino_energy')['passed']
        for attempt in range(3):
            if all(row['passed'] for row in checks):break
            if refine_recoil:current_er=2*current_er-1
            if refine_energy:current_enu*=2
            started=time.perf_counter()
            newer=predict_experiment(experiment,backend='slow',numerics={'n_er':current_er,'n_enu':current_enu})
            delta=abs(newer.counts-final.counts);tolerance=np.maximum(2e-4,.002*abs(newer.counts))
            checks=[{'axis':'joint_refinement','absolute_difference':delta.tolist(),'relative_difference':(delta/np.maximum(abs(newer.counts),1e-30)).tolist(),
                     'tolerance_events':tolerance.tolist(),'passed':bool(np.all(delta<=tolerance))}]
            results.append({'label':'adaptive_'+str(attempt+1),'n_er':current_er,'n_enu':current_enu,'counts':newer.counts.tolist(),'total_events':float(newer.counts.sum()),'seconds':time.perf_counter()-started})
            final=newer
            print(dataset,results[-1]['label'],'events',results[-1]['total_events'],flush=True)
            if checks[0]['passed']:break
    diagnostic=final.combined_prediction.diagnostics
    arrays={'counts':final.counts,'observable_edges':np.array(experiment.definition.observation.edges)}
    arrays.update({'counts_'+run:p.counts for run,p in final.detector_predictions.items()})
    for isotope,grid in diagnostic['recoil_grids_keV'].items():
        arrays['recoil_'+isotope]=grid
        arrays['rate_per_tyr_keV_'+isotope]=diagnostic['true_recoil_rates_per_tyr_keV'][isotope]
    np.savez_compressed(destination/'sm_prediction.npz',**arrays)
    components={'/'.join(key):values.tolist() for key,values in final.combined_prediction.components.items()}
    summary={'dataset_id':dataset,'calculation':'SM forward, no fit','backend':'slow','counts':final.counts.tolist(),
       'total_events':float(final.counts.sum()),'unit':'events/bin','per_run':{run:p.counts.tolist() for run,p in final.detector_predictions.items()},
       'components':components,'normalization_ledger':plain(final.combined_prediction.normalization_record),'execution_record':plain(final.record),
       'input_package':str(directory/'experiment.input.yaml'),'input_package_sha256':digest(directory/'experiment.input.yaml'),
       'resource_archive_sha256':digest(directory/'experiment.resources.npz'),'physics_fingerprint':final.physics_fingerprint,
       'parameter_point':{'include_sm':True,'sin2thetaW':.23857,'total_B8_flux_cm2_s':5.46e6,'nuclear':'Klein-Nystrand, 2411.11749v1 Eqs.(1)-(3)'},
       'convergence':{'runs':results,'checks':checks,'passed':all(row['passed'] for row in checks)},
       'limits':['public recasting response has independent model approximation; numerical convergence is not paper equivalence'] if family=='XENONnT' else
                ['true-recoil acceptance projection only','US2 electron response absent; no SM Ne spectrum computed']}
    save(destination/'SM_RESULT.json',summary)
    save(destination/'PREPARED_MODEL.json',experiment.describe())
    if family=='XENONnT':plot_xenon(experiment,final,directory,destination,summary)
    else:plot_pandax(experiment,final,directory,destination,summary)
    (destination/'README.md').write_text(f'# {dataset}: SM forward benchmark\n\n2026-11-07. '+('XENONnT early official accepted response.' if family=='XENONnT' else 'PandaX true-recoil diagnostic; electron response still missing.')+
        '\n\n[Result and convergence](SM_RESULT.json) · [Numerical arrays](sm_prediction.npz) · [Actual Runtime inputs](PREPARED_MODEL.json) · [Figure](events.png)\n',encoding='utf8')
    return summary


def errors(counts):
    from scipy.stats import chi2
    counts=np.asarray(counts,dtype=float);alpha=1-.682689492137
    lower=np.where(counts>0,.5*chi2.ppf(alpha/2,2*counts),0)
    upper=.5*chi2.ppf(1-alpha/2,2*(counts+1))
    return np.array([counts-lower,upper-counts])


def plot_xenon(experiment,prediction,data,out,summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    observed=np.loadtxt(data/'statistics/xenonnt_official_observed_bins.txt')[:,4].reshape(2,3)
    backgrounds={name:[] for name in ['AC','ER','neutron']};reference=[]
    for i in [0,1]:
        with np.load(data/f'statistics/xenonnt_sr{i}_background_and_b8_early_release.npz',allow_pickle=False) as a:
            exposure=experiment.model.exposures_tyr[i]
            for key,label in [('ac','AC'),('er','ER'),('rg','neutron')]:
                values=a[key+'_rate_per_tyr_bin'];values=values[3,3] if values.ndim==6 else values
                backgrounds[label].append(values.sum(axis=(1,2,3))*exposure)
            reference.append(a['b8_rate_per_tyr_bin'][3,3].sum(axis=(1,2,3))*exposure)
    backgrounds={key:np.array(value) for key,value in backgrounds.items()};reference=np.array(reference)
    counts=np.array([prediction.detector_predictions[run].counts for run in ['SR0','SR1']])
    compare={'computed_signal':counts.tolist(),'native_release_signal_reference':reference.tolist(),
             'fractional_difference_per_run_bin':(counts/reference-1).tolist(),'backgrounds':{key:value.tolist() for key,value in backgrounds.items()},
             'observed':observed.tolist(),'reference_total_events':float(reference.sum()),
             'paper_exposure_total_tyr':3.51,'adopted_release_exposure_total_tyr':float(experiment.model.exposures_tyr.sum()),
             'signal_rescaled_only_to_paper_total_exposure':(counts*3.51/experiment.model.exposures_tyr.sum()).tolist(),
             'scope':'SM cross section/source computed here. Native template is an independent released reference at its own source/model conventions, not a fit target.'}
    save(out/'REFERENCE_COMPARISON.json',compare)
    fig,axes=plt.subplots(1,3,figsize=(14,4.8),constrained_layout=True)
    colors={'AC':'#c8c2e8','ER':'#8fbdd8','neutron':'#d4aa75'};x=np.arange(3)
    for ax,selection,title in zip(axes,[None,0,1],['SR0 + SR1 (bin ordinals)','SR0','SR1']):
        select=lambda values:values.sum(axis=0) if selection is None else values[selection]
        bottom=np.zeros(3)
        for key,values in backgrounds.items():
            y=select(values);ax.bar(x,y,bottom=bottom,width=.72,color=colors[key],label=key);bottom+=y
        signal=select(counts);ax.bar(x,signal,bottom=bottom,width=.72,color='#36a493',label='Calculated SM')
        ax.plot(x,bottom+select(reference),'D--',color='#9753ac',ms=4,label='Native release SM + B')
        d=select(observed);ax.errorbar(x,d,yerr=errors(d),fmt='ko',capsize=3,label='Observed',ms=4,zorder=4)
        ax.set_xticks(x,['1','2','3']);ax.set_xlabel('cS2 analysis bin index');ax.set_title(title);ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.2)
        if selection is not None:
            edges=experiment.model.observation[selection].native_cs2_edges
            ax.set_xticks(x,[f'{a:g}-{b:.2f}' for a,b in zip(edges[:-1],edges[1:])],fontsize=8)
            ax.set_xlabel('cS2 bin interval [PE]')
    axes[0].set_ylabel('Events / bin');axes[0].legend(fontsize=8)
    fig.suptitle(r'XENONnT 2024: SM forward benchmark, $\Phi_{8B}=5.46\times10^6$ cm$^{-2}$s$^{-1}$'+
                 '\nPublic early response; KN form factor; no fitted scale or correction factors',fontsize=12)
    fig.savefig(out/'events.png',dpi=200);fig.savefig(out/'events.pdf');plt.close(fig)
    np.savetxt(out/'events_by_bin.tsv',np.column_stack([x+1,counts.sum(axis=0),reference.sum(axis=0),sum(backgrounds.values()).sum(axis=0),observed.sum(axis=0)]),delimiter='\t',
               header='bin_index calculated_SM_events native_reference_SM_events background_events observed_events; original per-run PE boundaries differ')


def plot_pandax(experiment,prediction,data,out,summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    edges=np.array(experiment.definition.observation.edges)
    reference=np.loadtxt(data/'statistics/pandax_benchmark_fig1.txt')
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),constrained_layout=True)
    axes[0].stairs(prediction.counts/np.diff(edges),edges,color='#008b88',lw=2,label='Calculated SM x published acceptance')
    axes[0].set(xlabel='True nuclear recoil energy [keVnr]',ylabel='Events / keVnr',title='Computed true-recoil diagnostic (1.04 t yr)')
    axes[0].legend(fontsize=8);axes[0].grid(alpha=.2)
    x=.5*(reference[:,1]+reference[:,2]);bottom=np.zeros(8)
    for values,color,label in [(reference[:,4],'#b1c6b1','Cathode reference'),(reference[:,5],'#e4c582','MD reference'),(reference[:,6],'#c49edb','Paper fitted/reference signal')]:
        axes[1].bar(x,values,bottom=bottom,width=.46,color=color,label=label);bottom+=values
    axes[1].errorbar(x,reference[:,3],yerr=errors(reference[:,3]),fmt='ko',capsize=2,ms=3,label='Observed')
    axes[1].set(xlabel='Reconstructed electron number',ylabel='Events / bin',title='Reference only: Ne response not available',ylim=(0,None))
    axes[1].legend(fontsize=8);axes[1].grid(axis='y',alpha=.2)
    fig.suptitle('PandaX-4T US2: SM calculation boundary kept explicit',fontsize=13)
    fig.savefig(out/'events.png',dpi=200);fig.savefig(out/'events.pdf');plt.close(fig)
    save(out/'REFERENCE_COMPARISON.json',{'electron_spectrum_prediction':'BLOCKED missing response','paper_reference_signal_events':float(reference[:,6].sum()),
        'true_recoil_efficiency_projection_events':float(prediction.counts.sum()),'scope':'Different observables; these totals must not be interpreted as a reproduction ratio.'})
    np.savetxt(out/'true_recoil_counts.tsv',np.column_stack([edges[:-1],edges[1:],prediction.counts]),delimiter='\t',header='true_recoil_low_keVnr true_recoil_high_keVnr calculated_SM_ROI_accepted_true_recoil_events; includes_ROI_selection_but_not_a_reconstructed_Ne_histogram')


def main():
    # Compatibility gateway only. The two analysis executors, resources,
    # statistical meanings and output roots are independent.
    if '--analysis' in sys.argv:
        index = sys.argv.index('--analysis')
        if index+1 >= len(sys.argv) or sys.argv[index+1] not in ('singlebin', 'multibin'):
            raise SystemExit('--analysis must be singlebin or multibin')
        analysis = sys.argv[index+1]
        del sys.argv[index:index+2]
        if analysis == 'singlebin':
            if '--legacy-kn' in sys.argv:
                raise SystemExit('singlebin requires the nuclear Response route; --legacy-kn is multibin history only')
            from tools.run_solar_b8_singlebin_benchmark import main as singlebin_main
            return singlebin_main()
        if '--legacy-kn' not in sys.argv:
            from tools.run_solar_b8_multibin_benchmark import main as multibin_main
            return multibin_main()
    if '--legacy-kn' not in sys.argv:
        from tools.run_solar_b8_nuclear_benchmark import main as nuclear_main
        return nuclear_main()
    sys.argv.remove('--legacy-kn')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'outputs/solar_b8_sm/20261107_run1')
    parser.add_argument('--dataset',choices=['all','XENONnT','PandaX4T'],default='all')
    parser.add_argument('--resume',action='store_true',help='reuse saved numbers only when the full physical fingerprint still matches')
    args=parser.parse_args()
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=getattr(args,'resume',False))
    records=[run_one(family,dataset,output,getattr(args,'resume',False)) for family,dataset in FAMILIES if args.dataset in ('all',family)]
    save(output/'BENCHMARK_SUMMARY.json',{'date':'2026-11-07','results':records,'status':'PARTIAL because PandaX Ne response is absent and exact-paper equivalence is not asserted'})
    (output/'README.md').write_text('# Solar B8 SM benchmark\n\n2026-11-07. [Summary](BENCHMARK_SUMMARY.json)\n\n'+''.join(f"- [{row['dataset_id']}]({row['dataset_id']}/README.md)\n" for row in records),encoding='utf8')
    print('Saved benchmark:',output,flush=True)


if __name__=='__main__':main()
