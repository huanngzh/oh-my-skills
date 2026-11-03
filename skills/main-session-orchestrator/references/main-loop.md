# The Main loop

## Establish the project entry point

Read AGENTS, the roadmap, state, relevant handoffs, Git status, and the latest user decisions. Identify Main and existing owners. A missing template file does not mean the project is new.

Persist the goal, success criteria, scope/non-goals, authorization source, autonomous scope, human decision gates, concurrency/cost/resources, pauses, publication audience, and supervision method. Use the [charter](../assets/charter.md) if useful. Record instructions already given; ask only for information that affects the concrete next action, and continue independent work.

Example authorization: “As Main, create and contact execution sessions within this project, progress through A → B → C, and track them to acceptance. Run at most two stages concurrently, create no new paid resources, and publish the overview to our existing internal site.” Record the user's actual instruction and time, then act within it without asking at every stage. If the user asks only for a plan, deliver a plan. Host rules for sessions, messages, and scheduling still apply.

Divide the dependency graph into independently verifiable stages with stable handoffs. Preserve decision points that may change direction. Parallel work requires clear inputs, non-conflicting resources, and stable interfaces. Assign a merger for shared files.

## Each cycle

1. **Read instructions and state.** Apply user revisions to the affected scope. Recheck pauses, authorization, and resources; an old idle snapshot does not establish current availability.
2. **Collect changes.** Use bounded waits and cursors. Read detailed logs when something changes or troubleshooting requires them. Track chats, background jobs, and stages separately; a job may outlive the chat's turn.
3. **Accept deliveries.** Compare against the brief's gates: artifacts, versions/hashes, tests, failures, limitations, resources, and recovery. Inspect representative outputs proportionate to risk. Reviewing a report is not independently rerunning it. Record Main acceptance before DONE; missing items remain IN_PROGRESS with a concrete request for completion.
4. **Update decisions.** Record finding → supported judgment → reason for the next step. Revise a route that the evidence no longer supports. Prepare concrete proposals for branches outside authorization.
5. **Dispatch READY stages.** Recheck authorization, pauses, resources, concurrency, and duplicates. Persist the brief and dispatch intent first. Immediately save the returned ID/receipt, then verify owner receipt. Verify actual compute startup separately.
6. **Update the overview and report.** Refresh at delivery, important findings, blocks/pauses, or changes of direction. Do not generate repetitive notifications when nothing has changed.

## Dispatch and deduplication

Use a [stage brief](../assets/stage-brief.md). Send a self-contained goal, role, file entry points, and boundaries, rather than the entire conversation. A dispatch key can be `project/stage/attempt-N`. Record the host, actual session/agent ID, brief version, input fingerprint, time, call result, receipt, and external job IDs.

If a call times out or its outcome is unknown, inspect dispatch keys, sessions, records, and actual jobs before retrying. If the state is unobservable, record the uncertainty and advance independent work. A timeout does not mean the action failed to happen. Give conditional handoff one sender: if the predecessor is already authorized to send it, Main verifies the receipt instead of dispatching again.

## Supervision and recovery

- Wait within bounded intervals and allow interruption; back off on unchanged state. Configure host automation only when the user requests continued monitoring or later follow-up. Record its ID, cadence, notifications, and exit conditions.
- Prefer one Main supervisor. Independent stage monitors need explicit, non-overlapping scopes to prevent duplicate restarts or dispatches. Close monitors you own when their purpose ends.
- Separate compute, report, and publication failures. The latter two usually need report repair or artifact republishing, not expensive recomputation. Retry within the authorized budget and runbook limits, retaining the failed attempt and evidence.
- BLOCKED records the cause, release condition, and independent work still possible. PAUSED_USER is reserved for explicit user pauses and never expires automatically.
- Recover Main from the charter, stage state, dispatches, jobs, handoff, and acceptance. A quiet owner is not a reason to create duplicate work.
- Pausing stops new dispatch in the specified scope. Follow the user's direction separately for running compute and read-only monitoring. Resuming one branch does not release other pauses.

## Close out

Verify goals, acceptance records, remaining jobs, handoffs, the final overview, and recovery files. State unresolved limitations. Clean up only temporary resources and monitors you own and no longer need. Report completion only when the entire authorized scope is satisfied.
