# State, files, and local tools

Retain reliable existing ledgers and reports. This schema is a lightweight default for new projects, not a mandate to migrate every old record. Utilities require Python 3.9+ and only the standard library; they have no network or API dependencies.

## States

| State | Meaning |
|---|---|
| TODO | Prerequisites or the brief are incomplete. |
| READY | Inputs, dependencies, and brief are ready; Main must still check authorization, resources, and duplicates. |
| IN_PROGRESS | Preparing, executing, completing delivery, or awaiting Main acceptance. |
| BLOCKED | A specific obstacle prevents progress; record the release condition and advance independent work. |
| PAUSED_USER | Explicitly paused by the user; record the source and resumption condition. Never resume automatically. |
| DONE | Gates passed, artifacts traceable, and Main accepted the stage. |

On READY → IN_PROGRESS, register the actual owner and dispatch receipt. After compute finishes, retain IN_PROGRESS until Main accepts. Preserve failures; return to TODO or BLOCKED according to cause. When a new protocol or scope requires more work on a completed stage, prefer a revision stage referencing historical acceptance instead of silently rewriting results.

## Layout and commands

Set `$SKILL_DIR` to the verified skill directory and `$PROJECT_DIR` to the verified project root.

```bash
python3 "$SKILL_DIR/scripts/project.py" init --root "$PROJECT_DIR" --name 'Example project' --goal 'Deliver verifiable project outcomes' --main 'actual-main-id'
python3 "$SKILL_DIR/scripts/project.py" add-stage --root "$PROJECT_DIR" --id S01 --title 'Input preflight' --purpose 'Verify prerequisites' --method 'Freeze inputs and run a minimal smoke test'
python3 "$SKILL_DIR/scripts/project.py" check --root "$PROJECT_DIR"
python3 "$SKILL_DIR/scripts/project.py" build --root "$PROJECT_DIR"
python3 "$SKILL_DIR/scripts/project.py" audit --root "$PROJECT_DIR"
```

init never overwrites `.orchestrator` or changes AGENTS. Merge applicable parts of the [AGENTS fragment](../assets/agents-fragment.md), preserving existing rules.

```text
.orchestrator/
  charter.md                 Goals, authorization, resources, decisions
  project.json               Global configuration maintained by Main
  stages/S01.json            One owner and file per stage
  briefs/S01.md              Frozen stage brief
  handoffs/                  Executor deliveries
  acceptance/                Main acceptance
  receipts/                  Dispatch, job, and publication receipts
  web/report.html            Offline overview; no automatic publication
  web/snapshot.json          Selected display fields
  web/manifest.json          Source and output SHA256 hashes
```

Re-read your JSON before editing. Main and the executor agree who writes state during handoff. Scripts provide no concurrent merge or cross-machine locks: never write the same file/build directory concurrently. Separate stages can have independent writers; shared configuration and generated outputs have one writer. Run audit after every build and rebuild when sources change.

## Fields and gates

project.json: name, goal, main_owner, verified_at (with time zone), charter, autonomy (MANUAL/BOUNDED), authorization_source, authorized_stage_ids, paused_stage_ids, max_parallel. Set BOUNDED only on actual user authorization; the field itself grants no permission. Templates do not create schedulers.

stage.json: id, title, purpose, method, status, owner, verified_at, depends_on, brief, finding, limitations, next_action, blocker, resume_condition, gates, evidence, jobs, dispatches; add handoff and acceptance for completion. Local paths are relative to the project root. Traversal and symlinks pointing outside are rejected. Reference external large artifacts through an in-project audit or manifest.

```json
{
  "gates": [{"criterion": "Frozen-input smoke passed", "status": "PASS", "evidence_ids": ["smoke"]}],
  "evidence": [{"id": "smoke", "label": "Actual smoke audit", "path": "artifacts/s01/smoke.json", "sha256": "actual-file-SHA256"}],
  "acceptance": {"decision": "ACCEPT", "by": "actual-ID-matching-main_owner", "at": "2026-01-01T12:00:00+00:00", "record": ".orchestrator/acceptance/S01.md", "sha256": "actual-acceptance-file-SHA256"}
}
```

Gate states are PENDING/PASS/FAIL; PASS must reference evidence. URL evidence uses url, checked_at, and verification instead of path/hash. Record the actual HTTP/content check scope, not merely a time. HTTP(S) URLs cannot contain credentials or query parameters. Audience restrictions still apply to internal links; valid syntax does not establish a real network check.

Each jobs entry has id, status, checked_at. States: UNKNOWN/QUEUED/RUNNING/SUCCEEDED/FAILED/STOPPED. DONE cannot retain unresolved jobs; preserve historical failures in the runbook. Record evidence of resource handoff for services transferred downstream. List only compute this stage is responsible for closing in jobs.

Each dispatches entry has key and status (INTENT/UNKNOWN/SENT/ACKNOWLEDGED/CLOSED); after sending, include target_id and a local receipt file. Keys must be unique across the project. READY stages with UNKNOWN or other non-CLOSED dispatches are excluded from candidates for Main review. Candidate selection is still not permission to resend or execute.

DONE requires passed gates, evidence with matching hashes, a finding, handoff, Main acceptance, and closed jobs/dispatches. check also detects dependency cycles, missing dependencies, and pause conflicts. Exceeding max_parallel emits a warning because awaiting acceptance need not consume compute.

**Checks validate record structure, file hashes, and consistency. They do not establish truth, verify user authorization, prove tests ran, or enforce the entire historical state-transition sequence.** Main must inspect original evidence and prior decisions rather than declaring completion by filling JSON.

## Web and publication

build creates an offline static page with search/state filters and no external requests. Public display fields include owners, findings, limitations, and evidence paths: review them for the intended audience before publishing. It omits job commands and dispatch receipts. Never publish the whole `.orchestrator` directory.

audit checks unchanged sources and output hashes and lists URLs needing actual HTTP checks. **It performs no HTTP or browser tests.** Full flow: build → audit → external-link/UI checks → publish to an authorized destination → verify HTTP/content/UI → save a receipt. Without publication capability, supply the real local path, not an invented URL.

Extend results tables only when needed: group comparable protocols/versions, label metric directions with up/down arrows, and share ranks for ties. Coverage and initialization references are not automatically quality ranks. Do not produce aggregate scores across incompatible protocols.
