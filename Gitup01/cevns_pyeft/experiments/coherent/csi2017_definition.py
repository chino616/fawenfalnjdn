"""CsI2017 identity adapter; canonical package owns every experimental value."""
from cevns_pyeft.foundation.paths import resource_root
from cevns_pyeft.experiments.package_loader import definition_from_package
PACKAGE_RELATIVE="data/experiments/COHERENT_CsI/CsI2017"
DEFINITION=definition_from_package(resource_root()/PACKAGE_RELATIVE,resource_prefix=PACKAGE_RELATIVE)
