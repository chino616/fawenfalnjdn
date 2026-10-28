"""Recovery-only backups for this engineering migration (not physics inputs)."""
from pathlib import Path
import hashlib
import shutil

ROOT = Path(__file__).resolve().parents[1]
_saved = set()
def write(relative, content):
    path = ROOT / relative
    if path.exists() and relative not in _saved:
        dest = ROOT / 'backup' / relative
        if dest.exists():
            dest = ROOT / 'backup/experiment_modularization_20261028' / relative
            n = 1
            while dest.exists():
                dest = ROOT / f'backup/experiment_modularization_20261028_r{n}' / relative
                n += 1
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        manifest = ROOT / 'backup/BACKUP_MANIFEST.md'
        with manifest.open('a', encoding='utf-8') as stream:
            stream.write(f'\n- Experiment modularization: `{relative}` → `{dest.relative_to(ROOT)}`; SHA256 {hashlib.sha256(path.read_bytes()).hexdigest()}\n')
        _saved.add(relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def edit(relative, old, new):
    s = (ROOT / relative).read_text(encoding='utf-8-sig')
    if old not in s:
        raise ValueError(f'Expected text absent: {relative}: {old[:90]}')
    write(relative, s.replace(old, new))
