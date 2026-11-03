# Stage execution and handoff

Read project rules, your brief, input provenance, and code-specific instructions. Record the actual owner, start time, and next action. Check for duplicate jobs, Git changes, and resource ownership; prefer recovering an existing instance of the same stage.

Use a risk-appropriate smoke test before scaling: actual inputs, dependencies, read/write locations, save/resume, and essential outputs. The project defines storage and remote connections. ML projects may separate logs/media from large checkpoints; this skill carries no fixed mount paths.

Maintain the stage state/runbook with real commands, working directories, code/config/input versions, job/process/node IDs, logs, outputs, exit status, time zone, recovery commands/state, gate progress, failures, limitations, and next steps. Never record secrets. A submitted background job remains IN_PROGRESS. Distinguish fresh initialization from a full training resume.

Submit patches or hand shared edits to the assigned merger. Main generates the overview, or an executor receives exclusive ownership during handoff; do not concurrently edit the catalog and publish it.

Deliver a [handoff](../assets/handoff.md) mapping each gate to evidence. State the scope of tests, sampling, and human judgment, along with cost and recovery entry points. A successor recommendation is not authorization to dispatch it. Conditional handoff needs prior user authorization. Follow host rules when messaging Main; without messaging authorization, save files for Main to collect.

After a complete delivery, keep the stage IN_PROGRESS with “awaiting Main acceptance” until accepted. You may separately record successful execution_status; it does not replace stage acceptance. Someone without the chat history should be able to reproduce and recover the work.
