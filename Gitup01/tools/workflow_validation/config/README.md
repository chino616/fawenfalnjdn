# Workflow validator configuration

Status: MACHINE_CONSUMED
Scope: Existing workflow structure validator inputs relocated from documentation storage.

PROTECTED_FILES.json is the SHA256 baseline for protected files. HISTORICAL_PATH_EXCEPTIONS.json records allowed historical locators; entries for removed documentation are removed with it.
The consumer remains [validate_skill_pack.py](../../../workflows/cevns-pyeft/qa/validate_skill_pack.py); [tests](../../../tests/workflows/test_workflow_structure.py) verify actual reads from this directory. No workflow architecture or routing behavior changed.
