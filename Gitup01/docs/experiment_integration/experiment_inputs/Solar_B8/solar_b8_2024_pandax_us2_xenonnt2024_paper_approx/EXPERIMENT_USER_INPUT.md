# Solar B8 2024 paper-approx input

## Identity

```yaml
experiment_name: Solar 8B neutrino scattering
experiment_slug: Solar_B8
dataset_id: solar_b8_2024_pandax_us2_xenonnt2024_paper_approx
task_scope: physics_onboarding
input_mode: guided
scope_gate: APPROVED
scientific_claim: paper_approximate_single_bin_eft_benchmark
```

## Scope

This dataset records the single-bin phenomenological benchmark of
arXiv:2409.04703v2. It contains two separate detector inputs: PandaX-4T US2
and XENONnT 2024. It is not an official multidimensional collaboration
likelihood and must not be combined with the XENONnT 2026 public-template
dataset.

The published benchmark inputs are reference values. They do not replace the
detector efficiencies, xenon response conventions, or propagation arrays that
are still required for a forward reproduction.

## Detector inputs

| detector | exposure | threshold | N_meas | N_SM | sigma_stat | sigma_alpha |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PandaX-4T US2 | 1.04 t yr | 0.33 keVnr | 69.1 | 44.9 | 0.37 x 69.1 | 0.245 |
| XENONnT 2024 | 3.51 t yr | 0.50 keVnr | 10.7 | 11.15 | 3.95 | 0.13 |

The paired PandaX exposure values and the XENONnT 2026 science-run release
are outside this dataset's likelihood. The 2024 and 2026 XENONnT samples may
overlap and must not be added as independent observations.

## Statistical contract

The paper-approximate statistic is

```text
chi2(C) = min_alpha [(N_meas - (1 + alpha) N_pred(C))^2 / sigma_stat^2
                     + alpha^2 / sigma_alpha^2]
```

Use DeltaChi2=2.71 for one scanned parameter and DeltaChi2=4.61 for two
parameters. Any result must retain the `paper_approximate` label.

## Current blockers

PandaX US2 and XENONnT 2024 signal efficiencies, the paper Xe-131 response
convention, PEANUTS exposure-averaged probabilities, and quantitative Fig.4--6
reference contours are not yet available as verified machine-readable inputs.

