"""Presentation-only helpers for the five partial onboarding report exporters.

No physics, contract values, source choices or approval state is changed here.
"""
from pathlib import Path
import os
import re

NAV_START = '<!-- report-navigation:start -->'
NAV_END = '<!-- report-navigation:end -->'
BACK_START = '<!-- report-backlink:start -->'
BACK_END = '<!-- report-backlink:end -->'


def file_link(label, target, owner):
    relative = os.path.relpath(target, Path(owner).parent).replace('\\', '/')
    destination = '<' + relative + '>' if ' ' in relative else relative
    return '[' + label + '](' + destination + ')'


def document_links(owner, run, *, summary=False, user_input=False):
    owner, run = Path(owner), Path(run)
    doc = owner.parent
    links = []
    if owner.name != 'experiment.physics.summary.md':
        links.append(file_link('精简说明', doc / 'experiment.physics.summary.md', owner))
    if owner.name != 'experiment.physics.md':
        links.append(file_link('详细物理说明', doc / 'experiment.physics.md', owner))
    if not user_input:
        links.append(file_link('用户资料', doc / 'EXPERIMENT_USER_INPUT.md', owner))
    links += [file_link('来源登记 P00', run / 'P00_SOURCE_REGISTER.yaml', owner),
              file_link('证据台账 P01', run / 'P01_EVIDENCE_LEDGER.yaml', owner),
              file_link('缺失与冲突 P02', run / 'P02_MISSING_AND_CONFLICTS.md', owner),
              file_link('配置草稿 P03', run / 'P03_PHYSICS_CONTRACT.yaml', owner),
              file_link('Benchmark 登记', run / 'benchmark/BENCHMARK_REGISTER.md', owner),
              file_link('资料目录', doc / 'README.md', owner)]
    return links


def _headings(lines):
    fence = None
    for i, line in enumerate(lines):
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            if fence is None:
                fence = marker[1][0]
            elif fence == marker[1][0]:
                fence = None
            continue
        if fence is None:
            match = re.match(r'^## (.+?)\s*$', line)
            if match:
                yield i, match[1]


def prepare_markdown(text, *, links=(), toc=True):
    """Add repeatable navigation while preserving prose and TeX bodies."""
    text = text.replace('\r\n', '\n')
    text = text.replace('原项目未改', '原项目实验输入与 Runtime 未改')
    for start, end in [(NAV_START, NAV_END), (BACK_START, BACK_END)]:
        text = re.sub(re.escape(start) + r'.*?' + re.escape(end) + r'\n*', '', text, flags=re.S)
    text = re.sub(r'(?m)^<a id="(?:report-toc|section-\d+)"></a>\s*\n', '', text)
    text = re.sub(r'(?m)^\$\$(.+)\$\$[ \t]*$', lambda m: '$$\n' + m[1] + '\n$$', text)
    lines = text.splitlines()
    old = next((i for i, title in _headings(lines) if title == '目录'), None)
    if old is not None:
        following = next((i for i, title in _headings(lines) if i > old), len(lines))
        del lines[old:following]
    # Useful labels instead of long visible URLs inside resource tables.
    for i, line in enumerate(lines):
        if line.startswith('|'):
            lines[i] = re.sub(r'(?<=\|)\s*(https?://[^|\s]+)\s*(?=\|)',
                              lambda m: ' [官方资源](' + m[1] + ') ', line)
    headings = list(_headings(lines))
    if links and headings:
        # The top navigation supersedes an old single-link header, not body references.
        first = headings[0][0]
        lines = [line for i, line in enumerate(lines)
                 if not (i < first and re.fullmatch(
                     r'\[[^\]]+\]\(experiment\.physics(?:\.summary)?\.md\)', line.strip()))]
        headings = list(_headings(lines))
    body = '\n'.join(lines).strip()
    if toc and len(headings) >= 3:
        header = '\n'.join(lines[:headings[0][0]]).strip()
        content = []
        for n, (index, title) in enumerate(headings, 1):
            end = headings[n][0] if n < len(headings) else len(lines)
            section = '\n'.join(lines[index:end]).strip()
            content += ['<a id="section-' + str(n) + '"></a>', '', section, '',
                        BACK_START, '[返回目录](#report-toc)', BACK_END, '']
        toc_lines = ['<a id="report-toc"></a>', '', '## 目录', '']
        toc_lines += ['- [' + title + '](#section-' + str(n) + ')' for n, (_, title) in enumerate(headings, 1)]
        body = header + '\n\n' + '\n'.join(toc_lines) + '\n\n' + '\n'.join(content)
    if links:
        navigation = NAV_START + '\n' + ' · '.join(links) + '\n' + NAV_END
        title_end = body.find('\n')
        body = body[:title_end] + '\n\n' + navigation + '\n' + body[title_end:]
    return re.sub(r'\n{3,}', '\n\n', body).rstrip() + '\n'
