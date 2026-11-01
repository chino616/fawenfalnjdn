# Missing and conflicting inputs — XENONnT 2026 public templates

## Blocking audit items

| item | status | downstream owner | needed by | candidate source |
| --- | --- | --- | --- | --- |
| HDF5 keys and array shapes | MISSING | detector response | P06 | official release files |
| Four-dimensional axis ordering | MISSING | detector response | P06 | binning YAML and notebook |
| Mono-NR template units | MISSING | detector response | P06 | README and HDF5 attributes |
| Background template rate units | MISSING | detector response | P06 | README and HDF5 attributes |
| Science-run exposure mapping | MISSING | target/exposure | P02/P06 | release metadata |
| Nuisance priors and correlations | MISSING | statistics | P09 | public analysis materials |
| Masks, interpolation, truncation | MISSING | detector response | P06 | notebook and template audit |

## Conflict retained

The 2024 XENONnT paper benchmark is not a substitute for this release. The two inputs may
share science-run data and must not be combined as independent likelihood terms.

