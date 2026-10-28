"""Neutral material declarations remain lightweight during catalog discovery."""
from importlib import import_module
__all__=['csi_target_inventory','inventory_from_mass_fractions','inventory_from_number_fractions']
def __getattr__(name):
    if name not in __all__:raise AttributeError(name)
    return getattr(import_module('.materials',__name__),name)
