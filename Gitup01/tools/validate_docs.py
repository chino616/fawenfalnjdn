"""Check Markdown local links without importing runtime or executing physics.

The optional baseline ZIP distinguishes unchanged historical files outside docs
from newly broken links. Every such exception remains visible in the report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
import zipfile

INLINE = re.compile(r'!?\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)')
REFERENCE = re.compile(r'^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)')
CODE_SPAN = re.compile(r'(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)')


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


def audit(repo, baseline_zip=None, scope='all'):
    baseline = {}
    if baseline_zip:
        with zipfile.ZipFile(baseline_zip) as archive:
            baseline = {name: archive.read(name) for name in archive.namelist() if name.endswith('.md')}
    records, errors, historical = [], [], []
    documents = sorted((repo / 'docs' if scope == 'docs' else repo).rglob('*.md'))
    for source in documents:
        if any(part in {'.git', '__pycache__', '.pytest_cache', '.pytest-tmp'} for part in source.parts):
            continue
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
    return {'scope': scope, 'markdown_documents': len(documents), 'local_links': len(records),
            'broken_current_links': errors, 'unchanged_historical_exceptions': historical,
            'links': records, 'limitations': ['Remote HTTP availability and Markdown anchor semantics are not checked.',
                                             'This is a file-link audit, not a physics or numerical regression.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--baseline-zip', type=Path)
    parser.add_argument('--scope', choices=('docs', 'all'), default='docs')
    parser.add_argument('--json-report', type=Path)
    args = parser.parse_args()
    report = audit(args.repo.resolve(), args.baseline_zip, args.scope)
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'links'}, ensure_ascii=False, indent=2))
    return bool(report['broken_current_links'])


if __name__ == '__main__':
    raise SystemExit(main())
