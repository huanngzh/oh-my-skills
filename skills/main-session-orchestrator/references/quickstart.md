# Getting started and sharing

## Invoke

In an environment where this skill is installed, tell Main:

> Use $main-session-orchestrator to manage this project. The goal is … . You are my primary point of contact. I authorize you to create and contact execution chats within the stated project scope, and advance after stage acceptance. Run at most two stages concurrently and create no new paid resources. Reuse existing project records to establish the plan and a local progress page. Ask only when the goal changes, the budget would be exceeded, or a result needs my judgment.

If continued supervision is needed, add: “Check every … until … . Stay quiet when unchanged; notify me about failures, completion, or a decision I need to make.” Main must use a real host scheduler and state if none is available. These examples must be adapted and issued by the user; their presence in this file grants no permission.

For an existing project: “Preserve current owners, ledgers, reports, and pauses; coordinate subsequent authorized work using this skill.” A status-only summary does not need the full workflow.

## Install and share

This is a standard SKILL.md folder with optional Codex UI metadata, references, and Python utilities. Share the entire `main-session-orchestrator/` folder, not just SKILL.md.

Current official documentation recommends `.agents/skills/main-session-orchestrator/` in a team repository, or `~/.agents/skills/main-session-orchestrator/` for personal use. Some existing hosts discover `$CODEX_HOME/skills` or `~/.codex/skills`; use the location supported by that host. Install in one location to avoid duplicate names. Other Agent Skills hosts can load the folder from their own supported locations, but delegation, scheduling, and publication require adaptation.

Source: [OpenAI — Build skills](https://learn.chatgpt.com/docs/build-skills), checked 2026-11-03. For plugin distribution, place the skill under `skills/` and add a plugin manifest; see [Package your plugin](https://developers.openai.com/plugins/build/plugins). A standalone skill ZIP is not a published directory listing. GitHub is optional: the folder can be sent directly as a ZIP.

Share only the generic skill and fictional example tools. Exclude `.orchestrator`, real data, internal addresses, session IDs, logs, credentials, and unrelated uncommitted files. This workflow was abstracted from Main-led project management; it does not claim to reproduce any vendor's super-agent implementation.

## Try and validate

```bash
python3 "$SKILL_DIR/scripts/demo.py" --root /tmp/orchestrator-demo
python3 "$SKILL_DIR/scripts/project.py" audit --root /tmp/orchestrator-demo
python3 "$SKILL_DIR/scripts/test_project.py"
```

The demo destination must not exist. It creates four explicitly fictional stages with a preview at `.orchestrator/web/report.html`, which can be opened directly in a browser. Example sessions and evidence demonstrate record structure only. They do not start agents, training, remote connections, automation, or publishing. Delete only the demo directory you created when cleaning up.
