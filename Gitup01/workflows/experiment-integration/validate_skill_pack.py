from pathlib import Path
import sys, re

root = Path(__file__).resolve().parent
required = [
    'AGENTS.md','_shared.md','AUTO_RUN_PROTOCOL.md','START_PROMPT_GENERAL.txt',
    'skills/cevns-experiment/SKILL.md','skills/cevns-onboarding/SKILL.md',
    'skills/cevns-dataset/SKILL.md','skills/cevns-target/SKILL.md',
    'skills/cevns-source/SKILL.md','skills/cevns-theory-response/SKILL.md',
    'skills/cevns-kinematics-cross-section/SKILL.md',
    'skills/cevns-detector-response/SKILL.md','skills/cevns-slow-counts/SKILL.md',
    'skills/cevns-fast-counts/SKILL.md','skills/cevns-statistics/SKILL.md',
    'skills/cevns-validation/SKILL.md',
    'templates/onboarding/PHYSICS_CONTRACT_TEMPLATE.yaml',
    'templates/onboarding/EVIDENCE_LEDGER_TEMPLATE.yaml',
    'templates/onboarding/STATE_TEMPLATE.yaml',
    'templates/auto/AUTO_RUN_PLAN_TEMPLATE.yaml',
    'templates/auto/AUTO_MODULE_REPORT_TEMPLATE.md',
]
err=[]
for r in required:
    if not (root/r).is_file(): err.append(f'MISSING {r}')

skills=list((root/'skills').glob('*/SKILL.md'))
if len(skills)!=12: err.append(f'expected 12 SKILL.md, found {len(skills)}')
for p in skills:
    t=p.read_text(encoding='utf-8')
    if not t.startswith('---') or '\nname:' not in t[:300]: err.append(f'bad frontmatter {p}')
    if 'AUTO_RUN_PROTOCOL.md' not in t: err.append(f'missing isolated-auto protocol reference {p}')

# Structural anti-regression rules
for banned in ['AGENTS_REVIEWED.md','EXPERIMENT_WORKFLOW_REVIEWED.md','PAPER_ONBOARDING_PROTOCOL.md','INTERACTION_PROTOCOL.md']:
    if (root/banned).exists(): err.append(f'v2 control layer must not exist: {banned}')
if list((root/'skills').glob('*-reviewed')): err.append('reviewed wrapper directories still exist')

master=(root/'skills/cevns-experiment/SKILL.md').read_text(encoding='utf-8')
for token in ['candidate_count > 1','PRE_DATASET_FREEZE','skill_debug','guided']:
    if token not in master: err.append(f'master missing hard rule: {token}')
shared=(root/'_shared.md').read_text(encoding='utf-8')
if 'confirm_mode=minimal' not in shared or 'Physics Gate' not in shared:
    err.append('_shared missing minimal/Physics Gate rule')

# backup/** is recovery-only and must never re-enter automatic physics discovery.
repo_root = root.parent.parent
quarantine_docs = {
    'repository AGENTS': repo_root/'AGENTS.md',
    'workflow router': root/'AGENTS.md',
    'shared contract': root/'_shared.md',
    'master': root/'skills/cevns-experiment/SKILL.md',
    'onboarding': root/'skills/cevns-onboarding/SKILL.md',
}
for label, path in quarantine_docs.items():
    text = path.read_text(encoding='utf-8')
    if 'backup/**' not in text:
        err.append(f'{label} missing backup/** quarantine path')
for label, path in {
    'workflow router': root/'AGENTS.md',
    'shared contract': root/'_shared.md',
    'master': root/'skills/cevns-experiment/SKILL.md',
    'onboarding': root/'skills/cevns-onboarding/SKILL.md',
}.items():
    if 'BACKUP_QUARANTINE' not in path.read_text(encoding='utf-8'):
        err.append(f'{label} missing BACKUP_QUARANTINE rule')
if '不计入 `candidate_count`' not in master:
    err.append('master does not exclude backup/** from candidate_count')

if err:
    print('\n'.join(err)); sys.exit(1)
print(f'OK: {len(required)} required files; {len(skills)} authoritative Skill files; no reviewed wrappers.')
