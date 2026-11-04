"""Default dataset identity now resolves package resources, including old views."""
from pathlib import Path
import builtins
import numpy as np
import pytest

from cevns_pyeft.contracts import TheoryPoint
from cevns_pyeft.experiments.loader import load_experiment
from cevns_pyeft.experiments.runtime import predict_experiment
from tests.helpers.regression_cases import GRIDS, points


def test_default_catalog_reads_only_package_physical_resources(monkeypatch):
    original = Path.read_bytes
    def guarded(path):
        if path.name == 'responses_all.json':
            raise AssertionError('external nuclear resource read')
        return original(path)
    monkeypatch.setattr(Path, 'read_bytes', guarded)
    exp = load_experiment('CsI2021')
    assert set(exp.resolved_resources) == {'package_input', 'package_arrays'}
    assert type(exp.executor).__module__.endswith('package_loader')
    assert predict_experiment(exp, numerics=GRIDS['small']).counts.shape == (9,)


def test_package_fast_all_operators_and_legacy_template_match_slow():
    from cevns_pyeft.kernels.compiler import compile_fast
    from cevns_pyeft.experiments.package_compatibility import legacy_fast_template
    from cevns_pyeft.kernels.basis import li2026_left_basis_current, coeff_tensor_from_triplets
    from cevns_pyeft.kernels.reconstruction import reconstruct_counts_from_kernel
    exp = load_experiment('CsI2021')
    ns = GRIDS['small']
    kernel = compile_fast(exp.model, numerics=exp.executor.settings(ns))
    legacy = legacy_fast_template(exp, basis=li2026_left_basis_current(), numerics=ns)
    for name, (wc, include) in points().items():
        point = TheoryPoint(wc, include_sm=include, sin2thetaW=exp.definition.reproduction_sin2thetaW)
        slow = predict_experiment(exp, parameters=point, numerics=ns)
        fast = kernel.predict(model=exp.model, parameters=point, numerics=exp.executor.settings(ns))
        np.testing.assert_allclose(fast.counts, slow.counts, rtol=1e-10, atol=1e-12)
        saved = reconstruct_counts_from_kernel(legacy, coeff_tensor_from_triplets(legacy['basis'], wc,
            include_sm=include, sin2thetaW=point.sin2thetaW))
        np.testing.assert_allclose(saved['counts_per_bin']['total'], slow.counts, rtol=1e-10, atol=1e-12)


def test_explicit_detector_values_never_import_legacy_defaults(monkeypatch):
    from cevns_pyeft.detectors.csi2021 import CsIGammaResponse, CsI2021Efficiency, CsI2021EfficiencyParams
    exp = load_experiment('CsI2021')
    settings = exp.definition.physical
    importer = builtins.__import__
    def guarded(name, *args, **kwargs):
        if name.endswith('legacy_parameters'):
            raise AssertionError('hidden legacy defaults import')
        return importer(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', guarded)
    response = CsIGammaResponse(settings.quenching, settings.gamma_a, settings.gamma_b)
    eff = CsI2021Efficiency(CsI2021EfficiencyParams(*settings.efficiency))
    assert response.density(15., 20., target=None) > 0
    assert 0 < eff(15.) < 1
