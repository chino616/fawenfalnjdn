"""Historical CsI2017 Fast dictionary interface backed by its formal package."""
from .csi2017_definition import DEFINITION


def build_fast_kernel_csi2017(responses_json=None,*,basis=None,efficiency_data_path=None,
        pe_bins=None,pe_per_keV=None,sin2thetaW=None,c10_mass_mode=None,n_er=None,n_enu=None,definition=None):
    from dataclasses import replace
    from cevns_pyeft.experiments.package_compatibility import legacy_profile_fast
    config=definition or DEFINITION
    if pe_bins is not None:config=replace(config,observation=replace(config.observation,edges=tuple(pe_bins)))
    if pe_per_keV is not None:config=replace(config,physical=replace(config.physical,pe_per_keV=pe_per_keV))
    ns={k:v for k,v in dict(n_er=n_er,n_enu=n_enu).items() if v is not None}
    return legacy_profile_fast(config,responses_json,basis=basis,numerics=ns,c10_mass_mode=c10_mass_mode)


__all__=["build_fast_kernel_csi2017"]
