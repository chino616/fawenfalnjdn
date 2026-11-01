"""Read-only audit of this skill's source-symbol anchors and local links.

This does not import the physics package or execute its models. It cannot
validate physical correctness, convergence, or external provenance.
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path
from urllib.parse import unquote


ANCHOR = re.compile(
    r"(?<![\w/])(src/cevns_pyeft/[A-Za-z0-9_/.]+\.py)::"
    r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)"
)
LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
REQUIRED_REFERENCES = (
    "01-physics-contracts.md",
    "02-current-code-map.md",
    "03-replacement-playbook.md",
    "04-proposed-interfaces.md",
    "05-validation-and-invalidation.md",
)


def find_repo(skill: Path) -> Path:
    for candidate in skill.parents:
        if (candidate / "src" / "cevns_pyeft").is_dir():
            return candidate
    raise ValueError("Cannot find src/cevns_pyeft; provide --repo explicitly")


def declared_symbols(tree: ast.Module) -> dict[str, int]:
    symbols: dict[str, int] = {}

    def visit(nodes: list[ast.stmt], prefix: str = "") -> None:
        for node in nodes:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                qualified = prefix + node.name
                symbols[qualified] = node.lineno
                visit(node.body, qualified + ".")
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    for name in ast.walk(target):
                        if isinstance(name, ast.Name):
                            symbols[prefix + name.id] = node.lineno

    visit(tree.body)
    return symbols


def audit_frontmatter(skill: Path) -> list[str]:
    """Validate this skill's two plain scalar fields without a YAML package.

    Deliberately reject complex YAML rather than pretending to parse it. For
    metadata maps or multiline YAML use the upstream PyYAML-based validator.
    """
    content = (skill / "SKILL.md").read_text(encoding="utf-8")
    header = re.match(r"\A---\n(.*?)\n---(?:\n|$)", content, re.S)
    if header is None:
        return ["Invalid or missing YAML frontmatter delimiters"]
    values: dict[str, str] = {}
    for line in header.group(1).splitlines():
        match = re.fullmatch(r"(name|description): (.+)", line)
        if match is None or match.group(1) in values:
            return ["Frontmatter must contain unique plain name/description scalars"]
        values[match.group(1)] = match.group(2)
    name = values.get("name", "")
    description = values.get("description", "")
    errors = []
    if (
        not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
        or len(name) > 64
        or name != skill.name
    ):
        errors.append("Invalid skill name or folder/name mismatch")
    if (
        not description.strip()
        or len(description) > 1024
        or any(mark in description for mark in ("<", ">", "[TODO:"))
        or re.search(r":\s|\s#", description)
    ):
        errors.append("Invalid or non-plain description scalar")
    return errors


def audit(repo: Path, skill: Path, verbose: bool = False) -> list[str]:
    errors: list[str] = []
    documents = [skill / "SKILL.md"] + sorted((skill / "references").glob("*.md"))
    for filename in REQUIRED_REFERENCES:
        if not (skill / "references" / filename).is_file():
            errors.append("Missing reference: " + filename)
    cache: dict[Path, dict[str, int]] = {}
    anchors: set[tuple[str, str]] = set()
    local_links = 0
    for document in documents:
        if not document.is_file():
            errors.append("Missing document: " + str(document))
            continue
        content = document.read_text(encoding="utf-8")
        for filename, symbol in ANCHOR.findall(content):
            anchors.add((filename, symbol))
            source = repo / filename
            if not source.is_file():
                errors.append(f"{document.name}: missing source {filename}")
                continue
            if source not in cache:
                try:
                    cache[source] = declared_symbols(
                        ast.parse(source.read_text(encoding="utf-8-sig"), filename=str(source))
                    )
                except (SyntaxError, UnicodeError) as exc:
                    errors.append(f"Cannot parse {filename}: {exc}")
                    cache[source] = {}
            if symbol not in cache[source]:
                errors.append(f"{document.name}: missing symbol {filename}::{symbol}")
        for raw_target in LINK.findall(content):
            target = raw_target.strip().strip("<>")
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            local_links += 1
            target = unquote(target.split("#", 1)[0])
            if target and not (document.parent / target).resolve().exists():
                errors.append(f"{document.name}: broken local link {raw_target}")
    if verbose:
        for filename, symbol in sorted(anchors):
            line = cache.get(repo / filename, {}).get(symbol)
            print(f"{filename}:{line or '?'} :: {symbol}")
    print(
        f"Audited {len(documents)} Markdown documents, {len(anchors)} unique Python "
        f"symbol anchors in {len(cache)} source files, and {local_links} local links."
    )
    print("Scope: source existence, AST declarations and local-link existence only.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    skill = Path(__file__).resolve().parents[1]
    repo = args.repo.resolve() if args.repo is not None else find_repo(skill)
    if not (repo / "src" / "cevns_pyeft").is_dir():
        parser.error("--repo must contain src/cevns_pyeft")
    errors = audit_frontmatter(skill) + audit(repo, skill, args.verbose)
    for error in sorted(set(errors)):
        print("ERROR:", error)
    if errors:
        return 1
    print("PASS: plain frontmatter, documented source anchors and local links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
