"""Generate manuscript macros, tables and a compilable CONUS+ preview."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "conus-plus-completion-20261012"
PAPER = OUT / "paper"


def main() -> None:
    PAPER.mkdir(parents=True, exist_ok=True)
    summary = json.loads((OUT / "statistics" / "fit_summary.json").read_text(encoding="utf-8"))
    eff = summary["effective_119"]
    three = summary["three_detector_119_each"]
    intervals = eff["sin2thetaW_1sigma"][0]
    macros = f"""% Generated from statistics/fit_summary.json; do not edit by hand.
\\newcommand{{\\ConusCtwoEvents}}{{{three['detector_totals'][0]:.6f}}}
\\newcommand{{\\ConusCthreeEvents}}{{{three['detector_totals'][1]:.6f}}}
\\newcommand{{\\ConusCfiveEvents}}{{{three['detector_totals'][2]:.6f}}}
\\newcommand{{\\ConusThreeDetectorEvents}}{{{three['combined_events']:.6f}}}
\\newcommand{{\\ConusEffectiveSMEvents}}{{{eff['sm_events']:.6f}}}
\\newcommand{{\\ConusSinSqBest}}{{{eff['sin2thetaW_best']:.6f}}}
\\newcommand{{\\ConusSinSqLeft}}{{{intervals['left']:.6f}}}
\\newcommand{{\\ConusSinSqRight}}{{{intervals['right']:.6f}}}
\\newcommand{{\\ConusMagneticUpper}}{{{eff['magnetic_moment_cevns_only_90cl_muB'] / 1e-10:.6f}\\times 10^{{-10}}\\,\\mu_B}}
\\newcommand{{\\ConusCoordinateCount}}{{114}}
"""
    (PAPER / "conus_results_macros.tex").write_text(macros, encoding="utf-8")
    tables = f"""% Generated from statistics/fit_summary.json.
\\begin{{table}}[ht]
\\centering
\\caption{{CONUS+ forward prediction with Ge73 and 119 kg day for each detector.}}
\\label{{tab:conus-forward}}
\\begin{{tabular}}{{lrr}}
\\toprule
Detector & Exposure [kg day] & SM events \\\\
\\midrule
C2 & 119 & \\ConusCtwoEvents \\\\
C3 & 119 & \\ConusCthreeEvents \\\\
C5 & 119 & \\ConusCfiveEvents \\\\
Total & 357 & \\ConusThreeDetectorEvents \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}

\\begin{{table}}[ht]
\\centering
\\caption{{Effective-119 approximate paper benchmark.}}
\\label{{tab:conus-benchmark}}
\\begin{{tabular}}{{lr}}
\\toprule
Quantity & Result \\\\
\\midrule
SM events & \\ConusEffectiveSMEvents \\\\
Best $\\sin^2\\theta_W$ & \\ConusSinSqBest \\\\
1$\\sigma$ interval & [\\ConusSinSqLeft, \\ConusSinSqRight] \\\\
CEvNS-only $\\mu_\\mathrm{{eff}}$ (90\\% CL) & \\ConusMagneticUpper \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    (PAPER / "conus_results_tables.tex").write_text(tables, encoding="utf-8")
    validation_table = r"""% Generated from the formal CONUS+ phase records and validation JSON.
\begin{table*}[ht]
\centering
\caption{CONUS+ Skill-guided integration checks.  PASS-WITH-LIMITATION rows
retain an explicit scope boundary; they are not claims of an official
likelihood or complete EFT Fast implementation.}
\label{tab:conus-validation}
\begin{tabular}{llll}
\toprule
Stage & Check & Metric / evidence & Status \\
\midrule
P03 & Source spectrum & $0$--$10$ MeV; Kopeikin--Mueller join; source CSV & PASS with source-extension limitation \\
P04 & Ge73 nuclear response & Li2026 Ge73 response database and cross-section API & PASS in declared scope \\
P06 & Detector response & Lindhard, Gaussian resolution, threshold and efficiency contract & PASS in declared scope \\
P07 & Direct integration & nominal/fine maximum relative bin change $1.62\times10^{-14}$ & PASS \\
P08 & Detector matrix & max $|N_{\rm fast}-N_{\rm direct}|=1.78\times10^{-14}$ & PASS; matrix only \\
P09 & Paper benchmark & 19 digitized bins, Eq.~(33) Gaussian pull & PASS with approximate-likelihood limitation \\
P10 & Delivery & machine-readable arrays, figures, macros, tables and manifest & PASS with documented blockers \\
\bottomrule
\end{tabular}
\end{table*}
"""
    (PAPER / "conus_validation_table.tex").write_text(validation_table, encoding="utf-8")
    validation_csv = """stage,check,metric_or_evidence,status\nP03,source spectrum,0-10 MeV Kopeikin-Mueller join,PASS_WITH_SOURCE_EXTENSION_LIMITATION\nP04,Ge73 nuclear response,Li2026 Ge73 response database and cross-section API,PASS_IN_DECLARED_SCOPE\nP06,detector response,Lindhard Gaussian threshold efficiency contract,PASS_IN_DECLARED_SCOPE\nP07,direct integration,nominal/fine max relative bin change 1.62e-14,PASS\nP08,detector matrix,max abs fast-direct difference 1.78e-14,PASS_MATRIX_ONLY\nP09,paper benchmark,19 digitized bins Eq.(33) Gaussian pull,PASS_APPROXIMATE\nP10,delivery,arrays figures macros tables manifest,PASS_WITH_DOCUMENTED_BLOCKERS\n"""
    (PAPER / "conus_validation_table.csv").write_text(validation_csv, encoding="utf-8")
    section = r"""\section{Skill-guided CONUS+ integration}
\label{sec:conus-skill}

The CONUS+ case study uses a staged integration record to keep the source,
target, detector response, direct prediction and statistical benchmark
independently auditable.  The formal dataset is the Ge73-only configuration
with C2, C3 and C5 each assigned 119 kg day.  The workflow record distinguishes
the shared Li2026 theory from the experiment adapter and retains the direct
arrays used to make every plot (Fig.~\ref{fig:conus-forward}).  It is a
development and integration process, rather than a runtime theory module.

We have not performed a controlled with-Skill versus without-Skill onboarding
experiment.  Consequently this case study reports traceable artifacts and
validation gates, but does not claim a Skill success rate, error-reduction
factor, correction count or time saving.

\begin{figure}[ht]
\centering
\includegraphics[width=0.98\linewidth]{../figures/fig_conus_skill_workflow.pdf}
\caption{CONUS+ integration workflow.  Green stages have machine-validated
direct outputs; the yellow stages retain a documented limitation.}
\label{fig:conus-workflow}
\end{figure}

\subsection{Forward model and exposure roles}
The source is the frozen Kopeikin--Mueller reactor spectrum, continued to
10~MeV as documented in the configuration.  The target response is Ge73 and
the detector model applies the detector-specific threshold, Gaussian
resolution and reconstructed-energy efficiency.  Direct integration gives
\ConusCtwoEvents, \ConusCthreeEvents and \ConusCfiveEvents events for C2, C3
and C5, respectively, or \ConusThreeDetectorEvents events in the three-detector
119-each configuration.  These numbers are a forward prediction; they are not
combined with the independent effective-119 statistical sample.

\begin{figure}[ht]
\centering
\includegraphics[width=0.99\linewidth]{../figures/fig_conus_forward_chain.pdf}
\caption{Frozen source spectrum, Ge73 recoil rate and reconstructed CONUS+
counts.  Each detector uses 119 kg day; the overlaid digitized points in the
right panel belong only to the effective-119 C3-like comparison.}
\label{fig:conus-forward}
\end{figure}

\subsection{Numerical and statistical validation}
The available Fast artifact is a detector-response matrix.  It reproduces the
stored direct bin counts at machine precision for the tested points, but it
does not evaluate the Li2026 amplitude or its Wilson-coefficient dependence.
The declared reactor-visible basis contains \ConusCoordinateCount real
coordinates (real and imaginary parts with the LNV diagonal constraints).  A
full coefficient-dependent quadratic kernel is therefore kept pending until
all direct mixed samples and held-out validation points have been run.

The paper comparison is an approximate Gaussian benchmark based on 19
digitized excess points and the single normalization pull used for Eq.~(33) of
the target paper.  It yields $\\sin^2\\theta_W=\\ConusSinSqBest$ with the
interval $[\\ConusSinSqLeft,\\ConusSinSqRight]$ and a CEvNS-only magnetic
moment upper limit of $\\ConusMagneticUpper$.  The benchmark is not the
official CONUS+ likelihood.

\begin{figure}[ht]
\centering
\includegraphics[width=0.99\linewidth]{../figures/fig_conus_reconstructed_counts_with_data.pdf}
\caption{Reconstructed effective-119 spectrum with the digitized
background-subtracted excess and asymmetric error bars from the paper Fig.~1.
The points are not replicated for the three-detector 357 kg day prediction.}
\label{fig:conus-reconstructed-data}
\end{figure}

\begin{figure}[ht]
\centering
\includegraphics[width=0.99\linewidth]{../figures/fig_conus_statistical_analysis.pdf}
\caption{Approximate statistical analysis: reconstructed spectrum and pulls,
profile $\sin^2\theta_W$, and the CEvNS-only magnetic-moment profile.}
\label{fig:conus-statistics}
\end{figure}

\begin{figure}[ht]
\centering
\includegraphics[width=0.99\linewidth]{../figures/fig_conus_fast_validation.pdf}
\caption{Detector-response matrix validation and measured cost comparison.
This is not a full EFT-kernel speedup measurement.}
\label{fig:conus-fast}
\end{figure}

\subsection{Physics scope}
The four vector-NSI panels are supplied as an approximate digitized benchmark
in Fig.~\ref{fig:conus-nsi}.  Electronic recoil scattering, the official
likelihood and the additional model-dependent paper figures remain outside
the present validated scope.  The low-energy tail difference and the 8--10
MeV source continuation are retained as documented limitations of the frozen
candidate model.

\begin{figure}[ht]
\centering
\includegraphics[width=0.90\linewidth]{../figures/fig_conus_nsi_four_panels.pdf}
\caption{Four-panel vector-NSI approximate benchmark from the formal CONUS+
statistics artifacts.}
\label{fig:conus-nsi}
\end{figure}
"""
    (PAPER / "section_conus_skill.tex").write_text(section, encoding="utf-8")
    bib = r"""@article{CONUSPlus2025,
  author = {CONUS+ Collaboration},
  title = {First observation of coherent elastic neutrino-nucleus scattering at a nuclear power plant},
  eprint = {2501.17843},
  archivePrefix = {arXiv},
  year = {2025},
  note = {version 2 used for the local benchmark}
}
"""
    (PAPER / "conus_references.bib").write_text(bib, encoding="utf-8")
    preview = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{amsmath}
\input{conus_results_macros.tex}
\title{CONUS+ completion preview}
\author{CEvNS-pyEFT local project}
\begin{document}
\maketitle
\input{section_conus_skill.tex}
\clearpage
\input{conus_results_tables.tex}
\input{conus_validation_table.tex}
\end{document}
"""
    (PAPER / "preview.tex").write_text(preview, encoding="utf-8")


if __name__ == "__main__":
    main()
