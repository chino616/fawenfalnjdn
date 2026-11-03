# CsI2017 dataset specification

This directory is the Phase 1 runtime dataset specification for the existing
COHERENT CsI2017 reproduction path. It does not implement new experiment
physics.

## Identity and provenance

- Dataset: CsI2017
- Family: COHERENT CsI
- Source: stopped-pion SNS
- Target: equal-stoichiometry CsI using Cs-133 and I-127
- Approved inputs:
  - workflows/experiment-integration/runs/CsI2017/00_INPUT_INVENTORY.md
  - workflows/experiment-integration/runs/CsI2017/00_IMPLEMENTATION_MANIFEST.yaml

## Observable and output contract

The true axes are incident energy in MeV and recoil energy in keV. The
reconstructed observable is PE. The output contains 25 PE bins for each source
component key mu, e, mub, plus total, with unit expected events per bin.

The PE edges are regular from 0.001 to 50.0 with width 1.99996.

## Statistical mode

The recorded mode is background_subtracted_excess. It is provisional and is
not used by the Flavor Slow migration. Statistics remains blocked pending
authoritative observed/background/covariance provenance.

## Implemented phase

DATASET_VALIDATED only. Existing Python registry behavior is unchanged.

## Pending modules

- Target text validation: Phase 2.
- Canonical SNS source states: Phase 3.
- Theory coverage report: Phase 4.
- Cross-section validation: Phase 5.
- Detector-response validation: Phase 6.
- Flavor-aware Slow counts: Phase 7.
- Fast counts: blocked until P4 Flavor contract.
- Statistics: blocked pending provenance.

## Known blockers

ANTI-NU AUDIT is required before changing interaction-kernel physics.
The 14.57/14.6 kg and physical/legacy prompt-energy differences remain explicit
reproduction conventions and are not resolved in Phase 1.

