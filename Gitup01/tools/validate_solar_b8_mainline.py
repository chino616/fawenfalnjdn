"""Read-only package/phase/preservation checks for the canonical SM benchmark."""
from pathlib import Path
import hashlib,importlib.util,json,re,shutil,sys,tempfile
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
OUT=ROOT/'outputs/solar_b8_sm/20261107_run1'
from cevns_pyeft.experiments.input_package import validate_package
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.runtime import predict_experiment
from jsonschema import Draft202012Validator
import numpy as np

def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

manifest=read(OUT/'MAINLINE_DOCUMENTS.json')
qa_path=ROOT/'workflows/cevns-pyeft/qa/validate_phase_contract.py'
spec=importlib.util.spec_from_file_location('phaseqa',qa_path);qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
phases=[];errors=[];selected=[]
for name in manifest['phase_reports']:
    path=ROOT/name
    if '```json phase-result' not in path.read_text(encoding='utf8'):continue
    record=qa.read_record(path);e=qa.validate_record(record,artifact_root=ROOT)
    phases.append({'file':name,'phase':record['phase'],'machine_gate':record['machine_gate'],'errors':e})
    errors.extend(e)
packages=[];portability=[]
for family,dataset in [('XENONnT','XENONnT_2024_SolarB8'),('PandaX4T','PandaX4T_2024_US2')]:
    path=ROOT/'data/experiments'/family/dataset;run=ROOT/'workflows/cevns-pyeft/runs'/family/dataset
    result=validate_package(path);packages.append({'dataset':dataset,'status':result['status'],'errors':result['errors']})
    errors.extend(result['errors'])
    execution=read(OUT/dataset/'SM_RESULT.json')
    exp=load_experiment_package(path)
    assert exp.physics_fingerprint==execution['physics_fingerprint']
    assert sha(path/'experiment.input.yaml')==execution['input_package_sha256']
    assert sha(path/'experiment.resources.npz')==execution['resource_archive_sha256']
    assert execution['convergence']['passed']
    for record_name,schema_name in [('P01_EVIDENCE_LEDGER.yaml','evidence-ledger.schema.yaml'),('P03_PHYSICS_CONTRACT.yaml','physics-contract.schema.yaml')]:
        check=Draft202012Validator(read(ROOT/'workflows/_shared/schemas'/schema_name))
        e=[error.message for error in check.iter_errors(read(run/record_name))]
        errors.extend(e)
    evidence=read(run/'P01_EVIDENCE_LEDGER.yaml')
    claims={row['claim_id']:row for row in evidence['claims']}
    assert len(claims)==len(evidence['claims']), 'Duplicate evidence claim'
    for row in evidence['claims']:
        if row['claim_id'].startswith('SM20261107-'):
            assert set(row.get('input_claims',[]))<=set(claims), row['claim_id']
    package=read(path/'experiment.input.yaml')
    arrays=[row for row in evidence['claims'] if row['claim_id'].startswith('SM20261107-A')]
    assert len(arrays)==len(package['resources']['arrays'])
    with np.load(path/'experiment.resources.npz',allow_pickle=False) as numerical:
        for row in arrays:
            value=row['value'];values=numerical[value['key']]
            assert list(values.shape)==value['shape']
            assert hashlib.sha256(values.tobytes(order='C')).hexdigest()==value['sha256_raw_c_order']
    assert set(row['claim_id'] for row in arrays)<=set(claims['SM20261107-RESULT']['input_claims'])
    assert 'SM20261107-MODEL' in claims['SM20261107-RESULT']['input_claims']
    # A relocated machine pair must execute without workflows, raw releases or adjacent tables.
    with tempfile.TemporaryDirectory(prefix='solar_pkg_',dir=OUT) as temp:
        directory=Path(temp)
        assert directory.resolve().is_relative_to(OUT.resolve())
        for name in ['experiment.input.yaml','experiment.resources.npz']:shutil.copy2(path/name,directory/name)
        copy=load_experiment_package(directory)
        prediction=predict_experiment(copy,numerics={'n_er':9,'n_enu':12})
        assert set(copy.resolved_resources)=={'package_input','package_arrays'}
        assert prediction.counts.shape==((3,) if family=='XENONnT' else (27,))
        assert np.isfinite(prediction.counts).all() and np.all(prediction.counts>=0)
        portability.append({'dataset':dataset,'machine_files':2,'runtime_execution':'PASS','scope':'small-grid portability contract only, not the scientific reference'})
    selected.extend([str((path/name).relative_to(ROOT)).replace('\\','/') for name in ['experiment.physics.md','experiment.physics.summary.md','README.md']])
old=ROOT.parent/'重构/20261106_Onboarding_provenance_revision'
preserved=read(old/'PRESERVED_VERSIONS.json')
assert all(sha(Path(name))==expected for name,expected in preserved.items())
for row in read(old/'DATA_FILES.json'):
    assert sha(ROOT/row['file'])==row['sha256'],row['file']
selected+=sorted({name for name in manifest['modified']+manifest['created'] if name.endswith('.md')})
selected+=['workflows/cevns-pyeft/runs/README.md','tools/README.md','tests/README.md']
selected=sorted(set(selected))
from tools.validate_docs import audit,link_targets
current=[name for name in selected if not name.startswith('outputs/')]
output_navigation=[name for name in selected if name.startswith('outputs/')]
assert set(output_navigation)=={'outputs/README.md','outputs/solar_b8_sm/README.md','outputs/solar_b8_sm/20261107_run1/README.md'}
docs=audit(ROOT,files=current)
# The general auditor deliberately quarantines all outputs. Check only the three
# explicitly maintained navigation files here, without changing that policy.
navigation_links=[]
for name in output_navigation:
    source=ROOT/name
    for line,raw in link_targets(source.read_text(encoding='utf8')):
        value=raw.strip().strip('<>')
        if re.match(r'^(https?:|mailto:|data:|#)',value):continue
        target=(source.parent/unquote(value.split('#',1)[0])).resolve()
        row={'file':name,'line':line,'target':raw,'status':'PASS' if target.exists() else 'BROKEN'}
        navigation_links.append(row)
        if not target.exists():errors.append(row)
docs['explicit_output_navigation']={'documents':output_navigation,'links':navigation_links}
errors.extend(docs['broken_current_links'])
save(OUT/'DOC_LINKS.json',docs)
save(OUT/'DOC_SELECTION.json',selected)
save(OUT/'PHASE_VALIDATION.json',{'reports':len(phases),'phases':phases,'errors':[p for p in phases if p['errors']]})
report={'date':'2026-11-07','scope':'canonical package, runtime, numerical convergence, source/evidence schema, links and preservation',
        'packages':packages,'phase_reports':len(phases),'portable_machine_pairs':portability,'old_core_solar_reports_preserved':len(preserved),
        'original_numeric_files_preserved':45,'docs_checked':docs['markdown_documents'],'links_checked':docs['local_links'],
        'errors':errors,'actual_test_result':read(OUT/'TEST_RESULTS.json'),
        'scientific_delivery':'PARTIAL: public response precision retained; PandaX Ne spectrum BLOCKED',
        'default_global_activation':'NOT_PERFORMED; explicit package/scoped Catalog standard Runtime is connected'}
save(OUT/'VALIDATION.json',report)
print(json.dumps({key:report[key] for key in ['packages','phase_reports','old_core_solar_reports_preserved','docs_checked','links_checked','errors']},ensure_ascii=False))
raise SystemExit(bool(errors))
