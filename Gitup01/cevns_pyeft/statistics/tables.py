"""Coordinate-bearing statistical inputs with explicit legacy schemas."""
from pathlib import Path
import json
import numpy as np


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
