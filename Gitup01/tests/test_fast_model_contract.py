from dataclasses import dataclass, replace
from pathlib import Path
import json
import numpy as np
import pytest

from cevns_pyeft.contracts import IntegrationSettings, TheoryPoint, StateParameters, IncidentStateBatch
from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
from cevns_pyeft.contracts.validation import plain
from cevns_pyeft.core.predict import predict
from cevns_pyeft.experiments.coherent.csi2021 import make_csi2021_model
from cevns_pyeft.kernels.compiler import compile_fast, fast_capability, StaleCompiledKernelError
from cevns_pyeft.kernels.interface_storage import save_compiled_kernel, load_compiled_kernel
from cevns_pyeft.sources.composable import ScaledSource, IntegratedFluenceSource
from cevns_pyeft.contracts.source import DetectorFluence, IntegratedRunReference
from cevns_pyeft.detectors.csi2021 import ConstantEfficiency
from cevns_pyeft.targets import csi_target_inventory
from cevns_pyeft.theory.li2026.amplitude import flavor_kernel_onebody_li2026
from cevns_pyeft.theory.li2026.coefficients import differential_coefficients, CHANNELS
from cevns_pyeft.theory.li2026.operators import LI2026_OPERATOR_SPECS
from cevns_pyeft.foundation.constants import GEV_INV2_TO_CM2, AMU_GEV
from cevns_pyeft.nuclear.response import ResponseDB
from tools.refactor.freeze_baseline import points, GRIDS

ROOT = Path(__file__).resolve().parents[1]
RESPONSE = ROOT / "data/responses/responses_all.json"


def lnv_point():
    a = np.array([[0, 2e-8j, -1e-8], [3e-8, 0, .5e-8j], [1e-8, -2e-8j, 0]], complex)
    return {(7, 3, "u"): a, (7, 4, "d"): a * (.3 + .2j), (7, 5, "u"): a * .4j}


@pytest.fixture(scope="module", params=["small", "medium"])
def compiled(request):
    model = make_csi2021_model(RESPONSE)
    numerics = IntegrationSettings.legacy_csi2021_v1(**GRIDS[request.param])
    return compile_fast(model, numerics=numerics)


@pytest.mark.parametrize("name", list(points()) + ["lnv_phase"])
def test_all_operator_fast_matches_slow_per_source_isotope_bin_and_pair(compiled, name):
    wc, sm = (lnv_point(), True) if name == "lnv_phase" else points()[name]
    point = TheoryPoint(wc, include_sm=sm)
    slow = predict(compiled.model, parameters=point, numerics=compiled.numerics)
    full = compiled.predict(parameters=point)
    pair = compiled.predict(parameters=point, representation="pair")
    for key in slow.components:
        np.testing.assert_allclose(full.components[key], slow.components[key], rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(pair.components[key], full.components[key], rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(full.counts, slow.counts, rtol=1e-10, atol=1e-12)
    assert full.numerical_record["backend"] == "fast"
    assert len(compiled.basis_keys) == 22
    assert compiled.full_kernel.shape[:3] == (2, 3, 8)


def test_low_level_coefficients_match_each_slow_channel_for_complex_flavor_matrices():
    model = make_csi2021_model(RESPONSE)
    target = model.targets.isotopes[0]
    response = ResponseDB(RESPONSE).get("Cs133")
    keys = tuple(spec.key for spec in LI2026_OPERATOR_SPECS)
    rng = np.random.default_rng(20261028)
    matrices = []
    for spec in LI2026_OPERATOR_SPECS:
        matrix = (rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))) * 10**(-spec.dimension - 1)
        if spec.lepton_number == "LNV":
            np.fill_diagonal(matrix, 0)
        matrices.append(matrix)
    matrices = np.asarray(matrices)
    state = np.array([1, .3j, -.2])
    rho = np.outer(state, state.conj()) / np.vdot(state, state).real
    bilinear = np.einsum("ab,ifb,jfa->ij", rho, matrices.conj(), matrices)
    for energy, recoil in [(20., .5), (35., 4.), (50., 10.)]:
        coefficient = differential_coefficients(response, target, np.array([energy]), recoil, keys, c10_mass_mode="quark_mass_resolved")[0]
        old = flavor_kernel_onebody_li2026(response, E_nu_GeV=energy * 1e-3, ER_keV=recoil,
                                          left_hat=dict(zip(keys, matrices)))
        factor = target.kinematic_mass_GeV / (8*np.pi*(energy*1e-3)**2) * GEV_INV2_TO_CM2 * 1e-6
        for index, name in enumerate(CHANNELS):
            expected = np.trace(rho @ old.pieces.get(name, np.zeros((3, 3)))) * factor
            actual = np.sum(coefficient[index] * bilinear)
            assert abs(actual - expected) <= 1e-10 * max(abs(expected), np.max(np.abs(coefficient[index] * bilinear)), 1e-300)
        sectors = [s.lepton_number for s in LI2026_OPERATOR_SPECS]
        for i in range(22):
            for j in range(22):
                if sectors[i] != sectors[j]:
                    np.testing.assert_array_equal(coefficient[:, i, j], 0)


def test_save_load_and_scan_changes_reuse_same_kernel(compiled, tmp_path):
    path = tmp_path / "kernel.npz"
    save_compiled_kernel(path, compiled)
    loaded = load_compiled_kernel(path, model=compiled.model)
    point = TheoryPoint(points()["complex"][0], sin2thetaW=.23)
    np.testing.assert_array_equal(loaded.predict(parameters=point).counts, compiled.predict(parameters=point).counts)
    via_public = predict(compiled.model, parameters=point, numerics=compiled.numerics, backend="fast", compiled=loaded)
    np.testing.assert_array_equal(via_public.counts, loaded.predict(parameters=point).counts)
    assert via_public.numerical_record["kernel_fingerprint"] == compiled.record["dependency_fingerprint"]
    with pytest.raises(UnsupportedCapabilityError, match="state parameters"):
        compiled.predict(parameters=TheoryPoint(state=StateParameters({"matter": 1})))


@pytest.mark.parametrize("change", ["source", "mass", "selection", "efficiency", "axis", "numerics"])
def test_dependent_input_changes_reject_stale_kernel(compiled, change):
    model, numerics = compiled.model, compiled.numerics
    if change == "source": model = replace(model, source=ScaledSource(model.source, 2))
    if change == "mass": model = replace(model, targets=csi_target_inventory(29.14))
    if change == "efficiency": model = replace(model, observation=replace(model.observation, efficiency=ConstantEfficiency(.5)))
    if change == "selection":
        selection = replace(model.observation.selection, values={k: .5 for k in model.observation.selection.values})
        model = replace(model, observation=replace(model.observation, selection=selection))
    if change == "axis":
        axis = model.binning.axes[0]
        model = replace(model, binning=replace(model.binning, axes=(replace(axis, edges=axis.edges + .01),)))
    if change == "numerics": numerics = replace(numerics, n_enu=numerics.n_enu + 1)
    with pytest.raises(StaleCompiledKernelError): compiled.predict(model=model, numerics=numerics)


@dataclass(frozen=True)
class TableEfficiency:
    path: Path

    def __call__(self, x):
        data = np.loadtxt(self.path)
        return np.interp(x, data[:, 0], data[:, 1])

    def describe(self):
        return {"model_id": "test_fixture_table", "resources": {"path": str(self.path)}}


def test_same_path_data_edits_invalidate_but_identical_content_at_new_path_does_not(tmp_path):
    a, b = tmp_path/"a.txt", tmp_path/"b.txt"
    a.write_text("0 0.5\n100 0.5\n"); b.write_bytes(a.read_bytes())
    model = make_csi2021_model(RESPONSE)
    model = replace(model, observation=replace(model.observation, efficiency=TableEfficiency(a)))
    numerics = IntegrationSettings(n_er=3, n_enu=6)
    compiled = compile_fast(model, numerics=numerics, basis_keys=[(6,1,"u"),(6,1,"d"),(6,2,"u"),(6,2,"d")])
    equivalent = replace(model, observation=replace(model.observation, efficiency=TableEfficiency(b)))
    np.testing.assert_array_equal(compiled.predict().counts, compiled.predict(model=equivalent).counts)
    a.write_text("0 0.4\n100 0.4\n")
    with pytest.raises(StaleCompiledKernelError): compiled.predict()
    # Statistical inputs never enter the compiler or physical dependency record.
    assert "statistical" not in json.dumps(plain(compiled.record["dependencies"])).lower()


def test_energy_dependent_and_undeclared_state_providers_reject_explicit_fast():
    model = make_csi2021_model(RESPONSE)
    base = model.source.for_run(model.run)
    part = base.components[0]
    @dataclass(frozen=True)
    class LyingProvider:
        original: object
        def fixed_state_for_fast(self): return self.original.fixed_state_for_fast()
        def __call__(self, energy_MeV, *, parameters):
            rho = np.zeros((len(energy_MeV), 3, 3), complex)
            rho[:, 0, 0] = energy_MeV / 100
            rho[:, 1, 1] = 1 - energy_MeV / 100
            return IncidentStateBatch(energy_MeV, rho, "nu", "test_energy_dependent")
    changed = replace(part, state_provider=LyingProvider(part.state_provider))
    source = IntegratedFluenceSource(DetectorFluence((changed,), "test"), model.source.describe())
    model = replace(model, source=source, run=IntegratedRunReference("test"))
    with pytest.raises(UnsupportedCapabilityError, match=r"rho\(E\)"):
        compile_fast(model, numerics=IntegrationSettings(n_er=3, n_enu=6))
    changed = replace(changed, state_provider=lambda e, **kw: None)
    model = replace(model, source=replace(source, fluence=DetectorFluence((changed,), "test")))
    assert not fast_capability(model).supported


def test_legacy_files_are_not_auto_promoted_to_interface_kernels(tmp_path):
    path = tmp_path/"old.npz"
    np.savez(path, full_kernel=np.zeros(1))
    with pytest.raises(StaleCompiledKernelError, match="legacy"):
        load_compiled_kernel(path, model=make_csi2021_model(RESPONSE))


def test_statistical_data_changes_reuse_physical_kernel(compiled):
    from cevns_pyeft.statistics.datasets import csi2021_dataset
    from cevns_pyeft.statistics.adapters import to_statistical_vector
    from cevns_pyeft.statistics.likelihoods import chi2_csi2021
    original = csi2021_dataset()
    first = compiled.predict()
    vector = to_statistical_vector(first, target_observable=original.observable)
    changed = replace(original, observed=original.observed + 10)
    assert chi2_csi2021(vector, original).chi2 != pytest.approx(chi2_csi2021(vector, changed).chi2)
    repeated = compiled.predict()
    np.testing.assert_array_equal(first.counts, repeated.counts)
    assert first.numerical_record["kernel_fingerprint"] == repeated.numerical_record["kernel_fingerprint"]
    assert vector.metadata["backend"] == "fast"


def test_saved_array_corruption_is_rejected(compiled, tmp_path):
    path = tmp_path/"kernel.npz"
    save_compiled_kernel(path, compiled)
    with np.load(path, allow_pickle=False) as f:
        contents = {name: np.array(f[name]) for name in f.files}
    contents["full_kernel"].flat[0] += 1
    np.savez_compressed(path, **contents)
    with pytest.raises(ValueError, match="content hash"):
        load_compiled_kernel(path, model=compiled.model)


def test_resource_edit_invalidates_existing_model_snapshot_and_missing_basis_is_rejected(tmp_path):
    path = tmp_path/"responses.json"
    path.write_bytes(RESPONSE.read_bytes())
    model = make_csi2021_model(path)
    kernel = compile_fast(model, numerics=IntegrationSettings(n_er=3,n_enu=6),
                           basis_keys=[(6,1,"u"),(6,1,"d"),(6,2,"u"),(6,2,"d")])
    with pytest.raises(UnsupportedCapabilityError, match="outside compiled basis"):
        kernel.predict(parameters=TheoryPoint({(7,1,"d"): np.eye(3)*1e-8}))
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(StaleCompiledKernelError, match="resource changed"):
        kernel.predict()


@pytest.mark.parametrize("dataset", ["CsI2021", "CsI2017", "Ar2020"])
def test_existing_fast_builders_preserve_pre_refactor_arrays_exactly(dataset):
    from cevns_pyeft.experiments.coherent.fast_kernel_csi2021 import build_fast_kernel_csi2021
    from cevns_pyeft.experiments.coherent.fast_kernel_csi2017 import build_fast_kernel_csi2017
    from cevns_pyeft.experiments.coherent.fast_kernel_ar2020 import build_fast_kernel_ar2020
    from cevns_pyeft.kernels.basis import BasisElement
    folder = ROOT/"tests/reference/interface_kernel_v1"
    meta = json.loads((folder/"metadata.json").read_text())
    basis = [BasisElement(i,str(i),str(k),tuple(k)) for i,k in enumerate(meta["basis"])]
    builder = {"CsI2021":build_fast_kernel_csi2021,"CsI2017":build_fast_kernel_csi2017,"Ar2020":build_fast_kernel_ar2020}[dataset]
    result = builder(RESPONSE,basis=basis,n_enu=meta["n_enu"],**meta["grids"][dataset])
    with np.load(folder/"legacy_builder.npz", allow_pickle=False) as ref:
        for key in ("full_kernel","diag","pair_re","pair_im","pair_index"):
            np.testing.assert_array_equal(result[key],ref[dataset+"/"+key])
