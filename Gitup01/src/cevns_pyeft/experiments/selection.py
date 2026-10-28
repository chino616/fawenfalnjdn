"""Strict finite selection format; this is not an executable configuration language."""
from dataclasses import dataclass,field
from collections.abc import Mapping
from .definition import frozen_mapping
from .catalog import BUILTIN_CATALOG
import json
import re

@dataclass(frozen=True)
class DatasetSelection:
    id: str
    enabled: bool = True
    backend: str = 'slow'
    numerics: Mapping = field(default_factory=dict)
    def __post_init__(self):
        if not isinstance(self.id,str) or type(self.enabled) is not bool or self.backend not in ('slow','fast','auto') or not isinstance(self.numerics,Mapping):
            raise ValueError('invalid dataset selection')
        object.__setattr__(self,'numerics',frozen_mapping(self.numerics))

@dataclass(frozen=True)
class AnalysisSelection:
    datasets: tuple[DatasetSelection,...]

    def __post_init__(self):
        values=tuple(self.datasets)
        if any(not isinstance(item,DatasetSelection) for item in values) or len({item.id for item in values})!=len(values):
            raise ValueError('invalid or duplicate dataset selections')
        object.__setattr__(self,'datasets',values)

    @classmethod
    def from_mapping(cls,value,*,registry=None):
        catalog = registry if registry is not None else BUILTIN_CATALOG
        if not isinstance(value,Mapping) or set(value)!={'datasets'} or not isinstance(value['datasets'],list):
            raise ValueError('selection requires only a datasets list')
        result,seen=[],set()
        for item in value['datasets']:
            if not isinstance(item,Mapping) or set(item)-{'id','enabled','backend','numerics'} or 'id' not in item:
                raise ValueError('dataset entry requires id and accepts enabled/backend/numerics only')
            key=catalog.canonical_id(item['id'])
            if key in seen:
                raise ValueError(f'duplicate dataset after alias normalization: {key}')
            seen.add(key)
            enabled=item.get('enabled',True)
            if type(enabled) is not bool:
                raise ValueError('enabled must be a boolean')
            backend=item.get('backend','slow')
            definition=catalog.definition(key)
            if backend not in ('slow','fast','auto') or (backend!='auto' and backend not in definition.numerical_profiles):
                raise ValueError(f'{key}: unsupported backend {backend!r}')
            numerics=item.get('numerics',{})
            if not isinstance(numerics,Mapping) or set(numerics)-set(definition.numerical_profiles['slow' if backend=='auto' else backend]):
                raise ValueError(f'{key}: unsupported or unconsumed numerics')
            result.append(DatasetSelection(key,enabled,backend,numerics))
        return cls(tuple(result))


def _scalar(value):
    value=value.strip()
    if value in ('true','false'):
        return value=='true'
    if re.fullmatch(r'[-+]?[0-9]+',value):
        return int(value)
    if re.fullmatch(r'[-+]?[0-9]+(?:\.[0-9]*)?(?:[eE][-+]?[0-9]+)?',value):
        return float(value)
    if value.startswith('"'):
        parsed=json.loads(value)
        if not isinstance(parsed,str): raise ValueError('only scalar strings allowed')
        return parsed
    if re.fullmatch(r"'[^']*'",value): return value[1:-1]
    if not value or any(c in value for c in '{}[]:&*!|>'):
        raise ValueError('unsupported YAML value/structure')
    return value


def parse_selection_yaml(text):
    """Accept the documented block list, scalar fields and nested numerics only."""
    lines=[x.rstrip() for x in text.splitlines() if x.strip() and not x.lstrip().startswith('#')]
    if lines==['datasets: []']: return {'datasets':[]}
    if not lines or lines[0]!='datasets:': raise ValueError('expected datasets: root')
    rows=[]; current=None; nested=False
    for line in lines[1:]:
        if '\t' in line: raise ValueError('tabs are unsupported')
        if line.startswith('  - '):
            current={};rows.append(current);content=line[4:];nested=False
        elif line.startswith('      ') and not line.startswith('       ') and nested:
            content=line[6:]
        elif line.startswith('    ') and not line.startswith('     ') and current is not None:
            content=line[4:];nested=False
        else: raise ValueError(f'unsupported YAML indentation/structure: {line}')
        if ':' not in content: raise ValueError('expected key: value')
        key,value=content.split(':',1)
        target=current['numerics'] if nested else current
        if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',key) or key in target:
            raise ValueError('duplicate or invalid YAML key')
        if key=='numerics' and not value.strip() and not nested:
            current[key]={};nested=True
        else: target[key]=_scalar(value)
    return {'datasets':rows}


def load_selection(path,*,registry=None):
    from pathlib import Path
    return AnalysisSelection.from_mapping(parse_selection_yaml(Path(path).read_text(encoding='utf-8-sig')),registry=registry)
