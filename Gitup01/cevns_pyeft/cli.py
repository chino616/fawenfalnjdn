"""Small command-line entry for the split minimal package."""

from __future__ import annotations

from cevns_pyeft import __version__


def main() -> int:
    print(f"CEvNS-pyEFT split minimal package {__version__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

