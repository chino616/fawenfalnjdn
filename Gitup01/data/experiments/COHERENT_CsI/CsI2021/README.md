# CsI2021 dataset specification

This directory is the Phase 1 runtime dataset specification for the existing
COHERENT CsI2021 reproduction path. It does not implement new experiment
physics.

## Identity and provenance

- Dataset: CsI2021
- Family: COHERENT CsI
- Source: stopped-pion SNS
- Target: equal-stoichiometry CsI using Cs-133 and I-127
- Approved inputs:
  - workflows/experiment-integration/runs/CsI2021/00_INPUT_INVENTORY.md
  - workflows/experiment-integration/runs/CsI2021/00_IMPLEMENTATION_MANIFEST.yaml

## Observable and output contract

The true axes are incident energy in MeV and recoil energy in keV. The
reconstructed observable is PE. The output contains nine PE bins for each
source component key mu, e, mub, plus total, with unit expected events per bin.

The explicit PE edges are 0.001, 8.001, 12.001, 16.001, 20.001, 24.001,
32.001, 40.001, 48.001 and 60.001.

## Statistical mode

The recorded mode is background_subtracted_excess. It is provisional and is
not used by the Flavor Slow migration. Statistics remains blocked pending
authoritative provenance.

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

ANTI-NU AUDIT is required before changing interaction-kernel physics. The
physical/legacy prompt-energy difference remains a reproduction convention.

