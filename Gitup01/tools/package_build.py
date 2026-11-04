"""Setuptools hook: bundle declared formal datasets without a second source copy."""
from pathlib import Path
import json
import shutil
from setuptools.command.build_py import build_py


class BuildWithDatasetPackages(build_py):
    def run(self):
        super().run()
        root=Path(__file__).resolve().parents[1]
        registry=json.loads((root/'cevns_pyeft/experiments/dataset_registry.json').read_text('utf8'))
        destination=Path(self.build_lib)/'cevns_pyeft/_data'
        names={'experiment.input.yaml','experiment.resources.npz','experiment.physics.md'}
        for entry in registry['datasets']:
            if not entry['installed'] or entry['status']!='active':continue
            records=[r['path'] for r in entry['owned_files'] if Path(r['path']).name in names]
            if not records:continue
            if {Path(p).name for p in records}!=names:
                raise ValueError('formal dataset distribution requires all three files: '+entry['dataset_id'])
            for name in records:
                source=root/name
                if not source.is_file():raise FileNotFoundError(source)
                target=destination/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source,target)
