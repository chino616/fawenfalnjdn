# Experimental Experiment-Integration Workflow

This workflow is experimental support material for adding CEvNS experiment
datasets to CEvNS-pyEFT. It is scoped to experiment integration only. Future
workflows for nuclear-response work, statistics, EFT mapping, or other domains
should live beside this directory under `workflows/`.

Use this workflow for tasks that explicitly ask to add a new experiment, migrate
an experiment dataset, implement experiment event counts, implement Fast counts,
or add statistics for a new experiment.

Workflow entry points:

1. Read `EXPERIMENT_WORKFLOW.md`.
2. Read the user-provided experiment physics document and its data attachments.
3. Start with `skills/cevns-experiment-intake/SKILL.md`.
4. Continue through the workflow stages in order.
5. In each stage, read only the matching stage template and the relevant local
   CsI reference module.
6. Do not copy the CsI source, target, detector, or statistics implementation
   wholesale into a new experiment.
7. Do not ask the user again for data already present in the physics document
   or attachments.
8. Before modifying existing project files, save a backup under `backup/` and
   record it in `backup/BACKUP_MANIFEST.md`.
9. Implement and validate Slow counts before Fast counts.
10. Statistics inputs must be explicitly classified as raw counts, ON/OFF,
    signal+background, or background-subtracted excess.
11. Stop when any gate fails; do not hide differences by changing references,
    applying global rescaling, or loosening tolerances.
