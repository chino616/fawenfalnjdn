"""Compile one-dimensional model inputs into an operator bilinear kernel."""
from dataclasses import dataclass, asdict
import numpy as np
from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
from cevns_pyeft.contracts.parameters import IntegrationSettings, StateParameters, TheoryPoint
from cevns_pyeft.contracts.prediction import Prediction
from cevns_pyeft.contracts.validation import freeze, plain, readonly
from cevns_pyeft.rates.folding import linear_fold_weights
from .fingerprint import dependency_record, digest


class StaleCompiledKernelError(ValueError):
    pass


@dataclass(frozen=True)
class FastCapabilityReport:
    supported: bool
    reasons: tuple[str, ...]
    representation: str = "operator_bilinear_v1"
    state_requirement: str = "constant, independent of scanned parameters"


def fast_capability(model, *, numerics=None):
    numerics = IntegrationSettings() if numerics is None else numerics
    reasons = []
    if getattr(model.interaction, "coefficient_contract", None) != "operator_bilinear_v1":
        reasons.append("interaction has no operator_bilinear_v1 coefficient representation")
    if not all(callable(getattr(model.interaction, name, None)) for name in ("coefficient_dsigma", "coefficient_values")):
        reasons.append("interaction is missing coefficient evaluation or reconstruction")
    if len(model.binning.axes) != 1:
        reasons.append("compiler requires one observed axis")
    try:
        fluence = model.source.for_run(model.run)
        for component in fluence.components:
            method = getattr(component, "fixed_state_for_fast", None)
            if not callable(method):
                reasons.append(f"{component.component_id}: no fixed-state contract")
                continue
            try:
                state = method()
                if state.is_energy_dependent or state.particle_kind != component.particle_kind:
                    reasons.append(f"{component.component_id}: state is not a matching constant density")
            except (ValueError, TypeError, UnsupportedCapabilityError) as exc:
                reasons.append(str(exc))
    except (ValueError, TypeError) as exc:
        reasons.append(str(exc))
    capability = "sampled_density_1d" if numerics.strategy == "legacy_csi2021_v1" else "bin_probabilities_1d"
    if capability not in model.observation.describe().capabilities:
        reasons.append(f"observation does not implement {capability}")
    return FastCapabilityReport(not reasons, tuple(reasons))


def _prepare(model, numerics):
    # Import lazily: Slow owns the common unit/axis validation, not compilation.
    from cevns_pyeft.core.predict import validate_compatibility
    capability = fast_capability(model, numerics=numerics)
    if not capability.supported:
        raise UnsupportedCapabilityError("; ".join(capability.reasons))
    checked = validate_compatibility(model, parameters=TheoryPoint(), numerics=numerics, backend="slow")
    fluence = checked.fluence
    if not fluence.components:
        raise UnsupportedCapabilityError("Fast compilation requires at least one explicit component")
    energy_grids, rhos = [], []
    for component in fluence.components:
        grid = np.unique(np.r_[np.linspace(*component.support.integration_domain_MeV, numerics.n_enu),
                               component.support.breakpoints_MeV])
        density = np.asarray(component.continuum(grid), float)
        if density.shape != grid.shape or not np.all(np.isfinite(density)) or np.any(density < 0):
            raise ValueError(f"invalid continuum for {component.component_id}")
        query = np.unique(np.r_[grid[grid > 0], [line.energy_MeV for line in component.lines]])
        batch = component.state_at(query, parameters=StateParameters())
        batch.require_coordinates(query, component.particle_kind)
        fixed = component.fixed_state_for_fast()
        if batch.parameter_dependencies or not np.allclose(batch.rho, fixed.rho, rtol=0, atol=1e-12):
            raise UnsupportedCapabilityError(f"{component.component_id}: rho(E) or parameter-dependent state is unsupported")
        energy_grids.append(grid)
        rhos.append(fixed.rho)
    maxima = [max([part.support.integration_domain_MeV[1]] + [line.energy_MeV for line in part.lines]) for part in fluence.components]
    recoil_grids, fold_weights = {}, {}
    for target in model.targets.isotopes:
        maximum = max(model.interaction.kinematics.maximum_recoil_keV(target, energy) for energy in maxima)
        recoil = np.linspace(numerics.recoil_min_keV, max(maximum, numerics.recoil_min_keV * (1 + 1e-12)), numerics.n_er)
        recoil_grids[target.isotope_id] = recoil
        for component in fluence.components:
            fold_weights[(component.component_id, target.isotope_id)] = linear_fold_weights(
                target, model.observation, model.binning, numerics, recoil, component.component_id)
    return {"fluence": fluence, "energy_grids": energy_grids, "rhos": np.asarray(rhos),
            "recoil_grids": recoil_grids, "fold_weights": fold_weights}


def _basis(model, basis_keys):
    keys = tuple(model.interaction.operator_keys) if basis_keys is None else tuple(tuple(key) for key in basis_keys)
    if not keys or len(set(keys)) != len(keys) or any(key not in model.interaction.operator_keys for key in keys):
        raise ValueError("compiled basis must have distinct supported operator keys")
    return keys


def _assert_psd(matrix, scales):
    # Same-dimensional validation uses fixed coefficient scales for numerical
    # conditioning. Channel contributions may have either sign; their sum may not.
    scaled = matrix * scales[:, None] * scales[None, :]
    eigen = np.linalg.eigvalsh(.5 * (scaled + scaled.conj().T))
    magnitude = max(float(np.max(np.abs(eigen))), np.finfo(float).tiny)
    if float(eigen.min()) < -1e-10 * magnitude:
        raise UnsupportedCapabilityError("total coefficient response is not positive semidefinite; legacy clipping cannot be reordered")


def pair_templates(full):
    size = full.shape[3]
    diag = np.stack([full[:, :, :, i, i, :].real for i in range(size)])
    index = np.array([(i, j) for i in range(size) for j in range(i + 1, size)], dtype=int).reshape(-1, 2)
    shape = (0, *full.shape[:3], full.shape[-1])
    real = np.stack([full[:, :, :, i, j, :].real for i, j in index]) if len(index) else np.zeros(shape)
    imag = np.stack([-full[:, :, :, i, j, :].imag for i, j in index]) if len(index) else np.zeros(shape)
    return diag, real, imag, index


def reconstruct_channels(full, coeffs, rhos, *, representation="full", pairs=None):
    bilinear = np.einsum("sab,ifb,jfa->sij", rhos, coeffs.conj(), coeffs, optimize=True)
    if representation == "full":
        return np.einsum("tshijb,sij->tshb", full, bilinear, optimize=True).real
    if representation != "pair":
        raise ValueError("representation must be full or pair")
    diag, real, imag, index = pair_templates(full) if pairs is None else pairs
    output = np.zeros((*full.shape[:3], full.shape[-1]))
    for i in range(len(coeffs)):
        output += diag[i] * bilinear[:, i, i].real[None, :, None, None]
    for k, (i, j) in enumerate(index):
        output += 2 * (real[k] * bilinear[:, i, j].real[None, :, None, None]
                       + imag[k] * bilinear[:, i, j].imag[None, :, None, None])
    return output


@dataclass(frozen=True)
class CompiledKernel:
    model: object
    numerics: IntegrationSettings
    basis_keys: tuple
    full_kernel: np.ndarray
    record: object

    def __post_init__(self):
        object.__setattr__(self, "full_kernel", readonly(self.full_kernel, dtype=complex))
        object.__setattr__(self, "record", freeze(self.record))
        object.__setattr__(self, "basis_keys", tuple(tuple(key) for key in self.basis_keys))
        if self.record.get("schema") != "interface_kernel_v1":
            raise ValueError("unsupported compiled kernel schema")
        if tuple(tuple(k) for k in self.record["basis_keys"]) != self.basis_keys:
            raise ValueError("compiled basis record mismatch")
        if tuple(self.record["target_ids"]) != tuple(t.isotope_id for t in self.model.targets.isotopes):
            raise ValueError("compiled target order mismatch")
        if tuple(self.record["channels"]) != tuple(self.model.interaction.coefficient_channels):
            raise ValueError("compiled channel order mismatch")
        sources = self.model.source.for_run(self.model.run)
        if tuple(self.record["source_ids"]) != tuple(c.component_id for c in sources.components):
            raise ValueError("compiled source order mismatch")
        expected = (len(self.model.targets.isotopes), len(self.record["source_ids"]), len(self.record["channels"]),
                    len(self.basis_keys), len(self.basis_keys), self.model.binning.shape[0])
        if self.full_kernel.shape != expected:
            raise ValueError("compiled kernel axes do not match record")
        if not np.allclose(self.full_kernel, self.full_kernel.swapaxes(3, 4).conj(), rtol=1e-12, atol=0):
            raise ValueError("compiled operator kernel must be Hermitian")

    def predict(self, *, parameters=None, model=None, numerics=None, representation="full"):
        parameters = TheoryPoint() if parameters is None else parameters
        model = self.model if model is None else model
        numerics = self.numerics if numerics is None else numerics
        if parameters.state.values:
            raise UnsupportedCapabilityError("compiled kernels do not consume scanned state parameters")
        try:
            prepared = _prepare(model, numerics)
            current = dependency_record(model, numerics, self.basis_keys, prepared)
        except ValueError as exc:
            if isinstance(exc, UnsupportedCapabilityError):
                raise
            raise StaleCompiledKernelError(str(exc)) from exc
        if digest(current) != self.record["dependency_fingerprint"]:
            raise StaleCompiledKernelError("physical inputs, resources, code or numerical settings differ; recompile")
        coeffs = model.interaction.coefficient_values(parameters, self.basis_keys)
        channels = reconstruct_channels(self.full_kernel, coeffs, prepared["rhos"], representation=representation)
        summed = channels.sum(axis=2)
        scale = max(float(np.max(np.abs(summed))), np.finfo(float).tiny)
        if np.any(summed < -1e-12 * scale):
            raise ValueError("negative reconstructed event counts beyond floating point roundoff")
        parts = {(source.component_id, target.isotope_id): np.maximum(summed[t, s], 0)
                 for t, target in enumerate(model.targets.isotopes) for s, source in enumerate(prepared["fluence"].components)}
        record = model.describe()
        record["theory_point"] = {"wc_triplets": plain(parameters.wc_triplets), "include_sm": parameters.include_sm,
                                  "sin2thetaW": parameters.sin2thetaW, "state_parameters": plain(parameters.state.values)}
        return Prediction(sum(parts.values(), np.zeros(model.binning.shape)), model.binning, parts,
            {"source": prepared["fluence"].normalization_record,
             "number_of_nuclei": {t.isotope_id: t.number_of_nuclei for t in model.targets.isotopes},
             "external_rhos": prepared["rhos"], "selection": model.observation.describe().as_dict()},
            record, {**asdict(numerics), "backend": "fast", "representation": representation,
                     "kernel_schema": "interface_kernel_v1", "kernel_fingerprint": self.record["dependency_fingerprint"]},
            {"channel_counts": channels, "roundoff_clipped_bins": int(np.sum(summed < 0))})


def compile_fast(model, *, numerics=None, basis_keys=None):
    numerics = IntegrationSettings() if numerics is None else numerics
    prepared = _prepare(model, numerics)
    keys = _basis(model, basis_keys)
    interaction = model.interaction
    components = prepared["fluence"].components
    full = np.zeros((len(model.targets.isotopes), len(components), len(interaction.coefficient_channels),
                     len(keys), len(keys), model.binning.shape[0]), complex)
    scales = np.array([10.0 ** (-key[0]) for key in keys])
    for t, target in enumerate(model.targets.isotopes):
        recoil = prepared["recoil_grids"][target.isotope_id]
        for r, value in enumerate(recoil):
            all_energies = []
            for grid, component in zip(prepared["energy_grids"], components):
                minimum = interaction.kinematics.minimum_energy_MeV(target, float(value))
                all_energies.extend(grid[(grid >= minimum) & (grid > 0)].tolist())
                all_energies.extend(line.energy_MeV for line in component.lines if line.energy_MeV >= minimum)
            query = np.unique(all_energies)
            if not query.size:
                continue
            cross = interaction.coefficient_dsigma(target=target, energy_MeV=query, recoil_keV=float(value), basis_keys=keys)
            expected = (len(query), len(interaction.coefficient_channels), len(keys), len(keys))
            if cross.shape != expected or not np.all(np.isfinite(cross)):
                raise ValueError("coefficient cross-section axes/finiteness mismatch")
            for s, component in enumerate(components):
                grid = prepared["energy_grids"][s]
                minimum = interaction.kinematics.minimum_energy_MeV(target, float(value))
                energy = grid[(grid >= minimum) & (grid > 0)]
                integrated = np.zeros(expected[1:], complex)
                if energy.size:
                    values = component.continuum(energy)
                    integrated = np.trapezoid(cross[np.searchsorted(query, energy)] * values[:, None, None, None], energy, axis=0)
                for line in component.lines:
                    if line.energy_MeV >= minimum:
                        integrated += line.fluence_per_cm2 * cross[np.searchsorted(query, line.energy_MeV)]
                _assert_psd(integrated.sum(axis=0), scales)
                full[t, s] += integrated[..., None] * prepared["fold_weights"][(component.component_id, target.isotope_id)][r]
        full[t] *= target.number_of_nuclei
    full = .5 * (full + full.swapaxes(3, 4).conj())
    dependencies = dependency_record(model, numerics, keys, prepared)
    record = {"schema": "interface_kernel_v1", "dependency_fingerprint": digest(dependencies), "dependencies": dependencies,
              "target_ids": [t.isotope_id for t in model.targets.isotopes], "source_ids": [c.component_id for c in components],
              "channels": list(interaction.coefficient_channels), "basis_keys": [list(key) for key in keys],
              "axis_order": ["target", "source", "channel", "operator_i", "operator_j", "observed_bin"],
              "pair_convention": "pair_im=-Im(H_ij); contribution=2Re(B_ij)pair_re+2Im(B_ij)pair_im",
              "state_treatment": "constant external rho; no scanned state parameters", "normalization": "actual nucleus counts and detector fluence"}
    return CompiledKernel(model, numerics, keys, full, record)
