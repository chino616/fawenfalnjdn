"""Compile an explicit acquired draft/IR and declared NPZ arrays; never read papers."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cevns_pyeft.experiments.input_package import strict_json, read_arrays
from cevns_pyeft.experiments.package_compiler import write_package

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft')
    parser.add_argument('--arrays')
    parser.add_argument('--output',required=True)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--md-only',action='store_true',help='validate existing output YAML/NPZ read-only and render only MD')
    parser.add_argument('--overwrite',action='store_true')
    parser.add_argument('--report')
    args=parser.parse_args(argv)
    if args.md_only:
        if args.draft or args.arrays:
            parser.error('--md-only reads existing --output; do not pass --draft/--arrays')
        draft=arrays=None
    else:
        if not args.draft or not args.arrays:
            parser.error('--draft and --arrays are required unless --md-only')
        draft=strict_json(Path(args.draft).read_text('utf8'))
        arrays=read_arrays(Path(args.arrays).read_bytes(),draft['document']['resources']['arrays'])
    report=write_package(draft,arrays,args.output,check=args.check,overwrite=args.overwrite,md_only=args.md_only)
    if args.report:Path(args.report).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2));return 0 if report['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
