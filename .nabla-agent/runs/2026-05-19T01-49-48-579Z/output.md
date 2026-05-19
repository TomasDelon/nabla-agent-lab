Implementation plan:

1. Create a GitHub Actions workflow (e.g., `.github/workflows/dry-run.yml`) that triggers on push or manual dispatch.
2. In the workflow, read the prompt (from the event payload or a fixed file) and assign to a variable.
3. Create a new run directory under `.nabla-agent/runs/` with a unique name (e.g., `run-<timestamp>`).
4. Write the prompt content into `prompt.txt` inside that directory.
5. Write a fake output file `output.txt` containing: "Dry-run: would ask agent to add subtract(a,b) later, but not yet executed."
6. Write `status.json` with content `{"status": "dry-run", "executed": false}`.
7. Use `git diff --exit-code` to assert no changes to `src/` or `tests/` were made; if changes exist, fail the workflow.
8. Optionally commit and push the new run directory to keep history, but do not modify any other files.
9. Print summary of created files and verify no code modification.
