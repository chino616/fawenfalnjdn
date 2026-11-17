"""CEvNS-pyEFT plotting style adapter, v4.0. Python + Matplotlib only.

No data transformation or experiment binding; caller owns an immutable
mapping from physical series identity to index.
"""
from __future__ import annotations
import json
from pathlib import Path

class PaperTheme:
    def __init__(self, path="PAPER_THEME.json"):
        self.cfg = json.loads(Path(path).read_text(encoding="utf-8"))
        self.palette = self.cfg["series_palette"]
        self.n = len(self.palette)
        self.styles = self.cfg["series_scaling"]["linestyle_cycle"]
        self.markers = self.cfg["series_scaling"]["marker_cycle"]
        self.hatches = self.cfg["series_scaling"]["hatch_cycle"]

    def _entry(self, index):
        if not isinstance(index,int) or index < 0:
            raise ValueError("series index must be a non-negative int")
        return self.palette[index % self.n], index // self.n

    def line_style(self, index, label=None):
        entry, cycle = self._entry(index)
        ls = entry["linestyle"] if cycle == 0 else self.styles[(self.styles.index(entry["linestyle"])+cycle) % len(self.styles)]
        marker = entry["marker"] if cycle == 0 else self.markers[(index+cycle) % len(self.markers)]
        result = {"color": entry["color"], "linestyle":ls,
                  "marker":marker,"linewidth":self.cfg["lines"]["secondary_pt"],
                  "markersize":self.cfg["markers"]["theory_pt"]}
        if label is not None:
            result["label"]=label
        return result

    def bar_style(self, index, label=None, *, use_hatch=False):
        entry, cycle = self._entry(index)
        result = {"color":entry["bar_fill"],
                  "edgecolor":self.cfg["bar_style"]["edge_color"],
                  "linewidth":self.cfg["bar_style"]["edge_pt"]}
        if use_hatch or cycle > 0:
            result["hatch"]=self.hatches[(index + cycle) % len(self.hatches)]
            if result["hatch"]:
                result["edgecolor"] = entry["color"]
                result["linewidth"] = .55
        if label is not None:
            result["label"]=label
        return result
