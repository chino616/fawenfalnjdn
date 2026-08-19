from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from cevns_pyeft.experiments.conus.fast_cumulative_conus_plus_ge73_pheno import (
    CumulativeFastRepresentation,
    CumulativeFastSettings,
    cumulative_fast_counts_conus_plus_ge73_pheno,
    load_cumulative_fast_representation,
    reconstruct_counts_from_cumulative,
    validate_cumulative_fast_representation,
)
from cevns_pyeft.experiments.conus.slow_counts_conus_plus_ge73_pheno import (
    SlowIntegrationSettings,
    slow_counts_conus_plus_ge73_pheno,
)
from cevns_pyeft.experiments.registry import get_experiment_spec

RUN_DIR = Path("workflows/experiment-integration/runs/conus_plus_ge73_pheno")
REFERENCE = Path("tests/reference_conus_plus_ge73_pheno/cumulative_reference.npz")
FAST_TEST_SLOW_SETTINGS = SlowIntegrationSettings(n_true_recoil=41, n_neutrino=80, reco_step_evee=5.0)


def test_public_cumulative_fast_shape_units_and_bin_agreement():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    slow = slow_counts_conus_plus_ge73_pheno(experiment_spec=spec, integration_settings=FAST_TEST_SLOW_SETTINGS)
    fast = cumulative_fast_counts_conus_plus_ge73_pheno(
        experiment_spec=spec,
        slow_integration_settings=FAST_TEST_SLOW_SETTINGS,
        fast_settings=CumulativeFastSettings(grid_step_evee=5.0),
    )

    counts = np.asarray(fast["counts_total"], dtype=float)
    assert counts.shape == (19,)
    assert fast["axes"] == ("reco_energy_evee",)
    assert fast["unit"] == "expected_events_per_bin"
    assert np.all(np.isfinite(counts))
    assert np.all(counts >= 0.0)
    assert np.allclose(counts, slow["counts_total"], rtol=1.0e-10, atol=1.0e-10)
    assert np.allclose(fast["counts_per_bin"]["nuebar_Ge73"], counts)


def test_saved_cumulative_reference_roundtrip_and_metadata():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    assert REFERENCE.exists()
    representation = load_cumulative_fast_representation(REFERENCE, spec)
    validate_cumulative_fast_representation(representation, spec)
    counts = reconstruct_counts_from_cumulative(representation)
    assert counts.shape == (19,)
    assert np.all(np.isfinite(counts))
    assert np.all(counts >= 0.0)
    assert representation.metadata["dataset_id"] == "conus_plus_ge73_pheno"
    assert representation.metadata["model"] == "conus_plus_ge73_pheno_cumulative_spectrum_v1"
    assert representation.metadata["eft_template_status"] == "BLOCKED_UNTIL_COMPLETE_20_GROUP_BASIS_DEFINED"


def test_stale_metadata_rejected():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    representation = load_cumulative_fast_representation(REFERENCE, spec)
    stale = CumulativeFastRepresentation(
        reco_energy_grid_evee=representation.reco_energy_grid_evee,
        dndE_reco_per_evee=representation.dndE_reco_per_evee,
        cumulative_counts=representation.cumulative_counts,
        metadata={**representation.metadata, "dataset_id": "other_dataset"},
    )
    with pytest.raises(ValueError, match="Unsupported dataset_id"):
        validate_cumulative_fast_representation(stale, spec)


def test_fast_vs_slow_artifacts_are_bin_by_bin_and_pass():
    fast_vs_slow = RUN_DIR / "artifacts" / "fast_vs_slow.csv"
    runtime = RUN_DIR / "artifacts" / "fast_runtime.csv"
    figures = [
        RUN_DIR / "figures" / "fast_vs_slow.png",
        RUN_DIR / "figures" / "fast_relative_error.png",
    ]
    assert fast_vs_slow.exists()
    assert runtime.exists()
    assert all(path.exists() and path.stat().st_size > 0 for path in figures)

    with fast_vs_slow.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 57
    assert {row["point"] for row in rows} == {"sm_full_response", "complex_c61u", "helm_sm"}
    assert all(row["pass"] == "True" for row in rows)
    assert max(float(row["relative_difference"]) for row in rows) < 1.0e-10

    with runtime.open(encoding="utf-8", newline="") as handle:
        runtime_rows = list(csv.DictReader(handle))
    assert len(runtime_rows) == 3
    assert min(float(row["speedup_reconstruct_vs_slow"]) for row in runtime_rows) > 1000.0


def test_unsupported_helm_eft_input_raises():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    with pytest.raises(ValueError, match="helm_sm supports only"):
        cumulative_fast_counts_conus_plus_ge73_pheno(
            experiment_spec=spec,
            cross_section_model="helm_sm",
            wc_triplets={(6, 1, "u"): 1.0e-8},
            slow_integration_settings=FAST_TEST_SLOW_SETTINGS,
            fast_settings=CumulativeFastSettings(grid_step_evee=5.0),
        )


def test_cumulative_fast_module_has_no_statistics_dependency():
    import cevns_pyeft.experiments.conus.fast_cumulative_conus_plus_ge73_pheno as fast_module

    text = Path(fast_module.__file__).read_text(encoding="utf-8").lower()
    assert "statistics" not in text
