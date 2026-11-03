# Workflow QA

The migrated `validate_skill_pack.py` owns catalog/discovery, frontmatter, route/definition
references, phase mapping, graph cycles, shared links, active stale paths and fixture structure.
The existing modularity `audit_references.py` checks code anchors and local links. Test code is
in tests/workflows and uses unittest; neither checker imports physics code.

Router inputs/expected outcomes: [router cases](../router/scenarios/router-cases.yaml).
Workflow fixtures: [onboarding](scenarios/onboarding-cases.yaml),
[Phase 0](scenarios/phase0-cases.yaml), [handoffs](scenarios/handoff-cases.yaml).
Fixture parsing/reference checks do not validate natural-language agent behavior.

Store raw evaluation requests separately from expectations, actual agent answers, reviewer
verdicts and unresolved failures. Record static, independent agent and human-acceptance
coverage separately. Human acceptance
is pending unless the user actually reviews the result; automated review is never labeled human.

All 17 Skills remain explicit repository-local packages. The catalog resolver demonstrates
discoverability via AGENTS -> Master/catalog; it does not install Skills globally.
