"""Catalog-backed Skill tables: lifecycle, stale detection and bounded writes."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[2]


def module_at(name, relative):
    spec = importlib.util.spec_from_file_location(name, REPO / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


library = module_at('skill_library_tests', 'tools/update_skill_library.py')
validator = module_at('skill_library_pack_tests', 'workflows/cevns-pyeft/qa/validate_skill_pack.py')


class SkillLibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='skill-library-')
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve()
        self.catalog = {'schema_version': 1, 'skills': []}
        self.add_skill('cevns.router.experiment', 'test-master', 'router')
        self.add_skill('cevns.engineering.example', 'test-example')
        self.write_catalog()
        self.routes = self.repo / 'workflows/cevns-pyeft/router/routes.yaml'
        self.routes.parent.mkdir(parents=True)
        self.routes.write_text(json.dumps({'entry_skill': 'cevns.router.experiment'}), 'utf-8')
        self.workflow = self.repo / 'workflows/cevns-pyeft/definitions/example/WORKFLOW.md'
        self.workflow.parent.mkdir(parents=True)
        self.set_callers(['cevns.engineering.example'])
        self.doc = self.repo / library.DOCUMENT
        self.doc.parent.mkdir(parents=True)
        self.doc.write_text('# Manual introduction\n\n' + library.BEGIN + '\nold table\n' + library.END
                            + '\n\nManual add/remove rules.\n', 'utf-8')

    def add_skill(self, sid, name, kind='engineering'):
        relative = f'cevns-pyeft/skills/{kind}/{name}/SKILL.md'
        path = self.repo / 'workflows' / relative
        path.parent.mkdir(parents=True)
        path.write_text(f'---\nname: {name}\ndescription: Synthetic example.\n---\n', 'utf-8')
        self.catalog['skills'].append({'id': sid, 'name': name, 'kind': kind, 'path': relative,
                                       'status': 'active', 'summary_zh': '合成职责', 'outputs_zh': '合成产物'})
        return path

    def write_catalog(self):
        path = self.repo / 'workflows/catalog.yaml'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.catalog, ensure_ascii=False), 'utf-8')

    def set_callers(self, skills):
        meta = {'workflow_id': 'cevns.example', 'skills': skills, 'handoffs': []}
        self.workflow.write_text('# Example\n\n<!-- workflow-metadata: test -->\n```json\n'
                                 + json.dumps(meta) + '\n```\n', 'utf-8')

    def test_check_is_read_only_and_detects_stale_table(self):
        before = {p.relative_to(self.repo): p.read_bytes() for p in self.repo.rglob('*') if p.is_file()}
        self.assertTrue(any('table is stale' in e for e in library.check_library(self.repo)))
        after = {p.relative_to(self.repo): p.read_bytes() for p in self.repo.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_refresh_preserves_manual_bytes_and_records_backup(self):
        before = self.doc.read_bytes().replace(b'\n', b'\r\n')
        self.doc.write_bytes(b'\xef\xbb\xbf' + before)
        before = self.doc.read_bytes()
        result = library.sync_library(self.repo)
        self.assertEqual(result['status'], 'UPDATED')
        self.assertEqual((self.repo / result['backup']).read_bytes(), before)
        self.assertIn(result['backup'], (self.repo / 'backup/BACKUP_MANIFEST.md').read_text('utf-8'))
        after = self.doc.read_bytes()
        self.assertEqual(before.split(library.BEGIN.encode())[0], after.split(library.BEGIN.encode())[0])
        self.assertEqual(before.split(library.END.encode())[1], after.split(library.END.encode())[1])
        self.assertNotIn(b'\n', after.replace(b'\r\n', b''))
        self.assertEqual(library.check_library(self.repo), [])
        self.assertIn('../workflows/cevns-pyeft/definitions/example/WORKFLOW.md', after.decode('utf-8'))
        self.assertIn('routes.entry_skill', after.decode('utf-8'))

    def test_refresh_is_idempotent_without_extra_backups(self):
        library.sync_library(self.repo)
        before = {p.relative_to(self.repo): p.read_bytes() for p in self.repo.rglob('*') if p.is_file()}
        self.assertEqual(library.sync_library(self.repo)['status'], 'UNCHANGED')
        after = {p.relative_to(self.repo): p.read_bytes() for p in self.repo.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_adding_and_removing_registered_skill_changes_table(self):
        library.sync_library(self.repo)
        extra = self.add_skill('cevns.engineering.additional', 'test-additional')
        self.write_catalog()
        self.assertTrue(library.check_library(self.repo))
        library.sync_library(self.repo)
        self.assertIn('cevns.engineering.additional', self.doc.read_text('utf-8'))
        self.assertIn('尚无工作流引用', self.doc.read_text('utf-8'))
        extra.unlink()
        self.catalog['skills'].pop()
        self.write_catalog()
        self.assertTrue(library.check_library(self.repo))
        library.sync_library(self.repo)
        self.assertNotIn('cevns.engineering.additional', self.doc.read_text('utf-8'))
        self.assertEqual(library.check_library(self.repo), [])

    def test_status_and_display_updates_are_detected_and_escaped(self):
        library.sync_library(self.repo)
        entry = self.catalog['skills'][1]
        entry.update(status='deprecated', summary_zh='first | second\n<third>', outputs_zh='changed output')
        self.write_catalog()
        self.assertTrue(library.check_library(self.repo))
        library.sync_library(self.repo)
        content = self.doc.read_text('utf-8')
        self.assertIn('**1** 个 deprecated', content)
        self.assertIn(r'first \| second<br>&lt;third&gt;', content)
        self.assertIn('changed output', content)

    def test_changed_workflow_consumers_make_table_stale(self):
        library.sync_library(self.repo)
        self.set_callers([])
        self.assertTrue(any('table is stale' in e for e in library.check_library(self.repo)))
        library.sync_library(self.repo)
        self.assertIn('尚无工作流引用', self.doc.read_text('utf-8'))

    def test_unregistered_skill_is_rejected(self):
        self.add_skill('cevns.engineering.unregistered', 'test-unregistered')
        self.assertTrue(any('discovery mismatch' in e for e in library.check_library(self.repo)))

    def test_missing_skill_file_is_rejected(self):
        (self.repo / 'workflows' / self.catalog['skills'][1]['path']).unlink()
        self.assertTrue(any('missing Skill file' in e for e in library.check_library(self.repo)))

    def test_unmigrated_workflow_reference_blocks_deletion(self):
        entry = self.catalog['skills'].pop()
        (self.repo / 'workflows' / entry['path']).unlink()
        self.write_catalog()
        self.assertTrue(any('unknown Skill' in e for e in library.check_library(self.repo)))
        self.set_callers([])
        library.sync_library(self.repo)
        self.assertEqual(library.check_library(self.repo), [])

    def test_missing_summary_and_duplicate_id_are_rejected(self):
        self.catalog['skills'][1].pop('summary_zh')
        self.write_catalog()
        self.assertTrue(any('summary_zh' in e for e in library.check_library(self.repo)))
        self.catalog['skills'][1]['summary_zh'] = 'Restored'
        self.catalog['skills'][1]['id'] = self.catalog['skills'][0]['id']
        self.write_catalog()
        self.assertTrue(any('duplicate/invalid Skill ID' in e for e in library.check_library(self.repo)))

    def test_path_escape_is_rejected_before_write(self):
        self.catalog['skills'][1]['path'] = '../outside/SKILL.md'
        self.write_catalog()
        before = self.doc.read_bytes()
        with self.assertRaises(library.LibraryError):
            library.sync_library(self.repo)
        self.assertEqual(self.doc.read_bytes(), before)
        self.assertFalse((self.repo / 'backup').exists())

    def test_invalid_markers_fail_without_writing(self):
        for markers in ['', library.END + '\n' + library.BEGIN,
                        library.BEGIN + library.END + library.BEGIN]:
            with self.subTest(markers=markers):
                self.doc.write_text('Manual rules\n' + markers, 'utf-8')
                before = self.doc.read_bytes()
                with self.assertRaises(library.LibraryError):
                    library.sync_library(self.repo)
                self.assertEqual(self.doc.read_bytes(), before)
                self.assertFalse((self.repo / 'backup').exists())

    def test_invalid_workflow_metadata_is_rejected(self):
        self.workflow.write_text('# No machine metadata\n', 'utf-8')
        self.assertTrue(any('missing workflow metadata' in e for e in library.check_library(self.repo)))

    def test_duplicate_registry_keys_are_rejected(self):
        (self.repo / 'workflows/catalog.yaml').write_text('{"skills": [], "skills": []}', 'utf-8')
        self.assertTrue(any('duplicate key' in e for e in library.check_library(self.repo)))

    def test_pack_validator_reports_stale_library(self):
        original = Path.read_bytes
        document = (REPO / library.DOCUMENT).resolve()

        def stale_bytes(path):
            data = original(path)
            if path.resolve() == document:
                data = data.replace(library.BEGIN.encode(), library.BEGIN.encode() + b'\nstale row', 1)
            return data

        with mock.patch.object(Path, 'read_bytes', new=stale_bytes):
            errors, _ = validator.validate(REPO)
        self.assertTrue(any('skill-library: table is stale' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
