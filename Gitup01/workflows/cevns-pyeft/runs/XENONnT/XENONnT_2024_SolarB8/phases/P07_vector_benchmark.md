# P07: p07

2026-11-08。按用户选择继续V与B−L事例数谱。机器验证与科学接受分开；Human仍为NOT_REVIEWED。

```json phase-result
{
  "schema_version": 1,
  "phase": "P07",
  "capability_id": "solar_b8.vector.p07",
  "workspace": "canonical",
  "plan_status": "READY",
  "machine_gate": "PASS",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "outputs/solar_b8_vector/20261108_run1/EXECUTION_PLAN.json",
  "input_refs": [
    "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml",
    "data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz",
    "data/benchmarks/solar_b8_vector_v1/benchmark.input.json",
    "cevns_pyeft/theory/light_vector.py",
    "cevns_pyeft/experiments/solar_vector.py"
  ],
  "input_fingerprint": "25003990a234559ccf2194ad02fd0d730a40f13363fde60c889778bea6e6f491",
  "evidence_refs": [
    "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P01_EVIDENCE_LEDGER.yaml"
  ],
  "decision_refs": [
    "D0002"
  ],
  "approval_refs": [],
  "artifacts": [
    {
      "path": "outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/DATASET_RESULT.json",
      "sha256": "b64fc73ac1ec96a1cf9c41ed3e0ec680721828e4d807cb959c68842921b58c3b",
      "role": "actual vector benchmark result"
    },
    {
      "path": "outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/BENCHMARK_REPORT.md",
      "sha256": "d945ce74dc894c59c07ee620f3b486b97207579545b9fa0ef8cdbfbc27f99b87",
      "role": "actual vector benchmark result"
    },
    {
      "path": "outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/events.png",
      "sha256": "02f9a78ce52928818a7053233acbf2da2f727f676bff7591491c83aafeea0e24",
      "role": "actual vector benchmark result"
    }
  ],
  "checks": [
    {
      "name": "fixed-point Slow and independent signed-interference closure",
      "status": "PASS",
      "command": "python -B tools/run_solar_b8_vector_benchmark.py --output outputs/solar_b8_vector/20261108_run1",
      "result_ref": "outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/DATASET_RESULT.json"
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
      "name": "run-specific cS2 analysis bin index",
      "unit": "1",
      "edges": [
        0.0,
        1.0,
        2.0,
        3.0
      ],
      "detector_ids": [
        "SR0",
        "SR1"
      ],
      "aggregation": "sum_identical_bins"
    },
    "numerics_and_convergence": {
      "SM": {
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
            "seconds": 3.306787899986375
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
            "seconds": 3.3998445000033826
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
            "seconds": 3.893423500005156
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
            "seconds": 2.71350930002518
          }
        ],
        "checks": [
          {
            "axis": "recoil",
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
      "V10_g1": {
        "runs": [
          {
            "label": "base",
            "n_er": 201,
            "n_enu": 120,
            "counts": [
              2.4361634034094557,
              4.084489190151463,
              2.405655068081798
            ],
            "total_events": 8.926307661642717,
            "seconds": 2.4677280000178143
          },
          {
            "label": "recoil_refined",
            "n_er": 401,
            "n_enu": 120,
            "counts": [
              2.4361518569289804,
              4.084478260836788,
              2.405678610520775
            ],
            "total_events": 8.926308728286545,
            "seconds": 5.013923200021964
          },
          {
            "label": "recoil_fine",
            "n_er": 801,
            "n_enu": 120,
            "counts": [
              2.436151150977024,
              4.0844927280404075,
              2.4057133651586993
            ],
            "total_events": 8.926357244176131,
            "seconds": 6.580611100012902
          },
          {
            "label": "energy_refined",
            "n_er": 801,
            "n_enu": 480,
            "counts": [
              2.4361800365535307,
              4.084558482827038,
              2.4057786795777076
            ],
            "total_events": 8.926517198958276,
            "seconds": 6.80629040003987
          }
        ],
        "checks": [
          {
            "axis": "recoil",
            "absolute_difference": [
              7.059519564478478e-07,
              1.4467203619084046e-05,
              3.475463792446121e-05
            ],
            "relative_difference": [
              2.897816730972231e-07,
              3.5419829541537436e-06,
              1.4446707753219189e-05
            ],
            "tolerance_events": [
              0.004872302301954048,
              0.008168985456080816,
              0.004811426730317398
            ],
            "passed": true
          },
          {
            "axis": "neutrino_energy",
            "absolute_difference": [
              2.8885576506709754e-05,
              6.575478663073397e-05,
              6.531441900836654e-05
            ],
            "relative_difference": [
              1.1856913722835625e-05,
              1.6098382948167074e-05,
              2.7148972414965182e-05
            ],
            "tolerance_events": [
              0.004872360073107061,
              0.008169116965654076,
              0.004811557359155416
            ],
            "passed": true
          }
        ],
        "passed": true
      },
      "V10_g2": {
        "runs": [
          {
            "label": "base",
            "n_er": 201,
            "n_enu": 120,
            "counts": [
              0.46300955636046864,
              1.0092413189024958,
              0.8020759940158338
            ],
            "total_events": 2.274326869278798,
            "seconds": 3.19677529996261
          },
          {
            "label": "recoil_refined",
            "n_er": 401,
            "n_enu": 120,
            "counts": [
              0.4630067577704245,
              1.0092371449828532,
              0.802083060337469
            ],
            "total_events": 2.2743269630907466,
            "seconds": 4.061467799998354
          },
          {
            "label": "recoil_fine",
            "n_er": 801,
            "n_enu": 120,
            "counts": [
              0.4630060174192871,
              1.0092380628852262,
              0.8020919856861767
            ],
            "total_events": 2.27433606599069,
            "seconds": 6.268970299977809
          },
          {
            "label": "energy_refined",
            "n_er": 801,
            "n_enu": 480,
            "counts": [
              0.46301385366428766,
              1.0092597822640426,
              0.8021189920101682
            ],
            "total_events": 2.2743926279384983,
            "seconds": 6.906464700005017
          }
        ],
        "checks": [
          {
            "axis": "recoil",
            "absolute_difference": [
              7.403511373960114e-07,
              9.179023729988245e-07,
              8.925348707666814e-06
            ],
            "relative_difference": [
              1.5990097526649794e-06,
              9.095003515570055e-07,
              1.112758744251923e-05
            ],
            "tolerance_events": [
              0.0009260120348385742,
              0.0020184761257704526,
              0.0016041839713723533
            ],
            "passed": true
          },
          {
            "axis": "neutrino_energy",
            "absolute_difference": [
              7.836245000558684e-06,
              2.1719378816342783e-05,
              2.7006323991551895e-05
            ],
            "relative_difference": [
              1.6924428801736078e-05,
              2.152010730836846e-05,
              3.366872528958839e-05
            ],
            "tolerance_events": [
              0.0009260277073285753,
              0.002018519564528085,
              0.0016042379840203365
            ],
            "passed": true
          }
        ],
        "passed": true
      },
      "V10_g3": {
        "runs": [
          {
            "label": "base",
            "n_er": 201,
            "n_enu": 120,
            "counts": [
              1.3756821364130574,
              1.2782416590937646,
              0.26695591117159
            ],
            "total_events": 2.920879706678412,
            "seconds": 3.103176500007976
          },
          {
            "label": "recoil_refined",
            "n_er": 401,
            "n_enu": 120,
            "counts": [
              1.3756806340705878,
              1.2782448456794806,
              0.26695947754922594
            ],
            "total_events": 2.920884957299294,
            "seconds": 4.333744400006253
          },
          {
            "label": "recoil_fine",
            "n_er": 801,
            "n_enu": 120,
            "counts": [
              1.3756834812114935,
              1.2782580733335116,
              0.266967303019207
            ],
            "total_events": 2.9209088575642124,
            "seconds": 6.89955239999108
          },
          {
            "label": "energy_refined",
            "n_er": 801,
            "n_enu": 480,
            "counts": [
              1.3756917529965038,
              1.2782671832986736,
              0.2669710824385743
            ],
            "total_events": 2.920930018733752,
            "seconds": 6.7476801999728195
          }
        ],
        "checks": [
          {
            "axis": "recoil",
            "absolute_difference": [
              2.8471409057040376e-06,
              1.3227654031000569e-05,
              7.82546998107092e-06
            ],
            "relative_difference": [
              2.069619170826059e-06,
              1.0348187355081409e-05,
              2.9312465955832485e-05
            ],
            "tolerance_events": [
              0.002751366962422987,
              0.002556516146667023,
              0.000533934606038414
            ],
            "passed": true
          },
          {
            "axis": "neutrino_energy",
            "absolute_difference": [
              8.27178501028314e-06,
              9.109965162013012e-06,
              3.7794193673001963e-06
            ],
            "relative_difference": [
              6.012818636344737e-06,
              7.126808292538651e-06,
              1.4156661960457006e-05
            ],
            "tolerance_events": [
              0.0027513835059930075,
              0.002556534366597347,
              0.0005339421648771486
            ],
            "passed": true
          }
        ],
        "passed": true
      },
      "BL10_g2": {
        "runs": [
          {
            "label": "base",
            "n_er": 201,
            "n_enu": 120,
            "counts": [
              5.2778980078226505,
              8.154610610570742,
              4.317886879060211
            ],
            "total_events": 17.750395497453603,
            "seconds": 3.1166480000247248
          },
          {
            "label": "recoil_refined",
            "n_er": 401,
            "n_enu": 120,
            "counts": [
              5.277875524761232,
              8.154593214197506,
              4.317930690557607
            ],
            "total_events": 17.750399429516346,
            "seconds": 4.8020322999800555
          },
          {
            "label": "recoil_fine",
            "n_er": 801,
            "n_enu": 120,
            "counts": [
              5.277875979509441,
              8.15462907501066,
              4.317998585422986
            ],
            "total_events": 17.75050363994309,
            "seconds": 6.932830700010527
          },
          {
            "label": "energy_refined",
            "n_er": 801,
            "n_enu": 480,
            "counts": [
              5.2779322867577605,
              8.154747989804658,
              4.31810633233558
            ],
            "total_events": 17.750786608897997,
            "seconds": 6.899111600010656
          }
        ],
        "checks": [
          {
            "axis": "recoil",
            "absolute_difference": [
              4.5474820975499597e-07,
              3.586081315454237e-05,
              6.789486537872591e-05
            ],
            "relative_difference": [
              8.616121551936564e-08,
              4.39760200306787e-06,
              1.5723688657039012e-05
            ],
            "tolerance_events": [
              0.010555751959018884,
              0.016309258150021322,
              0.008635997170845972
            ],
            "passed": true
          },
          {
            "axis": "neutrino_energy",
            "absolute_difference": [
              5.6307248319065195e-05,
              0.00011891479399750438,
              0.0001077469125938535
            ],
            "relative_difference": [
              1.0668429464383068e-05,
              1.458227699325297e-05,
              2.495235279108453e-05
            ],
            "tolerance_events": [
              0.010555864573515521,
              0.016309495979609318,
              0.00863621266467116
            ],
            "passed": true
          }
        ],
        "passed": true
      },
      "V1_g2": {
        "runs": [
          {
            "label": "base",
            "n_er": 201,
            "n_enu": 120,
            "counts": [
              0.3478160249080541,
              0.5963303468277352,
              0.5102783097593736
            ],
            "total_events": 1.454424681495163,
            "seconds": 3.2625364999985322
          },
          {
            "label": "recoil_refined",
            "n_er": 401,
            "n_enu": 120,
            "counts": [
              0.34781503347636256,
              0.5963284795035397,
              0.5102824789300432
            ],
            "total_events": 1.4544259919099454,
            "seconds": 4.633586700016167
          },
          {
            "label": "recoil_fine",
            "n_er": 801,
            "n_enu": 120,
            "counts": [
              0.34781483904661115,
              0.5963291012060807,
              0.5102870741618225
            ],
            "total_events": 1.4544310144145145,
            "seconds": 7.230205500032753
          },
          {
            "label": "energy_refined",
            "n_er": 801,
            "n_enu": 480,
            "counts": [
              0.3478199023152621,
              0.5963432478963042,
              0.5103070353561254
            ],
            "total_events": 1.4544701855676918,
            "seconds": 7.769742400036193
          }
        ],
        "checks": [
          {
            "axis": "recoil",
            "absolute_difference": [
              1.9442975141004126e-07,
              6.217025410037991e-07,
              4.595231779314091e-06
            ],
            "relative_difference": [
              5.590036122178946e-07,
              1.0425493905066856e-06,
              9.005189455096503e-06
            ],
            "tolerance_events": [
              0.0006956296780932223,
              0.0011926582024121616,
              0.001020574148323645
            ],
            "passed": true
          },
          {
            "axis": "neutrino_energy",
            "absolute_difference": [
              5.063268650962183e-06,
              1.4146690223482139e-05,
              1.996119430291987e-05
            ],
            "relative_difference": [
              1.455715621003442e-05,
              2.372239523694926e-05,
              3.9116047633930135e-05
            ],
            "tolerance_events": [
              0.0006956398046305243,
              0.0011926864957926085,
              0.001020614070712251
            ],
            "passed": true
          }
        ],
        "passed": true
      },
      "V100_g2": {
        "runs": [
          {
            "label": "base",
            "n_er": 201,
            "n_enu": 120,
            "counts": [
              3.3420364563580556,
              5.373744211350554,
              3.001335023730538
            ],
            "total_events": 11.71711569143915,
            "seconds": 3.389891600003466
          },
          {
            "label": "recoil_refined",
            "n_er": 401,
            "n_enu": 120,
            "counts": [
              3.3420214351816666,
              5.373731296244441,
              3.0013649322916547
            ],
            "total_events": 11.717117663717762,
            "seconds": 4.3802623999654315
          },
          {
            "label": "recoil_fine",
            "n_er": 801,
            "n_enu": 120,
            "counts": [
              3.3420211197711414,
              5.3737526616634215,
              3.0014101756887315
            ],
            "total_events": 11.717183957123295,
            "seconds": 6.03311560000293
          },
          {
            "label": "energy_refined",
            "n_er": 801,
            "n_enu": 480,
            "counts": [
              3.3420586554540317,
              5.373834988708223,
              3.00148838077725
            ],
            "total_events": 11.717382024939505,
            "seconds": 6.577368400001433
          }
        ],
        "checks": [
          {
            "axis": "recoil",
            "absolute_difference": [
              3.154105252534123e-07,
              2.1365418980678896e-05,
              4.524339707678848e-05
            ],
            "relative_difference": [
              9.437717894344466e-08,
              3.9758843262550395e-06,
              1.5074046674212569e-05
            ],
            "tolerance_events": [
              0.006684042239542283,
              0.010747505323326844,
              0.0060028203513774634
            ],
            "passed": true
          },
          {
            "axis": "neutrino_energy",
            "absolute_difference": [
              3.753568289033282e-05,
              8.232704480182207e-05,
              7.820508851841268e-05
            ],
            "relative_difference": [
              1.1231305838716182e-05,
              1.531998004680305e-05,
              2.6055436036091233e-05
            ],
            "tolerance_events": [
              0.006684117310908064,
              0.010747669977416446,
              0.0060029767615545
            ],
            "passed": true
          }
        ],
        "passed": true
      }
    },
    "reference_comparison": "Previous SM counts matched; independent per-isotope reweight/fold closure for each nonzero point",
    "freeze_scope": {
      "kind": "versioned fixed-point numerical candidate",
      "human_freeze": "NOT_REVIEWED",
      "Fast_authorized": false
    }
  }
}
```
