"""Read-only validation of a canonical experiment.input.yaml + NPZ + Physics MD."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cevns_pyeft.experiments.input_package import validate_package, schema_document


def main(argv=None):
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package',nargs='?',type=Path)
    parser.add_argument('--check-schema',action='store_true')
    args=parser.parse_args(argv)
    if args.check_schema:
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema_document())
        report={'status':'PASS','scope':'JSON Schema meta-schema only'}
    elif args.package is None:
        parser.error('give an explicit package directory, or --check-schema')
    else:
        report=validate_package(args.package)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report['status']!='PASS'


if __name__=='__main__':
    raise SystemExit(main())
