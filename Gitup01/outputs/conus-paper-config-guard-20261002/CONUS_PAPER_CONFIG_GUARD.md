# CONUS+ Paper Comparison Configuration Guard

Status: PASS

Configuration mismatch guarded: actual C2+C3+C5 counts and paper effective-detector Fig. 1 bins are separate comparison objects. No duplicate exposure factor is detected.

Key checks:
- Fig. 1 effective total: 152.09295
- Hybrid effective total: 150.34082
- Hybrid actual C2+C3+C5 total: 323.65254
- Common 119-day detector totals round to paper 90/143/113: True
- 180-190 eVee unit-exposure reconstruction passes: True

Interpretation:
- The candidate slow integrator multiplies each detector by its own kg day exposure once.
- The large visual mismatch appears when actual C2+C3+C5 counts are plotted against the paper's effective-detector Fig. 1 curve.
- The unresolved issue is the same-effective-configuration shape residual, not a duplicate exposure factor.

Guardrails:
- Do not compare hybrid_actual_combined_bins directly to paper_fig1_effective bins as a same-configuration residual.
- Use hybrid_effective_bins for the 1 kg, 119 day, 160 eVee Fig. 1 comparison.
- Use hybrid_actual_combined_bins for the C2/C3/C5 detector-contract prediction.
- Do not rescale the actual prediction to 346 as a fix; investigate the same-configuration shape residual.
