"""Unfitted real-vector NSI benchmark using existing main-project kernels.

The SM inputs and the previously checked time weights are kept unchanged.
Only the existing four LEFT operators needed by SM + vector NSI are compiled.
This is a scoped numerical benchmark, not a canonical P08/likelihood freeze.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
from dataclasses import asdict
import importlib.util
from importlib import import_module
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
SM_HELPER = ROOT / "examples/COHERENT_CsI/time_resolved_common/sm_support.py"
spec = importlib.util.spec_from_file_location("_csi_sm_forward_reference", SM_HELPER)
sm = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = sm
spec.loader.exec_module(sm)

from cevns_pyeft.contracts.parameters import IntegrationSettings, TheoryPoint
from cevns_pyeft.contracts.modules import ModuleDescriptor, UnsupportedCapabilityError
from cevns_pyeft.kernels.compiler import compile_fast, CompiledKernel, reconstruct_channels
from cevns_pyeft.foundation.constants import G_F

BASIS = ((6, 1, "u"), (6, 1, "d"), (6, 2, "u"), (6, 2, "d"))
SOURCE_IDS = ("prompt_numu", "delayed_nue", "delayed_numubar")
TARGETS = ("Cs133", "I127")
BASE = ROOT / "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved"
SM_RUN = ROOT / "outputs/csi2021_time_sm_20261107"


class CheckedCoefficientEnergy:
    """Evaluate the same restricted dim6 coefficient tensor with native checks.

    Three native probes determine E^2 H(E). Four additional native probes
    (two interior and both endpoints) check every tensor entry at each recoil.
    Any failed check uses the original full native energy array. Only the
    four current dim6 operators are accepted; this is not a general EFT rule.
    """
    def __init__(self, original):
        self.original = original
        self.statistics = {"checked_calls": 0, "fallback_calls": 0, "direct_small_queries": 0,
            "max_normalized_tensor_holdout_error": 0.0}

    def __getattr__(self, name):
        return getattr(self.original, name)

    def coefficient_dsigma(self, *, target, energy_MeV, recoil_keV, basis_keys):
        if tuple(basis_keys) != BASIS:
            raise UnsupportedCapabilityError("Checked energy evaluation is restricted to the declared four dim6 operators")
        energy = np.asarray(energy_MeV, dtype=float)
        keywords = dict(target=target, recoil_keV=recoil_keV, basis_keys=basis_keys)
        if energy.size < 8 or energy.max()-energy.min() < 1e-8:
            self.statistics["direct_small_queries"] += 1
            return self.original.coefficient_dsigma(energy_MeV=energy, **keywords)
        lo, hi = float(energy.min()), float(energy.max())
        probes = lo + (hi-lo)*np.array([0., .10, .31, .52, .73, .94, 1.])
        native = self.original.coefficient_dsigma(energy_MeV=probes, **keywords)
        measured = native * probes[:, None, None, None]**2
        scale = np.maximum(np.max(np.abs(measured), axis=0), np.finfo(float).tiny)
        normalized = measured / scale[None, ...]
        vandermonde = np.polynomial.polynomial.polyvander(probes[[1,3,5]]/hi, 2)
        coefficients = np.linalg.solve(vandermonde, normalized[[1,3,5]].reshape(3,-1))
        checked = (np.polynomial.polynomial.polyvander(probes/hi,2) @ coefficients).reshape(normalized.shape)
        error = float(np.max(np.abs(checked-normalized)))
        if not np.allclose(checked, normalized, rtol=2e-10, atol=2e-12):
            self.statistics["fallback_calls"] += 1
            return self.original.coefficient_dsigma(energy_MeV=energy, **keywords)
        self.statistics["checked_calls"] += 1
        self.statistics["max_normalized_tensor_holdout_error"] = max(self.statistics["max_normalized_tensor_holdout_error"], error)
        value = (np.polynomial.polynomial.polyvander(energy/hi,2) @ coefficients).reshape((len(energy),*scale.shape))
        return value * scale[None, ...] / energy[:, None, None, None]**2

    def describe(self):
        return ModuleDescriptor("interaction", "native_dim6_coefficient_checked_energy", capabilities=("slow_elastic","operator_bilinear_v1"),
            parameters={"original": self.original.describe().as_dict(), "numerical_method": "E^2 coefficient tensor quadratic;3 defining and4 holdout native probes",
                "basis_restriction": BASIS, "driver_sha256": sm.sha(__file__)},
            resources=self.original.describe().resources)


def legacy_mapping(legacy_time):
    """Load the actual old epsilon-to-Wilson implementation, without running it."""
    local = legacy_time / "vector_nsi.py"
    if local.is_file():
        module = sm.local_module(local, "_csi_local_vector_nsi")
        if module.G_F != G_F:
            raise ValueError("NSI mapping and native theory G_F differ")
        return module
    import cevns_pyeft.experiments.coherent as coherent
    parent = str(legacy_time.parent)
    if parent not in coherent.__path__:
        coherent.__path__.append(parent)
    module = import_module("cevns_pyeft.experiments.coherent.2021CsI_root_time.kernels.vector_nsi")
    if Path(module.__file__).resolve() != (legacy_time / "kernels/vector_nsi.py").resolve():
        raise ValueError("Unexpected legacy NSI mapping path")
    if module.G_F != G_F:
        raise ValueError("NSI conversion and native theory must use the same G_F")
    return module


def benchmark_points(legacy_time):
    """Read the exact latest 24 declared coordinates; no old fit directory is needed."""
    source = ROOT / "data/benchmarks/COHERENT_CsI/CsI2021_time/nsi_20261108/points.json"
    return json.loads(source.read_text(encoding="utf-8")), source


def point_parameters(point, mapping, sin2):
    wc = mapping.vector_nsi_wilson(np.array(point["epsilon_u"]), np.array(point["epsilon_d"]))
    return TheoryPoint(wc, include_sm=True, sin2thetaW=sin2)


def frame(onboarding, legacy_time):
    claims, register = sm.inputs(onboarding)
    model = sm.build_model(claims)
    time_module, profile = sm.time_modules(legacy_time)
    time_source = sm.time_source(onboarding, profile)
    time_edges = np.array(claims["C_TIME"]["value"])
    efficiency = time_module.CsITimeEfficiency(*claims["C_TIME_EFF"]["value"])
    tables = {scope: time_module.build_time_weights(time_source, time_edges, efficiency=efficiency,
        template_normalization="reference_window", energy_fluence_scope=scope, reference_window_us=[0, 6])
        for scope in ("reference_window", "full_support")}
    return model, claims, register, tables


def cached_evaluate(kernel, model, parameters, rhos):
    """Existing reconstruction on an immutable, dependency-checked kernel."""
    coefficients = model.interaction.coefficient_values(parameters, BASIS)
    channels = reconstruct_channels(kernel.full_kernel, coefficients, rhos)
    energy = channels.sum(axis=2)
    scale = max(float(np.max(np.abs(energy))), np.finfo(float).tiny)
    if np.any(energy < -1e-12 * scale):
        raise ValueError("Negative NSI total beyond the unchanged stock kernel roundoff rule")
    return np.maximum(energy, 0), channels, coefficients


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-time-dir", type=Path, default=sm.LOCAL_TIME, help="Local adopted time/mapping modules; optional explicit compatibility override")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--onboarding", type=Path, default=BASE)
    parser.add_argument("--n-er", type=int, required=True)
    parser.add_argument("--n-enu", type=int, required=True)
    parser.add_argument("--n-pe-bin", type=int, required=True)
    parser.add_argument("--pe-step", type=float, required=True)
    parser.add_argument("--checked-coefficient-energy", action="store_true")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists():
        parser.error("Output grid directory already exists; choose a new directory")
    legacy_time = args.legacy_time_dir.resolve()
    mapping = legacy_mapping(legacy_time)
    model, claims, sources, tables = frame(args.onboarding.resolve(), legacy_time)
    if args.checked_coefficient_energy:
        from dataclasses import replace
        model = replace(model, interaction=CheckedCoefficientEnergy(model.interaction))
    points, point_source = benchmark_points(legacy_time)
    numerical = IntegrationSettings(n_er=args.n_er, n_enu=args.n_enu, n_observed_bin=args.n_pe_bin,
        observed_step=args.pe_step, recoil_min_keV=float(claims["C_QF_DOMAIN"]["value"][0]))
    sin2 = float(claims["C_SIN2_PAPER"]["value"])
    print(json.dumps({"started": True, "grid": asdict(numerical), "NSI_points": len(points)}), flush=True)
    driver_fingerprint = sm.sha(__file__)
    started = time.perf_counter()
    kernel = compile_fast(model, numerics=numerical, basis_keys=BASIS)
    # One public call performs the full stock dependency and state validation.
    public_sm = kernel.predict(parameters=point_parameters(points[0], mapping, sin2))
    components = model.source.for_run(model.run).components
    rhos = np.asarray([component.fixed_state_for_fast().rho for component in components])
    energy_all, channel_all, coefficients_all = [], [], []
    for point in points:
        energy, channels, coefficients = cached_evaluate(kernel, model, point_parameters(point, mapping, sin2), rhos)
        energy_all.append(energy); channel_all.append(channels); coefficients_all.append(coefficients)
    energy = np.array(energy_all)
    parts = energy[..., None] * tables["reference_window"].effective_weights[None, None, :, None, :]
    full_parts = energy[..., None] * tables["full_support"].effective_weights[None, None, :, None, :]
    expected_public = np.array([[public_sm.components[(c, t)] for c in SOURCE_IDS] for t in TARGETS])
    np.testing.assert_allclose(energy[0], expected_public, rtol=2e-13, atol=2e-11)
    output.mkdir(parents=True)
    np.savez_compressed(output / "prediction.npz", point_ids=np.array([point["id"] for point in points]),
        pe_edges=model.binning.axes[0].edges, time_edges_us=tables["reference_window"].time_edges_us,
        energy_before_time=energy, target_component_counts=parts, signal_counts=parts.sum(axis=(1, 2)),
        full_fluence_signal_counts=full_parts.sum(axis=(1, 2)), channel_counts_before_time=np.array(channel_all),
        coefficients_GeV_minus2=np.array(coefficients_all), time_weights=tables["reference_window"].effective_weights,
        full_time_weights=tables["full_support"].effective_weights)
    np.savez_compressed(output / "kernel.npz", full_kernel=kernel.full_kernel, rhos=rhos)
    sm.write_json(output / "compiled_record.json", kernel.record)
    sm.write_json(output / "points.json", points)
    report = {"date": datetime.now(timezone(timedelta(hours=8))).date().isoformat(), "timezone": "Asia/Shanghai", "scope": "Unfitted real symmetric u/d vector NSI; finite declared points; no likelihood, confidence contour or canonical Fast freeze",
        "numerical_settings": asdict(numerical), "basis_keys": BASIS, "kernel_shape": list(kernel.full_kernel.shape),
        "kernel_units": "events GeV^4 before multiplication by dimension-6 Wilson coefficients squared",
        "coefficient_units": "GeV^-2", "epsilon_units": "dimensionless", "flavor_axes": "[final,initial]; e,mu,tau",
        "mapping": "C61q[final,initial] = -sqrt(2) G_F epsilon_q.T; epsilon_q real symmetric",
        "mapping_source": {"path": str(Path(mapping.__file__).resolve()), "sha256": sm.sha(mapping.__file__), "locator": "vector_nsi_wilson and _matrix"},
        "paper": {"source_id": "S_2211", "original_url": "https://arxiv.org/abs/2211.11905v2", "locator": "PDF p5, Sec2.2, Eqs5-6; physical vector-NSI definition, not a reference table for these points"},
        "historical_coordinate_source": {"path": str(point_source), "sha256": sm.sha(point_source), "adopted": "latest declared 24 ids and matrices; origin fields remain provenance, no old fitted values used"},
        "SM_helper_sha256": sm.sha(SM_HELPER), "driver_sha256": driver_fingerprint,
        "checked_coefficient_energy": args.checked_coefficient_energy,
        "coefficient_energy_checks": model.interaction.statistics if args.checked_coefficient_energy else None,
        "response_sha256": sm.sha(model.interaction.responses_json), "parent_source_register_sha256": sm.sha(args.onboarding / "P00_SOURCE_REGISTER.yaml"),
        "SM_configuration_sha256": sm.sha(BASE / "sm_benchmark_20261107/SM_CONFIG.json"),
        "legacy_time_files": {name: {"path": str(legacy_time/name), "sha256": sm.sha(legacy_time/name)} for name in ("time_acceptance.py", "time_profile.py")},
        "source_rhos": rhos, "time_contract": dict(tables["reference_window"].metadata),
        "model": public_sm.model_record, "normalization": public_sm.normalization_record,
        "points": [{"id": point["id"], "total_events": float(parts[i].sum()), "full_fluence_total_events": float(full_parts[i].sum())} for i, point in enumerate(points)],
        "stock_public_SM_vs_cached_reconstruction_max_error": float(np.max(np.abs(energy[0]-expected_public))),
        "elapsed_s": time.perf_counter()-started, "external_paper_reproduction": "NOT_CERTIFIED"}
    if sm.sha(__file__) != driver_fingerprint:
        raise ValueError("Benchmark driver changed during calculation; do not accept this run")
    sm.write_json(output / "report.json", report)
    print(json.dumps({"elapsed_s": report["elapsed_s"], "SM_events": report["points"][0]["total_events"],
        "NSI_points": len(points), "range_events": [float(parts.sum(axis=(1,2,3,4)).min()),float(parts.sum(axis=(1,2,3,4)).max())]}), flush=True)


if __name__ == "__main__":
    main()
