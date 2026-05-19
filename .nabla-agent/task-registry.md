# Nabla Agent Lab Task Registry

This registry is the shared state read by the ChatGPT app auditor.

The registry is not a complete database. It is a compact source-of-truth summary that points to GitHub commits, PRs, reports, and email run ids.

## Status Legend

| Status | Meaning |
|---|---|
| `planned` | task exists but no builder has started |
| `prompt_sent` | prompt email was sent to a builder or dispatcher |
| `running` | builder is expected to be working |
| `ready_for_audit` | builder reported completion |
| `accepted` | auditor accepted the result |
| `rejected` | auditor rejected the result |
| `retry` | auditor requested correction |
| `blocked` | cannot continue automatically |

## Current Phase

```yaml
project: nabla-agent-lab
phase: email-orchestration-v1
real_nabla_locked: true
last_known_real_nabla_commit: ed9481e8418459b5f66eee316a23ecb46609dfa5
```

## Runs

```yaml
runs:
  - run_id: LAB-AUTOLOOP-PR5
    status: ready_for_review
    repo: TomasDelon/nabla-agent-lab
    pr: 5
    branch: agent/autonomous-loop-v1-clean
    summary: "Adds first GitHub-native autonomous OpenCode loop. Requires OPENAI_API_KEY secret before execution."
    next_expected_action: "Human may merge infrastructure PR once reviewed; not part of normal autonomous loop yet."

  - run_id: EMAIL-ORCH-V1
    status: planned
    repo: TomasDelon/nabla-agent-lab
    branch: agent/email-orchestration-v1
    summary: "Defines the Gmail/email orchestration protocol for ChatGPT app scheduled auditors and OpenCode builders."
    next_expected_action: "Create PR and review docs."
```

## Builder Channels

```yaml
builders:
  - id: builder-a
    email_alias: tomas.delongago@gmail.com
    status: available
    role: "general OpenCode worker"

  - id: builder-b
    email_alias: tomasde.longago@gmail.com
    status: available
    role: "parallel OpenCode worker"
```

## Auditor Channels

```yaml
auditors:
  - id: chatgpt-auditor-a
    email_alias: tomas.delon.gago@gmail.com
    cadence: "hourly task offset 00"

  - id: chatgpt-auditor-b
    email_alias: tomas.delon.gago@gmail.com
    cadence: "hourly task offset 20"

  - id: chatgpt-auditor-c
    email_alias: tomas.delon.gago@gmail.com
    cadence: "hourly task offset 40"
```

## Next Prompt Template

When the auditor sends a prompt email, it should use this structure:

```yaml
kind: prompt
repo: TomasDelon/nabla-agent-lab
run_id: "<new-run-id>"
builder: "builder-a"
base_branch: "main"
allowed_paths:
  - src/**
  - tests/**
forbidden_paths:
  - .github/**
  - package.json
report_path: ".nabla-agent/runs/<new-run-id>"
task: |
  <precise bounded task>
acceptance:
  - npm test passes
  - diff touches only allowed paths
  - report files are generated
```
