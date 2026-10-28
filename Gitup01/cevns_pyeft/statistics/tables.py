"""Coordinate-bearing statistical inputs with explicit legacy schemas."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
from .datasets import BinnedDataset
from .observables import observable


def schema(path,*,dataset_id,axis_unit,observable_unit,edges,analysis_revision=None,profile_id=None):
    value=json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if value.get('schema_version')!=1 or value.get('dataset_id')!=dataset_id:
        raise ValueError('statistical schema dataset/version mismatch')
    if value.get('axis_unit')!=axis_unit or value.get('observable_unit')!=observable_unit:
        raise ValueError('statistical coordinate/observable unit mismatch')
    if not np.array_equal(value.get('bin_edges'),edges):
        raise ValueError('statistical schema bin edges mismatch')
    if analysis_revision is not None and value.get('analysis_revision')!=analysis_revision:raise ValueError('statistical analysis identity mismatch')
    if profile_id is not None and value.get('profile_id')!=profile_id:raise ValueError('statistical profile identity mismatch')
    return value


def csi2017_tables(paths,schema_path,edges,analysis_revision='legacy_25bin_modular_v1'):
    contract=schema(schema_path,dataset_id='CsI2017',axis_unit='PE',observable_unit='counts/bin',edges=edges,analysis_revision=analysis_revision,profile_id='legacy_25bin')
    result={}
    for role in ('data','lower','upper','spectrum'):
        arr=np.loadtxt(paths[role])
        if arr.shape!=(len(edges)-1,2) or not np.all(np.isfinite(arr)):
            raise ValueError(f'CsI2017 {role}: invalid coordinate/value shape')
        x=arr[:,0]
        if np.any(np.diff(x)<=0):raise ValueError(f'CsI2017 {role}: duplicate/unordered coordinates')
        if not np.allclose(x,contract['digitized_coordinates'][role],rtol=0,atol=contract['table_coordinate_tolerance']):
            raise ValueError(f'CsI2017 {role}: coordinate mapping mismatch')
        result[role]=arr[:,1].astype(float)
    data,lower,upper=result['data'],result['lower'],result['upper']
    result['sigma']=np.clip(.5*((upper-data)+(data-lower)),1e-12,None)
    return result


def conus_dataset(experiment):
    definition=experiment.definition;obs=definition.observation;stats=definition.statistics
    refs={r.id:r for r in definition.resources}
    path=experiment.resource_catalog.resolve(refs['observations'])
    contract=schema(experiment.resource_catalog.resolve(refs['observation_schema']),dataset_id=definition.dataset_id,
        axis_unit=obs.unit,observable_unit=stats.observable_unit,edges=obs.edges,analysis_revision=definition.analysis_revision,profile_id="effective119_C3_like_v1")
    if contract.get('profile_id')!='effective119_C3_like_v1' or contract.get('normalization')!='effective119_C3_like_legacy_no_rescaling':
        raise ValueError('CONUS statistical profile/normalization mismatch')
    with path.open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.DictReader(stream)
        fields=reader.fieldnames or []
        if len(set(fields))!=len(fields):raise ValueError('duplicate statistical CSV columns')
        required=[contract[k] for k in ('low_column','high_column','center_column','observed_column','sigma_column')]
        if set(required)-set(fields):raise ValueError('missing statistical coordinate/value columns: '+str(set(required)-set(fields)))
        rows=list(reader)
    if len(rows)!=len(obs.edges)-1 or any(None in row for row in rows):raise ValueError('statistical row/bin count mismatch')
    values={name:np.asarray([float(row[name]) for row in rows]) for name in required}
    if any(not np.all(np.isfinite(arr)) for arr in values.values()):raise ValueError('statistical columns must be finite')
    low,high,center=(values[contract[k]] for k in ('low_column','high_column','center_column'))
    tolerance=contract['coordinate_tolerance_evee'];edges=np.asarray(obs.edges)
    if np.any(np.diff(low)<=0) or np.any(np.diff(center)<=0):raise ValueError('duplicate or unordered statistical coordinates')
    if not np.allclose(low,edges[:-1],rtol=0,atol=tolerance) or not np.allclose(high,edges[1:],rtol=0,atol=tolerance):
        raise ValueError('statistical coordinate/width mapping mismatch')
    if np.any(np.abs(center-.5*(low+high))>contract['digitization_center_tolerance_evee']):raise ValueError('statistical center mapping mismatch')
    for field,expected in [('dataset_id',definition.dataset_id),('profile_id',contract['profile_id']),('axis_unit',obs.unit),('observable_unit',stats.observable_unit)]:
        if field in fields and any(row[field]!=expected for row in rows):raise ValueError(f'statistical {field} mismatch')
    sigma=values[contract['sigma_column']]
    if np.any(sigma<=0):raise ValueError('statistical sigma must be positive')
    return BinnedDataset(definition.dataset_id,values[contract['observed_column']],
        observable(obs.name,stats.observable_unit,obs.edges),uncertainty=sigma,signal_norm_sigma=stats.signal_sigma,
        provenance_path=str(path),metadata={'analysis_revision':definition.analysis_revision,'profile_id':contract['profile_id'],
            'axis_unit':obs.unit,'normalization':contract['normalization'],'content_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'conversion':'none; preserve legacy plotted normalization; combined effective119 once','coordinates_verified':True})
