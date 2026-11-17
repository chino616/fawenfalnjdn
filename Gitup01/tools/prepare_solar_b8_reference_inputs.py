"""Explicit local ingestion of the already reviewed reference recipe.

Never execute the user's Mathematica/Python files. Copy the four adopted tables
byte-for-byte; parse only numeric probability literals from their named block.
This local input directory is ignored by Git and never installed or uploaded.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probability_table(path):
    text=path.read_text(encoding='utf8')
    start=text.index('8B  ( 2025-12-29)')
    block=text[start:]
    columns=[];locators={}
    for name in ['pEnu','pe','pmu','ptau']:
        match=re.search(r'\b'+name+r'=\{([^}]+)\};',block)
        if match is None:raise ValueError('missing probability column '+name)
        vals=[]
        for item in match[1].split(','):
            number=re.fullmatch(r'\s*([+-]?\d+(?:\.\d+)?)(?:\*10\^([+-]?\d+))?\s*',item)
            if number is None:raise ValueError('not a numeric literal: '+item)
            vals.append(float(number[1])*10.**int(number[2] or 0))
        if len(vals)!=10:raise ValueError('expected10probability nodes')
        columns.append(vals)
        locators[name]='supplied txt line '+str(text[:start+match.start()].count('\n')+1)
    return np.array(columns).T,locators


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--legacy-data',type=Path,required=True)
    ap.add_argument('--reference-root',type=Path,required=True)
    args=ap.parse_args()
    dest=ROOT/'data/benchmarks/solar_b8_reference_2601_19883'
    if dest.exists():raise FileExistsError('keep existing inputs; choose explicit review before replacing '+str(dest))
    txt=args.reference_root/'2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本.txt'
    probabilities,locators=probability_table(txt)
    pairs={'b8_source.txt':'8Bflux_nu.txt','paired_legacy.txt':'8Bflux_Paired.txt',
           'us2_legacy.txt':'8Bflux_eff.txt','xenonnt_legacy.txt':'8Bflux_Eff_XENONnT.txt'}
    tables={new:np.loadtxt(args.legacy_data/old) for new,old in pairs.items()}
    for name,a in tables.items():
        if a.ndim!=2 or a.shape[1]!=2 or not np.all(np.isfinite(a)) or np.any(np.diff(a[:,0])<=0) or np.min(a[:,1])<0:
            raise ValueError('invalid original array '+name)
    dest.mkdir(parents=True)
    files={}
    for new,old in pairs.items():
        original=args.legacy_data/old;path=dest/new;shutil.copyfile(original,path)
        assert sha(path)==sha(original)
        a=tables[new]
        files[new]={'sha256':sha(path),'shape':list(a.shape),'range':[a[0].tolist(),a[-1].tolist()],
            'direct_source':str(original.resolve()),'original_sha256':sha(original),
            'columns':['E_MeV','normalized_shape_per_MeV'] if new=='b8_source.txt' else ['T_keVnr','total_acceptance'],
            'transformation':'byte-identical local adoption',
            'verification':'source spectrum independently matched Bahcall; efficiency files are local historical digitizations, not official numerical releases'}
    path=dest/'flavor_probabilities.txt'
    np.savetxt(path,probabilities,fmt='%.17g',header='E_MeV P_e P_mu P_tau; supplied reference numeric literals; fixed propagation')
    files[path.name]={'sha256':sha(path),'shape':[10,4],'range':[probabilities[0].tolist(),probabilities[-1].tolist()],
        'direct_source':str(txt.resolve()),'original_sha256':sha(txt),'locator':locators,
        'columns':['E_MeV','P_e','P_mu','P_tau'],'transformation':'literal a*10^b parsed into float; no code evaluation',
        'verification':'direct supplied reference table; called PEANUTS in reference, its upstream production not independently certified'}
    card={'schema':'solar_b8_reference_recipe/1','version':'1.0','date':'2026-11-13',
        'identity':'2601Fig4_solar_legacy_recipe_full_trace','scientific_status':'reference recipe reproduced approximately; no claim of official likelihood or exact paper equality',
        'privacy':'LOCAL_ONLY; no upload of original reference materials or these derived local inputs',
        'physics':{'GF_GeV_minus2':1.1664e-5,'sin2thetaW':.2312,'flux_cm2_s':5.69e6,
            'year_days':365.,'seconds_per_day':86400.,'isotope':'Xe131','A':131,'Z':54,
            'kg_per_A_u':1.66054e-27,'kg_per_tonne':1000.,'kinematic_amu_GeV':.9315,
            'nuclear_resource':'data/responses/responses_all.json','nuclear_sha256':sha(ROOT/'data/responses/responses_all.json'),
            'acceptance_minimum_exclusive':.01,'probability_interpolation_order':2,'flavor_flux_nodes':101,
            'flavor_flux_interpolation_order':2,'acceptance_interpolation_order':3,'E_integrand_interpolation_order':3},
        'numerics':{'n_er':41,'n_enu':21},
        'samples':{'paired':{'T_bounds_keVnr':[1.1,3.],'exposure_tyr':1.25,'efficiency':'paired_legacy.txt','energy_guard_gt_keVnr':1.1,'enforce_table_domain':True},
                   'US2':{'T_bounds_keVnr':[.3,3.],'exposure_tyr':1.04,'efficiency':'us2_legacy.txt','energy_guard_gt_keVnr':.31,'enforce_table_domain':True},
                   'xenon':{'T_bounds_keVnr':[.5,3.],'exposure_tyr':3.51,'efficiency':'xenonnt_legacy.txt','energy_guard_gt_keVnr':.5,'enforce_table_domain':False}},
        'statistics':{'order':['paired','US2','xenon'],'D':[3.5,75.,10.7],'sigma_stat':[1.3,28.,3.95],
            'normalization':'one shared alpha','sigma_alpha':.12,'contour_level':4.6,'paper_level_control':4.61,
            'minimum_domain':[-1.,1.],'minimum_grid_nodes':101,'plot_grid_nodes':601,
            'meaning':'Gaussian comparison to fitted signal yields, not raw332/37candidates'},
        'files':files,'provenance':{
            'primary_reference':{'citation':'LI G, SONG C Q, TANG F J, et al. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[J]. Physical Review D,2026,114:055032. arXiv:2601.19883v2.',
                'file':'docs/references/General_CEvNS/2601.19883v2.pdf','locator':'p20Eqs87,88;p22Delta4.61;p23Fig4green',
                'scope':'validation/method context; reference recipe differs from printed Eq88 pull correlation'},
            'notebook':{'citation':'用户提供.260113 CEvNSPyConstrain - 综合版本[CP].本地未发表notebook,2026.',
                'direct_source':str((args.reference_root/'260113 CEvNSPyConstrain - 综合版本.ipynb').resolve()),
                'sha256':sha(args.reference_root/'260113 CEvNSPyConstrain - 综合版本.ipynb'),
                'locator':'cell6L68-78GF/angle/mapping;cell7L119-152fitted-yields/sharedpull/grid;cell21L12Delta4.6'},
            'upstream_recipe':{'citation':'用户提供.2026-01-08 CsI - CONUS - 8B(propagation) 能标限制 - 副本[CP].本地Mathematica及文本.',
                'direct_source':str(txt.resolve()),'sha256':sha(txt),
                'locator':'L3030,L3040-3088efficiency/cut;L3091-3154flavorflux;L3157-3187mass/energy;L3192-3257exposure/flux/integral;L3639,L3694Xe131'},
            'source_spectrum':{'citation':'BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from8B decay[J].Phys.Rev.C,1996,54:411-422.DOI:10.1103/PhysRevC.54.411.',
                'url':'https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt','locator':'829rows,first2columns; shape only; local exact-value comparison recorded in prior audit'},
            'efficiency_papers':[
                {'citation':'BO Z, et al.(PandaX Collaboration).First Indication of Solar8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J].Phys.Rev.Lett.,2024,133:191001.arXiv:2407.10892v3.',
                 'file':'docs/references/Solar_CEvNS/2407.10892v3.pdf','locator':'p3Fig1Totalpaired/US2;1%threshold description;not direct certification of legacy digitized files'},
                {'citation':'APRILE E, et al.(XENON Collaboration).First Indication of Solar8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J].Phys.Rev.Lett.,2024,133:191002.arXiv:2408.02877v2.',
                 'file':'docs/references/Solar_CEvNS/2408.02877v2.pdf','locator':'p3-5NRacceptance;p4Fig1blackcombined;does not prescribe clearing acceptance<=1%'}],
            'nuclear_resource':{'citation':'CEvNS-pyEFT local resource.responses_all.json[DS].User-selected existing shared nuclear table.',
                'locator':'Xe131,np basis p,n;all available shared response channels;no extraKN/spin normalization',
                'verification':'local use authorized; external author release/conversion certification remains unresolved'}},
        'limitations':['SciPy splines are not certified bitwise equivalent to Mathematica Interpolation',
            'fixed reference flavor probabilities; no parameter-dependent SNuDD propagation in this recipe',
            '1%cut is a local reference processing choice; not silently promoted to official XENONnT threshold',
            'reference coarse quadrature preserved; high-precision sensitivity is a separately labeled control']}
    (dest/'analysis.input.json').write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(str(dest))


if __name__=='__main__':main()
