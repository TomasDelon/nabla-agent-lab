# Nabla Agent Lab Global Context

This file is the compact context that the ChatGPT app auditor should read at the beginning of every scheduled audit cycle.

## Repository

- Lab repository: `TomasDelon/nabla-agent-lab`
- Purpose: test autonomous agent infrastructure before touching real Nabla.
- Real project repository: `TomasDelon/nabla`

## Current Goal

Build and test an autonomous development loop where:

1. ChatGPT app acts as a periodic external auditor, coordinator, and prompt writer.
2. OpenCode Go workers implement code changes.
3. GitHub stores code, reports, registries, commits, and PRs.
4. Gmail carries structured messages between auditor, dispatcher, and builders.
5. Human intervention is not part of the normal loop.

## Hard Rules

- ChatGPT app scheduled tasks must not write to GitHub.
- ChatGPT app may read Gmail and GitHub.
- ChatGPT app may send emails.
- OpenCode workers may modify code only through controlled runner/dispatcher execution.
- GitHub remains the source of truth.
- Email is only a transport layer.
- Real Nabla must not be modified until the lab is validated.

## Current Known State

- PR #5 in `TomasDelon/nabla-agent-lab` adds the first GitHub-native autonomous OpenCode loop.
- The email orchestration protocol is being defined separately in this branch.
- No `[NABLA]` orchestration emails have been observed yet.

## Auditor Responsibilities

Every scheduled audit cycle should:

1. Search Gmail for recent `[NABLA]` messages.
2. Group messages by `run_id`.
3. Read this global context.
4. Read `.nabla-agent/task-registry.md`.
5. Inspect referenced GitHub branches, commits, PRs, and reports.
6. Decide whether each builder result is accepted, rejected, retried, or blocked.
7. Send structured emails with `[NABLA]` subject tags.
8. If useful, generate the next builder prompt email.

## Prompt Writing Rules

Prompts sent to builders must:

- be precise and bounded;
- name the target repo and branch;
- state allowed and forbidden paths;
- require tests;
- require a report path;
- forbid unrelated refactors;
- forbid dependency additions unless explicitly required;
- include a machine-readable run id.

## Audit Rules

A builder result can be accepted only if:

- referenced code or diff was inspected;
- tests passed or failure is explicitly acceptable for the task type;
- changed files match the allowed paths;
- no forbidden files were touched;
- the result matches the prompt;
- the report is present or the reason for absence is acceptable.

If uncertain, reject or retry.
