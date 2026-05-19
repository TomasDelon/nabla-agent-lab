# Nabla Agent Lab Orchestration

This document records the validated automation model for the lab repository before any equivalent workflow is considered for the real Nabla project.

## Roles

| Component | Role | Write Access |
|---|---|---:|
| ChatGPT | Read-only planner, reviewer, auditor, notifier | No during scheduled tasks |
| GitHub Actions | Runner that may create branches, commits, reports, and pull requests | Yes |
| Human owner | Final gate for merges and sensitive changes | Yes |
| Gmail | Optional notification channel | No source-of-truth role |

## Core Rule

Scheduled ChatGPT tasks must be read-only. They may inspect repository state, pull requests, workflow reports, and CI status, then notify the user. They must not create commits, branches, pull requests, labels, comments, or merges.

## Source of Truth

GitHub remains the technical source of truth:

- source code lives in tracked files;
- agent run reports live under `.nabla-agent/runs/`;
- workflows live under `.github/workflows/`;
- human-reviewed changes land through pull requests.

Gmail may notify about events, but it is not the source of truth.

## Validated Lab Stages

### Stage 1 — Dry Run

Validated: GitHub Actions can run without the user's computer, read `.nabla-agent/prompts/next.md`, create a report under `.nabla-agent/runs/`, and commit that report.

### Stage 2 — AI Report Only

Validated: GitHub Actions can call an external model API and commit a report without modifying source code.

### Stage 3 — Proposal Only

Validated: GitHub Actions can call Groq and generate a proposal report. The first low-context proposal was incorrect, which showed that agents need explicit repository context.

### Stage 4 — PR Workflow Pattern

Validated manually and through lab PRs:

- a branch can hold agent-generated changes;
- tests can run through CI;
- a pull request can expose the diff for human review;
- the user remains the merge gate.

## Production Safety Rules

- No force-push in production workflows.
- No auto-merge in production workflows.
- No scheduled ChatGPT write actions.
- No secrets committed to the repository.
- No direct writes to protected branches.
- Every code change should go through a pull request.
- CI must pass before merge.
- The human owner remains the final approval gate.

## Recommended Production Migration Order

1. Add read-only orchestration documentation to Nabla.
2. Add `.nabla-agent/` state and prompt directories to Nabla.
3. Add report-only workflow first.
4. Add proposal-only workflow second.
5. Add PR-creating workflow only after proposal quality is stable.
6. Add scheduled ChatGPT audits only as read-only checks.

## Scheduled Task Policy

A scheduled ChatGPT audit may report:

- open PRs needing review;
- CI failures;
- new agent run reports;
- suspicious diffs;
- missing audit bundles;
- suggested next prompts.

It must not write to GitHub during the scheduled run.
