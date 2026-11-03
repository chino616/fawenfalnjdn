# Sec. 3.3 detector-level FV benchmark

| Source | SM | FV NP only | SM+FV NP | Delta N |
|---|---:|---:|---:|---:|
| Prompt nu_mu | 50.555729 | 480.800853 | 531.356583 | 480.800853 |
| Delayed nu_e | 107.132013 | 1037.307245 | 1144.439257 | 1037.307245 |
| Delayed anti-nu_mu | 170.958333 | 1663.631977 | 1834.590310 | 1663.631977 |
| Total | 328.646075 | 3181.740075 | 3510.386150 | 3181.740075 |

Selected grid: {'n_er': 128, 'n_enu': 192, 'n_pe_bin': 96, 'pe_step': 0.75}. Convergence passed: True.

The initial (32,48,24) grid is retained as a demonstration reference. The final two grids are compared in convergence_report.json. The declared tolerances are 1% for physical source/target/bin contributions >=1 event, 0.02 event below that threshold, and 0.2% for each inclusive scenario total. This is a numerical grid check, not an experimental precision claim.

The canonical get_slow_count_function('CsI2021') produces all PE predictions. Scoped exact memoization is checked against uncached public Slow results. Intermediate true recoils are independently folded back into PE and compared to physical target counts.

Raw target arrays describe a full detector mass made of one isotope before time acceptance. Physical target contributions multiply 133/260 or 127/260 and the source acceptance. Cs/I nucleus numbers are equal. POT already enters the SNS fluence, and detector mass enters once. True recoil arrays are saved both before and after the component time acceptance. The supplement shows the former.

The dimension-six non-diagonal Wilson coefficient and its Hermitian partner are 1e-5 GeV^-2; sin^2(theta_W)=0.23873 matches Sec. 3.2. The detector default 0.2387 is explicitly overridden. The mub source follows the existing shared-kernel antineutrino convention; this run does not independently audit general EFT antineutrino dynamics. There is no likelihood or data fit.

Reproduce from Gitup01 using the project Python environment:

```powershell
python -X utf8 -B "论文图NoteBook/generate_csi2021_detector_figures.py"
```

Reruns reuse only grid caches with matching physics/configuration/source fingerprints. Full results for every grid are retained under grids/.
