from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad

from cevns_pyeft.experiments.base import _interp_eff
from cevns_pyeft.experiments.coherent.sns import (
    loadNeutrinoEmpiricalFluxSNS,
    sns_component_state,
)
from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import (
    CSI2017_BINS_25,
    CSI2017_PE_PER_KEV,
)
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import (
    PE_BINS_9,
    efficiency_csi2021,
)
from cevns_pyeft.experiments.registry import get_experiment_spec
from cevns_pyeft.experiments.specs import (
    list_spec_experiment_names,
    required_input_fields,
)
from cevns_pyeft.sources.state import NeutrinoState, pure_flavor_density
from cevns_pyeft.rates.differential import eee_quenching_csi, p_smearing_csi


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "experiment.schema.json").read_text(encoding="utf-8"))
EXPECTED = {
    "CsI2017": {
        "shape": [25],
        "mode": "regular_edges",
        "minimum": 0.001,
        "maximum": 50.0,
        "number_of_bins": 25,
    },
    "CsI2021": {
        "shape": [9],
        "mode": "explicit_edges",
        "edges": [0.001, 8.001, 12.001, 16.001, 20.001, 24.001, 32.001, 40.001, 48.001, 60.001],
        "number_of_bins": 9,
    },
}
SOURCE_SAMPLE_ENERGIES_MEV = np.array(
    [
        0.0,
        0.001,
        1.0,
        10.0,
        29.792140909877446,
        52.0,
        55.0,
        56.0,
        56.5,
        100.0,
        300.0,
        301.0,
    ],
    dtype=float,
)
SOURCE_BASELINE = {
    "CsI2017": {
        "integrated_flux": 295672959326670.6,
        "hashes": {
            "e": "52b8033c513e0ac99b6dbfd3313dce197c112145994a1b6c5a3710965bc8a513",
            "mub": "40ae894df52a7c4ea674a8dfde82ce878e6974722a68644a287e3c6fbc3d080d",
            "totalContinuous": "d0382544a2adb74d6cdbb055c8ca0227b2f8cbd0b95efc39d52eea810e976cc2",
        },
        "integrals": (
            295492414065076.06,
            336935074005312.6,
            632427488070388.6,
        ),
    },
    "CsI2021": {
        "integrated_flux": 579361763793233.6,
        "hashes": {
            "e": "48153eb232678564df4301b638f7d662b96e7aa47b0508ca37eee76417997901",
            "mub": "4c3a7e7f060a7daed3e287ade54ae3cb13266d9cb023babc198196c5150e392f",
            "totalContinuous": "28aa929b4dcea2a1b7db3eb64e5f70c44b9a6b1ccfaeaa507ca6178b9d5ea966",
        },
        "integrals": (
            579007991093017.2,
            660213565704698.9,
            1239221556797716.0,
        ),
    },
}


def _validate_current_schema_contract(data: dict) -> None:
    for field in SCHEMA["required"]:
        assert field in data
        assert data[field] not in ("", None)
    assert isinstance(data["dataset_name"], str)
    assert data["dataset_name"]
    assert data["source_type"] in SCHEMA["properties"]["source_type"]["enum"]


@pytest.mark.parametrize("dataset_name", ("CsI2017", "CsI2021"))
def test_csi_phase1_specs_load_and_match_approved_dataset_contract(dataset_name):
    spec = get_experiment_spec(dataset_name)
    data = spec.data
    expected = EXPECTED[dataset_name]

    _validate_current_schema_contract(data)
    assert spec.dataset_name == dataset_name
    assert spec.source_type == "stopped_pion"
    assert spec.target_mode == "CsI_equal_stoichiometry"
    assert data["statistical_data_mode"] == "background_subtracted_excess"
    assert data["expected_output"]["axes"] == ["source_component", "pe_bin"]
    assert data["expected_output"]["shape"] == expected["shape"]
    assert data["expected_output"]["unit"] == "expected_events_per_bin"
    assert data["binning"]["mode"] == expected["mode"]
    assert data["binning"]["number_of_bins"] == expected["number_of_bins"]
    assert required_input_fields(data) == ()


def test_csi2017_regular_binning_matches_output_shape():
    data = get_experiment_spec("CsI2017").data
    binning = data["binning"]
    edges = np.linspace(
        float(binning["minimum"]),
        float(binning["maximum"]),
        int(binning["number_of_bins"]) + 1,
    )
    assert edges.size - 1 == data["expected_output"]["shape"][0]
    assert np.allclose(np.diff(edges), float(binning["width"]), rtol=0.0, atol=1.0e-14)


def test_csi2021_explicit_edges_match_output_shape():
    data = get_experiment_spec("CsI2021").data
    edges = np.asarray(data["binning"]["edges"], dtype=float)
    assert np.all(np.diff(edges) > 0.0)
    assert edges.size - 1 == data["expected_output"]["shape"][0]


def test_csi_phase1_dataset_ids_are_unique_and_paths_are_repository_relative():
    names = list_spec_experiment_names()
    assert names.count("CsI2017") == 1
    assert names.count("CsI2021") == 1

    for dataset_name in ("CsI2017", "CsI2021"):
        data = get_experiment_spec(dataset_name).data
        for value in data["planned_data_files"].values():
            assert not Path(str(value)).is_absolute()
        for key in ("physics_document", "implementation_spec", "workflow_run"):
            assert not Path(str(data["provenance"][key])).is_absolute()


def test_csi_phase6_connects_validated_detector_response_and_preserves_later_boundaries():
    for dataset_name in ("CsI2017", "CsI2021"):
        data = get_experiment_spec(dataset_name).data
        callables = data["callables"]
        assert data["spec_status"] in {"slow_validated", "fast_validated"}
        assert data["provenance"]["phase"] in {"SLOW_VALIDATED", "FAST_VALIDATED"}
        assert data["source"]["status"] == "VALIDATED_PHASE_3"
        assert data["source"]["classification"] == "SHARED_EXTENSION"
        assert data["detector"]["response_status"] == "VALIDATED_PHASE_6"
        assert data["detector"]["response_classification"] == "REUSE"
        assert callables["source_state"] == (
            "cevns_pyeft.experiments.coherent.sns.sns_component_state"
        )
        assert callables["source_flux"] == (
            "cevns_pyeft.experiments.coherent.sns.loadNeutrinoEmpiricalFluxSNS"
        )
        assert callables["slow_counts"].startswith(
            "cevns_pyeft.experiments.coherent.slow_counts_csi"
        )
        if data["phase_boundaries"]["fast_validated"]:
            assert callables["fast_counts"] == "cevns_pyeft.kernels.storage.reconstruct_saved_kernel"
        else:
            assert callables["fast_counts"] == "BLOCKED_UNTIL_P4_FLAVOR_CONTRACT"
        assert callables["statistics"] == "BLOCKED_PENDING_AUTHORITATIVE_PROVENANCE"
        assert data["phase_boundaries"]["dataset_validated"] is True
        assert data["phase_boundaries"]["target_validated"] is True
        assert data["phase_boundaries"]["source_validated"] is True
        assert data["phase_boundaries"]["theory_validated"] is True
        assert data["phase_boundaries"]["cross_section_validated"] is True
        assert data["phase_boundaries"]["detector_response_validated"] is True
        assert data["phase_boundaries"]["slow_validated"] is True
        assert data["phase_boundaries"]["registry_modified"] is False


@pytest.mark.parametrize(
    ("component", "particle_kind", "density_flavor"),
    (
        ("mu", "nu", "mu"),
        ("e", "nu", "e"),
        ("mub", "antinu", "mu"),
    ),
)
def test_sns_component_state_preserves_particle_and_flavor_identity(
    component,
    particle_kind,
    density_flavor,
):
    state = sns_component_state(component)

    assert isinstance(state, NeutrinoState)
    assert state.particle_kind == particle_kind
    np.testing.assert_array_equal(state.rho, pure_flavor_density(density_flavor))
    assert state.rho.flags.writeable is False


@pytest.mark.parametrize("component", ("total", "all", "nu_mu", "", None))
def test_sns_component_state_rejects_unknown_or_aggregate_labels(component):
    with pytest.raises(ValueError, match="SNS state component"):
        sns_component_state(component)


@pytest.mark.parametrize("dataset_name", ("CsI2017", "CsI2021"))
def test_sns_source_flux_and_prompt_line_match_pre_phase3_baseline(dataset_name):
    flux = loadNeutrinoEmpiricalFluxSNS(dataset_name)
    baseline = SOURCE_BASELINE[dataset_name]

    assert flux["basic"]["NTimeIntegratedFlux_cm^-2"] == baseline["integrated_flux"]
    assert flux["measured"]["muLine"] == (
        29.792140909877446,
        baseline["integrated_flux"],
    )
    for component, expected_hash in baseline["hashes"].items():
        actual = np.ascontiguousarray(
            np.asarray(
                flux["measured"][component](SOURCE_SAMPLE_ENERGIES_MEV),
                dtype=np.float64,
            )
        )
        assert hashlib.sha256(actual.view(np.uint8)).hexdigest() == expected_hash


@pytest.mark.parametrize("dataset_name", ("CsI2017", "CsI2021"))
def test_sns_source_scalar_array_boundaries_and_component_sum(dataset_name):
    flux = loadNeutrinoEmpiricalFluxSNS(dataset_name)
    measured = flux["measured"]

    assert isinstance(measured["e"](10.0), float)
    energy = np.linspace(0.0, 300.0, 3001, dtype=float)
    e = np.asarray(measured["e"](energy), dtype=float)
    mub = np.asarray(measured["mub"](energy), dtype=float)
    total = np.asarray(measured["totalContinuous"](energy), dtype=float)
    assert e.shape == energy.shape
    assert mub.shape == energy.shape
    assert total.shape == energy.shape
    assert np.all(np.isfinite(total))
    assert np.all(total >= 0.0)
    np.testing.assert_allclose(total, e + mub, rtol=5.0e-16, atol=0.0)
    assert measured["e"](0.0) == 0.0
    assert measured["mub"](301.0) == 0.0

    # Reproduction mode deliberately retains the final interpolation-cell
    # taper, while the direct formula uses the exact approved mask.
    assert measured["mub"](56.5) > 0.0
    direct = loadNeutrinoEmpiricalFluxSNS(dataset_name, use_interpolation=False)
    assert direct["measured"]["mub"](56.5) == 0.0


@pytest.mark.parametrize("dataset_name", ("CsI2017", "CsI2021"))
def test_sns_source_interpolated_normalization_diagnostics(dataset_name):
    flux = loadNeutrinoEmpiricalFluxSNS(dataset_name)
    energy = np.linspace(0.0, 300.0, 300001, dtype=float)
    measured = flux["measured"]
    integrals = np.array(
        [
            np.trapezoid(np.asarray(measured["e"](energy)), energy),
            np.trapezoid(np.asarray(measured["mub"](energy)), energy),
            np.trapezoid(np.asarray(measured["totalContinuous"](energy)), energy),
        ],
        dtype=float,
    )

    np.testing.assert_allclose(
        integrals,
        SOURCE_BASELINE[dataset_name]["integrals"],
        rtol=2.0e-15,
        atol=0.0,
    )


def test_sns_source_rejects_unknown_dataset():
    with pytest.raises(KeyError, match="Unknown dataset"):
        loadNeutrinoEmpiricalFluxSNS("CsI2099")


def test_csi2017_detector_mapping_dirac_response_efficiency_and_bins():
    recoil_kev = np.linspace(0.0, 50.0 / CSI2017_PE_PER_KEV, 101)
    mean_pe = CSI2017_PE_PER_KEV * recoil_kev
    width_pe = np.zeros_like(mean_pe)
    formal_probability_mass = np.ones_like(mean_pe)

    assert CSI2017_PE_PER_KEV == 1.17
    assert np.all(np.diff(mean_pe) > 0.0)
    np.testing.assert_array_equal(width_pe, 0.0)
    np.testing.assert_array_equal(formal_probability_mass, 1.0)
    assert CSI2017_BINS_25.shape == (26,)
    assert np.all(np.diff(CSI2017_BINS_25) > 0.0)

    eff = _interp_eff(
        ROOT / "data" / "datafiles" / "COHERENT_eff.txt",
        0,
        1,
        low=1.0e-10,
        threshold=4.9,
    )
    assert isinstance(eff(10.0), float)
    pe = np.linspace(0.0, 55.0, 551)
    values = np.asarray(eff(pe), dtype=float)
    assert values.shape == pe.shape
    assert eff(4.9) == 1.0e-10
    assert np.all(values >= 0.0)
    assert np.all(values <= 1.0)


@pytest.mark.parametrize("recoil_kev", (1.0, 5.0, 20.0, 40.0))
def test_csi2021_gamma_response_normalization_mean_and_width(recoil_kev):
    eee = float(eee_quenching_csi(recoil_kev))
    gamma_shape = 1.0 + 9.56 * eee
    gamma_rate = (0.0749 / eee) * gamma_shape
    expected_mean = gamma_shape / gamma_rate
    expected_width = np.sqrt(gamma_shape) / gamma_rate
    density = lambda pe: float(p_smearing_csi(pe, recoil_kev))

    normalization = quad(density, 0.0, np.inf, epsabs=1.0e-12, epsrel=1.0e-12)[0]
    mean = quad(
        lambda pe: pe * density(pe),
        0.0,
        np.inf,
        epsabs=1.0e-12,
        epsrel=1.0e-12,
    )[0]
    variance = quad(
        lambda pe: (pe - expected_mean) ** 2 * density(pe),
        0.0,
        np.inf,
        epsabs=1.0e-12,
        epsrel=1.0e-12,
    )[0]

    assert normalization == pytest.approx(1.0, rel=2.0e-14, abs=2.0e-14)
    assert mean == pytest.approx(expected_mean, rel=2.0e-14, abs=1.0e-14)
    assert np.sqrt(variance) == pytest.approx(
        expected_width,
        rel=2.0e-14,
        abs=1.0e-14,
    )
    assert expected_width > 0.0


def test_csi2021_detector_scalar_array_efficiency_and_bins():
    assert isinstance(p_smearing_csi(10.0, 5.0), float)
    pe = np.linspace(-1.0, 80.0, 812)
    density = np.asarray(p_smearing_csi(pe, 5.0), dtype=float)
    efficiency = np.asarray(efficiency_csi2021(pe), dtype=float)
    assert density.shape == pe.shape
    assert efficiency.shape == pe.shape
    assert np.all(np.isfinite(density))
    assert np.all(density >= 0.0)
    assert np.all(density[pe <= 0.0] == 0.0)
    assert isinstance(efficiency_csi2021(10.0), float)
    assert np.all(np.isfinite(efficiency))
    assert np.all(efficiency >= 0.0)
    assert np.all(efficiency <= 1.0)
    assert float(np.max(efficiency)) < 1.0
    assert PE_BINS_9.shape == (10,)
    assert np.all(np.diff(PE_BINS_9) > 0.0)


def test_csi_detector_response_helpers_are_scalar_detector_only():
    detector_helpers = (
        _interp_eff,
        eee_quenching_csi,
        p_smearing_csi,
        efficiency_csi2021,
    )
    source = "\n".join(inspect.getsource(helper) for helper in detector_helpers)
    forbidden = (
        "loadNeutrinoEmpiricalFluxSNS",
        "differential_cross_section",
        "detectorMassKg",
        "wc_triplets",
        "counts_per_bin",
    )
    for token in forbidden:
        assert token not in source
