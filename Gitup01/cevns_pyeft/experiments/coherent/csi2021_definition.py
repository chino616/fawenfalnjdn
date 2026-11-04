"""Compatibility identity; all experimental values come from the input package."""
from cevns_pyeft.foundation.paths import resource_root
from cevns_pyeft.experiments.package_loader import definition_from_package, PackageSettings

PACKAGE_RELATIVE = "data/experiments/COHERENT_CsI/CsI2021"
CsI2021Settings = PackageSettings
DEFINITION = definition_from_package(resource_root()/PACKAGE_RELATIVE, resource_prefix=PACKAGE_RELATIVE)
