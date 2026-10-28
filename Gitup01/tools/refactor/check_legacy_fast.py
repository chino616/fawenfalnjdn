"""Bounded legacy Fast diagnostic; does not implement R4 model compilation."""
from pathlib import Path
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from cevns_pyeft.experiments.coherent.fast_kernel_csi2021 import build_fast_kernel_csi2021
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import slow_counts_csi2021
from cevns_pyeft.kernels.basis import BasisElement, coeff_tensor_from_triplets
from cevns_pyeft.foundation.constants import GEV_INV2_TO_CM2
from cevns_pyeft.kernels.reconstruction import (reconstruct_counts_from_kernel,
    reconstruct_from_full_kernel_flavor, reconstruct_from_pair_templates_flavor,
    source_densities_for_fast_flavors)


def main():
    keys = [(6, 1, "u"), (6, 1, "d"), (6, 2, "u"), (6, 2, "d")]
    basis = [BasisElement(i, str(i), str(key), key) for i, key in enumerate(keys)]
    kernel = build_fast_kernel_csi2021(ROOT / "data/responses/responses_all.json", basis=basis,
                                      n_er=5, n_enu=12, n_pe_sub=4, pe_step=4)
    cases = {"sm": {}, "complex_multiflavor": {(6, 1, "u"): 1e-6 * np.array([[1, .2j, 0], [.3, -.4, 0], [0, 0, .1]])}}
    report = {"scope": "legacy Fast diagnostic only; composable Fast compiler NOT_IMPLEMENTED",
              "settings": {"n_er": 5, "n_enu": 12, "n_pe_bin": 4, "pe_step": 4},
              "rtol": 1e-10, "atol_events": 1e-12, "cases": {}}
    conversion_ratio = (1.973269804e-14 ** 2) / GEV_INV2_TO_CM2
    report["existing_conversion_discrepancy"] = {
        "fast_to_slow_ratio": conversion_ratio,
        "fast_cm2_per_GeV_inv2": 1.973269804e-14 ** 2,
        "slow_cm2_per_GeV_inv2": GEV_INV2_TO_CM2,
        "action": "record only; no normalization correction applied"}
    for name, wc in cases.items():
        coeff = coeff_tensor_from_triplets(basis, wc, include_sm=True)
        rhos = source_densities_for_fast_flavors(kernel["source_flavors"])
        full = reconstruct_from_full_kernel_flavor(kernel["full_kernel"], coeff, rhos)
        pair = reconstruct_from_pair_templates_flavor(diag=kernel["diag"], pair_re=kernel["pair_re"],
            pair_im=kernel["pair_im"], pair_index=kernel["pair_index"], coeffs=coeff, source_rhos=rhos)
        slow = slow_counts_csi2021(ROOT / "data/responses/responses_all.json", wc, n_er=5, n_enu=12, n_pe_bin=4, pe_step=4)
        fast = reconstruct_counts_from_kernel(kernel, coeff)
        differences, residuals = {}, {}
        passed = bool(np.allclose(full, pair, rtol=1e-10, atol=1e-12))
        for source, value in slow["counts_per_bin"].items():
            other = fast["counts_per_bin"][source]
            differences[source] = float(np.max(np.abs(value - other)))
            residuals[source] = float(np.max(np.abs(other - value * conversion_ratio)))
            passed &= bool(np.allclose(value, other, rtol=1e-10, atol=1e-12))
        report["cases"][name] = {"status": "PASS" if passed else "FAIL",
                                  "max_full_pair_absolute": float(np.max(np.abs(full - pair))),
                                  "max_slow_fast_events": differences,
                                  "max_residual_after_known_constant_ratio_diagnostic_only": residuals}
    out = ROOT / "outputs/refactor/legacy_fast_diagnostic.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
