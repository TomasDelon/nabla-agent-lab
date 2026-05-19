# Scheduled Audit Policy

This policy defines how scheduled ChatGPT tasks may interact with this repository.

## Principle

Scheduled ChatGPT tasks are read-only auditors.

They may:

- inspect repository files;
- inspect pull requests;
- inspect workflow status;
- inspect agent run reports;
- summarize risks;
- notify the user;
- recommend a next action.

They must not:

- create commits;
- create branches;
- create pull requests;
- merge pull requests;
- approve pull requests;
- comment on GitHub;
- modify labels;
- modify issues;
- update files;
- trigger destructive actions.

## Why

ChatGPT connector writes require human validation. Scheduled tasks should not depend on interactive connector write approvals. Therefore all autonomous writes must be performed by GitHub Actions or another runner with explicit repository permissions and clearly defined workflow files.

## Allowed Scheduled Audit Output

A scheduled audit should produce a chat notification such as:

- `PR #3 is ready: CI passed and changed only src/math.js/tests/math.test.mjs.`
- `Workflow X failed: model returned HTTP 429.`
- `New run report exists: status completed, selected model llama-3.3-70b-versatile.`
- `Do not merge yet: diff touches unexpected files.`

## Production Migration Rule

Before using this pattern in the real Nabla repository, the read-only scheduled audit policy must be documented in the production repository and accepted by the user.
