"""Historical CsI2017 dictionary interface backed by its formal package."""
import numpy as np
from .csi2017_definition import DEFINITION
CSI2017_PE_PER_KEV=DEFINITION.physical.pe_per_keV
CSI2017_BINS_25=np.asarray(DEFINITION.observation.edges)
CSI2017_WIDTHS_25=np.diff(CSI2017_BINS_25)
CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH="data/experiments/COHERENT_CsI/CsI2017/detector/COHERENT_eff.txt"


def slow_counts_csi2017(responses_json=None,wc_triplets=None,*,include_sm=True,sin2thetaW=None,
        c10_mass_mode=None,n_er=21,n_enu=None,n_pe_bin=8,pe_step=3.,
        efficiency_data_path=None,definition=None,model=None):
    from cevns_pyeft.experiments.package_compatibility import legacy_profile_counts
    ns={} if n_enu is None else {"n_enu":n_enu}
    return legacy_profile_counts(definition or DEFINITION,responses_json,wc_triplets,include_sm=include_sm,
        sin2thetaW=sin2thetaW,c10_mass_mode=c10_mass_mode,numerics=ns,model=model,efficiency_data_path=efficiency_data_path)


__all__=["CSI2017_PE_PER_KEV","CSI2017_BINS_25","CSI2017_WIDTHS_25","CSI2017_DEFAULT_EFFICIENCY_RELATIVE_PATH","slow_counts_csi2017"]
