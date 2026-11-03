"""Actual file changes and scoped README-link checks; no physics imports."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('lifecycle_doc_validator', REPO / 'tools/validate_docs.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class DocumentLifecycleTests(unittest.TestCase):
    def test_deleting_a_linked_file_is_reported_without_modifying_readme(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            readme = root / 'README.md'
            readme.write_text('[script](script.py)\n', encoding='utf-8')
            script = root / 'script.py'
            script.write_text('pass\n', encoding='utf-8')
            self.assertEqual(validator.audit(root, files=['README.md'])['broken_current_links'], [])
            script.unlink()
            before = readme.read_bytes()
            report = validator.audit(root, files=['README.md'])
            self.assertEqual(len(report['broken_current_links']), 1)
            self.assertEqual(report['broken_current_links'][0]['target'], 'script.py')
            self.assertEqual(readme.read_bytes(), before)

    def test_rename_requires_corresponding_readme_link_update(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            readme = root / 'README.md'
            old = root / 'old.txt'
            old.write_text('existing data', encoding='utf-8')
            readme.write_text('[input](old.txt)\n', encoding='utf-8')
            old.rename(root / 'new.txt')
            self.assertEqual(len(validator.audit(root, files=[readme])['broken_current_links']), 1)
            readme.write_text('[input](new.txt)\n', encoding='utf-8')
            self.assertEqual(validator.audit(root, files=[readme])['broken_current_links'], [])

    def test_explicit_files_override_docs_scope_and_deduplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'docs').mkdir()
            (root / 'docs/broken.md').write_text('[missing](absent.txt)\n', encoding='utf-8')
            readme = root / 'README.md'
            readme.write_text('owning directory description\n', encoding='utf-8')
            report = validator.audit(root, scope='docs', files=['README.md', readme])
            self.assertEqual(report['scope'], 'files')
            self.assertEqual(report['selected_documents'], ['README.md'])
            self.assertEqual(report['broken_current_links'], [])

    def test_explicit_outside_archive_and_missing_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            outer = Path(folder)
            root = outer / 'repo'
            root.mkdir()
            (outer / 'outside.md').write_text('outside', encoding='utf-8')
            (root / 'backup').mkdir()
            (root / 'backup/README.md').write_text('archive', encoding='utf-8')
            for target in ('../outside.md', 'backup/README.md', 'missing.md'):
                with self.subTest(target=target), self.assertRaises(ValueError):
                    validator.audit(root, files=[target])

    def test_directory_walk_prunes_archive_and_outputs_before_visiting(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'README.md').write_text('current entry\n', encoding='utf-8')
            for name in ('backup', 'outputs', '.git', '__pycache__'):
                (root / name).mkdir()
                (root / name / 'old.md').write_text('[stale](missing)\n', encoding='utf-8')
            original_walk = validator.os.walk
            visited = []
            def tracked_walk(*args, **kwargs):
                for parent, directories, filenames in original_walk(*args, **kwargs):
                    visited.append(Path(parent).relative_to(root).as_posix())
                    yield parent, directories, filenames
            with mock.patch.object(validator.os, 'walk', side_effect=tracked_walk):
                report = validator.audit(root, scope='all')
            self.assertEqual(visited, ['.'])
            self.assertEqual(report['selected_documents'], ['README.md'])
            self.assertEqual(report['broken_current_links'], [])


if __name__ == '__main__':
    unittest.main()
