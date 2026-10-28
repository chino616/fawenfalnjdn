"""Resource roots are explicit and independent of cwd and import depth."""
from pathlib import Path

def resource_root(root=None):
    """A root containing data/, not data/ itself; wheel callers pass it explicitly."""
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[1].parent

def responses_path(root=None):
    return resource_root(root)/'data/responses/responses_all.json'

def experiment_data_root(root=None):
    return resource_root(root)/'data/experiments'
