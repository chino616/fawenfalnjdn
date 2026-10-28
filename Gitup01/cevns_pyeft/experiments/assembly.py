"""Stable identities of actual assembled inputs; no callable addresses or repr."""
import inspect
import hashlib
from pathlib import Path
import numpy as np
from .definition import plain
from cevns_pyeft.kernels.fingerprint import canonical


def callable_identity(value):
    obj=value if inspect.isfunction(value) else type(value)
    module=inspect.getmodule(obj)
    path=getattr(module,'__file__',None)
    if not path or not Path(path).is_file():
        raise ValueError('execution components require an inspectable implementation and describe contract')
    return {'module':obj.__module__,'name':obj.__qualname__,
            'implementation_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}


def actual_assembly(model,executor):
    from cevns_pyeft.core.model import ExperimentModel
    if isinstance(model,ExperimentModel):
        record=model.describe()
        fluence=model.source.for_run(model.run)
        samples=[]
        for component in fluence.components:
            grid=np.linspace(*component.support.integration_domain_MeV,65)
            samples.append({'id':component.component_id,'support':plain(component.support),
                'spectrum':component.continuum(grid).tolist(),'lines':plain(component.lines)})
        record['actual_source_samples']=samples
        implementations={name:callable_identity(getattr(model,name)) for name in ('source','interaction','observation')}
    else:
        record=model.describe() if hasattr(model,'describe') else plain(model)
        implementations={name:callable_identity(getattr(model,name)) for name in ('source','interaction','observation') if hasattr(model,name)}
    if hasattr(executor,'describe_execution'):
        execution=executor.describe_execution(model)
    elif hasattr(executor,'__dict__') and vars(executor):
        raise ValueError('stateful executor requires describe_execution(model)')
    else:
        execution={'kind':'stateless_executor','cache_reuse':'requires explicit compiler contract'}
    return canonical({'model':record,'executor':execution,'implementations':implementations,
                      'execution_implementation':callable_identity(executor)})
