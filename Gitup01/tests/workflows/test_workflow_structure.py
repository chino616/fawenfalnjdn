"""Workflow invariants and adverse edits, without runtime/physics imports."""
import copy
import importlib.util
import tempfile
import unittest
from unittest import mock
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('workflow_validator', REPO / 'workflows/cevns-pyeft/qa/validate_skill_pack.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class WorkflowStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = validator.read_json(REPO / 'workflows/catalog.yaml')
        cls.routes = validator.read_json(REPO / validator.PROJECT / 'router/routes.yaml')
        cls.definitions = {}
        for path in (REPO / validator.PROJECT / 'definitions').glob('*/WORKFLOW.md'):
            meta = validator.definition_metadata(path)
            cls.definitions[meta['workflow_id']] = (path, meta)

    def test_complete_pack(self):
        errors, summary = validator.validate(REPO)
        self.assertEqual(errors, [])
        self.assertEqual(summary['skills'], 17)

    def test_duplicate_identity(self):
        bad = copy.deepcopy(self.catalog)
        bad['skills'].append(copy.deepcopy(bad['skills'][0]))
        self.assertTrue(any('duplicate/missing ID' in e for e in validator.check_catalog(REPO, bad)))

    def test_path_escape(self):
        bad = copy.deepcopy(self.catalog)
        bad['skills'][0]['path'] = '../AGENTS.md'
        self.assertTrue(any('escapes workflows' in e for e in validator.check_catalog(REPO, bad)))

    def test_unregistered_skill(self):
        bad = copy.deepcopy(self.catalog)
        bad['skills'].pop()
        self.assertTrue(any('unregistered' in e for e in validator.check_catalog(REPO, bad)))

    def test_phase_mapping(self):
        bad = copy.deepcopy(self.catalog)
        phases = [e for e in bad['skills'] if e.get('phase')]
        phases[0]['phase'] = phases[1]['phase']
        self.assertTrue(any(e.startswith('phase:') for e in validator.check_catalog(REPO, bad)))

    def test_unknown_route_target(self):
        bad = copy.deepcopy(self.routes)
        bad['routes'][0]['workflow'] = 'cevns.nonexistent'
        self.assertTrue(any('workflow target' in e for e in validator.check_routes(REPO, self.catalog, bad, self.definitions)))

    def test_name_only_onboarding(self):
        bad = copy.deepcopy(self.routes)
        bad['intent_contract']['experiment_name_alone_selects_onboarding'] = True
        self.assertTrue(any('experiment name' in e for e in validator.check_routes(REPO, self.catalog, bad, self.definitions)))

    def test_alias_collision(self):
        bad = copy.deepcopy(self.routes)
        bad['routes'][0]['aliases'].append(bad['routes'][1]['request_kind'])
        self.assertTrue(any('alias collision' in e for e in validator.check_routes(REPO, self.catalog, bad, self.definitions)))

    def test_unknown_workflow_skill(self):
        bad = copy.deepcopy(self.definitions)
        next(iter(bad.values()))[1]['skills'].append('cevns.physics.unimplemented')
        self.assertTrue(any('unknown Skill' in e for e in validator.check_routes(REPO, self.catalog, self.routes, bad)))

    def test_cycles_and_missing_handoffs(self):
        self.assertTrue(any('cycle' in e for e in validator.graph_errors({'a': ['b'], 'b': ['a']}, 'workflow')))
        self.assertTrue(any('unknown target' in e for e in validator.graph_errors({'a': ['missing']}, 'workflow')))

    def test_master_recursive_dispatch(self):
        bad = copy.deepcopy(self.definitions)
        next(iter(bad.values()))[1]['skills'].append('cevns.router.experiment')
        self.assertTrue(any('recursive dispatch' in e for e in validator.check_routes(REPO, self.catalog, self.routes, bad)))

    def test_broken_link_and_stale_path(self):
        with tempfile.TemporaryDirectory(prefix='workflow-check-') as folder:
            root = Path(folder)
            doc = root / 'example.md'
            doc.write_text('[missing](absent.md)\nworkflows/experiment-integration/skills/x/SKILL.md\n', 'utf-8')
            errors = validator.check_links(root, [doc], {'retained_paths': []})
            self.assertTrue(any(e.startswith('link:') for e in errors))
            self.assertTrue(any('stale active' in e for e in errors))

    def test_duplicate_record_keys(self):
        with tempfile.TemporaryDirectory(prefix='workflow-json-') as folder:
            path = Path(folder) / 'bad.yaml'
            path.write_text('{"skills": [], "skills": []}', 'utf-8')
            with self.assertRaises(ValueError):
                validator.read_json(path)

    def test_protected_fingerprints(self):
        self.assertEqual(validator.protected_errors(REPO), [])

    def test_machine_configuration_is_read_from_tools(self):
        expected = {
            REPO / 'tools/workflow_validation/config/PROTECTED_FILES.json',
            REPO / 'tools/workflow_validation/config/HISTORICAL_PATH_EXCEPTIONS.json',
        }
        self.assertTrue(all(path.is_file() for path in expected))
        with mock.patch.object(validator, 'read_json', wraps=validator.read_json) as reader:
            validator.validate(REPO)
        paths = {call.args[0] for call in reader.call_args_list}
        self.assertTrue(expected.issubset(paths))
        self.assertFalse(any(path.is_relative_to(REPO / 'docs') for path in paths))

    def test_missing_machine_configuration_does_not_use_old_docs_copy(self):
        original_reader = validator.read_json
        for filename, check in [
            ('PROTECTED_FILES.json', validator.protected_errors),
            ('HISTORICAL_PATH_EXCEPTIONS.json', validator.validate),
        ]:
            missing = REPO / 'tools/workflow_validation/config' / filename
            def without_config(path):
                if path == missing:
                    raise FileNotFoundError(path)
                return original_reader(path)
            with self.subTest(filename=filename):
                with mock.patch.object(validator, 'read_json', side_effect=without_config):
                    with self.assertRaises(FileNotFoundError):
                        check(REPO)


if __name__ == '__main__':
    unittest.main()
