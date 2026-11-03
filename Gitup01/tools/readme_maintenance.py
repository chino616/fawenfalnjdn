"""Plan README maintenance from Git/snapshots and sync explicit inventory blocks.

Git operations are read-only. Sync edits only named README inventory blocks and
backs up their previous bytes; it never deletes source files or commits changes.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import quote, unquote
import uuid

BEGIN = '<!-- readme-inventory:start -->'
END = '<!-- readme-inventory:end -->'
EXCLUDED = {'backup', 'outputs', '.git', '__pycache__', '.pytest_cache', '.pytest-tmp', '.ipynb_checkpoints'}


class MaintenanceError(ValueError):
    pass


def relative_name(value):
    value = str(value).replace('\\', '/')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or ':' in value or not path.parts:
        raise MaintenanceError(f'expected a repository-relative path: {value}')
    return path.as_posix()


def excluded(value):
    parts = PurePosixPath(str(value)).parts
    if any(part.casefold() in EXCLUDED for part in parts):
        return True
    return (bool(parts) and parts[0] == 'workflows' and 'runs' in parts
            or bool(parts) and parts[0] == 'docs' and 'reviews' in parts
            or parts[:2] == ('tests', 'reference'))


def safe_path(repo, value):
    name = relative_name(value)
    path = (repo / name).resolve()
    if not path.is_relative_to(repo) or excluded(name):
        raise MaintenanceError(f'excluded or outside current repository scope: {name}')
    return path


def walk_files(repo):
    """Prune archives before traversal, and do not follow symlinks."""
    for parent, directories, names in os.walk(repo, followlinks=False):
        folder = Path(parent)
        directories[:] = [name for name in directories
                          if not excluded((folder / name).relative_to(repo).as_posix())
                          and not (folder / name).is_symlink()]
        for name in sorted(names):
            path = folder / name
            relative = path.relative_to(repo).as_posix()
            if not excluded(relative) and not path.is_symlink():
                yield relative, path


def snapshot(repo):
    repo = Path(repo).resolve()
    files = {}
    for name, path in walk_files(repo):
        content = path.read_bytes()
        files[name] = {'sha256': hashlib.sha256(content).hexdigest(), 'size': len(content)}
    return {'schema_version': 1, 'kind': 'readme-maintenance-snapshot',
            'created_utc': datetime.now(timezone.utc).isoformat(),
            'repository': str(repo), 'files': files,
            'scope': 'current files; archives, generated outputs and frozen evidence excluded'}


def compare_snapshots(before, after):
    for value in (before, after):
        if value.get('schema_version') != 1 or value.get('kind') != 'readme-maintenance-snapshot':
            raise MaintenanceError('unsupported snapshot identity/version')
        for name, record in value['files'].items():
            relative_name(name)
            if not re.fullmatch('[0-9a-f]{64}', record.get('sha256', '')):
                raise MaintenanceError(f'invalid snapshot hash: {name}')
    old, new = before['files'], after['files']
    removed, added = set(old) - set(new), set(new) - set(old)
    by_old, by_new = defaultdict(list), defaultdict(list)
    for name in removed:
        by_old[old[name]['sha256']].append(name)
    for name in added:
        by_new[new[name]['sha256']].append(name)
    changes = []
    for digest in sorted(set(by_old) & set(by_new)):
        if len(by_old[digest]) == len(by_new[digest]) == 1:
            left, right = by_old[digest][0], by_new[digest][0]
            changes.append({'status': 'R100', 'old_path': left, 'new_path': right})
            removed.remove(left)
            added.remove(right)
    changes += [{'status': 'D', 'old_path': name, 'new_path': None} for name in sorted(removed)]
    changes += [{'status': 'A', 'old_path': None, 'new_path': name} for name in sorted(added)]
    changes += [{'status': 'M', 'old_path': name, 'new_path': name}
                for name in sorted(set(old) & set(new)) if old[name]['sha256'] != new[name]['sha256']]
    return [item for item in changes if not excluded(item['new_path'] or item['old_path'])]


def git(repo, *args):
    environment = os.environ.copy()
    environment['GIT_OPTIONAL_LOCKS'] = '0'
    result = subprocess.run(['git', '-C', str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=environment)
    if result.returncode:
        raise MaintenanceError(result.stderr.decode('utf-8', errors='replace').strip())
    return result.stdout


def parse_name_status(raw):
    tokens = raw.decode('utf-8', errors='surrogateescape').split('\0')
    if tokens and tokens[-1] == '':
        tokens.pop()
    changes, index = [], 0
    while index < len(tokens):
        status = tokens[index]
        count = 2 if status.startswith(('R', 'C')) else 1
        if not re.fullmatch(r'[ACDMRTUXB][0-9]*', status) or index + count >= len(tokens):
            raise MaintenanceError('invalid NUL-delimited Git name-status record')
        names = [relative_name(value) for value in tokens[index + 1:index + count + 1]]
        old = None if status.startswith('A') else names[0]
        new = None if status.startswith('D') else names[-1]
        changes.append({'status': status, 'old_path': old, 'new_path': new})
        index += count + 1
    return changes


def scope_changes(changes):
    result = []
    for item in changes:
        old, new = item['old_path'], item['new_path']
        old_active, new_active = bool(old and not excluded(old)), bool(new and not excluded(new))
        if not old_active and not new_active:
            continue
        if item['status'].startswith('R') and old_active != new_active:
            result.append({'status': 'D' if old_active else 'A',
                           'old_path': old if old_active else None, 'new_path': new if new_active else None,
                           'scope_note': 'move crosses the current-content/archive boundary'})
        elif item['status'].startswith('C') and not new_active:
            continue
        elif item['status'].startswith('C') and not old_active:
            result.append({'status': 'A', 'old_path': None, 'new_path': new})
        else:
            result.append(item)
    return result


def git_changes(repo, base='HEAD'):
    top = Path(os.fsdecode(git(repo, 'rev-parse', '--show-toplevel')).strip()).resolve()
    if not repo.is_relative_to(top):
        raise MaintenanceError('selected project is outside its Git worktree')
    revision = base + '^{commit}'
    commit = git(repo, 'rev-parse', '--verify', '--end-of-options', revision).decode().strip()
    changes = parse_name_status(git(repo, 'diff', '--relative', '--name-status', '-z', '-M', commit, '--', '.'))
    existing = {item['new_path'] for item in changes}
    for name in git(repo, 'ls-files', '--others', '--exclude-standard', '-z', '--', '.').decode('utf-8', errors='surrogateescape').split('\0'):
        if name and name not in existing:
            changes.append({'status': 'A', 'old_path': None, 'new_path': relative_name(name), 'untracked': True})
    prefix = repo.relative_to(top).as_posix()
    prefix = '' if prefix == '.' else prefix + '/'
    baseline_names = git(top, 'ls-tree', '-r', '-z', '--name-only', commit, '--', prefix or '.')
    names = [name[len(prefix):] for name in baseline_names.decode('utf-8', errors='surrogateescape').split('\0')
             if name and name.startswith(prefix)]
    active = scope_changes(changes)
    return active, set(names), {'mode': 'git', 'base_ref': base, 'base_commit': commit,
                              'git_root': str(top), 'project_prefix': prefix,
                              'excluded_changes': len(changes) - len(active)}


def ancestors(name):
    parent = PurePosixPath(name).parent
    while True:
        yield (parent / 'README.md').as_posix()
        if parent == PurePosixPath('.'):
            break
        parent = parent.parent


def doc_checker():
    path = Path(__file__).with_name('validate_docs.py')
    spec = importlib.util.spec_from_file_location('readme_maintenance_doc_checker', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def maintenance_plan(repo, *, base='HEAD', before=None):
    repo = Path(repo).resolve()
    if before is None:
        changes, baseline_names, source = git_changes(repo, base)
    else:
        current = snapshot(repo)
        changes = compare_snapshots(before, current)
        baseline_names = set(before['files'])
        source = {'mode': 'snapshot', 'base_created_utc': before.get('created_utc'),
                  'current_created_utc': current['created_utc'], 'rename_detection': 'unique identical hashes only'}
    groups = defaultdict(list)
    unowned, removed_targets, removed_readmes = [], set(), []
    for index, item in enumerate(changes):
        names = {name for name in (item['old_path'], item['new_path']) if name}
        owners = set()
        for name in names:
            for candidate in ancestors(name):
                if not excluded(candidate) and (repo / candidate).is_file():
                    owners.add(candidate)
        item['previous_readme'] = next((name for name in ancestors(item['old_path']) if name in baseline_names), None) if item['old_path'] else None
        item['current_readme'] = next((name for name in ancestors(item['new_path']) if (repo / name).is_file()), None) if item['new_path'] else None
        if item['new_path'] and item['current_readme'] is None:
            unowned.append(item['new_path'])
        for owner in sorted(owners):
            groups[owner].append(index)
        if item['status'].startswith(('D', 'R')) and item['old_path']:
            old = item['old_path']
            removed_targets.add(old)
            for parent in PurePosixPath(old).parents:
                if parent == PurePosixPath('.'):
                    break
                if not (repo / parent).exists():
                    removed_targets.add(parent.as_posix())
            if PurePosixPath(old).name.casefold() == 'readme.md':
                removed_readmes.append(old)
    checker = doc_checker()
    reverse, read_count, referrers = [], 0, set()
    needles = sorted(removed_targets, key=len, reverse=True)
    pattern = re.compile('|'.join(re.escape(value) for value in needles)) if needles else None
    if needles:
        for name, path in walk_files(repo):
            if path.suffix.casefold() != '.md':
                continue
            content = path.read_text(encoding='utf-8-sig')
            read_count += 1
            for line, raw in checker.link_targets(content):
                value = raw.strip().strip('<>')
                if re.match(r'^(https?:|mailto:|data:|#)', value):
                    continue
                target = (path.parent / unquote(value.split('#', 1)[0])).resolve()
                if target.is_relative_to(repo) and target.relative_to(repo).as_posix() in removed_targets:
                    reverse.append({'document': name, 'line': line, 'kind': 'link',
                                    'old_target': target.relative_to(repo).as_posix()})
                    referrers.add(name)
            for number, line in enumerate(content.splitlines(), 1):
                for value in set(pattern.findall(line)):
                    reverse.append({'document': name, 'line': number, 'kind': 'literal_review', 'old_target': value})
                    referrers.add(name)
    documents = sorted(set(groups) | referrers)
    link_audit = checker.audit(repo, files=documents) if documents else {'broken_current_links': [], 'local_links': 0}
    return {'schema_version': 1, 'status': 'REVIEW_REQUIRED' if changes else 'NO_CHANGES',
            'source': source, 'changes': changes, 'change_count': len(changes),
            'readme_tasks': [{'path': name, 'change_indices': indices, 'action': 'review current description, navigation and inventory'}
                             for name, indices in sorted(groups.items())],
            'referring_documents': sorted(referrers),
            'files_without_current_readme': unowned, 'removed_readmes': removed_readmes,
            'old_path_references': reverse, 'reverse_reference_documents_read_once': read_count,
            'broken_links': link_audit['broken_current_links'],
            'limitations': ['Git status does not prove semantic README completeness.',
                            'Literal mentions may be intentional history and require review; no prose is deleted automatically.',
                            'No file deletion, Git staging, commit or push is performed.']}


def checked_readmes(repo, names):
    paths = []
    for name in names:
        path = safe_path(repo, name)
        if path.name.casefold() != 'readme.md' or not path.is_file():
            raise MaintenanceError(f'expected an existing current README: {name}')
        paths.append(path)
    if not paths:
        raise MaintenanceError('select at least one README explicitly')
    return sorted(set(paths))


def inventory_content(repo, path, content):
    newline = '\r\n' if '\r\n' in content else '\n'
    entries = []
    for child in sorted(path.parent.iterdir(), key=lambda item: (not item.is_dir(), item.name.casefold())):
        name = child.relative_to(repo).as_posix()
        if child == path or excluded(name) or child.is_symlink():
            continue
        directory = child.is_dir()
        label = child.name.replace('|', r'\|').replace('[', r'\[').replace(']', r'\]').replace('\n', r'\n')
        destination = child.name + ('/README.md' if directory and (child / 'README.md').is_file() else '/' if directory else '')
        entries.append(f'| [{label}{"/" if directory else ""}]({quote(destination, safe="/")}) | {"目录" if directory else "文件"} |')
    lines = [BEGIN, '**当前活动目录内容（自动维护区）**', '',
             '备份、生成结果和历史/冻结证据不列入此区；用途见人工说明。', '',
             '| 路径 | 类型 |', '|---|---|', *entries, END]
    block = newline.join(lines)
    starts, ends = content.count(BEGIN), content.count(END)
    if starts == ends == 0:
        return content + (newline if content and not content.endswith('\n') else '') + newline + block + newline
    if starts != 1 or ends != 1 or content.index(BEGIN) > content.index(END):
        raise MaintenanceError(f'inventory markers must form one ordered pair: {path}')
    first, last = content.index(BEGIN), content.index(END) + len(END)
    return content[:first] + block + content[last:]


def check_readmes(repo, names):
    repo = Path(repo).resolve()
    paths = checked_readmes(repo, names)
    states = []
    for path in paths:
        content = path.read_bytes().decode('utf-8')
        expected = inventory_content(repo, path, content)
        state = 'CURRENT' if content == expected else 'STALE' if BEGIN in content else 'NOT_MANAGED'
        states.append({'path': path.relative_to(repo).as_posix(), 'inventory': state})
    links = doc_checker().audit(repo, files=paths)
    ok = all(item['inventory'] == 'CURRENT' for item in states) and not links['broken_current_links']
    return {'status': 'PASS' if ok else 'NEEDS_UPDATE', 'readmes': states,
            'broken_links': links['broken_current_links'],
            'scope': 'managed inventory and Markdown links only; manual descriptions still require review'}


def sync_readmes(repo, names):
    repo = Path(repo).resolve()
    paths = checked_readmes(repo, names)
    prepared = []
    for path in paths:
        before = path.read_bytes()
        after = inventory_content(repo, path, before.decode('utf-8')).encode('utf-8')
        if before != after:
            prepared.append((path, before, after))
    # Validate every target and marker before writing any of them.
    for path, before, _ in prepared:
        if path.read_bytes() != before:
            raise MaintenanceError(f'README changed during preparation: {path}')
    backup = repo / 'backup' / ('readme-sync-' + uuid.uuid4().hex)
    records = []
    for path, before, after in prepared:
        if path.read_bytes() != before:
            raise MaintenanceError(f'README changed before its write: {path}')
        relative = path.relative_to(repo)
        saved = backup / relative
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(before)
        path.write_bytes(after)
        records.append({'path': relative.as_posix(), 'backup': saved.relative_to(repo).as_posix(),
                        'sha256_before': hashlib.sha256(before).hexdigest(),
                        'sha256_after': hashlib.sha256(after).hexdigest()})
    if records:
        with (repo / 'backup/BACKUP_MANIFEST.md').open('a', encoding='utf-8') as stream:
            stream.write('\n\n## README managed inventory sync\n\n')
            for item in records:
                stream.write(f"- `{item['path']}` → `{item['backup']}`; SHA256 `{item['sha256_before']}`.\n")
    return {'status': 'SYNCED' if records else 'UNCHANGED', 'updated_readmes': records,
            'check': check_readmes(repo, names),
            'manual_content_preserved': True, 'git_mutations': []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('plan', 'snapshot', 'sync', 'check'))
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--base', default='HEAD', help='Git commit/ref to compare against the current index+worktree')
    parser.add_argument('--snapshot-base', type=Path, help='compare this saved snapshot instead of Git')
    parser.add_argument('--readmes', nargs='+', help='explicit repository-relative READMEs for sync/check')
    parser.add_argument('--out', type=Path, help='JSON result; snapshot requires this path')
    parser.add_argument('--overwrite-report', action='store_true')
    args = parser.parse_args()
    repo = args.repo.resolve()
    if not repo.is_dir():
        parser.error('--repo must be an existing project directory')
    if args.action == 'snapshot' and args.out is None:
        parser.error('snapshot requires --out')
    if args.action in ('sync', 'check') and not args.readmes:
        parser.error('sync/check requires explicit --readmes')
    if args.out and args.out.exists() and not args.overwrite_report:
        parser.error('report exists; choose a new path or explicitly use --overwrite-report')
    exit_code = 0
    try:
        if args.action == 'snapshot':
            result = snapshot(repo)
        elif args.action == 'plan':
            before = json.loads(args.snapshot_base.read_text(encoding='utf-8')) if args.snapshot_base else None
            result = maintenance_plan(repo, base=args.base, before=before)
        elif args.action == 'sync':
            result = sync_readmes(repo, args.readmes)
            exit_code = int(result['check']['status'] != 'PASS')
        else:
            result = check_readmes(repo, args.readmes)
            exit_code = int(result['status'] != 'PASS')
    except (MaintenanceError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        result = {'status': 'BLOCKED', 'error': str(error), 'action': args.action,
                  'next_step': 'For a folder without Git, save a snapshot before changes and use --snapshot-base; no Git repository is initialized.'}
        exit_code = 2
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary = {key: value for key, value in result.items() if key not in ('files', 'changes', 'old_path_references', 'readme_tasks')}
    if args.action == 'snapshot':
        summary['file_count'] = len(result.get('files', {}))
    if args.action == 'plan':
        summary['readme_task_count'] = len(result.get('readme_tasks', []))
        summary['old_reference_count'] = len(result.get('old_path_references', []))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
