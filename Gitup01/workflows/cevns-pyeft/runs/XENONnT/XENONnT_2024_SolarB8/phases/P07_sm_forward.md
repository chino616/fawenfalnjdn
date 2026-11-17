# P07: sm_forward

2026-11-07。本轮固定SM前向输出的实际实施与校验，具体数值见结果文件。

物理实施范围见D0001/W0001。机器检查和实际输入/代码指纹见结构化记录；结果尚未由用户验收，不将其记为APPROVED。

```json phase-result
{
  "schema_version": 1,
  "phase": "P07",
  "capability_id": "solar_b8.sm_forward",
  "workspace": "canonical",
  "plan_status": "READY",
  "machine_gate": "PASS",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/00_PHASE0_PLAN.md",
  "input_refs": [
    "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml",
    "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz"
  ],
  "input_fingerprint": "b1311e633159e0d57dfb57290181d68cb3399ef530e63d83292183e20b90e6b1",
  "evidence_refs": [
    "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P01_EVIDENCE_LEDGER.yaml"
  ],
  "decision_refs": [
    "D0001"
  ],
  "approval_refs": [],
  "artifacts": [
    {
      "path": "outputs/solar_b8_sm/20261107_run1/XENONnT_2024_SolarB8/SM_RESULT.json",
      "sha256": "910c0641cc21d82cc14a55c09692d3dc16499bfaf2fea1a699463923c81305c0",
      "role": "actual result or package"
    },
    {
      "path": "outputs/solar_b8_sm/20261107_run1/XENONnT_2024_SolarB8/REFERENCE_COMPARISON.json",
      "sha256": "e2667121f0378025bc11b7b0a8827ad48962cf6be16b53794fa711a33ce1c4f7",
      "role": "actual result or package"
    },
    {
      "path": "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml",
      "sha256": "271e18b89398ed90c29db2f88924a10514125328a7c27f69de49baa33c1111c4",
      "role": "actual result or package"
    },
    {
      "path": "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz",
      "sha256": "39aa001f5c5657ddbb0099f232ee7e2a81f78ff383da3cf43b0dc214b62fdeb2",
      "role": "actual result or package"
    }
  ],
  "checks": [
    {
      "name": "actual artifact and scoped computation",
      "status": "PASS",
      "command": "python -B tools/run_solar_b8_sm_benchmark.py",
      "result_ref": "outputs/solar_b8_sm/20261107_run1/XENONnT_2024_SolarB8/SM_RESULT.json"
    }
  ],
  "handoff": {
    "normalization_ledger": {
      "reference_fluence": {
        "input_unit": "cm^-2 s^-1 MeV^-1",
        "live_seconds": 31557600.0,
        "output_unit": "cm^-2 MeV^-1",
        "geometry_included": true
      },
      "anchor_mass_kg": 1000.0,
      "run_exposures_tyr": [
        1.174398,
        2.342593
      ],
      "mass_time_application": "one reference-year fluence * anchor nuclei * exposure_tyr/anchor_tonne",
      "efficiency": "included in response; applied once",
      "c_i": "absent"
    },
    "output_contract": {
      "observable": {
        "name": "run-specific cS2 analysis bin index",
        "unit": "1",
        "edges_ref": "observable_edges",
        "bin_count": 3
      },
      "per_run": {
        "SR0": [
          1.5829929639656017,
          1.9436397082967674,
          0.968433185827647
        ],
        "SR1": [
          1.9310379539657767,
          3.705468864915228,
          2.1856605465766727
        ]
      }
    },
    "numerics_and_convergence": {
      "runs": [
        {
          "label": "base",
          "n_er": 201,
          "n_enu": 120,
          "counts": [
            3.5140075849392067,
            5.649013159795075,
            3.1539325968303573
          ],
          "total_events": 12.31695334156464,
          "seconds": 2.729718499991577
        },
        {
          "label": "recoil_refined",
          "n_er": 401,
          "n_enu": 120,
          "counts": [
            3.5139917941382772,
            5.648999588833418,
            3.1539640273336045
          ],
          "total_events": 12.3169554103053,
          "seconds": 3.590504800027702
        },
        {
          "label": "recoil_fine",
          "n_er": 801,
          "n_enu": 120,
          "counts": [
            3.5139914641351107,
            5.649022061662823,
            3.1540115866282634
          ],
          "total_events": 12.317025112426196,
          "seconds": 5.607643200026359
        },
        {
          "label": "energy_refined",
          "n_er": 801,
          "n_enu": 480,
          "counts": [
            3.5140309179313785,
            5.649108573211995,
            3.1540937324043195
          ],
          "total_events": 12.317233223547694,
          "seconds": 5.6774405999458395
        }
      ],
      "checks": [
        {
          "axis": "recoil",
          "from": "recoil_refined",
          "to": "recoil_fine",
          "absolute_difference": [
            3.3000316657094686e-07,
            2.247282940448514e-05,
            4.755929465893871e-05
          ],
          "relative_difference": [
            9.391120323969531e-08,
            3.978180499063254e-06,
            1.5078985397698262e-05
          ],
          "tolerance_events": [
            0.007027982928270221,
            0.011298044123325647,
            0.006308023173256527
          ],
          "passed": true
        },
        {
          "axis": "neutrino_energy",
          "from": "recoil_fine",
          "to": "energy_refined",
          "absolute_difference": [
            3.945379626779655e-05,
            8.651154917238557e-05,
            8.214577605603068e-05
          ],
          "relative_difference": [
            1.1227504022936146e-05,
            1.5314194806349145e-05,
            2.6044177194890197e-05
          ],
          "tolerance_events": [
            0.007028061835862757,
            0.01129821714642399,
            0.006308187464808639
          ],
          "passed": true
        }
      ],
      "passed": true
    },
    "reference_comparison": {
      "computed_signal": [
        [
          1.5829929639656017,
          1.9436397082967674,
          0.968433185827647
        ],
        [
          1.9310379539657767,
          3.705468864915228,
          2.1856605465766727
        ]
      ],
      "native_release_signal_reference": [
        [
          1.5193861288836636,
          1.8462526548067415,
          0.8802765818958079
        ],
        [
          1.9238115769962885,
          3.6670498753127183,
          2.079317557470305
        ]
      ],
      "fractional_difference_per_run_bin": [
        [
          0.0418635091322519,
          0.05274849746944299,
          0.1001464832132426
        ],
        [
          0.0037562810495044285,
          0.010476811308500089,
          0.051143217025370724
        ]
      ],
      "backgrounds": {
        "AC": [
          [
            2.49382709753674,
            2.493917407781454,
            2.493917407781454
          ],
          [
            5.922360224535165,
            5.922360224535165,
            5.922360224535165
          ]
        ],
        "ER": [
          [
            0.0029035816053515195,
            0.012084318984795542,
            0.11085828616724965
          ],
          [
            0.007597281561417551,
            0.043438445446377365,
            0.5025988660836795
          ]
        ],
        "neutron": [
          [
            0.027756136104055477,
            0.036911187546053,
            0.06812122025998578
          ],
          [
            0.04222990054879811,
            0.08355387762090191,
            0.20836285879881414
          ]
        ]
      },
      "observed": [
        [
          5.0,
          3.0,
          1.0
        ],
        [
          11.0,
          11.0,
          6.0
        ]
      ],
      "reference_total_events": 11.916094375365525,
      "paper_exposure_total_tyr": 3.51,
      "adopted_release_exposure_total_tyr": 3.516991,
      "signal_rescaled_only_to_paper_total_exposure": [
        [
          1.5798463241786123,
          1.9397761825724469,
          0.9665081549128334
        ],
        [
          1.9271994777410222,
          3.6981032126190967,
          2.1813159369711554
        ]
      ],
      "scope": "SM cross section/source computed here. Native template is an independent released reference at its own source/model conventions, not a fit target."
    },
    "freeze_scope": {
      "kind": "versioned numerical candidate reference",
      "physics_fingerprint": "86c45c9280e7ea74de38576960958a3f7b664f3331f865e7ceb934904a4aac32",
      "arrays": "outputs/solar_b8_sm/20261107_run1/XENONnT_2024_SolarB8/sm_prediction.npz",
      "sha256": "f1d9d2e357dc96c866315213bd174304f922b533f1cf2dce019e3f9d8cd3936a",
      "parameter_point": {
        "include_sm": true,
        "sin2thetaW": 0.23857,
        "total_B8_flux_cm2_s": 5460000.0,
        "nuclear": "Klein-Nystrand, 2411.11749v1 Eqs.(1)-(3)"
      },
      "human_freeze": "NOT_REVIEWED",
      "Fast_authorized": false
    }
  }
}
```
