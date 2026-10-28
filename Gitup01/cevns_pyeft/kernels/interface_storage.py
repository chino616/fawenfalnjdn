"""One-file interface kernel format, distinct from legacy Fast templates."""
from dataclasses import asdict
from pathlib import Path
import json
import numpy as np
from cevns_pyeft.contracts.parameters import IntegrationSettings
from cevns_pyeft.contracts.validation import plain
from .compiler import CompiledKernel, StaleCompiledKernelError, _prepare, pair_templates
from .fingerprint import canonical, dependency_record, digest


def save_compiled_kernel(path, compiled):
    if not isinstance(compiled, CompiledKernel):
        raise TypeError("expected CompiledKernel")
    destination = Path(path)
    if destination.suffix != ".npz":
        raise ValueError("compiled kernel path must end in .npz")
    diag, real, imag, index = pair_templates(compiled.full_kernel)
    arrays = dict(full_kernel=compiled.full_kernel, diag=diag, pair_re=real, pair_im=imag, pair_index=index)
    metadata = {"schema": "interface_kernel_v1", "record": plain(compiled.record),
                "numerics": asdict(compiled.numerics),
                "array_content": {name: canonical(value) for name, value in arrays.items()}}
    with destination.open("wb") as handle:
        np.savez_compressed(handle, metadata=np.array(json.dumps(metadata, sort_keys=True, allow_nan=False)), **arrays)


def load_compiled_kernel(path, *, model, numerics=None):
    with np.load(path, allow_pickle=False) as stored:
        if "metadata" not in stored:
            raise StaleCompiledKernelError("legacy kernel has no interface dependency fingerprint; explicit legacy loader required")
        metadata = json.loads(str(stored["metadata"].item()))
        if metadata.get("schema") != "interface_kernel_v1":
            raise StaleCompiledKernelError("unsupported interface kernel schema")
        record = metadata["record"]
        if digest(record["dependencies"]) != record.get("dependency_fingerprint"):
            raise ValueError("kernel dependency record fingerprint is corrupt")
        arrays = {name: np.array(stored[name]) for name in ("full_kernel", "diag", "pair_re", "pair_im", "pair_index")}
        if any(canonical(array) != metadata["array_content"].get(name) for name, array in arrays.items()):
            raise ValueError("kernel array content hash mismatch")
        expected_pairs = pair_templates(arrays["full_kernel"])
        if any(not np.array_equal(value, arrays[name]) for name, value in zip(("diag", "pair_re", "pair_im", "pair_index"), expected_pairs)):
            raise ValueError("full/pair templates are inconsistent")
    saved_numerics = IntegrationSettings(**metadata["numerics"])
    numerics = saved_numerics if numerics is None else numerics
    try:
        prepared = _prepare(model, numerics)
        current = dependency_record(model, numerics, tuple(tuple(k) for k in record["basis_keys"]), prepared)
    except ValueError as exc:
        raise StaleCompiledKernelError(str(exc)) from exc
    if digest(current) != record["dependency_fingerprint"]:
        raise StaleCompiledKernelError("saved physical dependencies do not match this model; rebuild")
    return CompiledKernel(model, numerics, tuple(tuple(k) for k in record["basis_keys"]), arrays["full_kernel"], record)
