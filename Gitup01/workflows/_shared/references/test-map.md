# Validation authority map

[Existing tests](../../../tests/) own runtime/physics regressions; do not alter their reference
arrays or tolerances for workflow QA. [Workflow tests](../../../tests/workflows/) exercise
catalog/discovery/reference/route graph invariants with mutation cases.
[QA guidance](../../cevns-pyeft/qa/README.md) separates static results from natural-language
agent evaluations and human acceptance. Skill reference auditing checks AST anchors and paths,
not numerical convergence or scientific provenance.
