"""Shared SM assembly used by the separate vector-NSI analysis."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sm_response"))
from calculate_sm import (DATA, EDGES, ISOTOPES, POINT, build_model, json_value, reactor_state, settings, sha256, write_json)
