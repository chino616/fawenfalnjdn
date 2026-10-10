# Legacy operator coverage

This file separates statistics architecture migration from old operator-scan physics validation.

| Old operator/workflow | Old scan function | New parameterization available? | New predictor available? | Validated? | Status |
|---|---|---:|---:|---:|---|
| `(6,1,u)` vector NSI diagonal ee/mumu and e-mu matrix entries | `chi2_2d.scan_eps_ud`, `cutoff_single.scan_one_operator` | yes, `statistics.parameters.VectorNSIParameters` | yes, through Slow/Fast predictor adapters | fixed statistics only | MIGRATED_NOT_VALIDATED |
| `(6,1,d)` vector NSI diagonal ee/mumu and e-mu matrix entries | `chi2_2d.scan_eps_ud`, `cutoff_single.scan_one_operator` | yes, `statistics.parameters.VectorNSIParameters` | yes, through Slow/Fast predictor adapters | fixed statistics only | MIGRATED_NOT_VALIDATED |
| Full scalar legacy triplet basis from saved kernels | `cutoff_single.run_single_experiment` | no complete Flavor parameter object yet | partially, kernel reconstruction exists | no | DEFERRED |
| Multi-experiment 1D cutoff scans | `cutoff_multi.scan_one_operator_multi` | partially | partially | fixed likelihood components only | DEFERRED |
| Flow A CsI2021/Ar2020 2D original pointwise scan | `chi2_2d.scan_model_two_operator_plane` | partially | partially | no full scan reference yet | DEFERRED |
| Flow B complete NSI CsI2017/CsI2021/Ar2020 combinations | `chi2_2d.run_complete_nsi_2d_workflow` | partially | partially | no full scan reference yet | DEFERRED |

`MIGRATED_NOT_VALIDATED` here means the new statistics layer can represent the fixed-input likelihood mathematics, not that every old physics scan or figure has been restored.
