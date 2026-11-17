"""Repeat one CONUS+ method in a fresh repository-local output directory."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from conusplus_paths import Layout, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=("sm", "nsi"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--stage", choices=("all", "predictions", "validate", "report"), default="all")
    args = parser.parse_args()
    target = args.output_dir.resolve()
    if not target.is_relative_to(ROOT / "outputs"):
        parser.error("--output-dir must be inside this Gitup01/outputs")
    if target.exists():
        parser.error("Choose a new output directory; latest results are preserved")
    layout = Layout(args.method)
    layout.verify_inputs()
    target.mkdir(parents=True)
    env = os.environ.copy()
    env.update(CEVNS_CONUS_OUTPUT=str(target), CEVNS_CONUS_REVIEW=str(target / "evidence"),
               CEVNS_CONUS_DOCUMENT=str(target / "report"),
               CEVNS_CONUS_RUN_DATA=str(target / "prepared_data"), PYTHONDONTWRITEBYTECODE="1")
    for folder in ("evidence", "report"):
        (target / folder).mkdir()
    shutil.copytree(layout.canonical_data, target / "prepared_data")
    shutil.copytree(layout.canonical_review, target / "evidence", dirs_exist_ok=True)
    for name in ("ORIGINAL_OUTPUT_PROVENANCE.json",):
        source = layout.canonical_review / name
        if source.is_file():
            shutil.copy2(source, target / "evidence" / name)
    if args.stage in ("validate", "report"):
        # Verification/plot-only runs receive their own copies of numerical data.
        for source in layout.canonical_output.iterdir():
            if source.is_file():
                if args.method == "nsi" and args.stage == "validate" and source.name in (
                        "nsi_operator_kernel_161_641.npz", "compile_summary.json"):
                    continue
                shutil.copy2(source, target / source.name)
    steps = {"sm": ("calculate_sm.py", "validate_results.py", "build_reports.py"),
             "nsi": ("prepare_predictions.py", "benchmark_nsi.py", "publish_nsi.py")}[args.method]
    selected = steps if args.stage == "all" else (steps[("predictions", "validate", "report").index(args.stage)],)
    if args.method == "nsi" and args.stage == "validate":
        selected = steps[:2]  # Compile a current-identity cache; keep the copied Slow references.
    (target / "RUN_CONTEXT.json").write_text(json.dumps({
        "date": datetime.now(timezone(timedelta(hours=8))).date().isoformat(), "timezone": "Asia/Shanghai",
        "method": args.method, "stage": args.stage, "source": "Gitup01 repository-local latest inputs",
        "original_reference_run": layout.tag, "human_gate": "NOT_REVIEWED",
        "command": sys.argv, "python": sys.executable,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for script in selected:
        subprocess.run([sys.executable, "-B", str(layout.code / script)], cwd=ROOT, env=env, check=True)


if __name__ == "__main__":
    main()
