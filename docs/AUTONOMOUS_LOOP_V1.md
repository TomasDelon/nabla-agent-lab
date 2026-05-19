# Autonomous Loop V1

This document defines the first fully autonomous Nabla Agent Lab loop.

The goal is to remove human intervention from the execution cycle while keeping strict separation between planning, implementation, testing, auditing, and merge authority.

## Core Objective

The autonomous loop must be able to:

1. inspect the repository state;
2. generate the next worker prompt using a GPT-family prompt/audit model inside the runner;
3. execute OpenCode Go as the implementation worker;
4. run tests and policy gates;
5. create a branch and pull request;
6. audit the worker output and resulting diff;
7. merge automatically only when all gates pass;
8. persist a complete run report in GitHub.

No human approval is required inside the loop.

## Important Distinction

ChatGPT app scheduled tasks are not the autonomous executor.

They remain useful as external read-only audits, but they are not reliable event receivers and should not be required for the loop to progress.

The autonomous GPT role must therefore run from GitHub Actions through an API-accessible model.

## Roles

| Component | Role | Write Access |
|---|---|---:|
| GPT prompt/audit model inside runner | writes worker prompts and audits outputs | No direct repo writes |
| OpenCode Go | modifies source code according to the generated prompt | Workspace only |
| GitHub Actions | executes commands, creates branches, commits, PRs, reports, and controlled merges | Yes |
| ChatGPT app | optional external read-only auditor/notifier | No in scheduled tasks |
| Human owner | configures secrets/policies, not part of normal execution cycle | Optional |

## Loop Phases

### Phase 1 — Plan

The runner calls the GPT prompt/audit model with:

- current repository context;
- allowed file paths;
- previous run summaries;
- current seed objective;
- safety policy.

The model must return a structured worker prompt for OpenCode Go.

### Phase 2 — Implement

The runner invokes OpenCode Go with the generated worker prompt.

OpenCode may edit only the workspace checked out by the workflow.

### Phase 3 — Test

The runner executes deterministic gates, at minimum:

- `npm test`;
- changed-file allowlist;
- maximum changed file count;
- forbidden path checks;
- non-empty diff check.

### Phase 4 — Audit

The runner calls the GPT prompt/audit model again with:

- the original generated worker prompt;
- OpenCode output;
- git diff;
- test output;
- policy gate output.

The audit must return a machine-readable verdict.

### Phase 5 — PR and Merge

If the audit verdict is `pass` and all deterministic gates pass, the workflow may:

1. commit changes to an agent branch;
2. open a pull request;
3. merge the pull request automatically.

If any gate fails, the workflow must preserve a report and stop without merging.

## Minimum Safety Gates for Lab V1

The first autonomous loop is allowed to touch only:

- `src/**`;
- `tests/**`;
- `.nabla-agent/runs/**`.

It must not touch:

- `.github/workflows/**`;
- repository secrets;
- package installation scripts;
- lockfiles unless explicitly allowed;
- arbitrary docs unless the seed task says documentation-only.

## Merge Policy

Autonomous merge is allowed only in the lab repository and only when:

- tests pass;
- changed files are inside the allowlist;
- the GPT audit verdict is `pass`;
- the PR was created by the workflow branch pattern `agent/autonomous-*`;
- there is no failed policy gate;
- the diff is small enough for audit.

## Non-Goals

This v1 does not migrate the system to the real Nabla repository.

This v1 does not grant ChatGPT app write permissions during scheduled tasks.

This v1 does not rely on Gmail as a trigger source.

## Source of Truth

The repository remains the source of truth.

Every autonomous run must write a report under:

```text
.nabla-agent/runs/<run-id>/
```

The report must include:

- generated OpenCode prompt;
- OpenCode output;
- test output;
- git diff;
- deterministic gate results;
- GPT audit verdict;
- final action taken.
