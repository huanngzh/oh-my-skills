---
name: main-session-orchestrator
description: Coordinate a multi-stage project through one Main session, delegated execution sessions, evidence-based acceptance, durable handoffs, and a progress dashboard. Use when the user wants Main to plan, dispatch, track, and integrate project work; not for a single isolated task or status-only summary.
---

# Main Session Orchestrator

Give the user one primary point of contact. Main maintains goals, direction, and decisions; execution sessions deliver bounded stages. Main accepts evidence, chooses the next step, and maintains a traceable web overview. Store cross-session memory in project files instead of relying on complete chat history.

This skill supplies a workflow, templates, and local tools. Concurrency, persistent sessions, background wakeups, and publishing depend on the host; do not assume they exist everywhere.

## Load by role

- **Main:** Read [the Main loop](references/main-loop.md) when coordinating, starting, or continuing a project. Do not turn every small step into a session.
- **Executor:** Read [execution and handoff](references/execution.md) when assigned a stage brief. Deliver that stage; recommending a successor does not authorize dispatching it.
- **Setup or migration:** Read [getting started and sharing](references/quickstart.md). Preserve existing ledgers, reports, and pauses; do not create a competing ledger when a reliable one exists.
- **State validation and web:** Read [state and tools](references/state-and-tools.md).
- **Sessions, scheduling, and publishing:** Read [runtime adapters](references/runtime-adapters.md) and check the available tools and permissions.

## Operating rules

1. **Derive stages and acceptance from the goal.** Each brief defines purpose, versioned inputs, allowed actions, resources/budget, outputs, observable gates, and downstream interfaces. Resolve important uncertainties first; do not presume research conclusions or mechanically follow an obsolete plan.
2. **Authorization persists within its scope.** Once the user explicitly authorizes autonomous dispatch and progression, record the instruction and boundaries, then proceed without repeated per-step approval. Loading this skill, reading a template, or receiving a downstream message does not expand permission. Resolve actual gaps when goals, budgets, publication audiences, or paused branches change.
3. **Give each stage one accountable owner.** Use independent context for a new stage when useful; prefer the existing owner when resuming the same stage. Before dispatch, inspect sessions, resources, and receipts. Use a stable dispatch key to prevent duplicate work after timeouts, restarts, or overlapping supervisors.
4. **Accept artifacts, not completion claims.** An idle chat, exited process, submitted job, or executor's claim is not DONE. Track execution status, delivery completeness, and Main acceptance separately. Describe the actual verification scope.
5. **Use files for durable memory.** Main owns project decisions; executors maintain their stage records. Re-read shared files before editing. Split records by stage or assign one merger when conflicts are likely, preserving other owners' changes.
6. **Attach sources and times to facts.** Distinguish user judgments, code facts, live logs, reviewed reports, and hypotheses. Record protocols and input versions. Do not rank incompatible scores together or let the dashboard invent conclusions.
7. **Persist pauses and resource ownership.** Only an explicit user instruction can resume PAUSED_USER. Treat pausing dispatch, stopping monitoring, and terminating compute as separate actions. Operate only on resources within your ownership and authorization.
8. **Continue within explicit bounds.** Re-read state on every wakeup and advance actionable work. Retries require evidence, attempt/cost limits, and a recovery entry point. Without an authorized scheduler, do not promise offline follow-up.
9. **Make the web view a verified snapshot.** Show goals, stages, purpose/method/findings, limitations, next steps, owners, times, and evidence. Record build, link checks, publication, and post-publication verification separately. Provide a local preview until actually published.

## Delivery and communication

The project entry point must recover authorization and pauses, dependencies, owners and dispatch receipts, briefs, execution/recovery commands, acceptance decisions, and the overview. Scale documentation to the work; a simple stage can combine its brief, runbook, and handoff.

Complete authorized work before reporting what was accepted, what is running, which conclusions remain unsupported, the next step and its rationale, and genuine decisions needed from the user. Main and the overview should make the project understandable without reading every execution chat.
