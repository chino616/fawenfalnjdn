"""Explicit multibin entry: 2411.11749v1-style observable spectra.

Delegates only to the existing nuclear-Response runner. Its old inputs, model,
eight Ne bins / three cS2 bins and output convention remain the multibin route.
"""
from pathlib import Path
import argparse
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.run_solar_b8_nuclear_benchmark import main as nuclear_main


def main():
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output',type=Path)
    options,_=parser.parse_known_args()
    if options.output is not None:
        output=options.output.resolve()
        root=Path(__file__).resolve().parents[1]/'outputs/solar_b8_sm'
        if not output.is_relative_to(root):
            raise SystemExit('multibin output must be under outputs/solar_b8_sm/, separate from singlebin')
    return nuclear_main()

if __name__ == '__main__':
    main()
