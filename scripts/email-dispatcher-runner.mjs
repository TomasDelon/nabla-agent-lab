import { spawnSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const payloadPath = process.env.NABLA_DISPATCH_PAYLOAD_PATH || "";
const rawPayload = process.env.NABLA_DISPATCH_PAYLOAD || "{}";
const runIdFallback = new Date().toISOString().replace(/[:.]/g, "-");

function run(cmd, args, options = {}) {
  const result = spawnSync(cmd, args, {
    cwd: root,
    env: process.env,
    encoding: "utf8",
    shell: false,
    ...options,
  });
  const output = `${result.stdout || ""}${result.stderr || ""}`;
  return { status: result.status ?? 1, stdout: result.stdout || "", stderr: result.stderr || "", output };
}

function must(cmd, args, options = {}) {
  const result = run(cmd, args, options);
  if (result.status !== 0) {
    throw new Error(`${cmd} ${args.join(" ")} failed with status ${result.status}\n${result.output}`);
  }
  return result;
}

function parsePayload() {
  if (payloadPath) {
    return JSON.parse(require("node:fs").readFileSync(payloadPath, "utf8"));
  }
  return JSON.parse(rawPayload || "{}");
}

function validate(payload) {
  const errors = [];
  if (payload.kind !== "prompt") errors.push("payload.kind must be prompt");
  if (!payload.repo) errors.push("payload.repo is required");
  if (!payload.run_id) errors.push("payload.run_id is required");
  if (!payload.builder) errors.push("payload.builder is required");
  if (!payload.task) errors.push("payload.task is required");

  const allowedRepo = process.env.GITHUB_REPOSITORY;
  if (allowedRepo && payload.repo !== allowedRepo) {
    errors.push(`payload.repo must match ${allowedRepo}`);
  }

  const allowedBuilders = new Set(["builder-a", "builder-b"]);
  if (payload.builder && !allowedBuilders.has(payload.builder)) {
    errors.push(`unknown builder: ${payload.builder}`);
  }

  return errors;
}

function report(runDir, name, value) {
  const text = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  writeFileSync(join(runDir, name), text + (text.endsWith("\n") ? "" : "\n"), "utf8");
}

function main() {
  const payload = parsePayload();
  const errors = validate(payload);
  const runId = payload.run_id || `DISPATCH-${runIdFallback}`;
  const runDir = join(root, ".nabla-agent", "runs", runId);
  mkdirSync(runDir, { recursive: true });

  report(runDir, "dispatch-payload.json", payload);

  if (errors.length) {
    report(runDir, "dispatch-status.json", { status: "rejected", errors });
    throw new Error(`Invalid dispatch payload: ${errors.join("; ")}`);
  }

  const branchName = payload.branch || `agent/${runId}`;
  const taskPrompt = [
    "You are OpenCode Go working inside Nabla Agent Lab.",
    "Follow the task exactly.",
    "Do not ask for human confirmation.",
    "Do not perform unrelated refactors.",
    "Do not add dependencies unless the task explicitly says so.",
    "Use JavaScript/Node/ESM for this lab unless explicitly told otherwise.",
    "",
    `Run ID: ${runId}`,
    `Builder: ${payload.builder}`,
    `Report path: .nabla-agent/runs/${runId}`,
    "",
    "Allowed paths:",
    ...(payload.allowed_paths || ["src/**", "tests/**"]).map((x) => `- ${x}`),
    "",
    "Forbidden paths:",
    ...(payload.forbidden_paths || [".github/**", "package.json"]).map((x) => `- ${x}`),
    "",
    "Task:",
    payload.task,
    "",
    "Acceptance:",
    ...(payload.acceptance || ["npm test passes", "diff touches only allowed paths", "report files are generated"]).map((x) => `- ${x}`),
  ].join("\n");

  report(runDir, "builder-prompt.md", taskPrompt);

  must("git", ["checkout", "-B", branchName]);

  const args = ["run", "--dangerously-skip-permissions", "--dir", root, taskPrompt];
  if (process.env.NABLA_OPENCODE_MODEL) args.splice(1, 0, "--model", process.env.NABLA_OPENCODE_MODEL);

  const worker = run("opencode", args, { timeout: 1000 * 60 * 20 });
  report(runDir, "opencode-output.txt", worker.output);
  if (worker.status !== 0) {
    report(runDir, "final-status.json", { status: "opencode_failed", code: worker.status });
    process.exit(worker.status);
  }

  const changed = must("git", ["diff", "--name-only"]).stdout.split("\n").map((x) => x.trim()).filter(Boolean);
  const diff = changed.length ? must("git", ["diff", "--", ...changed]).stdout : "";
  report(runDir, "changed-files.json", changed);
  report(runDir, "diff.patch", diff);

  const tests = run("npm", ["test"], { timeout: 1000 * 60 * 5 });
  report(runDir, "test-output.txt", tests.output);

  must("git", ["add", "src", "tests", ".nabla-agent/runs"]);
  const staged = must("git", ["diff", "--cached", "--name-only"]).stdout.trim();
  if (!staged) {
    report(runDir, "final-status.json", { status: "no_changes" });
    throw new Error("No staged changes after builder run.");
  }

  must("git", ["commit", "-m", `agent: ${runId}`]);
  must("git", ["push", "--set-upstream", "origin", branchName]);

  const prBody = [
    "Email-dispatched OpenCode builder run.",
    "",
    `Run ID: ${runId}`,
    `Builder: ${payload.builder}`,
    `Report path: .nabla-agent/runs/${runId}`,
    `Test status: ${tests.status}`,
    "",
    "This PR was created by the email dispatcher workflow.",
  ].join("\n");

  const pr = must("gh", [
    "pr", "create",
    "--repo", process.env.GITHUB_REPOSITORY,
    "--base", payload.base_branch || "main",
    "--head", branchName,
    "--title", `Agent result: ${runId}`,
    "--body", prBody,
  ]).stdout.trim();

  report(runDir, "final-status.json", {
    status: "pr_created",
    pr,
    run_id: runId,
    builder: payload.builder,
    test_status: tests.status,
    changed_files: changed,
  });

  if (process.env.NABLA_RESULT_EMAIL_TO) {
    const subject = `[NABLA][RESULT][${payload.builder.toUpperCase()}][RUN:${runId}]`;
    const body = [
      "kind: result",
      `repo: ${process.env.GITHUB_REPOSITORY}`,
      `run_id: "${runId}"`,
      `builder: "${payload.builder}"`,
      `branch: "${branchName}"`,
      `pr: "${pr}"`,
      `report_path: ".nabla-agent/runs/${runId}"`,
      `status: "ready_for_audit"`,
      `test_status: ${tests.status}`,
      "summary: |",
      "  Builder finished and created a PR. The auditor should inspect the PR, diff, tests, and report files.",
    ].join("\n");
    must("gh", ["api", "/user"], { timeout: 1000 * 30 });
    console.log(`Result email should be sent externally: ${subject}\n${body}`);
  }
}

main();
