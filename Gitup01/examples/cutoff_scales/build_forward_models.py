"""Build and refine independent full22 ground and fixed-state solar forwards."""
from __future__ import annotations
import argparse
from dataclasses import replace
import os
from pathlib import Path
import sys
import time
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import ROOT, PART, new_run, sha, write_json


def build(output, *, resume=False, ground_only=False, solar_only=False):
    output = Path(output).resolve()
    if resume:
        if not output.is_relative_to((ROOT/"outputs/cutoff_scales").resolve()) or not (output/"BUILD_PLAN.json").is_file():
            raise ValueError("resume requires this Part's own incomplete model-build directory")
    else:
        output = new_run(output)
        write_json(output/"BUILD_PLAN.json", {"part_id": PART, "stage": "FULL22_FORWARD_BUILD", "date": "2026-11-14",
                   "flavor": "LNC ee; LNV e<->mu antisymmetric dipole/tensor and symmetric scalar, entries magnitude c",
                   "solar": "fixed SM propagation control; explicitly distinct from dim6 variable propagation"})
    os.environ["NUMBA_CACHE_DIR"] = str(output/"cache")
    from forward22 import build_csi, build_ar, build_conus, compile_ground, compile_solar, KEYS
    from model_adapters import load_ground, Solar
    adopted, _ = load_ground()
    started = time.perf_counter()
    reports = {}
    if not solar_only:
        for name, factory, settings in (
            ("CsI2021_9PE", build_csi, dict(n_er=512, n_enu=1920, n_observed=256, step=.0625)),
            ("Ar2020_average", build_ar, dict(n_er=321, n_enu=1920, n_observed=64)),
            ("CONUS_plus", lambda: build_conus()[0], dict(n_er=161, n_enu=641, n_observed=8))):
            report_path = output/(name+"_FORWARD.json")
            if resume and report_path.exists():
                print("REUSE_COMPLETED", name, flush=True); continue
            model = factory()
            built = []
            for label, factor in (("baseline", 1), ("refined", 2)):
                path = output/(name+"_"+label+".npz")
                ns = {**settings, "n_er": settings["n_er"]*factor, "n_enu": settings["n_enu"]*factor,
                      "n_observed": settings["n_observed"]*factor, "step": settings.get("step", .0625)/factor}
                if resume and path.exists():
                    with np.load(path, allow_pickle=False) as a:
                        full = a["full_kernel"].copy()
                    report = {"resumed_saved_array": True, **ns}
                else:
                    full, report = compile_ground(model, name, **ns)
                    np.savez_compressed(path, full_kernel=full, basis_keys=np.array([str(k) for k in KEYS]))
                built.append(full)
                if label == "baseline":
                    indices = [KEYS.index(k) for k in adopted[name].basis]
                    projection = full[:, :, :, indices, :, :][:, :, :, :, indices, :]
                    old = adopted[name].full
                    scales = np.max(abs(old), axis=(0, 1, 2, 5), keepdims=True)
                    residual = np.max(abs(projection-old)/(np.maximum(scales, 1.)*1.))
                    np.testing.assert_allclose(projection, old, rtol=2e-8, atol=2e-5)
                    report["adopted_dim6_projection_max_relative"] = float(residual)
                reports[name+"_"+label] = report
                write_json(output/(name+"_"+label+"_NUMERICS.json"), report)
            write_json(report_path, {"restoration": "readable mainline human-readable inputs/records plus direct numerical resources; no native package load",
                        "baseline": reports[name+"_baseline"], "refined": reports[name+"_refined"],
                        "refined_kernel": name+"_refined.npz", "refined_sha256": sha(output/(name+"_refined.npz"))})
    if not ground_only:
        solar = Solar()
        for label, n_er in (("baseline", 401), ("refined", 801)):
            path = output/("Solar_"+label+".npz")
            if resume and path.exists():
                print("REUSE_COMPLETED", path.name, flush=True); continue
            polynomial, record = compile_solar(solar, n_er=n_er)
            np.savez_compressed(path, polynomial=polynomial, basis_keys=np.array([str(k) for k in KEYS]))
            write_json(output/("Solar_"+label+"_NUMERICS.json"), record)
    write_json(output/"BUILD_EXECUTION.json", {"part_id": PART, "last_call_seconds": time.perf_counter()-started,
               "ground_only": ground_only, "solar_only": solar_only,
               "code_fingerprints": {p.relative_to(ROOT).as_posix(): sha(p) for p in HERE.glob("*.py")},
               "limitation": "full22 solar control uses fixed SM source rho, not arbitrary-LEFT matter evolution"})
    print("FORWARD_BUILD_CALL_FINISHED", output, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--ground-only", action="store_true")
    parser.add_argument("--solar-only", action="store_true")
    args = parser.parse_args()
    build(args.output, resume=args.resume, ground_only=args.ground_only, solar_only=args.solar_only)
