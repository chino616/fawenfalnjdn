# CONUS+ C2/C3/C5 Ge73 pyEFT dataset

This directory contains the Phase 1 dataset specification for the approved
`hybrid_approximate_signal_forward_model` claim.

## Identity

- Experiment: CONUS+
- Dataset ID: `conus_plus_2025_c2c3c5_ge73_pyeft`
- Detectors: C2, C3 and C5; C4 is excluded.
- Target contract: Ge73 only. This is not the natural-germanium publication model.
- Primary output: expected CEvNS signal events with shape `(3, 19)` ordered as
  detector `[C2, C3, C5]` by reconstructed-energy bin.

## Dataset boundary

The reconstructed observable is `E_reco` in eVee. The analysis window is
`[160, 350)` eVee with 19 adjacent 10 eVee bins. Detector thresholds are
C2=180 eVee, C3=160 eVee and C5=170 eVee. Their exact efficiency implementation
belongs to Phase 6.

The detector exposures are 111.15, 103.40 and 111.86 kg day. They already own
the mass-times-live-time normalization and must not be multiplied by detector
mass or live time again. The 327 kg day publication total is a rounded reference.

## Current capability

Only the dataset contract is implemented here. Source, target normalization,
theory-response applicability, detector response, Slow, Fast and release gates
remain pending their owning phases. No observed statistical data are attached,
and the natural-Ge publication counts 90/143/113/346 are reference-only.

The authoritative onboarding record is under
`workflows/experiment-integration/runs/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/`.
