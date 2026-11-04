"""Ar2020 identity adapter; values live only in its canonical input package."""
from cevns_pyeft.foundation.paths import resource_root
from cevns_pyeft.experiments.package_loader import definition_from_package
PACKAGE_RELATIVE="data/experiments/COHERENT_Ar/Ar2020"
DEFINITION=definition_from_package(resource_root()/PACKAGE_RELATIVE,resource_prefix=PACKAGE_RELATIVE)
