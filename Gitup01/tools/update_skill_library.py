"""Check or explicitly refresh the catalog-backed, user-facing Skill library.

Uses only the standard library. The default is read-only; --write replaces only
the marked table, saves the previous bytes, and records the backup. Runtime
code, Skill instructions, scientific gates and protected baselines are untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import uuid
from pathlib import Path, PurePosixPath
from urllib.parse import quote

DOCUMENT = Path('cevns_pyeft/SKILLS.md')
BEGIN = '<!-- skill-library:start -->'
END = '<!-- skill-library:end -->'
KINDS = {'router': '主路由', 'onboarding': '资料接入', 'phase': '物理阶段',
         'engineering': '工程能力', 'physics': '物理能力', 'qa': '质量检查'}
METADATA = re.compile(r'<!-- workflow-metadata:[^\n]+ -->\s*```json\n(.*?)\n```', re.S)


class LibraryError(ValueError):
    """An invalid registry, missing consumer or unsafe update target."""


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise LibraryError(f'duplicate key {key}: {path}')
            result[key] = value
        return result
    return json.loads(path.read_text('utf-8-sig'), object_pairs_hook=unique)


def inside(root, path):
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise LibraryError(f'path escapes {root}: {path}')
    return resolved


def load_inputs(repo):
    catalog = read_json(repo / 'workflows/catalog.yaml')
    routes = read_json(repo / 'workflows/cevns-pyeft/router/routes.yaml')
    definitions = {}
    for path in sorted((repo / 'workflows/cevns-pyeft/definitions').glob('*/WORKFLOW.md')):
        inside(repo / 'workflows', path)
        match = METADATA.search(path.read_text('utf-8-sig'))
        if not match:
            raise LibraryError(f'missing workflow metadata: {path}')
        meta = json.loads(match[1])
        wid = meta['workflow_id']
        if wid in definitions:
            raise LibraryError(f'duplicate workflow ID {wid}')
        definitions[wid] = (path, meta)
    return catalog, routes, definitions


def cell(value):
    return html.escape(value, quote=False).replace('|', r'\|').replace('\r\n', '\n').replace('\n', '<br>')


def link(repo, path, label):
    relative = inside(repo, path).relative_to(repo).as_posix()
    # SKILLS.md lives immediately below the repository root.
    return f'[{cell(label)}]({quote("../" + relative, safe="/")})'


def render_block(repo, catalog, routes, definitions):
    """Generate from identity/display fields and actual workflow references."""
    entries = catalog.get('skills')
    if catalog.get('schema_version') != 1 or not isinstance(entries, list) or not entries:
        raise LibraryError('catalog requires schema_version 1 and a nonempty skills array')
    ids, names, paths, rows = set(), set(), set(), []
    for entry in entries:
        for field in ('id', 'name', 'kind', 'path', 'status', 'summary_zh', 'outputs_zh'):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                raise LibraryError(f'{entry.get("id", "unknown")}: missing/non-string {field}')
        sid, name, relative = entry['id'], entry['name'], entry['path']
        if not re.fullmatch(r'cevns\.[a-z0-9_.]+', sid) or sid in ids:
            raise LibraryError(f'duplicate/invalid Skill ID {sid}')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in names:
            raise LibraryError(f'duplicate/invalid Skill name {name}')
        raw = PurePosixPath(relative)
        if raw.is_absolute() or '..' in raw.parts or '\\' in relative or ':' in relative:
            raise LibraryError(f'invalid catalog path {relative}')
        path = inside(repo / 'workflows', repo / 'workflows' / relative)
        if path in paths or path.name != 'SKILL.md' or not path.is_file():
            raise LibraryError(f'duplicate/missing Skill file {relative}')
        if path.parent.name != name:
            raise LibraryError(f'folder/name mismatch {relative}')
        header = re.match(r'\A---\n(.*?)\n---(?:\n|$)', path.read_text('utf-8-sig'), re.S)
        if not header or not re.search(r'^name: ' + re.escape(name) + r'$', header[1], re.M):
            raise LibraryError(f'frontmatter/name mismatch {relative}')
        if entry['kind'] not in KINDS or entry['status'] not in {'active', 'deprecated'}:
            raise LibraryError(f'invalid kind/status {sid}')
        phase = entry.get('phase', '')
        if phase and (entry['kind'] != 'phase' or not re.fullmatch(r'P\d{2}', phase)):
            raise LibraryError(f'invalid phase {sid}')
        ids.add(sid)
        names.add(name)
        paths.add(path)
        rows.append((entry, path))
    discovered = {inside(repo / 'workflows', path)
                  for path in (repo / 'workflows').rglob('SKILL.md')}
    if paths != discovered:
        raise LibraryError('catalog discovery mismatch: unregistered/missing authoritative Skills')
    entry_id = routes.get('entry_skill')
    if entry_id not in ids:
        raise LibraryError(f'unknown route entry Skill {entry_id}')
    callers = {sid: [] for sid in ids}
    callers[entry_id].append(link(repo, repo / 'workflows/cevns-pyeft/router/routes.yaml', '统一入口 routes.entry_skill'))
    for wid, (path, meta) in sorted(definitions.items()):
        inside(repo / 'workflows', path)
        if not path.is_file() or not isinstance(meta.get('skills'), list):
            raise LibraryError(f'invalid workflow definition {wid}')
        for sid in meta['skills']:
            if sid not in callers:
                raise LibraryError(f'unknown Skill {sid} in workflow {wid}')
            callers[sid].append(link(repo, path, path.parent.name))
    active = sum(entry['status'] == 'active' for entry in entries)
    lines = [BEGIN, f'共 **{len(entries)}** 个已登记 Skill：**{active}** 个 active，'
             f'**{len(entries) - active}** 个 deprecated。', '',
             '类别统计：' + '；'.join(f'{label} {sum(e["kind"] == kind for e in entries)}'
                                    for kind, label in KINDS.items() if any(e['kind'] == kind for e in entries)) + '。', '',
             '| 类别 / 阶段 | Skill（点击查看完整指令） | 稳定 ID | 负责什么 | 主要产物 | 调用它的流程 | 状态 |',
             '|---|---|---|---|---|---|---|']
    for entry, path in rows:
        kind = entry.get('phase') or KINDS[entry['kind']]
        values = [cell(kind), link(repo, path, entry['name']), f'`{entry["id"]}`',
                  cell(entry['summary_zh']), cell(entry['outputs_zh']),
                  '<br>'.join(callers[entry['id']]) or '尚无工作流引用（仅登记）', entry['status']]
        lines.append('| ' + ' | '.join(values) + ' |')
    lines.append(END)
    return '\n'.join(lines)


def replace_block(content, block):
    if content.count(BEGIN) != 1 or content.count(END) != 1 or content.index(BEGIN) > content.index(END):
        raise LibraryError('SKILLS.md must contain exactly one ordered skill-library marker pair')
    newline = '\r\n' if '\r\n' in content else '\n'
    first, last = content.index(BEGIN), content.index(END) + len(END)
    return content[:first] + block.replace('\n', newline) + content[last:]


def prepare(repo, *, catalog=None, routes=None, definitions=None):
    repo = Path(repo).resolve()
    if catalog is None or routes is None or definitions is None:
        catalog, routes, definitions = load_inputs(repo)
    path = inside(repo, repo / DOCUMENT)
    before = path.read_bytes()
    block = render_block(repo, catalog, routes, definitions)
    after = replace_block(before.decode('utf-8'), block).encode('utf-8')
    return path, before, after


def check_library(repo, **inputs):
    try:
        _, before, after = prepare(repo, **inputs)
        if before != after:
            return ['skill-library: table is stale; run python -B tools/update_skill_library.py --write']
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f'skill-library: {exc}']
    return []


def sync_library(repo):
    repo = Path(repo).resolve()
    path, before, after = prepare(repo)
    if before == after:
        return {'status': 'UNCHANGED', 'document': DOCUMENT.as_posix()}
    backup_root = inside(repo, repo / 'backup')
    saved = inside(backup_root, backup_root / ('skill-library-' + uuid.uuid4().hex) / DOCUMENT)
    manifest = inside(backup_root, backup_root / 'BACKUP_MANIFEST.md')
    saved.parent.mkdir(parents=True, exist_ok=False)
    saved.write_bytes(before)
    digest = hashlib.sha256(before).hexdigest()
    with manifest.open('a', encoding='utf-8') as stream:
        stream.write(f'\n\n## Skill library table sync\n\n- `{DOCUMENT.as_posix()}` → '
                     f'`{saved.relative_to(repo).as_posix()}`; SHA256 `{digest}`.\n')
    if path.read_bytes() != before:
        raise LibraryError('SKILLS.md changed during preparation; no table was written')
    path.write_bytes(after)
    return {'status': 'UPDATED', 'document': DOCUMENT.as_posix(),
            'backup': saved.relative_to(repo).as_posix(), 'sha256_before': digest,
            'sha256_after': hashlib.sha256(after).hexdigest(),
            'manual_content_preserved': True, 'protected_manifest_modified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='read-only check (default)')
    mode.add_argument('--write', action='store_true', help='back up and refresh the marked table only')
    args = parser.parse_args()
    try:
        if args.write:
            result = sync_library(args.repo)
        else:
            errors = check_library(args.repo)
            result = {'status': 'FAIL' if errors else 'PASS', 'errors': errors}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'status': 'FAIL', 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(result['status'] == 'FAIL')


if __name__ == '__main__':
    raise SystemExit(main())
