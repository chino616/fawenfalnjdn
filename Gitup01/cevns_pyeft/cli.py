"""Small command-line entry for the split minimal package."""

from __future__ import annotations

from cevns_pyeft import __version__


def main(argv=None) -> int:
    import sys
    args=list(sys.argv[1:] if argv is None else argv)
    if args and args[0]=='datasets':
        from cevns_pyeft.experiments.management import cli
        return cli(args[1:])
    if args and args not in (['--version'],['-V']):
        print('Usage: cevns-pyeft [--version | datasets --help]')
        return 2
    print(f"CEvNS-pyEFT split minimal package {__version__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

