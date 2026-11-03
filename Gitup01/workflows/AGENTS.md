# Common workflow governance

This directory contains repository-local Human–AI workflow documentation and QA. It is not
imported or packaged by cevns_pyeft. Use [catalog.yaml](catalog.yaml) for stable Skill identity,
then [project governance](cevns-pyeft/AGENTS.md) and the Master Skill. Task classification is
owned only by the project route table; a catalog kind is not a routing condition.

Read the applicable [shared policies](./_shared/README.md): scientific integrity,
evidence/approval, write authorization, archive isolation, automation, interaction, dataset
layout and progress continuity. Active experiment migration uses the interaction policy;
ordinary engineering/documentation work answers the actual request without artificial physics gates.

Workflow definitions orchestrate stable Skill IDs. Skill packages preserve focused responsibility.
Schemas, templates, references and QA fixtures are distinct. Never discover backup/**, generated
output or historical run records as active Skills or user-selected physics material. Historical
provenance exceptions are explicitly recorded in tools/workflow_validation/config/HISTORICAL_PATH_EXCEPTIONS.json.

This workflow-only restructure is an authorized engineering task. Keep physical code, data,
experiment definitions, reference arrays and numerical tolerances outside its write scope.
