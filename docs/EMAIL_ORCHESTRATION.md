# Email Orchestration Protocol

This document defines the email-based orchestration layer for Nabla Agent Lab.

The goal is to let the ChatGPT app act as an external periodic auditor, coordinator, and prompt writer, while OpenCode workers remain the code executors.

## Core Model

Email is used as a message bus.

GitHub remains the source of truth.

ChatGPT app scheduled tasks poll Gmail periodically, inspect GitHub, audit builder results, and send structured prompt emails to builders or dispatchers.

All orchestration email bodies must be JSON objects.

## Roles

| Role | Component | Responsibility | Writes Code |
|---|---|---|---:|
| Auditor | ChatGPT app scheduled task | Reads context, results, code, reports, and decides accept/reject/next prompts | No |
| Redactor | ChatGPT app scheduled task | Writes precise worker prompts and sends them by email | No |
| Dispatcher | External script, Apps Script, or GitHub Actions bridge | Detects prompt emails and launches workers | No direct code design |
| Builder | OpenCode Go | Implements code changes and writes reports | Yes |
| Repository | GitHub | Source of truth for code, reports, registries, and PRs | N/A |

## Email Aliases

Gmail dot aliases may be used to separate logical channels while receiving mail in the same inbox.

Recommended aliases:

| Alias | Logical Role |
|---|---|
| `tomas.delon.gago@gmail.com` | Auditor inbox |
| `tomasdelon.gago@gmail.com` | Dispatcher inbox |
| `tomas.delongago@gmail.com` | Builder A inbox |
| `tomasde.longago@gmail.com` | Builder B inbox |

The system must not rely only on dots in the address. Every message must also include structured subject tags.

## Subject Tags

All orchestration emails must start with `[NABLA]`.

Allowed subject forms:

```text
[NABLA][PROMPT][BUILDER-A][RUN:<run-id>]
[NABLA][PROMPT][BUILDER-B][RUN:<run-id>]
[NABLA][RESULT][BUILDER-A][RUN:<run-id>]
[NABLA][RESULT][BUILDER-B][RUN:<run-id>]
[NABLA][AUDIT][ACCEPT][RUN:<run-id>]
[NABLA][AUDIT][REJECT][RUN:<run-id>]
[NABLA][AUDIT][RETRY][RUN:<run-id>]
[NABLA][STATUS][RUN:<run-id>]
```

## Message Body Schema

Use JSON only.

JSON may be pasted directly as the whole email body or wrapped in a fenced `json` block.

### Prompt Email

```json
{
  "kind": "prompt",
  "repo": "TomasDelon/nabla-agent-lab",
  "run_id": "P1-001",
  "builder": "builder-a",
  "base_branch": "main",
  "branch": "agent/P1-001",
  "allowed_paths": ["src/**", "tests/**"],
  "forbidden_paths": [".github/**", "package.json"],
  "report_path": ".nabla-agent/runs/P1-001",
  "task": "Implement the requested change here.",
  "acceptance": [
    "npm test passes",
    "diff touches only allowed paths",
    "report files are generated"
  ]
}
```

### Result Email

```json
{
  "kind": "result",
  "repo": "TomasDelon/nabla-agent-lab",
  "run_id": "P1-001",
  "builder": "builder-a",
  "branch": "agent/P1-001",
  "commit": "<sha>",
  "pr": "<number or url>",
  "report_path": ".nabla-agent/runs/P1-001",
  "status": "ready_for_audit",
  "summary": "Short builder summary."
}
```

### Audit Email

```json
{
  "kind": "audit",
  "repo": "TomasDelon/nabla-agent-lab",
  "run_id": "P1-001",
  "verdict": "accept",
  "auditor": "chatgpt-scheduled-auditor",
  "checked_commit": "<sha>",
  "checked_pr": "<number or url>",
  "reasons": ["reason one"],
  "next_action": "What the dispatcher or builder should do next."
}
```

## Auditor Scheduled Task Behavior

Every auditor run must:

1. search Gmail for unread or recent `[NABLA]` messages;
2. group messages by `run_id`;
3. parse JSON bodies;
4. read the repository global context;
5. read the task registry;
6. inspect referenced commits, PRs, diffs, and run reports;
7. decide `accept`, `reject`, `retry`, or `prompt_next`;
8. send JSON email responses;
9. never modify GitHub directly.

## Builder Behavior

A builder must:

1. receive a prompt email;
2. execute OpenCode Go using the task body;
3. write a report under `.nabla-agent/runs/<run-id>/`;
4. create a branch/commit/PR if configured;
5. send a JSON result email back to the auditor channel or make the result visible through GitHub reports.

## Safety Rules

- Email is not the source of truth.
- GitHub is the source of truth.
- Prompts must reference GitHub paths, commits, PRs, and report directories.
- The auditor must not approve changes without inspecting the diff or referenced code.
- The dispatcher must ignore emails without `[NABLA]` subject tags.
- The dispatcher must ignore emails from unauthorized senders.
- The dispatcher must reject invalid JSON bodies.
- Builders must not execute shell commands copied from untrusted emails unless the dispatcher validates the JSON schema.
- Large code or logs should live in GitHub reports, not in email bodies.

## Failure Modes

| Failure | Behavior |
|---|---|
| Missing report | auditor sends `[NABLA][AUDIT][RETRY]` |
| Tests failed | auditor sends reject or retry |
| Diff touches forbidden paths | auditor rejects |
| Email malformed or invalid JSON | dispatcher labels `NABLA_DISPATCH_FAILED` and emails the auditor |
| Unknown builder | dispatcher rejects |
| Conflicting results for same run | auditor marks run blocked |

## Current Status

The protocol uses JSON email bodies.

The first implementation target is the lab repository, not the real Nabla repository.
