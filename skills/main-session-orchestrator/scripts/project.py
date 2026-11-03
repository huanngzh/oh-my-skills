#!/usr/bin/env python3
"""Local orchestration records and static dashboard. Python 3.9+, stdlib only.
Never dispatches jobs, sends messages, schedules work, or publishes anything.
"""
import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

STATES = ('TODO', 'READY', 'IN_PROGRESS', 'BLOCKED', 'PAUSED_USER', 'DONE')
ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inside(root, value):
    require(isinstance(value, str) and value and not Path(value).is_absolute(), 'Expected project-relative path')
    path = (root / value).resolve()
    require(path.is_relative_to(root.resolve()), 'Path escapes project: ' + value)
    return path


def timestamp(value):
    try:
        return bool(datetime.fromisoformat(value.replace('Z', '+00:00')).tzinfo)
    except (TypeError, ValueError, AttributeError):
        return False


def valid_url(value):
    try:
        u = urlsplit(value)
        return u.scheme in ('http', 'https') and bool(u.hostname) and not u.username and not u.password and not u.query and not any(c.isspace() for c in value)
    except ValueError:
        return False


def snapshot(root):
    base = root / '.orchestrator'
    paths = [base / 'project.json'] + sorted((base / 'stages').glob('*.json'))
    raw = {str(p.relative_to(root)): p.read_bytes() for p in paths}
    project = json.loads(raw['.orchestrator/project.json'])
    stages = [json.loads(raw[str(p.relative_to(root))]) for p in paths[1:]]
    return project, stages, {k: hashlib.sha256(v).hexdigest() for k, v in raw.items()}


def validate(root):
    project, stages, sources = snapshot(root)
    for key in ('name', 'goal', 'main_owner', 'verified_at', 'autonomy', 'charter'):
        require(project.get(key), 'Project missing ' + key)
    require(project.get('schema_version') == 1, 'Unsupported schema_version')
    require(timestamp(project['verified_at']), 'project.verified_at needs timezone')
    require(project['autonomy'] in ('MANUAL', 'BOUNDED'), 'autonomy must be MANUAL or BOUNDED')
    require(isinstance(project.get('paused_stage_ids'), list), 'paused_stage_ids must be a list')
    require(isinstance(project.get('authorized_stage_ids'), list), 'authorized_stage_ids must be a list')
    require(isinstance(project.get('max_parallel'), int) and project['max_parallel'] > 0, 'max_parallel must be positive')
    charter = inside(root, project['charter'])
    require(charter.is_file(), 'Missing charter')
    sources[project['charter']] = sha(charter)
    if project['autonomy'] == 'BOUNDED':
        require(project.get('authorization_source'), 'BOUNDED needs actual user authorization source')
    ids = [s.get('id') for s in stages]
    require(len(set(ids)) == len(ids), 'Duplicate stage IDs')
    by_id = dict(zip(ids, stages))
    for key in ('paused_stage_ids', 'authorized_stage_ids'):
        require(set(project[key]) <= set(ids), key + ' contains unknown stage')
    dispatch_keys = set()
    for s in stages:
        sid = s.get('id')
        require(isinstance(sid, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', sid), 'Invalid stage ID')
        for key in ('title', 'purpose', 'method', 'status', 'verified_at'):
            require(s.get(key), sid + ' missing ' + key)
        require(s['status'] in STATES, sid + ' invalid status')
        require(timestamp(s['verified_at']), sid + ' verified_at needs timezone')
        deps = s.get('depends_on')
        require(isinstance(deps, list) and set(deps) <= set(ids) and sid not in deps, sid + ' invalid dependencies')
        if s['status'] in ('READY', 'IN_PROGRESS', 'DONE'):
            require(all(by_id[d]['status'] == 'DONE' for d in deps), sid + ' dependency not DONE')
        if sid in project['paused_stage_ids']:
            require(s['status'] == 'PAUSED_USER', sid + ' conflicts with project pause')
        if s['status'] in ('IN_PROGRESS', 'DONE'):
            require(s.get('owner'), sid + ' needs actual owner')
        if s['status'] != 'DONE':
            require(s.get('next_action'), sid + ' needs next_action')
        if s['status'] in ('BLOCKED', 'PAUSED_USER'):
            require(s.get('blocker') and s.get('resume_condition'), sid + ' needs blocker and resume_condition')
        for key in ('brief', 'handoff'):
            if s.get(key):
                p = inside(root, s[key])
                require(p.is_file(), sid + ' missing ' + key)
                sources[s[key]] = sha(p)
        if s['status'] in ('READY', 'IN_PROGRESS', 'DONE'):
            require(s.get('brief'), sid + ' needs brief')
        evidence = s.get('evidence', [])
        require(isinstance(evidence, list), sid + ' evidence must be list')
        evidence_ids = [e.get('id') for e in evidence]
        require(all(evidence_ids) and len(set(evidence_ids)) == len(evidence_ids) if evidence else True, sid + ' invalid evidence IDs')
        for e in evidence:
            require(e.get('label'), sid + ' evidence needs label')
            require(bool(e.get('path')) != bool(e.get('url')), sid + ' evidence needs exactly one path/url')
            if e.get('path'):
                p = inside(root, e['path'])
                require(p.is_file(), sid + ' missing evidence ' + e['path'])
                digest = sha(p)
                require(e.get('sha256') == digest, sid + ' evidence hash mismatch: ' + e['path'])
                sources[e['path']] = digest
            else:
                require(valid_url(e['url']), sid + ' URL must be http(s), without credentials or query tokens')
                require(timestamp(e.get('checked_at')), sid + ' URL evidence needs checked_at')
                require(e.get('verification'), sid + ' URL evidence needs verification scope')
        gates = s.get('gates', [])
        require(isinstance(gates, list), sid + ' gates must be list')
        for g in gates:
            require(g.get('criterion') and g.get('status') in ('PENDING', 'PASS', 'FAIL'), sid + ' invalid gate')
            if g['status'] == 'PASS':
                require(g.get('evidence_ids') and set(g['evidence_ids']) <= set(evidence_ids), sid + ' PASS gate lacks evidence')
        for job in s.get('jobs', []):
            require(job.get('id') and job.get('status') in ('UNKNOWN', 'QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'STOPPED'), sid + ' invalid job')
            require(timestamp(job.get('checked_at')), sid + ' job needs checked_at')
        for d in s.get('dispatches', []):
            require(d.get('key') and d['key'] not in dispatch_keys, sid + ' duplicate/missing dispatch key')
            dispatch_keys.add(d['key'])
            require(d.get('status') in ('INTENT', 'UNKNOWN', 'SENT', 'ACKNOWLEDGED', 'CLOSED'), sid + ' invalid dispatch status')
            if d['status'] in ('SENT', 'ACKNOWLEDGED', 'CLOSED'):
                require(d.get('target_id') and d.get('receipt'), sid + ' dispatch needs target ID and receipt')
                receipt = inside(root, d['receipt'])
                require(receipt.is_file(), sid + ' missing dispatch receipt')
                sources[d['receipt']] = sha(receipt)
        if s['status'] == 'DONE':
            require(gates and all(g['status'] == 'PASS' for g in gates), sid + ' DONE requires passed gates')
            require(s.get('handoff') and s.get('finding'), sid + ' DONE requires handoff and finding')
            require(all(j['status'] in ('SUCCEEDED', 'STOPPED') for j in s.get('jobs', [])), sid + ' DONE has unresolved jobs')
            require(all(d['status'] == 'CLOSED' for d in s.get('dispatches', [])), sid + ' DONE has unresolved dispatches')
            a = s.get('acceptance', {})
            require(a.get('decision') == 'ACCEPT' and a.get('by') == project['main_owner'] and timestamp(a.get('at')), sid + ' DONE needs Main acceptance')
            record = inside(root, a.get('record', ''))
            require(record.is_file() and a.get('sha256') == sha(record), sid + ' acceptance record missing/changed')
            sources[a['record']] = sha(record)
    visiting, visited = set(), set()
    def visit(sid):
        require(sid not in visiting, 'Dependency cycle at ' + sid)
        if sid in visited:
            return
        visiting.add(sid)
        for dep in by_id[sid]['depends_on']:
            visit(dep)
        visiting.remove(sid)
        visited.add(sid)
    for sid in ids:
        visit(sid)
    active = sum(s['status'] == 'IN_PROGRESS' for s in stages)
    warnings = []
    if active > project['max_parallel']:
        warnings.append('IN_PROGRESS count exceeds max_parallel; check actual active work vs awaiting acceptance')
    candidates = [s['id'] for s in stages if s['status'] == 'READY' and s['id'] in project['authorized_stage_ids'] and project['autonomy'] == 'BOUNDED' and not any(d['status'] != 'CLOSED' for d in s.get('dispatches', []))]
    return project, stages, sources, {'ok': True, 'stages': len(stages), 'warnings': warnings, 'ready_for_main_review': candidates, 'note': 'Candidates still require current authorization, resource, owner and dispatch checks; no work was dispatched.'}


def init(root, name, goal, main):
    base = root / '.orchestrator'
    require(root.is_dir(), 'Project root must exist')
    require(not base.exists(), '.orchestrator exists; inspect and merge, do not overwrite')
    base.mkdir()
    for directory in ('stages', 'briefs', 'handoffs', 'acceptance', 'receipts'):
        (base / directory).mkdir()
    shutil.copyfile(ASSETS / 'charter.md', base / 'charter.md')
    write_json(base / 'project.json', {'schema_version': 1, 'name': name, 'goal': goal, 'main_owner': main, 'verified_at': now(), 'autonomy': 'MANUAL', 'authorization_source': '', 'authorized_stage_ids': [], 'paused_stage_ids': [], 'max_parallel': 1, 'charter': '.orchestrator/charter.md'})
    return {'created': str(base), 'note': 'Fill charter and actual authorization before dispatch. Existing AGENTS untouched.'}


def add_stage(root, sid, title, purpose, method):
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', sid), 'Invalid ID')
    base = root / '.orchestrator'
    require((base / 'project.json').is_file(), 'Initialize or use existing project records first')
    path = base / 'stages' / (sid + '.json')
    brief = base / 'briefs' / (sid + '.md')
    require(not path.exists() and not brief.exists(), 'Stage already exists')
    # Exclusive creation avoids overwriting another owner during concurrent setup.
    with brief.open('x', encoding='utf-8') as f:
        f.write((ASSETS / 'stage-brief.md').read_text(encoding='utf-8'))
    with path.open('x', encoding='utf-8') as f:
        json.dump({'id': sid, 'title': title, 'purpose': purpose, 'method': method, 'status': 'TODO', 'owner': '', 'verified_at': now(), 'depends_on': [], 'brief': str(brief.relative_to(root)), 'finding': '', 'limitations': '', 'next_action': 'Complete the brief and acceptance criteria; check dependencies and authorization.', 'blocker': '', 'resume_condition': '', 'gates': [], 'evidence': [], 'jobs': [], 'dispatches': []}, f, ensure_ascii=False, indent=2)
        f.write('\n')
    return {'created': str(path)}


def build(root):
    project, stages, sources, result = validate(root)
    out = root / '.orchestrator' / 'web'
    if out.exists():
        require((out / '.generated-by-main-session-orchestrator').is_file(), 'Output directory ownership unknown')
    else:
        out.mkdir()
    # Export only dashboard fields. Private dispatch receipts and job commands stay local.
    public = {'project': {k: project[k] for k in ('name', 'goal', 'main_owner', 'verified_at', 'autonomy')}, 'generated_at': now(), 'stages': [{k: s.get(k, '') for k in ('id', 'title', 'purpose', 'method', 'status', 'owner', 'verified_at', 'depends_on', 'finding', 'limitations', 'next_action', 'blocker', 'resume_condition', 'evidence')} for s in stages]}
    esc = lambda v: html.escape(str(v), quote=True)
    cards = []
    for s in public['stages']:
        rows = ''.join('<dt>' + label + '</dt><dd>' + esc(s[key] or '—') + '</dd>' for key, label in [('purpose', 'Purpose'), ('method', 'Method'), ('finding', 'Finding'), ('limitations', 'Limitations'), ('next_action', 'Next step'), ('blocker', 'Block / pause'), ('resume_condition', 'Release condition')])
        links = []
        for e in s['evidence']:
            if e.get('url'):
                links.append('<li><a rel="noopener noreferrer" href="' + esc(e['url']) + '">' + esc(e['label']) + '</a></li>')
            else:
                links.append('<li>' + esc(e['label']) + ' <small>Local evidence · ' + esc(e['path']) + '</small></li>')
        cards.append('<article data-status="' + s['status'] + '"><header><span class="badge ' + s['status'] + '">' + s['status'] + '</span><h2>' + esc(s['id'] + ' · ' + s['title']) + '</h2></header><p class="meta">Owner ' + esc(s['owner'] or 'Unassigned') + ' · Verified ' + esc(s['verified_at']) + '</p><p class="meta">Dependencies ' + esc(', '.join(s['depends_on']) or 'None') + '</p><dl>' + rows + '</dl><details><summary>Evidence and delivery (' + str(len(links)) + ')</summary><ul>' + ''.join(links) + '</ul></details></article>')
    counts = ''.join('<span><b>' + str(sum(s['status'] == state for s in stages)) + '</b> ' + state + '</span>' for state in STATES)
    template = (ASSETS / 'dashboard.html').read_text(encoding='utf-8')
    for key, value in {'TITLE': esc(project['name']), 'GOAL': esc(project['goal']), 'TIME': esc(project['verified_at']), 'GENERATED': esc(public['generated_at']), 'COUNTS': counts, 'CARDS': ''.join(cards), 'OPTIONS': ''.join('<option>' + st + '</option>' for st in STATES)}.items():
        template = template.replace('{{' + key + '}}', value)
    (out / 'report.html').write_text(template, encoding='utf-8')
    write_json(out / 'snapshot.json', public)
    write_json(out / 'manifest.json', {'generated_at': public['generated_at'], 'sources': sources, 'files': {name: sha(out / name) for name in ('report.html', 'snapshot.json')}})
    (out / '.generated-by-main-session-orchestrator').write_text('Generated preview only. No publishing or dispatch.\n', encoding='utf-8')
    return {**result, 'preview': str(out / 'report.html'), 'published': False}


def audit(root):
    _, _, current, _ = validate(root)
    out = root / '.orchestrator' / 'web'
    m = json.loads((out / 'manifest.json').read_text(encoding='utf-8'))
    require(m['sources'] == current, 'Sources changed after build; rebuild before publishing')
    for name, digest in m['files'].items():
        p = inside(out, name)
        require(p.is_file() and sha(p) == digest, 'Generated file mismatch: ' + name)
    public = json.loads((out / 'snapshot.json').read_text(encoding='utf-8'))
    urls = sorted({e['url'] for s in public['stages'] for e in s['evidence'] if e.get('url')})
    return {'ok': True, 'files_verified': len(m['files']), 'sources_verified': len(current), 'external_urls_to_check': urls, 'note': 'Local files and source freshness checked. HTTP reachability and browser behavior require separate checks; nothing was published.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('init', 'add-stage', 'check', 'build', 'audit'))
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--name')
    parser.add_argument('--goal')
    parser.add_argument('--main')
    parser.add_argument('--id')
    parser.add_argument('--title')
    parser.add_argument('--purpose')
    parser.add_argument('--method')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == 'init':
            require(args.name and args.goal and args.main, 'init needs --name --goal --main')
            result = init(root, args.name, args.goal, args.main)
        elif args.command == 'add-stage':
            require(args.id and args.title and args.purpose and args.method, 'add-stage needs --id --title --purpose --method')
            result = add_stage(root, args.id, args.title, args.purpose, args.method)
        elif args.command == 'check':
            result = validate(root)[3]
        elif args.command == 'build':
            result = build(root)
        else:
            result = audit(root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
