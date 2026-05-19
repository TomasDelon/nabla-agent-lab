# LAB-001 — Dry Run

## Goal

Verify that GitHub Actions can read this prompt and create a run report without calling an AI model and without modifying source code.

## Required Behavior

- Read this prompt.
- Create a run directory under `.nabla-agent/runs/`.
- Write the prompt copy, fake output, and status JSON.
- Do not modify `src/**`.
- Do not modify `tests/**`.

## Expected Fake Output

The dry-run runner should report that it would ask an agent to add `subtract(a, b)` later, but it must not do it yet.
