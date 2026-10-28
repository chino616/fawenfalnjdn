"""Run from any cwd after installing the package (external data remain external).

python run_experiments.py --resources /absolute/path/to/Gitup01
python run_experiments.py --resources /data-root --selection /path/selection.yaml
Small demonstration grids exercise interfaces; they do not establish convergence.
"""
from dataclasses import replace
from pathlib import Path
import argparse
import json
from cevns_pyeft.experiments.loader import load_experiment,ResourceCatalog
from cevns_pyeft.experiments.runtime import predict_experiment,evaluate_experiment,predict_selection
from cevns_pyeft.experiments.selection import load_selection

parser=argparse.ArgumentParser()
parser.add_argument('--resources',type=Path,required=True)
parser.add_argument('--selection',type=Path)
args=parser.parse_args()
resources=ResourceCatalog(args.resources)
if args.selection:
    results=predict_selection(load_selection(args.selection),resources=resources)
    print(json.dumps({key:p.counts.tolist() for key,p in results.items()},indent=2))
else:
    exp=load_experiment('CsI2021',resources=resources)
    ns={'n_er':5,'n_enu':12,'n_pe_bin':3}
    first=predict_experiment(exp,numerics=ns)
    fit=evaluate_experiment(exp,first)
    print('CsI2021',first.counts.tolist(),'approximate chi2',fit.chi2)
    for key,ns2 in [('Ar2020',ns),('CsI2017',{'n_enu':12}),('conus_plus_2025_c2c3c5_ge73_pyeft',{'n_recoil':8,'n_energy':2})]:
        p=predict_experiment(load_experiment(key,resources=resources),numerics=ns2)
        print(key,p.counts.tolist(),'detectors',list(p.detector_predictions))
    # Override one immutable instance; the built-in definition stays unchanged.
    definition=replace(exp.definition,physical=replace(exp.definition.physical,
        run=replace(exp.definition.physical.run,total_pot=2*exp.definition.physical.run.total_pot)))
    doubled=load_experiment('CsI2021',resources=resources,definition=definition)
    print('twice POT',predict_experiment(doubled,numerics=ns).counts.tolist())
