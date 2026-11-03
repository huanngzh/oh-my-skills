#!/usr/bin/env python3
"""Create a fictional, isolated four-stage project. Never starts real work."""
import argparse
from pathlib import Path
import project as p


def create(root):
    p.require(not root.exists(), 'Demo directory must not exist')
    root.mkdir(parents=True)
    p.init(root, 'Main collaboration · Fictional demo', 'Validate inputs → implement → evaluate → deliver. One Main connects stages, evidence, and next steps.', 'demo-main')
    specs = [('S01', 'Input and plan preflight', 'Confirm inputs support implementation', 'Freeze inputs and run a minimal example'), ('S02', 'Implementation', 'Turn an accepted plan into a working artifact', 'Executor implements independently and records recovery'), ('S03', 'Integration and evaluation', 'Check artifacts against project goals', 'Compare outputs under fixed acceptance criteria'), ('S04', 'Optional exploration', 'Explore possible next directions', 'Wait for the user to review results')]
    for sid, title, purpose, method in specs:
        p.add_stage(root, sid, title, purpose, method)
    base = root / '.orchestrator'
    evidence = base / 'receipts' / 'demo-smoke.json'
    p.write_json(evidence, {'fictional_demo': True, 'result': 'PASS', 'note': 'Synthetic example; no real test/job was run.'})
    acceptance = base / 'acceptance' / 'S01.md'
    acceptance.write_text('# Fictional Main acceptance example\n\nStructure demonstration only; no proof of real completed work.\n', encoding='utf-8')
    handoff = base / 'handoffs' / 'S01.md'
    handoff.write_text('# Fictional handoff\n\nThe demo freezes an input contract for the next implementation stage.\n', encoding='utf-8')
    import json
    stages = {}
    for sid, *_ in specs:
        stages[sid] = json.loads((base / 'stages' / (sid + '.json')).read_text(encoding='utf-8'))
    stages['S01'].update(status='DONE', owner='demo-executor-1', finding='Demo gate passed; synthetic data is not a real experiment result.', limitations='Demonstrates state and evidence structure only.', next_action='Hand off to S02.', handoff=str(handoff.relative_to(root)), gates=[{'criterion': 'Demo input smoke', 'status': 'PASS', 'evidence_ids': ['smoke']}], evidence=[{'id': 'smoke', 'label': 'Fictional smoke record', 'path': str(evidence.relative_to(root)), 'sha256': p.sha(evidence)}], acceptance={'decision': 'ACCEPT', 'by': 'demo-main', 'at': p.now(), 'record': str(acceptance.relative_to(root)), 'sha256': p.sha(acceptance)})
    stages['S02'].update(status='IN_PROGRESS', owner='demo-executor-2', depends_on=['S01'], finding='Demo: implementation in progress; final acceptance pending.', next_action='Complete artifacts and gate evidence for Main acceptance.', gates=[{'criterion': 'End-to-end example passes', 'status': 'PENDING', 'evidence_ids': []}])
    stages['S03'].update(depends_on=['S02'], next_action='Wait for S02 acceptance, then freeze evaluation inputs.')
    stages['S04'].update(status='PAUSED_USER', blocker='Fictional user requests a review of current results first.', resume_condition='User explicitly resumes optional exploration.', next_action='Keep paused.')
    for sid, s in stages.items():
        p.write_json(base / 'stages' / (sid + '.json'), s)
    config = json.loads((base / 'project.json').read_text(encoding='utf-8'))
    config['paused_stage_ids'] = ['S04']
    p.write_json(base / 'project.json', config)
    return p.build(root)


if __name__ == '__main__':
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    print(json.dumps(create(parser.parse_args().root.resolve()), ensure_ascii=False, indent=2))
