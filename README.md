# Nabla Agent Lab

A safe laboratory repository for testing autonomous agent orchestration before using similar workflows in the real Nabla repository.

## Goal

This repo tests a progressively safer automation loop:

1. GitHub Actions dry-run without AI.
2. AI response generation without code changes.
3. AI-generated patch proposal without applying it.
4. PR-based execution.
5. Controlled auto-commit only after the previous stages are proven safe.

## Current Stage

Stage 1 — dry-run runner.

The runner reads:

```text
.nabla-agent/prompts/next.md
```

and writes a run report under:

```text
.nabla-agent/runs/<timestamp>/
```

No AI is called in Stage 1.
No source code is modified in Stage 1.

## Safety Rules

- No force push.
- No auto-merge.
- No secrets committed to the repo.
- No code modification in dry-run mode.
- GitHub is the source of truth.
- ChatGPT acts as planner/reviewer.
- GitHub Actions acts as runner.
