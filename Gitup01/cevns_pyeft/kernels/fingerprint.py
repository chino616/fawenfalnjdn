"""Content fingerprints for actual inputs consumed by the model compiler."""
from dataclasses import asdict
from importlib import resources
from pathlib import Path
import hashlib
import inspect
import json
import numpy as np
from cevns_pyeft.contracts.validation import plain


def canonical(value):
    if isinstance(value, np.ndarray):
        array = np.ascontiguousarray(value)
        dtype = array.dtype.newbyteorder("<")
        return {"shape": list(array.shape), "dtype": dtype.str,
                "sha256": hashlib.sha256(array.astype(dtype, copy=False).tobytes()).hexdigest()}
    if isinstance(value, dict) or hasattr(value, "items"):
        result = {}
        for key, item in value.items():
            # Paths are provenance, not physical identity. For resources the
            # content is authoritative, including same-path edits.
            if key in ("path", "file", "file_path"):
                path = Path(item)
                result["resource_content_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            else:
                result[str(key)] = canonical(item)
        return result
    if isinstance(value, (list, tuple)):
        return [canonical(item) for item in value]
    if isinstance(value, Path):
        return {"resource_content_sha256": hashlib.sha256(value.read_bytes()).hexdigest()}
    return plain(value)


def digest(value):
    return hashlib.sha256(json.dumps(canonical(value), sort_keys=True, allow_nan=False, separators=(",", ":")).encode()).hexdigest()


def implementation_hashes(model):
    package = resources.files("cevns_pyeft")
    names = ["contracts/parameters.py", "contracts/source.py", "contracts/interaction.py", "contracts/observation.py",
             "foundation/constants.py", "foundation/units.py", "nuclear/response.py", "theory/kinematics.py",
             "theory/li2026/coefficients.py", "theory/li2026/responses.py", "theory/li2026/left_to_ci.py",
             "theory/li2026/flavor.py", "theory/li2026/operators.py", "theory/li2026/lec.py",
             "theory/li2026/amplitude.py", "rates/folding.py", "kernels/compiler.py", "kernels/fingerprint.py",
             "kernels/interface_storage.py"]
    result = {name: hashlib.sha256(package.joinpath(name).read_bytes()).hexdigest() for name in names}
    for obj in (model.source, model.interaction, model.observation,
                getattr(model.observation, "response", None), getattr(model.observation, "efficiency", None)):
        if obj is None:
            continue
        module = inspect.getmodule(type(obj))
        try:
            source = inspect.getsource(module).encode()
        except (OSError, TypeError):
            continue
        result[type(obj).__module__] = hashlib.sha256(source).hexdigest()
    return result


def dependency_record(model, numerics, basis_keys, prepared):
    source_record = model.source.describe().as_dict()
    interaction_record = model.interaction.describe().as_dict()
    response_path = interaction_record.get("resources", {}).get("path")
    if response_path:
        actual = hashlib.sha256(Path(response_path).read_bytes()).hexdigest()
        expected = interaction_record["resources"].get("nuclear_responses_sha256")
        if expected and actual != expected:
            raise ValueError("nuclear resource changed since model construction; rebuild the interaction snapshot")
    return canonical({"schema": "interface_kernel_v1", "coefficient_contract": model.interaction.coefficient_contract,
        "source": source_record, "run": asdict(model.run),
        "fluence": [{"id": c.component_id, "particle_kind": c.particle_kind, "support": asdict(c.support),
                     "grid_MeV": grid, "continuum": c.continuum(grid), "lines": [asdict(line) for line in c.lines],
                     "state_capability": "constant_parameter_independent_external_rho"}
                    for c, grid in zip(prepared["fluence"].components, prepared["energy_grids"])],
        "targets": {"isotopes": [asdict(t) for t in model.targets.isotopes], "composition": model.targets.composition_record},
        "interaction": interaction_record, "observation": model.observation.describe().as_dict(),
        "observed_inputs": prepared["fold_weights"],
        "axes": [{"name": a.name, "unit": a.unit, "edges": a.edges, "clock": a.clock} for a in model.binning.axes],
        "basis_keys": basis_keys, "coefficient_units": [f"GeV^{4-key[0]}" for key in basis_keys],
        "channels": model.interaction.coefficient_channels, "numerics": asdict(numerics),
        "implementations": implementation_hashes(model)})
