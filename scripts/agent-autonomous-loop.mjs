import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const env = process.env;
const runId = new Date().toISOString().replace(/[:.]/g, "-");
const runDir = join(root, ".nabla-agent", "runs", runId);
mkdirSync(runDir, { recursive: true });

const cfg = {
  seedPath: env.NABLA_SEED_PATH || ".nabla-agent/seeds/next-autonomous-task.md",
  plannerModel: env.NABLA_PLANNER_MODEL || "gpt-4.1-mini",
  auditorModel: env.NABLA_AUDITOR_MODEL || env.NABLA_PLANNER_MODEL || "gpt-4.1-mini",
  baseBranch: env.NABLA_BASE_BRANCH || "main",
  branchName: env.NABLA_BRANCH_NAME || `agent/autonomous-${runId}`,
  allowAutoMerge: env.NABLA_ALLOW_AUTO_MERGE === "true",
  maxDiffChars: Number(env.NABLA_MAX_DIFF_CHARS || "30000"),
};

const allowedPrefixes = ["src/", "tests/", ".nabla-agent/runs/"];
const forbiddenPrefixes = [".github/", ".git/", "node_modules/"];
const forbiddenExact = ["package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock"];

function pathOf(file) {
  return join(root, file);
}

function read(file) {
  return readFileSync(pathOf(file), "utf8");
}

function report(name, value) {
  const text = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  writeFileSync(join(runDir, name), text + (text.endsWith("\n") ? "" : "\n"), "utf8");
}

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

async function openAIJson(model, role, payload) {
  if (!env.OPENAI_API_KEY) throw new Error("Missing OPENAI_API_KEY repository secret.");

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.OPENAI_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      temperature: 0.2,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: role },
        { role: "user", content: JSON.stringify(payload) },
      ],
    }),
  });

  const raw = await response.text();
  report(`${model}-${Date.now()}-raw.json`, raw);
  if (!response.ok) throw new Error(`OpenAI API error ${response.status}: ${raw}`);

  const parsed = JSON.parse(raw);
  const content = parsed.choices?.[0]?.message?.content;
  if (!content) throw new Error(`OpenAI response has no content: ${raw}`);
  return JSON.parse(content);
}

function repoContext() {
  const files = ["package.json", "src/math.js", "tests/math.test.mjs", cfg.seedPath];
  return files
    .filter((file) => existsSync(pathOf(file)))
    .map((file) => `--- ${file} ---\n${read(file)}`)
    .join("\n\n");
}

function changedFiles() {
  const out = must("git", ["diff", "--name-only"]).stdout;
  return out.split("\n").map((x) => x.trim()).filter(Boolean);
}

function policy(files, diff) {
  const failures = [];
  if (files.length === 0) failures.push("No files changed.");
  if (files.length > 8) failures.push(`Too many files changed: ${files.length}.`);
  if (diff.length > cfg.maxDiffChars) failures.push(`Diff too large: ${diff.length}.`);

  for (const file of files) {
    if (forbiddenExact.includes(file)) failures.push(`Forbidden exact file changed: ${file}`);
    if (forbiddenPrefixes.some((prefix) => file.startsWith(prefix))) failures.push(`Forbidden path changed: ${file}`);
    if (!allowedPrefixes.some((prefix) => file.startsWith(prefix))) failures.push(`File outside allowlist: ${file}`);
  }

  return { pass: failures.length === 0, failures, files, diffChars: diff.length };
}

function writeFinal(status) {
  report("final-status.json", { runId, ...status });
}

async function main() {
  const context = repoContext();
  const seed = read(cfg.seedPath);
  report("repo-context.txt", context);

  const plan = await openAIJson(
    cfg.plannerModel,
    [
      "You are the GPT prompt writer for Nabla Agent Lab.",
      "Return JSON only with keys: title, worker_prompt, expected_files, risk_notes.",
      "You do not edit files directly. You write the prompt for OpenCode Go.",
      "The worker must not ask for human confirmation.",
      "The repository is JavaScript ESM. Do not use Python. Do not add dependencies.",
    ].join("\n"),
    {
      seed,
      context,
      constraints: { allowedPrefixes, forbiddenPrefixes, forbiddenExact, noHumanIntervention: true },
    },
  );

  if (!plan.worker_prompt) throw new Error("Planner returned no worker_prompt.");
  report("planner.json", plan);
  report("generated-worker-prompt.md", plan.worker_prompt);

  must("git", ["checkout", "-B", cfg.branchName]);

  const args = ["run", "--dangerously-skip-permissions", "--dir", root, plan.worker_prompt];
  if (env.NABLA_OPENCODE_MODEL) args.splice(1, 0, "--model", env.NABLA_OPENCODE_MODEL);

  const worker = run("opencode", args, { timeout: 1000 * 60 * 20 });
  report("opencode-output.txt", worker.output);
  if (worker.status !== 0) throw new Error(`OpenCode failed with status ${worker.status}`);

  const files = changedFiles();
  const diff = files.length ? must("git", ["diff", "--", ...files]).stdout : "";
  const gate = policy(files, diff);
  report("changed-files.json", files);
  report("diff.patch", diff);
  report("policy.json", gate);

  const tests = run("npm", ["test"], { timeout: 1000 * 60 * 5 });
  report("test-output.txt", tests.output);

  const audit = await openAIJson(
    cfg.auditorModel,
    [
      "You are the GPT auditor for Nabla Agent Lab.",
      "Return JSON only with keys: verdict, confidence, reasons, merge_allowed.",
      "verdict must be pass or fail. Be strict. If unsure, fail.",
      "Do not ask for human confirmation.",
    ].join("\n"),
    {
      workerPrompt: plan.worker_prompt,
      workerOutput: worker.output.slice(-12000),
      changedFiles: files,
      diff: diff.slice(0, cfg.maxDiffChars),
      policy: gate,
      testStatus: tests.status,
      testOutput: tests.output.slice(-12000),
    },
  );

  const gatesPass = gate.pass && tests.status === 0 && audit.verdict === "pass" && audit.merge_allowed === true;
  report("audit.json", audit);
  writeFinal({ status: "pre-commit", gatesPass, policy: gate, audit });

  must("git", ["add", "src", "tests", ".nabla-agent/runs"]);
  const staged = must("git", ["diff", "--cached", "--name-only"]).stdout.trim();
  if (!staged) throw new Error("No staged files after OpenCode run.");

  must("git", ["commit", "-m", `agent: ${plan.title || "autonomous change"}`]);
  must("git", ["push", "--set-upstream", "origin", cfg.branchName]);

  if (!env.GITHUB_REPOSITORY || !env.GITHUB_TOKEN) throw new Error("Missing GitHub repository context or token.");

  const body = [
    "Autonomous OpenCode Go run.",
    "",
    `Run ID: ${runId}`,
    `Planner model: ${cfg.plannerModel}`,
    `Auditor model: ${cfg.auditorModel}`,
    `Policy pass: ${gate.pass}`,
    `Test status: ${tests.status}`,
    `Audit verdict: ${audit.verdict}`,
    `Gates pass: ${gatesPass}`,
    "",
    "Reports are committed under `.nabla-agent/runs/`.",
  ].join("\n");

  const pr = must("gh", [
    "pr", "create",
    "--repo", env.GITHUB_REPOSITORY,
    "--base", cfg.baseBranch,
    "--head", cfg.branchName,
    "--title", `Agent: ${plan.title || "autonomous change"}`,
    "--body", body,
  ]).stdout.trim();

  if (gatesPass && cfg.allowAutoMerge) {
    must("gh", ["pr", "merge", pr, "--repo", env.GITHUB_REPOSITORY, "--squash", "--delete-branch"]);
    writeFinal({ status: "merged", pr, gatesPass });
  } else {
    writeFinal({ status: "pr-created-not-merged", pr, gatesPass });
  }
}

main().catch((error) => {
  report("fatal-error.txt", error.stack || String(error));
  console.error(error);
  process.exit(1);
});
