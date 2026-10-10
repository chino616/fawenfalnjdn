# Phase 2 Target / Exposure Report — CONUS+

## Identity and gates

```yaml
experiment_name: "CONUS+"
experiment_slug: CONUS_Plus
dataset_id: conus_plus_2025_c2c3c5_ge73_pyeft
phase: 2
machine_gate: PASS
contract_human_gate: APPROVED
implementation_human_gate: NOT_REVIEWED
```

## Approved target contract

- Material: germanium represented by the single-isotope `Ge73_only` hybrid
  approximation, not the publication's natural-germanium composition.
- Composition: Ge73 number fraction `1.0`.
- Nuclear identity: `A=73`, `Z=32`, `N=41`.
- Active project Response key: `Ge73` from
  `data/responses/responses_all.json`.
- Response basis: JSON-declared `(p,n)` matrix basis.
- Mass convention: `m_nucleus = A * 1.6605390666e-27 kg`.

## Nuclei-per-kg derivation

```text
m_Ge73 = 73 * 1.6605390666e-27 kg
       = 1.212193518618e-25 kg

nuclei_per_kg = 1 / m_Ge73
              = 8.249507893261811e24 kg^-1
```

This convention matches the active per-kg rate and kernel infrastructure. An
exact isotopic-mass convention was shown as a separate candidate and was not
selected.

## Exposure and normalization ownership

| Detector | Exposure (kg day) | Target nucleus seconds |
| --- | ---: | ---: |
| C2 | 119.0 | 8.481814035536064e31 |
| C3 | 119.0 | 8.481814035536064e31 |
| C5 | 119.0 | 8.481814035536064e31 |

- Selected calculation exposure sum: `357 kg day`.
- Raw observed values `111.15/103.40/111.86 kg day` and publication value
  `327 kg day` are retained as reference metadata.
- The detector exposure already owns detector mass times live time.
- Slow must multiply `exposure_kg_day * nuclei_per_kg * 86400 s/day` exactly
  once for a per-second source flux.
- Detector mass or live time must not be multiplied again.

## ResponseDB verification

`ResponseDB.get_by_symbol_A("Ge", 73)` resolves to `Ge73`. The entry reports
`A=73`, `Z=32`, `N=41`, and the eight active response channels `M`, `Delta`,
`SigmaP`, `SigmaPP`, `PhiPP`, `PhiPT`, `MPhiPP`, and `SigmaPDelta`. All eight
were finite at `y=0`; the coherent `M(0)` matrix was symmetric.

This verifies the project key and internal API only. The repository's nuclear
response audit states that the original external source tables and generation
pipeline remain unavailable. That external provenance limitation is carried to
Phase 4 and is not promoted to a completed source-table audit here.

## Implementation mapping

| Contract field | `experiment.yaml` key |
| --- | --- |
| Ge73-only composition | `target.isotopes`, `target.isotope_number_fractions` |
| Fraction semantics | `target.fraction_convention` |
| A/Z/N | `target.mass_numbers`, `proton_numbers`, `neutron_numbers` |
| Response | `target.response_keys`, `response_database`, `response_basis` |
| Nuclear mass and nuclei/kg | `target.nucleus_mass_convention`, `nucleus_masses_kg`, `nuclei_per_kg` |
| Detector exposure | `exposure.values_kg_day`, `selected_sum_kg_day`, `raw_observed_values_kg_day` |
| Normalization ownership | `exposure.normalization_owner`, `multiply_mass_or_live_time_again` |
| Day-to-second conversion | `exposure.seconds_per_day`, `seconds_per_day_owner` |

No target Python module was created. This phase is a `CONFIG_ONLY` static
contract and repository verification.

## Machine Gate P02

Dependency-free assertions verified:

- isotope number fractions sum to `1.0`;
- `Ge73` resolves through the active `ResponseDB`;
- A/Z/N equal 73/32/41;
- all eight response channels are finite at zero momentum;
- the `A*u` nucleus mass and nuclei-per-kg are reproducible;
- selected detector exposures sum to `357 kg day`;
- `detector_exposure_kg_day` is the unique mass-times-live-time owner;
- `multiply_mass_or_live_time_again` is false;
- the day-to-second constant is `86400`.

Result: `P02=PASS` for the Target / Exposure capability.

## Post-code review

The user approved the earlier raw-exposure implementation through decision
`D0012`. Decision `D0015` supersedes that profile for the selected mainline
calculation. The revised configuration passes its Machine Gate and now awaits
post-rebaseline human review.

## Human Gate Target / Exposure

```yaml
machine_gate: PASS
human_gate: NOT_REVIEWED
approval: null
decision_ref: D0015
evidence_claim: C0044
```

## 2026-10-09 selected-exposure rebaseline

The original detector exposures remain recorded as experimental metadata:
`111.15`, `103.40`, and `111.86 kg day` for C2, C3, and C5. They are no
longer the selected exposure profile for the requested mainline calculation.

The user selected independent calculations at `119 kg day` for each detector:

| Detector | Selected exposure (kg day) | Target nucleus seconds |
| --- | ---: | ---: |
| C2 | 119.0 | 8.481814035536064e31 |
| C3 | 119.0 | 8.481814035536064e31 |
| C5 | 119.0 | 8.481814035536064e31 |

The selected sum is `357 kg day`. Slow must integrate each detector from the
differential rate with its own detector response. It must not obtain these
results by scaling final counts computed at the raw observed exposures.

The configuration and arithmetic checks pass. The revised implementation
human gate is `NOT_REVIEWED` until the user reviews this post-write result.
