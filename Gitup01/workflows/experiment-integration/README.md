# Experimental Experiment-Integration Workflow

This directory contains the current experimental workflow for adding CEvNS
experiment datasets to CEvNS-pyEFT.

Scope:

- It is workflow guidance for Codex-assisted experiment integration.
- It is not runtime package code.
- It should not be used for ordinary package maintenance unless the user asks
  to add or migrate an experiment dataset.
- Future workflows for nuclear response, statistics, EFT mapping, or other
  domains should be added as sibling directories under `workflows/`.

Recommended use:

1. Put the experiment physics document under
   `physics_docs/experiments/<dataset_id>/`.
2. Load the project root `AGENTS.md`.
3. Load this workflow's `AGENTS.md`.
4. Follow `EXPERIMENT_WORKFLOW.md`.
5. Use the stage-specific files under `skills/`.
6. Fill the corresponding files under `templates/`.
7. Complete and validate each stage before moving to the next one.

Core rules:

- CsI is a local API and validation reference, not the physics input for a new
  experiment.
- Do not copy CsI source, target, detector, or statistics modules wholesale.
- Run target inventory as a text-only phase before source implementation.
- Scalars from user documents go into `experiment.yaml`; tables go into CSV or
  NPZ files; required formulas go into Python modules.
- Create Python modules based on implementation differences, not mechanically
  from document section titles.
- Implement Slow counts before Fast counts.
- Do not ask the user again for data already present in their documents.
