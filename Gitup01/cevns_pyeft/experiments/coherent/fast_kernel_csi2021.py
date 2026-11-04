"""Historical Fast dictionary view of the package-driven interface compiler."""
from .csi2021_definition import DEFINITION


def build_fast_kernel_csi2021(responses_json=None, basis=None, *, sin2thetaW=None,
        c10_mass_mode=None, n_er=None, n_enu=None, n_pe_sub=None, pe_step=None):
    from pathlib import Path
    from cevns_pyeft.experiments.loader import load_experiment
    from cevns_pyeft.experiments.package_compatibility import legacy_builder_from_package
    from cevns_pyeft.kernels.basis import li2026_left_basis_current
    if responses_json is not None and Path(responses_json).name != "responses_all.json":
        raise ValueError("external response overrides require explicit interaction components")
    if c10_mass_mode is not None and c10_mass_mode != DEFINITION.physical.c10_mass_mode:
        raise ValueError("theory mode differs from package binding")
    base = DEFINITION.numerical_profiles["slow"]
    ns = {"n_er": base["n_er"] if n_er is None else n_er,
          "n_enu": base["n_enu"] if n_enu is None else n_enu,
          "n_pe_bin": base["n_pe_bin"] if n_pe_sub is None else n_pe_sub,
          "pe_step": base["pe_step"] if pe_step is None else pe_step}
    experiment=load_experiment(DEFINITION.dataset_id)
    ns['recoil_min_keV']=experiment.executor.recoil_min_keV
    return legacy_builder_from_package(experiment,list(basis or li2026_left_basis_current()),ns)


__all__ = ["build_fast_kernel_csi2021"]
