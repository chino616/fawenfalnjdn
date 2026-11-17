"""Pin original code or compare native/checked coefficient-energy runs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[3]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir",type=Path,required=True)
    parser.add_argument("--stage",choices=["prepare","equivalence"],required=True)
    parser.add_argument("--output-name",default=None)
    args=parser.parse_args()
    run=args.run_dir.resolve();run.mkdir(parents=True,exist_ok=True)
    if args.stage=="prepare":
        output=run/(args.output_name or "SOURCE_STATE.json")
        files=list((ROOT/"cevns_pyeft").rglob("*.py"))+list((ROOT/"examples/COHERENT_CsI/time_resolved_sm").glob("*.py"))
        result={"date":"2026-11-08","scope":"Immutable original package Python and prior SM helpers before NSI calculation",
            "files":{file.relative_to(ROOT).as_posix():sha(file) for file in sorted(files)}}
    else:
        output=run/(args.output_name or "COEFFICIENT_ENERGY_EQUIVALENCE.json")
        records=[]
        for native,checked in [("pilot","pilot_checked"),("grid_256_480","grid_256_480_checked")]:
            a,b=run/native/"prediction.npz",run/checked/"prediction.npz"
            with np.load(a,allow_pickle=False) as left,np.load(b,allow_pickle=False) as right:
                np.testing.assert_array_equal(left["point_ids"],right["point_ids"])
                np.testing.assert_allclose(left["target_component_counts"],right["target_component_counts"],rtol=5e-11,atol=2e-9)
                error=float(np.max(np.abs(left["target_component_counts"]-right["target_component_counts"])))
            records.append({"native_grid":native,"checked_grid":checked,"native_sha256":sha(a),
                "checked_sha256":sha(b),"max_target_component_bin_difference":error,"status":"PASS"})
        result={"date":"2026-11-08","status":"PASS","scope":"All24 declared points; native and checked coefficient-energy evaluation at identical grids",
            "records":records,"script_sha256":sha(__file__)}
    if output.exists(): raise FileExistsError("Preserve previous output; choose a new name or run directory")
    output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"stage":args.stage,"saved":str(output),"status":result.get("status","PINNED")}))


if __name__=="__main__":main()
