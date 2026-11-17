"""Add the published diagonal/flavor-changing d-quark benchmark pairs.

The 33 base cases remain immutable. Eight supplemental cases are indexed with
them in BENCHMARK_RESULTS.json; the original RESULTS.json is never rewritten.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from models import ROOT, TerrestrialPlane, interpolate_quadratic, load_models, read, sha, write
from plane_inference import grid_points, minimize_plane
from run_analysis import polynomial_checks, save_case


class MixedPlane(TerrestrialPlane):
    def __init__(self,analysis,routes,flavor_changing):
        self.analysis,self.routes,self.kind=analysis,tuple(routes),'NSI'
        self.flavor='mixed_ee_'+flavor_changing+'_dV'
        self.parameters=['epsilon_ee_dV','epsilon_'+flavor_changing+'_dV']
        self.key=analysis+'__NSI_'+self.flavor
        self.polynomials=[interpolate_quadratic(lambda u,d,r=r:self.direct_signal(r,u,d)) for r in self.routes]
        self.flat=False;self.reference=[0.,0.];self.domain=self.make_domain()
        self.best_fit_semantics='two distinct real d-quark flavor coordinates, other NSI zero; all recovered degenerate minima retained'


def add_mixed(base):
    out=list(base)
    for analysis in ['CsI2021','Ar2020','COHERENT_CsI_Ar_mean_errors','CONUS_plus']:
        representative=next(p for p in base if p.analysis==analysis and p.kind=='NSI')
        out.extend(MixedPlane(analysis,representative.routes,f) for f in ['emu','etau'])
    return out


def load_all_models():
    planes,sources,old=load_models()
    return add_mixed(planes),sources,old


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    if (out/'BENCHMARK_RESULTS.json').exists(): raise FileExistsError('Complete benchmark bundle is immutable')
    base=read(out/'RESULTS.json')
    planes,sources,old=load_all_models()
    n=next(iter(base['scans'].values()))['views']['global']['shape'][0]
    supplemental={};holdouts=[];start=time.perf_counter()
    for p in planes:
        if p.key in base['scans']: continue
        holdouts+=polynomial_checks(p)
        minimum=minimize_plane(p,old)
        a,b,z=grid_points(p.domain['bounds'],n)
        values=p.cost(p.map(z).reshape(-1,2)).reshape(n,n)
        supplemental[p.key]=save_case(out,p,minimum,(a,b,z),values,None,n)
    assert len(supplemental)==8
    write(out/'MIXED_RESULTS.json',{'date':'2026-11-13','scans':supplemental,'wall_seconds':time.perf_counter()-start,
          'reason':'2501.17843v3 PDF p14 Fig4 lower panels vary ee-dV with emu-dV/etau-dV; same pairs separately calculated for all existing ground benchmarks'})
    bundle={**base,'scans':{**base['scans'],**supplemental},'components':{
        'base':{'file':'RESULTS.json','sha256':sha(out/'RESULTS.json'),'cases':33},
        'mixed':{'file':'MIXED_RESULTS.json','sha256':sha(out/'MIXED_RESULTS.json'),'cases':8}},
        'status':'COMPLETED_41_AVAILABLE_PLANES_MISSING_CAPABILITIES_EXPLICIT'}
    write(out/'BENCHMARK_RESULTS.json',bundle)
    write(out/'qa/MIXED_POLYNOMIAL_HOLDOUTS.json',{'status':'PASS_MIXED_FLAVOR_POINT_CHECKS','holdouts':holdouts})
    sources.update(read(out/'SOURCE_MANIFEST.json'))
    for p in HERE.glob('*.py'):sources[p.relative_to(ROOT).as_posix()]=sha(p)
    for p in [out/'RESULTS.json',out/'MIXED_RESULTS.json']:
        sources[p.relative_to(ROOT).as_posix()]=sha(p)
    write(out/'BENCHMARK_SOURCE_MANIFEST.json',sources)
    print('Completed 41-case benchmark bundle; base 33-case RESULTS.json unchanged',flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
