"""Official raw C/AC histograms and separately labelled neutron diagnostics."""
from dataclasses import dataclass
from pathlib import Path
import hashlib,json
import numpy as np
from ..kernels.builder import PE_EDGES,TIME_EDGES
from ..time_acceptance import TimeMassCDF


def histogram_events(events,time_edges=TIME_EDGES):
    events=np.asarray(events,float)
    if events.ndim!=2 or events.shape[1]!=2 or not np.isfinite(events).all():
        raise ValueError("Expected finite (PE,time_us) event rows")
    selected=(events[:,0]>=0)&(events[:,0]<60)&(events[:,1]>=time_edges[0])&(events[:,1]<time_edges[-1])
    return np.histogram2d(events[selected,0],events[selected,1],bins=(PE_EDGES,time_edges))[0].astype(int)


@dataclass
class TimeDataset:
    observed: np.ndarray
    control: np.ndarray
    ssb: np.ndarray
    neutron_pe: np.ndarray
    neutron_cdfs: tuple
    metadata: dict

    def backgrounds(self,shift_us=0.,normalization="raw_template_integrals"):
        b=np.array([pe[:,None]*cdf.integral(TIME_EDGES,shift_us)[None,:]
                    for pe,cdf in zip(self.neutron_pe,self.neutron_cdfs)])
        if normalization=="table_prior_sensitivity":
            nominal=np.array([p.sum()*c.integral(TIME_EDGES).sum() for p,c in zip(self.neutron_pe,self.neutron_cdfs)])
            b*=np.array([18.4,5.6])[:,None,None]/nominal[:,None,None]
        elif normalization=="full_support_probability":
            # Candidate convention audited separately from the published prior.
            b/=np.asarray(self.metadata["neutron_full_PE_table_sums"])[:,None,None]
        elif normalization!="raw_template_integrals":
            raise ValueError("Unknown background diagnostic configuration")
        return b[0],b[1],self.ssb


def load_time_dataset(data_dir=None):
    base=Path(data_dir) if data_dir is not None else Path(__file__).resolve().parents[1]/"data"
    manifest=json.loads((base/"statistics_inputs.json").read_text(encoding="utf-8"))
    raw=base/"raw"
    for name,expected in manifest["file_sha256"].items():
        if hashlib.sha256((raw/name).read_bytes()).hexdigest()!=expected:
            raise ValueError("Statistics input checksum changed: "+name)
    c=np.loadtxt(raw/"dataBeamOnC.txt");ac=np.loadtxt(raw/"dataBeamOnAC.txt")
    observed=histogram_events(c);control=histogram_events(ac)
    ac12=histogram_events(ac,np.array([0.,12.])).sum(axis=1)
    rate=.0494
    selected_integrals=np.exp(-rate*TIME_EDGES[:-1])*(-np.expm1(-rate*np.diff(TIME_EDGES)))/rate
    norm=-np.expm1(-rate*12)/rate
    ssb=ac12[:,None]*selected_integrals[None,:]/norm
    pe=[];cdfs=[];pe_sums=[]
    for name in ("brn","nin"):
        en=np.loadtxt(raw/(name+"PE.txt"));t=np.loadtxt(raw/(name+"Trec.txt"))
        if not np.allclose(np.diff(en[:,0]),1.) or not np.allclose(np.diff(t[:,0]),.01):
            raise ValueError("Unexpected neutron bin centers")
        pe.append(np.histogram(en[:,0],bins=PE_EDGES,weights=en[:,1])[0])
        pe_sums.append(float(en[:,1].sum()))
        cdfs.append(TimeMassCDF(t[:,1],np.r_[t[:,0]-.005,t[-1,0]+.005]))
    meta=dict(data_mode="raw_counts",axis_order=["PE","time"],counts_c=int(observed.sum()),
        counts_ac=int(control.sum()),control_events_0_12_us=int(ac12.sum()),ssb_total=float(ssb.sum()),
        c_ac_exposure_ratio=1.,file_hashes=manifest["file_sha256"],
        neutron_normalization_status="unresolved raw template vs published prior; diagnostic only",
        neutron_full_PE_table_sums=pe_sums,
        background_energy_efficiency="already applied; do not multiply again",
        ssb_efficiency="selected control template; no second signal efficiency")
    assert observed.sum()==1578 and control.sum()==1295 and ac12.sum()==2242
    return TimeDataset(observed,control,ssb,np.array(pe),tuple(cdfs),meta)

