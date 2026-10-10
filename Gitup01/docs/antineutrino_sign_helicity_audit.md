# Antineutrino Sign And Helicity Audit

Status: REQUIRES PHYSICS AUDIT.

This note records the current antineutrino handling after the flavor refactor.
It is intentionally not a claim that the antineutrino sign/helicity convention
has been fully validated for every Li2026 operator.

## Current Code Contract

- `src/cevns_pyeft/sources/state.py` defines `NeutrinoState(particle_kind,
  rho)` and states that `particle_kind` is metadata at the current boundary.
- `src/cevns_pyeft/rates/differential.py` accepts `rho` as either a
  `NeutrinoState` or a raw density matrix plus explicit `particle_kind`.
- `differential_cross_section_nn(...)` contracts the flavor kernel with
  `rho`; it returns the preserved `particle_kind`, but it does not branch the
  scattering kernel on `nu` versus `antinu`.
- `src/cevns_pyeft/experiments/coherent/sns.py` maps SNS `mub` to
  `NeutrinoState("antinu", rho_mu)`.

## Current Regression Coverage

`tests/test_source_state_p2.py::test_p2_antinu_label_is_preserved_without_silent_kernel_physics_change`
locks the current behavior:

- a `nu` and an `antinu` state with the same flavor density produce identical
  numerical `dsigma_cm2_per_keV` for the tested Wilson point;
- the returned result preserves the different `particle_kind` labels.

This protects against accidental silent physics changes during the flavor
refactor.  It does not validate that this behavior is the complete physical
answer for all LNC, LNV, interference, and parity-odd terms.

## External Formula Check Performed

The Li2026 arXiv HTML page for arXiv:2601.19883 was checked.  The experimental
rate section writes a common recoil-rate definition for an incident
`(anti)neutrino` flux and the COHERENT count formula sums over `nu_e`, `nu_mu`,
and `bar{nu}_mu`.  The same page search did not expose a `helicity` discussion
or a complete operator-by-operator antineutrino sign table.

The APS accepted-manuscript page for the same work was checked on 2026-09-10.
It lists the accepted manuscript date as 2026-08-07.  The accepted page does
not currently expose supplemental material or an operator-by-operator
antineutrino sign/helicity table that would close this audit.

Therefore the current program behavior may be consistent with the rate-level
contract used in parts of the paper, but this is still insufficient to close
the requested sign/helicity audit for every operator class.

## Required Evidence To Complete This Audit

To mark this PASS, compare the implementation against paper/source formulas
for each relevant term:

- LNC vector, axial, derivative, and gluonic operators;
- LNV operators and their diagonal/off-diagonal flavor rules;
- interference terms;
- parity-odd terms;
- SNS `bar{nu}_mu` and reactor `bar{nu}_e` use cases.

Only after that comparison should the code either keep the current shared
kernel or introduce an explicit `particle_kind` branch with dedicated tests.
