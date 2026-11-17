"""Explicit optional SNuDD source entry; all original runners stay unchanged."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from extensions.solar_rho_snudd.run_with_rho import main

if __name__ == '__main__':
    main()
