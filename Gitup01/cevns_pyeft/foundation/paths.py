"""Resource roots are explicit and independent of cwd and import depth."""
from pathlib import Path

def resource_root(root=None):
    """A root containing data/, not data/ itself; wheel callers pass it explicitly."""
    if root is not None:
        return Path(root).resolve()
    package=Path(__file__).resolve().parents[1]
    source=package.parent
    # Editable/source installs use the canonical data tree. Wheels carry a
    # build-generated copy of declared formal packages, never absolute paths.
    if (source/'data').is_dir():
        return source
    bundled=package/'_data'
    return bundled if (bundled/'data').is_dir() else source

def responses_path(root=None):
    return resource_root(root)/'data/responses/responses_all.json'

def experiment_data_root(root=None):
    return resource_root(root)/'data/experiments'
