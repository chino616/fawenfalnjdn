"""Finite legacy-to-canonical resource aliases; no cwd/name guessing."""
from pathlib import Path
import hashlib
ALIASES = {'data/datafiles/COHERENT_eff.txt': 'data/experiments/COHERENT_CsI/CsI2017/detector/COHERENT_eff.txt', 'data/datafiles/COHERENT_data.txt': 'data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_data.txt', 'data/datafiles/COHERENT_lower.txt': 'data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_lower.txt', 'data/datafiles/COHERENT_upper.txt': 'data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_upper.txt', 'data/datafiles/COHERENT_spectrum.txt': 'data/experiments/COHERENT_CsI/CsI2017/statistics/COHERENT_spectrum.txt', 'data/datafiles/CENNS10AnlAEfficiency.txt': 'data/experiments/COHERENT_Ar/Ar2020/detector/CENNS10AnlAEfficiency.txt', 'data/experiments/CsI2017/experiment.yaml': 'data/experiments/COHERENT_CsI/CsI2017/experiment.yaml', 'data/experiments/CsI2017/README.md': 'data/experiments/COHERENT_CsI/CsI2017/README.md', 'data/experiments/CsI2017/statistics/provenance.yaml': 'data/experiments/COHERENT_CsI/CsI2017/statistics/provenance.yaml', 'data/experiments/CsI2021/experiment.yaml': 'data/experiments/COHERENT_CsI/CsI2021/experiment.yaml', 'data/experiments/CsI2021/README.md': 'data/experiments/COHERENT_CsI/CsI2021/README.md', 'data/experiments/CsI2021/statistics/provenance.yaml': 'data/experiments/COHERENT_CsI/CsI2021/statistics/provenance.yaml', 'data/experiments/Ar2020/statistics/provenance.yaml': 'data/experiments/COHERENT_Ar/Ar2020/statistics/provenance.yaml'}

def resolve_resource(root, relative):
    root=Path(root).resolve()
    value=Path(relative)
    if value.is_absolute():
        if not value.resolve().is_relative_to(root):return value.resolve()
        value=value.resolve().relative_to(root)
    key=value.as_posix()
    canonical=ALIASES.get(key,key)
    names=[canonical]+[old for old,new in ALIASES.items() if new==canonical]
    paths=[root/name for name in dict.fromkeys(names)]
    present=[p for p in paths if p.is_file()]
    if len(present)>1:
        hashes={hashlib.sha256(p.read_bytes()).hexdigest() for p in present}
        if len(hashes)>1:raise ValueError('conflicting canonical/legacy resources: '+', '.join(map(str,present)))
    return present[0].resolve() if present else (root/canonical).resolve()
