"""Read-only Skill-pack validator: structure, references and immutable baseline.

Machine records use JSON syntax, a YAML 1.2 subset. This is neither a natural-language
router nor a physics validator. It does not import runtime code or grant approvals.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

PROJECT = Path('workflows/cevns-pyeft')
CONFIG = Path('tools/workflow_validation/config')
SKILL_ID = re.compile(r'\bcevns\.(?:router|onboarding|phase|engineering|physics|qa)\.[a-z0-9_.]+')
LINK = re.compile(r'(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)')


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate key {key}')
            result[key] = value
        return result
    return json.loads(path.read_text('utf-8-sig'), object_pairs_hook=unique)


def frontmatter(path):
    match = re.match(r'\A---\n(.*?)\n---(?:\n|$)', path.read_text('utf-8-sig'), re.S)
    if not match:
        raise ValueError('missing YAML frontmatter')
    fields = {}
    for line in match[1].splitlines():
        item = re.fullmatch(r'(name|description): (.+)', line)
        if not item or item[1] in fields:
            raise ValueError('expected unique plain name/description scalars')
        fields[item[1]] = item[2]
    if set(fields) != {'name', 'description'}:
        raise ValueError('name and description required')
    name, desc = fields['name'], fields['description']
    quoted = desc.startswith('"')
    if quoted:
        desc = json.loads(desc)
        if not isinstance(desc, str):
            raise ValueError('description must be a string scalar')
        fields['description'] = desc
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64 or name != path.parent.name:
        raise ValueError('invalid name or folder/name mismatch')
    if (not desc.strip() or len(desc) > 1024 or re.search(r'[<>]|\[TODO:', desc)
            or (not quoted and re.search(r':\s|\s#', desc))):
        raise ValueError('invalid plain description')
    return fields


def canonical_path(repo, value):
    base = (repo / 'workflows').resolve()
    path = (base / value).resolve()
    if not path.is_relative_to(base):
        raise ValueError('catalog path escapes workflows')
    return path


def check_catalog(repo, catalog):
    errors, ids, paths, names, phases = [], set(), set(), set(), {}
    if catalog.get('schema_version') != 1 or 'routes' in catalog:
        errors.append('catalog: invalid version or duplicated route authority')
    for entry in catalog.get('skills', []):
        sid, value = entry.get('id'), entry.get('path', '')
        if not sid or sid in ids:
            errors.append(f'catalog: duplicate/missing ID {sid}')
        ids.add(sid)
        try:
            path = canonical_path(repo, value)
        except (ValueError, TypeError) as exc:
            errors.append(f'catalog: {sid}: {exc}')
            continue
        if path in paths:
            errors.append(f'catalog: duplicate path {value}')
        paths.add(path)
        if path.name != 'SKILL.md' or not path.is_file():
            errors.append(f'catalog: missing Skill {value}')
            continue
        try:
            header = frontmatter(path)
            if entry.get('name') != header['name'] or header['name'] in names:
                errors.append(f'catalog: duplicate/mismatched name {value}')
            names.add(header['name'])
        except ValueError as exc:
            errors.append(f'frontmatter: {value}: {exc}')
        if entry.get('status') not in {'active', 'deprecated'}:
            errors.append(f'catalog: invalid status {sid}')
        kind = {'router': 'router', 'onboarding': 'onboarding', 'phase': 'phases',
                'engineering': 'engineering', 'physics': 'physics', 'qa': 'qa'}.get(entry.get('kind'))
        if not kind or not path.is_relative_to((repo / PROJECT / 'skills' / kind).resolve()):
            errors.append(f'catalog: kind/path mismatch {sid}')
        if entry.get('phase'):
            phase = entry['phase']
            if phase in phases or entry.get('kind') != 'phase' or f'.{phase.lower()}.' not in sid:
                errors.append(f'phase: duplicate/mismatched mapping {phase}')
            phases[phase] = sid
    found = {p.resolve() for p in (repo / 'workflows').rglob('SKILL.md')}
    if found != paths:
        errors.append(f'catalog: unregistered/missing authoritative Skills: {sorted(map(str, found ^ paths))}')
    if set(phases) != {f'P{i:02d}' for i in range(1, 11)}:
        errors.append('phase: expected exactly P01-P10')
    return errors


def definition_metadata(path):
    text = path.read_text('utf-8')
    if text.startswith('---'):
        raise ValueError('workflow definition must not have Skill frontmatter')
    match = re.search(r'<!-- workflow-metadata:[^\n]+ -->\s*```json\n(.*?)\n```', text, re.S)
    if not match:
        raise ValueError('missing workflow metadata')
    return json.loads(match[1])


def graph_errors(graph, label):
    errors, visited, visiting = [], set(), set()
    def visit(node):
        if node in visiting:
            errors.append(f'{label}: invocation cycle at {node}')
            return
        if node in visited:
            return
        visiting.add(node)
        for target in graph.get(node, []):
            if target not in graph:
                errors.append(f'{label}: unknown target {target}')
            else:
                visit(target)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)
    return errors


def check_routes(repo, catalog, routes, definitions):
    errors, kinds, aliases = [], set(), set()
    skills = {entry['id'] for entry in catalog['skills']}
    contract = routes.get('intent_contract', {})
    if contract.get('experiment_name_alone_selects_onboarding') is not False:
        errors.append('routing: experiment name must never select onboarding')
    if contract.get('missing_intent_action') != 'clarify_request_without_creating_artifacts':
        errors.append('routing: ambiguous intent must remain read-only clarification')
    if contract.get('machine_pass_is_human_approval') is not False or not contract.get('one_primary_route'):
        errors.append('routing: approval/primary-route invariant failed')
    if routes.get('entry_skill') not in skills:
        errors.append('routing: missing Master Skill')
    for route in routes.get('routes', []):
        kind = route.get('request_kind')
        if not kind or kind in kinds:
            errors.append(f'routing: duplicate/missing request kind {kind}')
        kinds.add(kind)
        for alias in route.get('aliases', []):
            if alias in aliases:
                errors.append(f'routing: duplicate alias {alias}')
            aliases.add(alias)
        target = route.get('workflow')
        path = (repo / PROJECT / route.get('definition', '')).resolve()
        if target not in definitions or definitions[target][0].resolve() != path:
            errors.append(f'routing: unknown/mismatched workflow target {target}')
    if kinds & aliases:
        errors.append(f'routing: canonical kind/alias collision {kinds & aliases}')
    for wid, (_, meta) in definitions.items():
        for sid in meta.get('skills', []):
            if sid not in skills:
                errors.append(f'workflow: unknown Skill {sid} in {wid}')
            if sid == routes.get('entry_skill'):
                errors.append(f'workflow: recursive dispatch through Master in {wid}')
    errors.extend(graph_errors({wid: meta.get('handoffs', []) for wid, (_, meta) in definitions.items()}, 'workflow'))
    errors.extend(graph_errors({e['id']: e.get('invokes', []) for e in catalog['skills']}, 'skill'))
    return errors


def without_fences(text):
    lines, marker = [], None
    for line in text.splitlines():
        match = re.match(r'^\s*(`{3,}|~{3,})', line)
        if match:
            if marker is None:
                marker = match[1][0]
            elif match[1][0] == marker:
                marker = None
            continue
        if marker is None:
            lines.append(line)
    return '\n'.join(lines)


def check_links(repo, documents, historical):
    errors = []
    historical_paths = {item['path'] for item in historical['retained_paths'] if 'path' in item}
    for path in documents:
        text = path.read_text('utf-8')
        rel = path.relative_to(repo).as_posix()
        for target in LINK.findall(without_fences(text)):
            if target.startswith(('http:', 'https:', 'mailto:', '#')) or '<' in target:
                continue
            target = unquote(target.split('#', 1)[0])
            if target and not (path.parent / target).resolve().exists():
                errors.append(f'link: {rel} -> {target}')
        if 'src/cevns_pyeft' in text:
            errors.append(f'path: stale src layout in {rel}')
        if 'workflows/experiment-integration/' in text and rel not in historical_paths:
            errors.append(f'path: stale active workflow path in {rel}')
        if '_shared.md' in text or 'AUTO_RUN_PROTOCOL.md' in text:
            errors.append(f'path: retired policy filename in {rel}')
    return errors


def protected_errors(repo):
    payload = read_json(repo / CONFIG / 'PROTECTED_FILES.json')
    errors = []
    for relative, expected in payload['files'].items():
        path = repo / relative
        if not path.is_file():
            errors.append(f'protected: missing {relative}')
            continue
        with path.open('rb') as handle:
            actual = hashlib.file_digest(handle, 'sha256').hexdigest()
        if actual != expected:
            errors.append(f'protected: changed {relative}')
    for area in ['cevns_pyeft', 'data', 'configs', 'schemas', 'examples']:
        for path in (repo / area).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.relative_to(repo).as_posix() not in payload['files']:
                errors.append(f'protected: unexpected addition {path.relative_to(repo)}')
    return errors


def validate(repo):
    catalog = read_json(repo / 'workflows/catalog.yaml')
    routes = read_json(repo / PROJECT / 'router/routes.yaml')
    historical = read_json(repo / CONFIG / 'HISTORICAL_PATH_EXCEPTIONS.json')
    errors, definitions = check_catalog(repo, catalog), {}
    for path in (repo / PROJECT / 'definitions').glob('*/WORKFLOW.md'):
        try:
            meta = definition_metadata(path)
            wid = meta['workflow_id']
            if wid in definitions:
                errors.append(f'workflow: duplicate ID {wid}')
            definitions[wid] = (path, meta)
        except (ValueError, KeyError) as exc:
            errors.append(f'workflow: {path}: {exc}')
    errors.extend(check_routes(repo, catalog, routes, definitions))
    documents = [repo / 'AGENTS.md', repo / 'workflows/AGENTS.md', repo / 'workflows/README.md']
    documents += list((repo / PROJECT).rglob('*.md')) + list((repo / 'workflows/_shared').rglob('*.md'))
    errors.extend(check_links(repo, documents, historical))
    ids = {entry['id'] for entry in catalog['skills']}
    for path in documents:
        for sid in SKILL_ID.findall(path.read_text('utf-8')):
            if sid not in ids:
                errors.append(f'workflow: unresolved Skill ID {sid} in {path.relative_to(repo)}')
    for name in ['scientific-integrity', 'write-authorization', 'evidence-and-approval', 'archive-isolation',
                 'automation', 'interaction', 'dataset-layout', 'progress-continuity']:
        if not (repo / 'workflows/_shared/policies' / (name + '.md')).is_file():
            errors.append(f'policy: missing owner {name}')
    for path in (repo / 'workflows/_shared/schemas').glob('*.yaml'):
        schema = read_json(path)
        if schema.get('$schema') != 'https://json-schema.org/draft/2020-12/schema' or schema.get('type') != 'object':
            errors.append(f'schema: invalid schema declaration {path.name}')
    cases = read_json(repo / PROJECT / 'router/scenarios/router-cases.yaml')['cases']
    kinds = {route['request_kind'] for route in routes['routes']}
    for case in cases:
        if case['expected_request_kind'] is not None and case['expected_request_kind'] not in kinds:
            errors.append(f'fixture: unresolved expected route {case["id"]}')
    workflow_cases = 0
    for path in (repo / PROJECT / 'qa/scenarios').glob('*.yaml'):
        fixtures = read_json(path)['cases']
        workflow_cases += len(fixtures)
        if len({case['id'] for case in fixtures}) != len(fixtures):
            errors.append(f'fixture: duplicate case ID in {path.name}')
        for case in fixtures:
            if not case.get('input') or not case.get('expected_behaviors'):
                errors.append(f'fixture: missing input/expectation {case.get("id")}')
    errors.extend(protected_errors(repo))
    return errors, {'skills': len(catalog['skills']), 'workflows': len(definitions),
                    'routes': len(routes['routes']), 'router_fixtures': len(cases),
                    'workflow_fixtures': workflow_cases, 'documents': len(documents),
                    'natural_language_behavior': 'not established by this validator'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--resolve', metavar='SKILL_ID')
    args = parser.parse_args()
    repo = args.repo.resolve()
    try:
        if args.resolve:
            catalog = read_json(repo / 'workflows/catalog.yaml')
            matches = [e for e in catalog['skills'] if e['id'] == args.resolve and e['status'] == 'active']
            if len(matches) != 1:
                raise ValueError('expected exactly one active Skill')
            path = canonical_path(repo, matches[0]['path'])
            frontmatter(path)
            print(path)
            return 0
        errors, summary = validate(repo)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('ERROR:', exc)
        return 1
    for error in errors:
        print('ERROR:', error)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print('PASS: static workflow structure and protected-file fingerprints.' if not errors else f'FAIL: {len(errors)} issues.')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
