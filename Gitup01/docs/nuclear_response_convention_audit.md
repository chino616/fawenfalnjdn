# Nuclear Response Convention Audit

Status: NOT COMPLETED for full external source-table validation.

This note records the current evidence for the nuclear-response convention used
by the flavor refactor.  It separates internal program invariants from the
external audit that still requires the original response tables or their
generation pipeline.

## Current Internal Contract

- `data/responses/responses_all.json` declares `basis: np`.
- Its metadata note says each response entry is a `2x2` matrix in `(p,n)`.
- `src/cevns_pyeft/nuclear/response.py` reads the JSON directly through
  `ResponseDB` and evaluates every matrix entry as
  `Exp[exp_factor*y] * poly(y)`.
- `ResponseW.W_np(...)` returns the JSON-declared matrix.
- `ResponseW.W_iso(...)` is derived inside the program from `W_np(...)` using
  the fixed change-of-basis matrix `[[1, 1], [1, -1]]`.

Therefore the current `np` / `iso` regression is an internal basis-change
invariance check.  It does not prove that the JSON numbers themselves match an
external paper/source-table convention.

## Current Regression Coverage

`tests/test_nuclear_response_convention.py` currently verifies:

- the JSON metadata declares `basis == "np"`;
- coherent `M(0)` for Cs, I, and Ar is closer to `(p,n)` ordering
  `[[Z^2, ZN], [ZN, N^2]]` than to swapped `(n,p)` ordering;
- the coherent `M(0)` cross term has the positive sign used by the current
  contraction path;
- the iodine `M_nn(0)` residual against exact integer `N^2` is frozen as
  unresolved normalization evidence, not promoted to a completed audit.

## Missing Evidence

The current worktree search found only the aggregated response file:

- `data/responses/responses_all.json`

No original source tables, table-conversion script, or source-table provenance
file was found under `data/responses` or `tools`.

The public CEvNS-pyEFT repository was also checked.  Its `data/responses`
directory exposes `responses_all.json`; its `docs/theory` directory exposes
Li2026 formula notes, but neither listing provides the original nuclear
response source tables or a generation pipeline for the JSON response file.

The APS accepted-manuscript page for the same work was checked on 2026-09-10.
It lists the accepted manuscript date as 2026-08-07 and notes that any
supplemental material, if provided, will be made available when the version of
record is published.  The accepted-manuscript page does not currently expose
source tables or response-generation code that can close this audit.

Additional local recovery searches under `codex-history-recovery`, older
project copies, and backup directories found repeated copies of
`responses_all.json`, legacy re-export tests, and generated workflow grids, but
no independent source tables or conversion code.  The legacy
`tests/test_nuclear_response.py` only checks that split modules reproduce the
old engine re-export behavior; it is not an external convention audit.

Without those external inputs, the following cannot be honestly marked PASS:

- all response-channel source-table ordering;
- all response-channel normalization;
- all response-channel sign convention.

## Required Evidence To Complete The External Audit

To close this item, supply or recover the original source tables or generation
pipeline for `responses_all.json`, then compare every response channel and
nucleus against the JSON-loaded `W_np` entries.  The audit should explicitly
cover ordering, normalization, sign convention, polynomial coefficient order,
and the shared exponential factor.
