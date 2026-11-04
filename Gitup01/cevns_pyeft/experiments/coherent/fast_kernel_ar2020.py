"""Historical Ar2020 Fast interface, using only the formal input package."""
from .ar2020_definition import DEFINITION


def build_fast_kernel_ar2020(responses_json=None,basis=None,*,sin2thetaW=None,c10_mass_mode=None,
        n_er=None,n_enu=None,n_obs_sub=None,efficiency_data_path=None,definition=None,physical=None):
    from cevns_pyeft.experiments.package_compatibility import legacy_profile_fast
    ns={k:v for k,v in dict(n_er=n_er,n_enu=n_enu,n_obs_sub=n_obs_sub).items() if v is not None}
    return legacy_profile_fast(definition or DEFINITION,responses_json,basis=basis,numerics=ns,c10_mass_mode=c10_mass_mode)


__all__=["build_fast_kernel_ar2020"]
