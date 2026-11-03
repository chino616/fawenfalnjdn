"""Git/snapshot impact plans and explicit inventory synchronization."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('readme_maintenance_tests', REPO / 'tools/readme_maintenance.py')
maintenance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(maintenance)


class RepositoryMaintenanceRoutingTests(unittest.TestCase):
    def test_request_contract_accepts_primary_and_supporting_maintenance_route(self):
        import jsonschema
        schema = json.loads((REPO / 'workflows/_shared/schemas/request.schema.yaml').read_text(encoding='utf-8'))
        request = {'request_kind': 'repository_maintenance', 'request_text': 'maintain README after cleanup',
                   'supporting_routes': ['repository_maintenance']}
        jsonschema.Draft202012Validator(schema).validate(request)

    def test_validator_detects_request_schema_drift_from_route_authority(self):
        spec = importlib.util.spec_from_file_location('maintenance_route_contract',
            REPO / 'workflows/cevns-pyeft/qa/validate_skill_pack.py')
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        original_reader = validator.read_json
        schema_path = REPO / 'workflows/_shared/schemas/request.schema.yaml'
        bad = original_reader(schema_path)
        bad['properties']['request_kind']['enum'].remove('repository_maintenance')
        def without_maintenance(path):
            return bad if path == schema_path else original_reader(path)
        with mock.patch.object(validator, 'read_json', side_effect=without_maintenance):
            errors, _ = validator.validate(REPO)
        self.assertTrue(any(error.startswith('request-schema:') for error in errors))


class ReadmeMaintenanceTests(unittest.TestCase):
    def test_git_nul_records_preserve_rename_spaces_and_unicode(self):
        raw = 'R100\0旧 目录/a.py\0new folder/a.py\0D\0old.txt\0'.encode('utf-8')
        changes = maintenance.parse_name_status(raw)
        self.assertEqual(changes[0], {'status': 'R100', 'old_path': '旧 目录/a.py', 'new_path': 'new folder/a.py'})
        self.assertEqual(changes[1]['new_path'], None)
        with self.assertRaises(maintenance.MaintenanceError):
            maintenance.parse_name_status(b'R100\0only-one-name\0')

    def test_snapshot_detects_unique_move_deletion_and_addition(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'README.md').write_text('[old](old.txt)\n', encoding='utf-8')
            (root / 'old.txt').write_text('same unique content', encoding='utf-8')
            (root / 'gone.txt').write_text('gone content', encoding='utf-8')
            before = maintenance.snapshot(root)
            (root / 'old.txt').rename(root / 'new.txt')
            (root / 'gone.txt').unlink()
            (root / 'added.txt').write_text('new content', encoding='utf-8')
            plan = maintenance.maintenance_plan(root, before=before)
            self.assertEqual(plan['source']['mode'], 'snapshot')
            self.assertEqual({row['status'] for row in plan['changes']}, {'R100', 'D', 'A'})
            self.assertEqual([row['path'] for row in plan['readme_tasks']], ['README.md'])
            self.assertTrue(any(row['old_target'] == 'old.txt' for row in plan['old_path_references']))
            self.assertEqual(len(plan['broken_links']), 1)

    def test_duplicate_hashes_do_not_invent_rename_identity(self):
        before = {'schema_version': 1, 'kind': 'readme-maintenance-snapshot', 'files': {
            'a.txt': {'sha256': 'a' * 64}, 'b.txt': {'sha256': 'a' * 64}}}
        after = {'schema_version': 1, 'kind': 'readme-maintenance-snapshot', 'files': {
            'c.txt': {'sha256': 'a' * 64}, 'd.txt': {'sha256': 'a' * 64}}}
        self.assertEqual([row['status'] for row in maintenance.compare_snapshots(before, after)], ['D', 'D', 'A', 'A'])

    def test_referring_guide_is_separate_from_readme_inventory_targets(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'README.md').write_text('current description\n', encoding='utf-8')
            (root / 'docs').mkdir()
            (root / 'docs/guide.md').write_text('[old](../old.txt)\n', encoding='utf-8')
            (root / 'old.txt').write_text('old input', encoding='utf-8')
            before = maintenance.snapshot(root)
            (root / 'old.txt').unlink()
            plan = maintenance.maintenance_plan(root, before=before)
            self.assertEqual([row['path'] for row in plan['readme_tasks']], ['README.md'])
            self.assertEqual(plan['referring_documents'], ['docs/guide.md'])
            self.assertEqual(plan['broken_links'][0]['file'], 'docs/guide.md')

    def test_many_deletions_share_one_readme_task_and_one_document_scan(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'README.md').write_text('bulk input category\n', encoding='utf-8')
            for index in range(50):
                (root / f'input_{index}.txt').write_text(str(index), encoding='utf-8')
            before = maintenance.snapshot(root)
            for index in range(50):
                (root / f'input_{index}.txt').unlink()
            plan = maintenance.maintenance_plan(root, before=before)
            self.assertEqual(plan['change_count'], 50)
            self.assertEqual(len(plan['readme_tasks']), 1)
            self.assertEqual(plan['reverse_reference_documents_read_once'], 1)

    def test_archive_boundary_move_keeps_the_current_directory_change(self):
        changes = [
            {'status': 'R100', 'old_path': 'active.txt', 'new_path': 'backup/active.txt'},
            {'status': 'R100', 'old_path': 'backup/restored.txt', 'new_path': 'restored.txt'},
            {'status': 'M', 'old_path': 'backup/old.txt', 'new_path': 'backup/old.txt'},
        ]
        scoped = maintenance.scope_changes(changes)
        self.assertEqual([item['status'] for item in scoped], ['D', 'A'])
        self.assertEqual(scoped[0]['old_path'], 'active.txt')
        self.assertEqual(scoped[1]['new_path'], 'restored.txt')

    def test_inventory_sync_preserves_manual_bytes_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            readme = root / 'README.md'
            original = b'\xef\xbb\xbf# Manual title\r\n\r\nKeep this explanation.\r\n'
            readme.write_bytes(original)
            (root / 'one.txt').write_text('first', encoding='utf-8')
            first = maintenance.sync_readmes(root, ['README.md'])
            self.assertEqual(first['check']['status'], 'PASS')
            self.assertTrue(readme.read_bytes().startswith(original))
            backup = root / first['updated_readmes'][0]['backup']
            self.assertEqual(backup.read_bytes(), original)
            self.assertEqual(maintenance.sync_readmes(root, ['README.md'])['status'], 'UNCHANGED')
            (root / 'one.txt').unlink()
            (root / 'two.txt').write_text('second', encoding='utf-8')
            self.assertEqual(maintenance.check_readmes(root, ['README.md'])['status'], 'NEEDS_UPDATE')
            second = maintenance.sync_readmes(root, ['README.md'])
            self.assertEqual(second['check']['status'], 'PASS')
            self.assertTrue(readme.read_bytes().startswith(original))
            self.assertNotIn('[one.txt]', readme.read_text(encoding='utf-8'))
            self.assertIn('[two.txt]', readme.read_text(encoding='utf-8'))

    def test_invalid_markers_prevent_all_target_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first = root / 'README.md'
            first.write_text('manual\n', encoding='utf-8')
            sub = root / 'sub'
            sub.mkdir()
            (sub / 'README.md').write_text(maintenance.BEGIN + '\nmissing end\n', encoding='utf-8')
            before = first.read_bytes()
            with self.assertRaises(maintenance.MaintenanceError):
                maintenance.sync_readmes(root, ['README.md', 'sub/README.md'])
            self.assertEqual(first.read_bytes(), before)
            self.assertFalse((root / 'backup').exists())

    def test_unmanaged_readme_does_not_pass_inventory_check(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'README.md').write_text('manual description\n', encoding='utf-8')
            result = maintenance.check_readmes(root, ['README.md'])
            self.assertEqual(result['status'], 'NEEDS_UPDATE')
            self.assertEqual(result['readmes'][0]['inventory'], 'NOT_MANAGED')

    def test_snapshot_excludes_archives_outputs_and_frozen_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'README.md').write_text('current\n', encoding='utf-8')
            for name in ('backup', 'outputs', '.git', 'tests/reference', 'workflows/project/runs/dataset', 'docs/experiment/reviews'):
                path = root / name
                path.mkdir(parents=True)
                (path / 'evidence.txt').write_text('keep historical content', encoding='utf-8')
            self.assertEqual(set(maintenance.snapshot(root)['files']), {'README.md'})

    def test_escaped_and_archived_sync_targets_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(maintenance.MaintenanceError):
                maintenance.sync_readmes(root, ['../README.md'])
            with self.assertRaises(maintenance.MaintenanceError):
                maintenance.sync_readmes(root, ['backup/README.md'])


@unittest.skipUnless(shutil.which('git'), 'Git executable unavailable')
class ActualGitMaintenanceTests(unittest.TestCase):
    def command(self, root, *arguments):
        environment = os.environ.copy()
        environment.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_OPTIONAL_LOCKS='0')
        result = subprocess.run(['git', '-C', str(root), *arguments], env=environment,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))
        return result.stdout

    def initialize(self, root):
        self.command(root, 'init', '--quiet', '--template=')
        self.command(root, 'config', 'core.autocrlf', 'false')

    def commit_fixture(self, root):
        self.command(root, 'add', '.')
        self.command(root, '-c', 'user.name=Temporary test fixture', '-c', 'user.email=fixture@example.invalid',
                     '-c', 'core.hooksPath=.no-hooks', 'commit', '--quiet', '-m', 'synthetic fixture baseline')

    def test_real_git_plan_merges_staged_unstaged_untracked_and_deleted_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.initialize(root)
            (root / 'README.md').write_text('[folder](sub/README.md)\n', encoding='utf-8')
            sub = root / 'sub'
            sub.mkdir()
            (sub / 'README.md').write_text('[old](old.py)\n', encoding='utf-8')
            for name, content in [('old.py', 'original\n'), ('gone.txt', 'remove\n'), ('modified.txt', 'before\n')]:
                (sub / name).write_text(content, encoding='utf-8')
            self.commit_fixture(root)
            self.command(root, 'mv', 'sub/old.py', 'sub/new name.py')
            (sub / 'gone.txt').unlink()
            (sub / 'modified.txt').write_text('after\n', encoding='utf-8')
            (sub / 'new untracked.txt').write_text('not staged\n', encoding='utf-8')
            index_before = (root / '.git/index').read_bytes()
            plan = maintenance.maintenance_plan(root)
            self.assertEqual({row['status'][0] for row in plan['changes']}, {'R', 'D', 'M', 'A'})
            self.assertEqual({row['path'] for row in plan['readme_tasks']}, {'README.md', 'sub/README.md'})
            self.assertTrue(any(row['kind'] == 'link' and row['old_target'] == 'sub/old.py' for row in plan['old_path_references']))
            self.assertEqual((root / '.git/index').read_bytes(), index_before)

    def test_git_project_subdirectory_does_not_include_sibling_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.initialize(root)
            project = root / 'project'
            project.mkdir()
            (project / 'README.md').write_text('project\n', encoding='utf-8')
            (root / 'outside.txt').write_text('before\n', encoding='utf-8')
            self.commit_fixture(root)
            (root / 'outside.txt').write_text('after\n', encoding='utf-8')
            (project / 'new.txt').write_text('new\n', encoding='utf-8')
            plan = maintenance.maintenance_plan(project)
            self.assertEqual([row['new_path'] for row in plan['changes']], ['new.txt'])
            self.assertEqual(plan['source']['project_prefix'], 'project/')

    def test_plain_folder_is_not_initialized_by_git_plan(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'README.md').write_text('folder\n', encoding='utf-8')
            with self.assertRaises(maintenance.MaintenanceError):
                maintenance.maintenance_plan(root)
            self.assertFalse((root / '.git').exists())


if __name__ == '__main__':
    unittest.main()
