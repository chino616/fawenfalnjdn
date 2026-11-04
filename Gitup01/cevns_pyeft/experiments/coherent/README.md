# COHERENT runtime adapters

CsI2021, CsI2017 and Ar2020 load registered YAML/NPZ packages through the common
loader. Their `*_definition.py` files are identity adapters. Legacy Slow/Fast APIs
retain return containers and frozen arithmetic through
[package_compatibility](../package_compatibility.py); experiment values are not
maintained here. The v2 profiles reuse common theory, recoil integration and
detector contracts. See the [migration report](../../../docs/PROJECT_WIDE_PACKAGE_MIGRATION_REPORT.md)
for separate runtime, regression, installation and scientific states.

`execution.py`, `sns.py` and `statistics_binding.py` retain historical compatibility
helpers. Default package execution does not recover parameters from those helpers.
The preserved `csi2021_package.py` and its contract belong to a separate phase
audit; this migration does not modify them or depend on their implementation.
