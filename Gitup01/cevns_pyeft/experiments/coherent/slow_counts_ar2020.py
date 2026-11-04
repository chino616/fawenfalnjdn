"""Historical Ar2020 dictionary interface backed by the formal package."""
import numpy as np
from .ar2020_definition import DEFINITION
from cevns_pyeft.rates.legacy_observables import observed_gaussian_fold as ar_fold_matrix
AR_BINS_12=np.asarray(DEFINITION.observation.edges)
AR_WIDTHS_12=np.diff(AR_BINS_12)
AR_DEFAULT_EFFICIENCY_RELATIVE_PATH="data/experiments/COHERENT_Ar/Ar2020/detector/CENNS10AnlAEfficiency.txt"
AR_D=np.asarray(DEFINITION.statistics.observed)
AR_B=np.asarray(DEFINITION.statistics.background)
AR_DMIN=np.asarray(DEFINITION.statistics.lower)
AR_DMAX=np.asarray(DEFINITION.statistics.upper)


def slow_counts_ar2020(responses_json=None,wc_triplets=None,*,include_sm=True,sin2thetaW=None,
        c10_mass_mode=None,n_er=None,n_enu=None,n_pe_bin=None,pe_step=3.,
        efficiency_data_path=None,definition=None,model=None):
    from cevns_pyeft.experiments.package_compatibility import legacy_profile_counts
    ns={k:v for k,v in dict(n_er=n_er,n_enu=n_enu,n_pe_bin=n_pe_bin).items() if v is not None}
    return legacy_profile_counts(definition or DEFINITION,responses_json,wc_triplets,include_sm=include_sm,
        sin2thetaW=sin2thetaW,c10_mass_mode=c10_mass_mode,numerics=ns,model=model,efficiency_data_path=efficiency_data_path)


__all__=["AR_BINS_12","AR_WIDTHS_12","AR_DEFAULT_EFFICIENCY_RELATIVE_PATH","AR_D","AR_B","AR_DMIN","AR_DMAX","slow_counts_ar2020"]
