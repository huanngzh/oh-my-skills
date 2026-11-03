# Runtime adapters

Discover tools and read their current schemas first; names and permissions can change. These mappings do not override host rules.

| Need | Codex desktop tool, when available | Constraint |
|---|---|---|
| Find projects and owners | list_projects / list_threads / read_thread | Use actual IDs; summaries do not prove compute state. |
| Persistent execution chat | create_thread | Requires explicit user authorization to create new chats, which can cover future stages within a project. List projects first; honor local/remote/worktree preferences and do not select a model without authorization. These are user-owned chats. |
| Subtasks within the current request | collaboration.spawn_agent and related tools | Use only when delegation is permitted. A subagent is not a persistent sidebar chat; check its lifetime across turns. |
| Collect progress | wait_threads / agent wait | Use cursor/afterCursor; read large histories only for changes or troubleshooting. |
| Send work to an existing chat | send_message_to_thread | Needs human authorization to message that chat. Main's message alone does not authorize replies from downstream chats; Main can collect handoff files. |
| Background wakeups | automation_update | Configure when requested, usually as a thread heartbeat. Save ownership, exit conditions, and quiet-notification rules. Do not substitute shell cron. |
| Show results | open_in_codex | Use real paths or URLs. Opening a result is not publication or acceptance. |

A request to document a workflow or create a skill does not authorize execution chats, resuming Main, or creating automation. During real project work, continue within recorded authorization without repeated approval.

Use self-contained briefs for independent stages. Fork only when inherited context is actually needed. If a tool returns clientThreadId, wait for the actual threadId before invoking tools that require it.

On other hosts, map create/read/wait/message to supported APIs. Without delegation, Main can execute sequentially and state that no separate executor was created. Without scheduling, advance during the current invocation and save a continuation entry point; do not promise offline monitoring.

For the web overview, reuse existing builders/hosting when suitable; otherwise provide a local preview. The project supplies the destination, audience, credentials, and storage. This skill includes no account or cloud host. Publish only reviewed static artifacts to an owned destination. Record the source hash, manifest, real URL, time, and rollback entry; use version directories and an atomic switch when available. Rebuild after source changes. Verify bytes, links, and UI after publishing. Repair only this publication; do not restart shared services or rerun compute to fix a page.
