"""Check Markdown local links without importing runtime or executing physics.

The optional baseline ZIP distinguishes unchanged historical files outside docs
from newly broken links. Every such exception remains visible in the report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote
import zipfile

INLINE = re.compile(r'!?\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)')
REFERENCE = re.compile(r'^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)')
CODE_SPAN = re.compile(r'(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)')
EXCLUDED_DIRECTORIES = {'backup', 'outputs', '.git', '__pycache__', '.pytest_cache', '.pytest-tmp'}


def link_targets(text):
    marker = None
    for line_number, line in enumerate(text.splitlines(), 1):
        fence = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fence:
            if marker is None:
                marker = fence[1][0]
            elif marker == fence[1][0]:
                marker = None
            continue
        if marker is not None:
            continue
        line = CODE_SPAN.sub(lambda match: ' ' * len(match[0]), line)
        for match in INLINE.finditer(line):
            yield line_number, match[1]
        reference = REFERENCE.match(line)
        if reference:
            yield line_number, reference[1]


def _selected_document(repo, value):
    path = Path(value)
    path = (repo / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(repo):
        raise ValueError(f'document path is outside the repository: {value}')
    relative = path.relative_to(repo)
    if any(part.casefold() in EXCLUDED_DIRECTORIES for part in relative.parts):
        raise ValueError(f'document path is in an excluded archive/cache directory: {relative}')
    if path.suffix.casefold() != '.md' or not path.is_file():
        raise ValueError(f'expected an existing Markdown file: {relative}')
    return path


def collect_documents(repo, scope='all', files=None):
    """Select current documents without traversing backup, outputs or caches."""
    repo = Path(repo).resolve()
    if files is not None:
        if not files:
            raise ValueError('--files needs at least one Markdown path')
        return sorted({_selected_document(repo, value) for value in files})
    if scope not in ('docs', 'all'):
        raise ValueError('scope must be docs or all')
    documents = []
    root = repo / 'docs' if scope == 'docs' else repo
    for parent, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = [name for name in directories if name.casefold() not in EXCLUDED_DIRECTORIES]
        for name in filenames:
            if Path(name).suffix.casefold() == '.md':
                documents.append(_selected_document(repo, Path(parent) / name))
    return sorted(set(documents))


def audit(repo, baseline_zip=None, scope='all', files=None):
    repo = Path(repo).resolve()
    documents = collect_documents(repo, scope=scope, files=files)
    baseline = {}
    if baseline_zip:
        with zipfile.ZipFile(baseline_zip) as archive:
            baseline = {name: archive.read(name) for name in archive.namelist() if name.endswith('.md')}
    records, errors, historical = [], [], []
    for source in documents:
        rel = source.relative_to(repo).as_posix()
        content = source.read_bytes()
        unchanged = rel in baseline and hashlib.sha256(content).digest() == hashlib.sha256(baseline[rel]).digest()
        for line, raw in link_targets(content.decode('utf-8-sig')):
            value = raw.strip().strip('<>')
            if re.match(r'^(https?:|mailto:|data:|#)', value):
                continue
            value = unquote(value.split('#', 1)[0])
            target = (source.parent / value).resolve()
            item = {'file': rel, 'line': line, 'target': raw, 'resolved': str(target)}
            if target.exists():
                item['status'] = 'PASS'
            elif unchanged and not rel.startswith('docs/'):
                item['status'] = 'PREEXISTING_UNCHANGED_OUTSIDE_DOCS'
                historical.append(item)
            else:
                item['status'] = 'BROKEN'
                errors.append(item)
            records.append(item)
    return {'scope': 'files' if files is not None else scope,
            'selected_documents': [path.relative_to(repo).as_posix() for path in documents],
            'excluded_directories': sorted(EXCLUDED_DIRECTORIES),
            'markdown_documents': len(documents), 'local_links': len(records),
            'broken_current_links': errors, 'unchanged_historical_exceptions': historical,
            'links': records, 'limitations': ['Remote HTTP availability and Markdown anchor semantics are not checked.',
                                             'New-file documentation coverage and paths in prose/code spans require change-list review.',
                                             'This checker never edits README content and is not a filesystem watcher.',
                                             'This is a file-link audit, not a physics or numerical regression.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--baseline-zip', type=Path)
    parser.add_argument('--scope', choices=('docs', 'all'), default='docs')
    parser.add_argument('--files', nargs='+', type=Path,
                        help='check only these repository-relative or absolute Markdown files; overrides --scope')
    parser.add_argument('--json-report', type=Path)
    args = parser.parse_args()
    try:
        report = audit(args.repo.resolve(), args.baseline_zip, args.scope, files=args.files)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'links'}, ensure_ascii=False, indent=2))
    return bool(report['broken_current_links'])


if __name__ == '__main__':
    raise SystemExit(main())
