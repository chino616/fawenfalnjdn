"""Source-only, piecewise constant time profiles.

Masses are weights per source bin, not probability densities or absolute
fluence. No detector efficiency, target count, exposure or PE binning lives
in this module. All public time coordinates use microseconds.
"""
from dataclasses import dataclass
import numpy as np

def _edges(value, name="time edges"):
    x=np.asarray(value,dtype=float)
    if x.ndim!=1 or x.size<2 or not np.isfinite(x).all() or np.any(np.diff(x)<=0):
        raise ValueError(f"{name} must be a finite strictly increasing 1D array")
    return x

@dataclass(frozen=True)
class BinnedTimeProfile:
    component: str
    edges_us: np.ndarray
    bin_masses: np.ndarray

    def __post_init__(self):
        edges=_edges(self.edges_us).copy()
        masses=np.asarray(self.bin_masses,dtype=float).copy()
        if masses.shape!=(edges.size-1,) or not np.isfinite(masses).all() or np.any(masses<0):
            raise ValueError("Time bin masses must match edges and be finite/nonnegative")
        total=float(masses.sum(dtype=float))
        if not np.isfinite(total) or total<=0:
            raise ValueError("Time profile must have a positive finite total mass")
        if not isinstance(self.component,str) or not self.component:
            raise ValueError("Time profile requires a component label")
        edges.flags.writeable=False;masses.flags.writeable=False
        object.__setattr__(self,"edges_us",edges)
        object.__setattr__(self,"bin_masses",masses)

    @property
    def total_mass(self):
        return float(self.bin_masses.sum(dtype=float))

    @property
    def support_us(self):
        return float(self.edges_us[0]),float(self.edges_us[-1])

    def density_per_us(self,t_us,*,shift_us=0.):
        """Full-support normalized h(t-shift); zero outside shifted support."""
        t=np.asarray(t_us,dtype=float)
        if not np.isfinite(t).all() or not np.isfinite(shift_us):
            raise ValueError("Time coordinates and shift must be finite")
        shifted=t-float(shift_us)
        index=np.searchsorted(self.edges_us,shifted,side="right")-1
        valid=(index>=0)&(index<len(self.bin_masses))
        index=np.clip(index,0,len(self.bin_masses)-1)
        value=self.bin_masses[index]/np.diff(self.edges_us)[index]/self.total_mass
        result=np.where(valid,value,0.)
        return float(result) if t.ndim==0 else result

    def probabilities(self,interval_edges_us,*,shift_us=0.):
        """Full-support probability of arbitrary intervals, before selection."""
        observed=_edges(interval_edges_us,"integration interval edges")
        if not np.isfinite(shift_us):
            raise ValueError("Time shift must be finite")
        shifted=self.edges_us+float(shift_us)
        density=self.bin_masses/np.diff(self.edges_us)/self.total_mass
        result=[]
        for a,b in zip(observed[:-1],observed[1:]):
            overlap=np.maximum(np.minimum(shifted[1:],b)-np.maximum(shifted[:-1],a),0.)
            result.append(np.dot(density,overlap))
        return np.asarray(result,dtype=float)

    def reference_fraction(self,window_us):
        """Nominal pre-efficiency fraction in a declared reference window.

        The denominator is fixed at zero shift. This source-only quantity
        does not include detector time efficiency.
        """
        window=_edges(window_us,"reference window")
        if window.size!=2:
            raise ValueError("Reference window must contain exactly two edges")
        fraction=float(self.probabilities(window)[0])
        if fraction<=0:
            raise ValueError("Reference window has zero source mass")
        return fraction

    def window_normalized_shape_integrals(self,interval_edges_us,*,reference_window_us,shift_us=0.):
        """Integral of h(t-shift)/q_ref with its NOMINAL denominator fixed.

        This is a window-normalized shape, not a globally normalized PDF.
        Its integral outside the reference window can exceed one. To use it
        with absolute fluence, the counting adapter must match fluence scope.
        """
        return self.probabilities(interval_edges_us,shift_us=shift_us)/self.reference_fraction(reference_window_us)

