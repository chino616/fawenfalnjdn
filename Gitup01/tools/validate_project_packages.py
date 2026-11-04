"""Build all active packages and verify installed, editable and two-file runtime."""
from pathlib import Path
import argparse
import hashlib
import importlib.abc
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile

FORMAL=('experiment.input.yaml','experiment.resources.npz','experiment.physics.md')


def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')


def run(command,cwd,env,log):
    result=subprocess.run(command,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log.write_text(result.stdout,encoding='utf8')
    result.check_returncode()


def driver(args):
    import numpy as np
    root=Path(__file__).resolve().parents[1];output=Path(args.output).resolve()
    if output.exists():raise ValueError('choose a fresh output directory')
    output.mkdir(parents=True);temporary=output/'build-temp';temporary.mkdir()
    env={k:v for k,v in os.environ.items() if k!='PYTHONPATH'}
    env.update(TEMP=str(temporary),TMP=str(temporary),PYTHONDONTWRITEBYTECODE='1')
    registry=json.loads((root/'cevns_pyeft/experiments/dataset_registry.json').read_text('utf8'))
    active=[e for e in registry['datasets'] if e['installed'] and e['status']=='active']
    formal={r['path']:(root/r['path']).read_bytes() for e in active for r in e['owned_files'] if Path(r['path']).name in FORMAL}
    assert len(formal)==3*len(active)
    sdist_dir=output/'sdist';sdist_dir.mkdir()
    run([sys.executable,'-B','-c','import sys;from setuptools.build_meta import build_sdist;build_sdist(sys.argv[1])',str(sdist_dir)],
        root,env,output/'sdist.log')
    sdist=next(sdist_dir.glob('*.tar.gz'))
    with tarfile.open(sdist) as archive:
        prefix=archive.getnames()[0].split('/')[0]+'/'
        assert {name.removeprefix(prefix) for name in archive.getnames() if Path(name).name in FORMAL}==set(formal)
        for path,content in formal.items():assert archive.extractfile(prefix+path).read()==content
    wheel_dir=output/'wheels'
    run([sys.executable,'-B','-m','pip','wheel',str(sdist),'--no-index','--no-deps','--no-build-isolation',
         '--no-cache-dir','--wheel-dir',str(wheel_dir)],output,env,output/'wheel-from-sdist.log')
    wheel=next(wheel_dir.glob('*.whl'))
    with zipfile.ZipFile(wheel) as archive:
        bundled=[name for name in archive.namelist() if name.startswith('cevns_pyeft/_data/') and Path(name).name in FORMAL]
        assert len(bundled)==len(formal)
        for path,content in formal.items():assert archive.read('cevns_pyeft/_data/'+path)==content
    installed=output/'engine'
    run([sys.executable,'-B','-m','pip','install','--no-index','--no-deps','--no-cache-dir','--target',str(installed),str(wheel)],
        output,env,output/'install.log')
    editable=output/'editable'
    run([sys.executable,'-B','-m','pip','install','--no-index','--no-deps','--no-build-isolation','--no-cache-dir',
         '--target',str(editable),'--editable',str(root)],output,env,output/'editable-install.log')
    reports={}
    def execute(mode,engine):
        outside=output/(mode+'-cwd');outside.mkdir()
        worker_file=outside/'worker.py';shutil.copy2(__file__,worker_file)
        if mode=='two-file':
            for entry in active:
                package=outside/entry['dataset_id'];package.mkdir()
                base=root/'data/experiments'/entry['experiment_slug']/entry['dataset_id']
                for name in FORMAL[:2]:shutil.copy2(base/name,package/name)
        bootstrap='import sys,site,runpy;site.addsitedir(sys.argv.pop(1));runpy.run_path(sys.argv.pop(1),run_name="__main__")'
        run([sys.executable,'-I','-B','-c',bootstrap,str(engine),str(worker_file),'--worker','--mode',mode,
             '--output',str(outside),'--source-root',str(root),'--ids',*[e['dataset_id'] for e in active]],
            outside,env,output/(mode+'.log'))
        return json.loads((outside/'worker-results.json').read_text('utf8'))
    reports['installed']=execute('installed',installed)
    reports['editable']=execute('editable',editable)
    excluded=[]
    candidates=[*installed.rglob('*_definition.py'),*installed.rglob('legacy_parameters.py'),
                installed/'cevns_pyeft/experiments/coherent/csi2021_package.py',
                installed/'cevns_pyeft/experiments/coherent/csi2021_package_contract.json']
    for path in candidates:
        if not path.resolve().is_relative_to(installed.resolve()):raise ValueError('isolation path escapes installed target')
        if path.is_file():excluded.append(path.relative_to(installed).as_posix());path.unlink()
    bundled=installed/'cevns_pyeft/_data'
    if not bundled.resolve().is_relative_to(installed.resolve()):raise ValueError('bundled target escapes installation')
    if bundled.is_dir():shutil.rmtree(bundled)
    reports['two-file']=execute('two-file',installed)
    frozen={}
    with np.load(root/'tests/reference/interface_refactor_v1/baseline.npz',allow_pickle=False) as reference:
        for mode,report in reports.items():
            frozen[mode]={}
            for sid,row in report['datasets'].items():
                key='csi2021/sm/small/counts_per_bin/total' if sid=='CsI2021' else sid.lower()+'/sm/total'
                actual=np.asarray(row['slow_counts']);expected=reference[key]
                np.testing.assert_allclose(actual,expected,rtol=1e-10,atol=1e-12)
                frozen[mode][sid]={'status':'PASS','max_abs':float(np.max(np.abs(actual-expected))),'rtol':1e-10,'atol':1e-12}
    result={'status':'PASS','active_ids':[e['dataset_id'] for e in active],'formal_files':list(formal),
        'sdist':{'name':sdist.name,'sha256':hashlib.sha256(sdist.read_bytes()).hexdigest(),'formal_count':len(formal)},
        'wheel_from_sdist':{'name':wheel.name,'sha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),'formal_count':len(formal)},
        'runs':reports,'frozen_comparison':frozen,'excluded_legacy_files':excluded,'bundled_data_removed_before_two_file':True,
        'scope':'same host, separate install directories, existing declared interpreter dependencies; no second machine or convergence claim'}
    dump(output/'results.json',result)
    print(json.dumps({'status':'PASS','report':str(output/'results.json'),'datasets':result['active_ids'],'formal_count':len(formal)}))


def worker(args):
    import numpy as np
    output=Path(args.output).resolve();source=Path(args.source_root).resolve();access=set()
    if args.mode=='two-file':
        class Guard(importlib.abc.MetaPathFinder):
            def find_spec(self,fullname,*unused):
                if fullname.endswith(('_definition','.legacy_parameters','.csi2021_package')):
                    raise ImportError('forbidden legacy import: '+fullname)
        sys.meta_path.insert(0,Guard())
    def audit(event,values):
        if event!='open' or not isinstance(values[0],(str,bytes,os.PathLike)):return
        path=Path(os.fsdecode(values[0])).resolve()
        if args.mode!='editable' and path.is_relative_to(source):raise PermissionError('hidden source access: '+str(path))
        if args.mode=='two-file' and (path.name in ('experiment.physics.md','experiment.yaml','responses_all.json','legacy_parameters.py') or
                (path.suffix=='.txt' and path.name.startswith(('COHERENT_','CENNS')))):
            raise PermissionError('hidden legacy resource: '+str(path))
        if path.is_relative_to(output):access.add(path.relative_to(output).as_posix())
    sys.addaudithook(audit)
    from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG
    from cevns_pyeft.experiments.loader import load_experiment
    from cevns_pyeft.experiments.package_loader import load_experiment_package
    from cevns_pyeft.experiments.runtime import predict_experiment,compile_experiment,evaluate_experiment
    from cevns_pyeft.kernels.storage import save_fastscan_template,load_fastscan_template
    from cevns_pyeft.kernels.interface_storage import save_compiled_kernel,load_compiled_kernel
    assert list(BUILTIN_CATALOG.ids())==args.ids
    rows={}
    for sid in args.ids:
        start=time.perf_counter()
        exp=load_experiment_package(output/sid) if args.mode=='two-file' else load_experiment(sid)
        slow_ns=({'n_enu':12} if sid=='CsI2017' else dict(n_er=11,n_enu=40,n_pe_bin=8) if sid=='Ar2020'
                 else dict(n_er=5,n_enu=12,n_pe_bin=4,pe_step=4.))
        fast_ns=({'n_er':251,'n_enu':12} if sid=='CsI2017' else dict(n_er=11,n_enu=40,n_obs_sub=8) if sid=='Ar2020' else slow_ns)
        slow=predict_experiment(exp,numerics=slow_ns);chi=evaluate_experiment(exp,slow).chi2
        kernel=compile_experiment(exp,numerics=fast_ns)
        fast=predict_experiment(exp,backend='fast',kernel=kernel,numerics=fast_ns)
        np.testing.assert_allclose(fast.counts,slow.counts,rtol=1e-10,atol=1e-12)
        path=output/(sid+'-kernel.npz')
        if sid=='CsI2021':
            save_compiled_kernel(path,kernel);restored=load_compiled_kernel(path,model=exp.model,numerics=exp.executor.settings(fast_ns))
        else:save_fastscan_template(path,kernel);restored=load_fastscan_template(path)
        repeated=predict_experiment(exp,backend='fast',kernel=restored,numerics=fast_ns)
        np.testing.assert_array_equal(repeated.counts,fast.counts)
        assert np.isfinite(slow.counts).all() and np.all(slow.counts>=0) and np.isfinite(chi)
        rows[sid]={'status':'PASS','slow_counts':slow.counts.tolist(),'fast_max_abs':float(np.max(np.abs(fast.counts-slow.counts))),
            'chi2_legacy_approximate':float(chi),'seconds':time.perf_counter()-start,'slow_numerics':slow_ns,'fast_numerics':fast_ns,
            'resolved_resources':{key:str(value) for key,value in exp.resolved_resources.items()},'saved_fast_reload':'PASS',
            'human_approval':'NOT_REVIEWED','official_likelihood':'BLOCKED','general_antineutrino_EFT':'BLOCKED'}
        print(args.mode,sid,'PASS',flush=True)
    import cevns_pyeft
    dump(output/'worker-results.json',{'status':'PASS','datasets':rows,'mode':args.mode,'cwd':str(Path.cwd()),
        'engine_import':str(cevns_pyeft.__file__),'accessed_output_files':sorted(access)})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True)
    parser.add_argument('--worker',action='store_true');parser.add_argument('--mode',choices=['installed','editable','two-file'])
    parser.add_argument('--source-root');parser.add_argument('--ids',nargs='+')
    args=parser.parse_args();worker(args) if args.worker else driver(args)
