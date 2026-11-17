"""Create-only solar NSI inputs from explicitly pinned public distribution files.

Run after downloading the two source archives into the documented evidence dir.
No external Python is imported/executed. Previous SM inputs stay read-only.
"""
from pathlib import Path
import hashlib,json,shutil,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'outputs/solar_b8_nsi/20261112_fig4_run1/source_evidence'
DATA=ROOT/'data/benchmarks/solar_b8_nsi_2601_19883'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')


def main():
    if DATA.exists() and any(DATA.iterdir()):raise FileExistsError('create-only NSI input directory')
    upstream=json.loads((EVIDENCE/'UPSTREAM.json').read_text(encoding='utf8'))
    DATA.mkdir(parents=True,exist_ok=True)
    files={}
    for composition,tag in [('gs98','gs98'),('agss09','agss09met')]:
        production=EVIDENCE/f'peanuts_Data_nudistr_b16_{composition}.dat'
        structure=EVIDENCE/f'magnus_src_magnus_data_solar_models_b16_{tag}.dat'
        a=np.loadtxt(production);b=np.loadtxt(structure)
        # Production is tabulated on the inner 1000 of the structure's2000
        # matching radius nodes. Select those exact rows; no interpolation or
        # extrapolation from a different solar model is introduced.
        indices=np.searchsorted(b[:,0],a[:,0])
        if np.any(indices>=len(b)) or not np.array_equal(a[:,0],b[indices,0]):
            raise ValueError('solar tables need an explicitly reviewed radial mapping')
        b=b[indices]
        # B16 columns: r, log10(ne/N_A), zone mass, ..., B8 production (col9).
        # rho*N_A is the baryon-density approximation (1u per baryon).
        # Charge neutrality: nn/N_A = rho[g/cm3] - ne/N_A. This is a project
        # derivation from sourced densities, NOT an official neutron table.
        ne=10**a[:,2];nn=b[:,1]-ne
        if np.any(nn<0):raise ValueError('negative derived solar neutron density')
        array=np.column_stack([a[:,0],ne,nn,a[:,8]])
        name=f'solar_b16_{composition}_profile.txt'
        np.savetxt(DATA/name,array,fmt='%.15g',header='r_Rsun ne_mol_cm3 nn_mol_cm3 B8_production_profile_arbitrary\n'
            'Sources: Vinyoles et al. ApJ835(2017)202; pinned PEANUTS col1,3,9 + pinned Magnus mass density.\n'
            'nn/N_A = rho_mass - ne/N_A (baryon mass=1u approximation); no r^2 factor; normalize integral in dr.\n'
            'See nsi.input.json for full citations, exact original locations, direct secondary source status and hashes.')
        for src in [production,structure]:shutil.copyfile(src,DATA/src.name)
        files[name]={'sha256':sha(DATA/name),'shape':list(array.shape),'ranges':np.array([array.min(axis=0),array.max(axis=0)]).tolist(),
            'production_raw':production.name,'production_sha256':sha(production),'structure_raw':structure.name,'structure_sha256':sha(structure),
            'derived_neutron_density':'nn/N_A=rho_mass - ne/N_A; neutral matter, baryon mass1u; not a printed primary neutron array'}
    reference={
        'paper2601':{'citation':'LI G, SONG C Q, TANG F J, et al. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[J]. Physical Review D, 2026, 114: 055032. arXiv:2601.19883v2.',
            'file':'docs/references/General_CEvNS/2601.19883v2.pdf','locator':'p19 Eq84; p20 Eqs87,88 (three independent .12 pulls, percentages); p22 Eq95 mapping and 2-parameter Delta chi2=4.61; p23 Fig4 green region'},
        'propagation':{'citation':'LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024.',
            'file':'docs/references/General_CEvNS/2409.04703v2.pdf','locator':'p5 explicitly includes NSI in propagation; p10 Appendix B EqsB4-B9, two-flavor adiabatic average, theta13_m=theta13, no Earth matter. For ee-only: epsilonD_q=-cos²theta13 epsilonee_q/2, epsilonN=0; sum u+d potentials.'},
        'b16':{'citation':'VINYOLES N, SERENELLI A M, VILLANTE F L, et al. A new generation of standard solar models[J]. Astrophysical Journal, 2017, 835: 202. DOI:10.3847/1538-4357/835/2/202. arXiv:1611.09867.',
            'url':'https://doi.org/10.3847/1538-4357/835/2/202','locator':'B16 GS98 / AGSS09 numerical model tables; n_e and B8 production from nudistr columns1,3,9; mass density from struct column4 (distributed as trimmed column2)'},
        'peanuts':{'citation':'GONZALO T E, LUCENTE M. PEANUTS: a software for the automatic computation of solar neutrino flux and its propagation within Earth[J]. European Physical Journal C, 2024, 84:119. DOI:10.1140/epjc/s10052-024-12423-3. arXiv:2303.15527.',
            'url':'https://github.com/michelelucente/PEANUTS/tree/'+upstream['peanuts_commit'],
            'commit':upstream['peanuts_commit'],'locator':'Data/nudistr_b16_gs98.dat and agss09.dat headers/columns; peanuts/solar.py SolarModel and solar_flux_mass use normalized integral in dr, not extra r²; examples/solar_test.yaml Neutrinos gives adopted oscillation inputs',
            'verification':'direct pinned software distribution verified; original B16 author URL not independently fetched this run'},
        'magnus':{'citation':'BUSTAMANTE M. Magnus: public tabulated solar model distribution[DS/OL]. Fixed Git commit, accessed2026-11-12.',
            'url':'https://github.com/mbustama/Magnus/tree/'+upstream['magnus_commit'],'commit':upstream['magnus_commit'],
            'locator':'src/magnus/data/solar_models/b16_gs98.dat and b16_agss09met.dat; tools/build_solar_model_tables.py. Header supplies original source URL and original SHA256.',
            'verification':'secondary transcription explicitly adopted; primary URL returned403/HTML challenge; original 47-column author-file equivalence not independently certified'},
    }
    for ref in reference.values():
        if 'file' in ref:ref['sha256']=sha(ROOT/ref['file'])
    base=ROOT/'data/benchmarks/solar_b8_singlebin_2601_19883'
    card={'schema':'solar_b8_ee_vector_nsi/1','version':'3.3','date':'2026-11-12',
        'base_singlebin_card':str(base.relative_to(ROOT)/'analysis.input.json').replace('\\','/'),
        'base_card_sha256':sha(base/'analysis.input.json'),'base_input_policy':'read-only reuse source/target/Total efficiencies; never old multibin Qy/D/B',
        'solar_model':'B16-GS98','solar_profile':'solar_b16_gs98_profile.txt','alternative_profile':'solar_b16_agss09_profile.txt',
        'files':files,'oscillation':{'theta12_rad':.583638,'theta13_rad':.149575,'dm21_eV2':7.42e-5,
            'source':'PEANUTS pinned examples/solar_test.yaml Neutrinos; explicit project benchmark selection, paper2601 does not print its oscillation input card',
            'theta23_and_delta':'not needed: mu/tau have equal SM cross sections in real ee-only vector NSI subspace'},
        'physics':{'sin2thetaW':.23857,'flux_cm2_s':5.46e6,'primary_propagation':'nsi_msw','comparison_propagation':'sm_fixed',
            'matter_potential':'Vee=sqrt(2)*G_F*[ne+(2ne+nn)*eu+(ne+2nn)*ed]',
            'nsi_mapping':'C61q_NSI=-sqrt(2)*G_F*epsilonee_qV; neutrinos, SM+NSI, others zero',
            'radial_quadrature_order_per_panel':8,'radial_panels_Rsun':[.02,.05,.1,.2,.4],
            'neutron_density_approximation':'nn=rho_mass*N_A-ne; one atomic mass unit per baryon',
            'earth_matter':False,'adiabatic_two_flavor':True,'theta13_m_equals_vacuum':True},
        'statistics':{'source':'paper2601 PDF p20 Eq88 and exact printed percentages',
            'independent_pulls':True,'pull_sigma':.12,'delta_chi2_90_2d':4.61,
            'D':[3.5,75.,10.7],'sigma_stat':[3.5*.371,75*.373,10.7*.369],
            'data_meaning':'fitted signal yields; no explicit background or raw-count Poisson',
            'minimum':'joint parameter minimum; do not subtract SM chi2 or sum separately minimized datasets'},
        'xenon_tail':{'primary':'flat_sensitivity','definition':'epsilon(last) constant for T>last up to3keV; project assumption, not experimental data',
            'sensitivity_modes':['zero','unit','profile_bounds'],'profile_bounds':'at each parameter point use allowed [known,known+unselected_tail] signal interval; additional unpenalized unknown-tail nuisance, not exact paper likelihood'},
        'references':reference,'status':'SOURCE_SPEC_READY_FOR_IMPLEMENTATION; paper input-card and neutron primary-source certification limitations retained'}
    write(DATA/'nsi.input.json',card)
    old=json.loads((base/'fitted_yields.json').read_text(encoding='utf8'))
    for sample,sigma in zip(old['samples'],card['statistics']['sigma_stat']):old['samples'][sample]['sigma_stat']=sigma;old['samples'][sample]['source']='paper2601 PDF p20 Eq88: measured count times37.1% /37.3% /36.9% respectively; yields from original experimental fits'
    old['data_origin']='exact paper2601 percentages, not previous rounded TableII sigmas';write(DATA/'fitted_yields.json',old)
    (DATA/'README.md').write_text('# 太阳⁸B电子味矢量NSI：独立参数与传播输入\n\n'
        '[nsi.input.json](nsi.input.json)拥有标准引文、原文公式位置、实际数值/范围、处理选择与哈希。[fitted_yields.json](fitted_yields.json)使用2601 p20 Eq88精确百分比误差及三个独立12% pull。\n\n'
        '主传播输入：[GS98派生profile](solar_b16_gs98_profile.txt)；模型敏感性：[AGSS09派生profile](solar_b16_agss09_profile.txt)。列为r/Rsun、ne/N_A、nn/N_A（mol/cm³）、⁸B产生区profile（归一化前）；实际原始分发表保留在同目录，文件名和哈希见card。\n\n'
        '电子密度和产生区来自固定PEANUTS版本；质量密度来自固定Magnus分发表（明确是二手转录）。nn由rho_mass*N_A-ne推导，采用每重子1u近似，不冒充原文提供的中子表；原作者结构表官网本轮不可直接取得。\n\n'
        '复用旧单bin源谱/天然Xe/效率的固定文件；不改其原卡，不读多bin数据。核响应仍按已选本地表约定。配置生成器：[prepare_solar_b8_nsi.py](../../../tools/prepare_solar_b8_nsi.py)。\n',encoding='utf8')
    print('Created',DATA,'profiles',[(k,v['shape']) for k,v in files.items()],flush=True)


if __name__=='__main__':main()
