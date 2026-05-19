# Email Dispatcher Setup

This document explains how to connect Gmail prompt emails to GitHub Actions/OpenCode workers.

## Architecture

```text
ChatGPT app auditor
  sends [NABLA][PROMPT][BUILDER-A][RUN:<id>] email
      ↓
Google Apps Script bridge
  polls Gmail for prompt emails
  parses the YAML-like body
  calls GitHub repository_dispatch
      ↓
GitHub Actions Email Dispatcher workflow
  receives payload
  runs OpenCode Go
  creates branch, report, commit, and PR
      ↓
ChatGPT app auditor
  sees [NABLA][RESULT] or PR/report during next scheduled audit
```

## Files

- `scripts/google-apps-script-gmail-to-github.js`
- `.github/workflows/email-dispatcher.yml`
- `scripts/email-dispatcher-runner.mjs`

## Required GitHub Setup

### 1. Repository Actions permissions

In GitHub:

```text
Repo → Settings → Actions → General
```

Enable:

- Read and write permissions
- Allow GitHub Actions to create and approve pull requests

### 2. GitHub token for Apps Script

Create a fine-grained token for `TomasDelon/nabla-agent-lab`.

Minimum permissions:

- Repository contents: Read
- Actions: Read and write or equivalent workflow dispatch permission
- Metadata: Read

The bridge uses:

```text
POST /repos/TomasDelon/nabla-agent-lab/dispatches
```

If a fine-grained token cannot dispatch repository events, use a classic token scoped only as tightly as possible for the lab.

## Required Apps Script Setup

1. Go to `script.google.com`.
2. Create a new Apps Script project.
3. Paste the content of:

```text
scripts/google-apps-script-gmail-to-github.js
```

4. Open project settings and add script properties:

```text
GITHUB_TOKEN=<your token>
GITHUB_REPO=TomasDelon/nabla-agent-lab
```

5. Create a time trigger:

```text
Function: pollNablaPromptEmails
Event source: Time-driven
Frequency: every 5 minutes or every 10 minutes
```

6. Authorize Gmail and external URL access when prompted.

## Test Prompt Email

Send an email to the builder/dispatcher alias with this subject:

```text
[NABLA][PROMPT][BUILDER-A][RUN:EMAIL-DISPATCH-TEST-001]
```

Body:

```yaml
kind: prompt
repo: TomasDelon/nabla-agent-lab
run_id: "EMAIL-DISPATCH-TEST-001"
builder: "builder-a"
base_branch: "main"
branch: "agent/EMAIL-DISPATCH-TEST-001"
allowed_paths:
  - src/**
  - tests/**
forbidden_paths:
  - .github/**
  - package.json
report_path: ".nabla-agent/runs/EMAIL-DISPATCH-TEST-001"
task: |
  Add a JavaScript ESM function named square(a) to src/math.js.
  Export it.
  Add tests in tests/math.test.mjs using node:test and node:assert/strict.
  Keep the project JavaScript/Node/ESM only.
  Do not add dependencies.
acceptance:
  - npm test passes
  - square(4) returns 16
  - square(-3) returns 9
```

## Expected Result

The Apps Script bridge should:

1. detect the prompt email;
2. apply label `NABLA_DISPATCHED`;
3. send repository_dispatch to GitHub.

GitHub Actions should:

1. run `Email Dispatcher` workflow;
2. install OpenCode Go;
3. execute the task;
4. create a branch;
5. commit source/test/report changes;
6. open a PR.

## Current Limitation

The GitHub workflow currently logs the result email content but does not send Gmail directly.

The auditor can still see the created PR and `.nabla-agent/runs/<run-id>/` report in GitHub.

A later version may add a dedicated email-sending bridge for builder result emails.

## Safety Notes

- The Apps Script bridge must ignore emails that do not start with `[NABLA][PROMPT]`.
- The bridge labels processed threads with `NABLA_DISPATCHED` to avoid duplicate dispatch.
- The dispatcher validates the repo, builder id, run id, and task before running OpenCode.
- The lab repository is the only intended target.
- Do not point this bridge to real Nabla until the lab is validated.
