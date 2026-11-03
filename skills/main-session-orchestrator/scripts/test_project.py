#!/usr/bin/env python3
"""Behavioral checks in disposable directories; no network or live project writes."""
import json
from pathlib import Path
import tempfile
import unittest
import project as p
import demo


class ProjectChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'project'
        demo.create(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def edit(self, relative, callback):
        path = self.root / '.orchestrator' / relative
        obj = json.loads(path.read_text(encoding='utf-8'))
        callback(obj)
        p.write_json(path, obj)

    def reject(self, message):
        with self.assertRaisesRegex(ValueError, message):
            p.validate(self.root)

    def test_complete_demo_and_offline_build(self):
        self.assertTrue(p.audit(self.root)['ok'])
        self.assertEqual(p.validate(self.root)[3]['stages'], 4)

    def test_no_overwrite_existing_project(self):
        old = (self.root / '.orchestrator/project.json').read_bytes()
        with self.assertRaises(ValueError):
            p.init(self.root, 'other', 'other', 'other')
        self.assertEqual(old, (self.root / '.orchestrator/project.json').read_bytes())

    def test_missing_evidence(self):
        (self.root / '.orchestrator/receipts/demo-smoke.json').unlink()
        self.reject('missing evidence')

    def test_evidence_tamper(self):
        (self.root / '.orchestrator/receipts/demo-smoke.json').write_text('changed')
        self.reject('hash mismatch')

    def test_false_done(self):
        self.edit('stages/S02.json', lambda s: s.update(status='DONE'))
        self.reject('passed gates')

    def test_wrong_acceptor(self):
        self.edit('stages/S01.json', lambda s: s['acceptance'].update(by='executor'))
        self.reject('Main acceptance')

    def test_pause_conflict(self):
        self.edit('stages/S04.json', lambda s: s.update(status='READY'))
        self.reject('conflicts with project pause')

    def test_dependency_cycle(self):
        self.edit('stages/S03.json', lambda s: s.update(depends_on=['S04']))
        self.edit('stages/S04.json', lambda s: s.update(depends_on=['S03']))
        self.reject('Dependency cycle')

    def test_incomplete_dependency(self):
        self.edit('stages/S03.json', lambda s: s.update(status='READY'))
        self.reject('dependency not DONE')

    def test_duplicate_dispatch(self):
        for sid in ('S02', 'S03'):
            self.edit('stages/' + sid + '.json', lambda s: s.update(dispatches=[{'key': 'same', 'status': 'INTENT'}]))
        self.reject('duplicate/missing dispatch key')

    def test_unknown_dispatch_not_candidate(self):
        self.edit('project.json', lambda s: s.update(autonomy='BOUNDED', authorization_source='Synthetic test only', authorized_stage_ids=['S02']))
        self.edit('stages/S02.json', lambda s: s.update(status='READY', dispatches=[{'key': 'test/S02/1', 'status': 'UNKNOWN'}]))
        self.assertEqual(p.validate(self.root)[3]['ready_for_main_review'], [])

    def test_stale_build(self):
        self.edit('stages/S02.json', lambda s: s.update(finding='New evidence'))
        with self.assertRaisesRegex(ValueError, 'Sources changed'):
            p.audit(self.root)

    def test_path_escape(self):
        self.edit('stages/S01.json', lambda s: s['evidence'][0].update(path='../secret'))
        self.reject('escapes project')

    def test_html_text_escaped(self):
        self.edit('stages/S02.json', lambda s: s.update(title='<img src=x onerror=alert(1)>'))
        p.build(self.root)
        markup = (self.root / '.orchestrator/web/report.html').read_text(encoding='utf-8')
        self.assertNotIn('<img src=x', markup)
        self.assertIn('&lt;img src=x', markup)

    def test_unsafe_url(self):
        self.edit('stages/S02.json', lambda s: s.update(evidence=[{'id': 'bad', 'label': 'bad', 'url': 'javascript:alert(1)', 'checked_at': p.now(), 'verification': 'test'}]))
        self.reject('URL must be')

    def test_live_job_prevents_done(self):
        self.edit('stages/S01.json', lambda s: s.update(jobs=[{'id': 'test-job', 'status': 'RUNNING', 'checked_at': p.now()}]))
        self.reject('unresolved jobs')


if __name__ == '__main__':
    unittest.main(verbosity=2)
