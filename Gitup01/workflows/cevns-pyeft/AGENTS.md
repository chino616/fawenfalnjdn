# CEvNS-pyEFT workflow governance

Read [common governance](../AGENTS.md), resolve `cevns.router.experiment` through
[catalog.yaml](../catalog.yaml), then read that Master Skill. The single task-routing authority
is [router/routes.yaml](router/routes.yaml). Never infer onboarding from an experiment name,
paper presence, placeholder directory or old implementation.

Current runtime layout is flat: cevns_pyeft/, data/, tests/, tools/. Resource roots explicitly
contain data/. Python code remains the implementation authority; workflows only describe its use.

P01–P10 are the experiment-onboarding phase family. Runtime maintenance, theory/resource work,
archive lifecycle, capability maintenance, release validation and Skill QA have their own
workflow definitions. Existing engineering milestones are historical, not a standing sequence.

Use shared policies for approval, isolated automatic runs, evidence, directory identity and
checkpoint recovery. New scientific meanings require the relevant human physics decision;
machine checks and existing file presence never substitute for it. Honor existing authorization
for routine engineering work. Preserve behavior of CsI2017, CsI2021 and Ar2020; shared physics
changes require affected regression coverage. The repository's backup rule remains applicable,
and backup material is excluded from automatic discovery by the archive-isolation policy.

Existing execution records remain in their documented historical locations. A resumed dataset
must verify its unique current index and authority/fingerprint references before proceeding;
moving Skill files grants no new dataset, scientific or write approval.
