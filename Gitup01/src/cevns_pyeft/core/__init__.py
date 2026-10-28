"""Compatibility core namespace for the split minimal package."""

__all__ = ["engine"]


def __getattr__(name):
    # Keep the compatibility namespace without making the neutral model and
    # prediction imports eagerly load every legacy experiment and Fast builder.
    if name != "engine":
        raise AttributeError(name)
    from importlib import import_module
    value = import_module(".engine", __name__)
    globals()[name] = value
    return value

