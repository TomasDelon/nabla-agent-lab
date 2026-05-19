import { execFileSync, spawnSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const repoRoot = process.cwd();
const runId = new Date().toISOString().replace(/[:.]/g, "-");
const runDir = join(repoRoot, ".nabla-agent", "runs", runId);
mkdirSync(runDir, { recursive: true });

const env = process.env;
const openaiApiKey = env.OPENAI_API_KEY;
const plannerModel = env.NABLA_PLANNER_MODEL || "gpt-4.1-mini";
const auditorModel = env.NABLA_AUDITOR_MODEL || plannerModel;
const seedPath = env.NABLA_SEED_PATH || ".nabla-agent/seeds/next-autonomous-task.md";
const maxDiffChars = Number(env.NABLA_MAX_DIFF_CHARS || "30000");
const allowAutoMerge = env.NABLA_ALLOW_AUTO_MERGE === "true";
const ghToken = env.GITHUB_TOKEN;
const repoFullName = env.GITHUB_REPOSITORY;
const baseBranch = env.NABLA_BASE_BRANCH || "main";
const branchName = env.NABLA_BRANCH_NAME || `agent/autonomous-${runId}`;

const allowedPrefixes = ["src/", "tests/", ".nabla-agent/runs/"];
const forbiddenPrefixes = [".github/", ".git/", "node_modules/"];
const forbiddenExact = ["package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock"];

function readText(path) {
  return readFileSync(join(repoRoot, path), "utf8");
}

function writeReport(name, content) {
  writeFileSync(join(runDir, name), content ?? "", "utf8");
}

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: repoRoot,
    env: process.env,
    encoding: "utf8",
    shell: false,
    ...options,
  });

  const output = [
    result.stdout || "",
    result.stderr || "",
  ].filter(Boolean).join("\n");

  return {
    status: result.status ?? 1,
    signal: result.signal,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
    output,
  };
}

function mustRun(command, args, options = {}) {
  const result = run(command, args, options);
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed with status ${result.status}\n${result.output}`);
  }
  return result;
}

async function callOpenAIJson({ model, system, user }) {
  if (!openaiApiKey) {
    throw new Error("OPENAI_API_KEY is required for autonomous prompt/audit generation.");
  }

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${openaiApiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      temperature: 0.2,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
    }),
  });

  const raw = await response.text();
  if (!response.ok) {
    throw new Error(`OpenAI API error ${response.status}: ${raw}`);
  }

  const parsed = JSON.parse(raw);
  const content = parsed.choices?.[0]?.message?.content;
  if (!content) {
    throw new Error(`OpenAI API returned no message content: ${raw}`);
  }

  writeReport(`openai-${model}-${Date.now()}.json`, raw);
  return JSON.parse(content);
}

function collectRepoContext() {
  const files = ["package.json", "src/math.js", "tests/math.test.mjs", seedPath];
  const chunks = [];

  for (const file of files) {
    if (existsSync(join(repoRoot, file))) {
      chunks.push(`--- ${file} ---\n${readText(file)}`);
    }
  }

  return chunks.join("\n\n");
}

function getChangedFiles() {
  const result = mustRun("git", ["diff", "--name-only"]);
  return result.stdout.split("\n").map((x) => x.trim()).filter(Boolean);
}

function checkPolicy(changedFiles, diff) {
  const failures = [];

  if (changedFiles.length === 0) {
    failures.push("No files changed.");
  }

  if (changedFiles.length > 8) {
    failures.push(`Too many files changed: ${changedFiles.length}.`);
  }

  for (const file of changedFiles) {
    if (forbiddenExact.includes(file)) {
      failures.push(`Forbidden exact file changed: ${file}`);
    }

    if (forbiddenPrefixes.some((prefix) => file.startsWith(prefix))) {
      failures.push(`Forbidden path changed: ${file}`);
    }

    if (!allowedPrefixes.some((prefix) => file.startsWith(prefix))) {
      failures.push(`File outside allowlist: ${file}`);
    }
  }

  if (diff.length > maxDiffChars) {
    failures.push(`Diff too large: ${diff.length} chars > ${maxDiffChars}.`);
  }

  return {
    pass: failures.length === 0,
    failures,
    changedFiles,
    diffChars: diff.length,
  };
}

async function main() {
  const repoContext = collectRepoContext();
  writeReport("repo-context.txt", repoContext);

  const seed = readText(seedPath);

  const planner = await callOpenAIJson({
    model: plannerModel,
    system: [
      "You are the GPT prompt writer for Nabla Agent Lab.",
      "Return JSON only.",
      "You do not modify the repository directly.",
      "You write a precise worker prompt for OpenCode Go.",
      "The worker must use JavaScript/Node/ESM only unless the repository clearly requires otherwise.",
      "Do not ask for human confirmation.",
    ].join("\n"),
    user: JSON.stringify({
      task: seed,
      repository_context: repoContext,
      constraints: {
        allowed_paths: allowedPrefixes,
        forbidden_paths: forbiddenPrefixes,
        forbidden_exact_files: forbiddenExact,
        no_human_intervention: true,
        no_dependencies: true,
      },
      required_json_shape: {
        title: "short title",
        worker_prompt: "complete prompt for OpenCode Go",
        expected_files: ["src/math.js", "tests/math.test.mjs"],
        risk_notes: ["short risk note"],
      },
    }),
  });

  if (!planner.worker_prompt) {
    throw new Error("Planner returned no worker_prompt.");
  }

  writeReport("generated-worker-prompt.md", planner.worker_prompt);
  writeReport("planner.json", JSON.stringify(planner, null, 2));

  mustRun("git", ["checkout", "-B", branchName]);

  const opencodeArgs = ["run", "--dangerously-skip-permissions", "--dir", repoRoot, planner.worker_prompt];
  if (env.NABLA_OPENCODE_MODEL) {
    opencodeArgs.splice(1, 0, "--model", env.NABLA_OPENCODE_MODEL);
  }

  const worker = run("opencode", opencodeArgs, { timeout: 1000 * 60 * 20 });
  writeReport("opencode-output.txt", worker.output);

  if (worker.status !== 0) {
    writeReport("final-status.json", JSON.stringify({ status: "failed", reason: "opencode_failed", code: worker.status }, null, 2));
    throw new Error(`OpenCode failed with status ${worker.status}`);
  }

  const changedFiles = getChangedFiles();
  const diff = mustRun("git", ["diff", "--", ...changedFiles]).stdout;
  writeReport("diff.patch", diff);
  writeReport("changed-files.json", JSON.stringify(changedFiles, null, 2));

  const policy = checkPolicy(changedFiles, diff);
  writeReport("policy.json", JSON.stringify(policy, null, 2));

  const test = run("npm", ["test"], { timeout: 1000 * 60 * 5 });
  writeReport("test-output.txt", test.output);

  const audit = await callOpenAIJson({
    model: auditorModel,
    system: [
      "You are the GPT auditor for Nabla Agent Lab.",
      "Return JSON only.",
      "You decide whether an autonomous OpenCode Go change is safe to merge.",
      "Be strict. If there is uncertainty, fail.",
      "Do not ask for human confirmation.",
    ].join("\n"),
    user: JSON.stringify({
      generated_worker_prompt: planner.worker_prompt,
      opencode_output: worker.output.slice(-12000),
      changed_files: changedFiles,
      diff: diff.slice(0, maxDiffChars),
      policy,
      test_status: test.status,
      test_output: test.output.slice(-12000),
      required_json_shape: {
        verdict: "pass or fail",
        confidence: "low, medium, high",
        reasons: ["reason"],
        merge_allowed: true,
      },
    }),
  });

  writeReport("audit.json", JSON.stringify(audit, null, 2));

  const gatesPass = policy.pass && test.status === 0 && audit.verdict === "pass" && audit.merge_allowed === true;

  // Include run reports in the same commit.
  mustRun("git", ["add", "src", "tests", ".nabla-agent/runs"]);

  const staged = run("git", ["diff", "--cached", "--name-only"]);
  const stagedFiles = staged.stdout.split("\n").map((x) => x.trim()).filter(Boolean);

  if (stagedFiles.length === 0) {
    writeReport("final-status.json", JSON.stringify({ status: "failed", reason: "no_staged_files" }, null, 2));
    throw new Error("No staged files after OpenCode run.");
  }

  const commitMessage = `agent: ${planner.title || "autonomous change"}`;
  mustRun("git", ["commit", "-m", commitMessage]);
  mustRun("git", ["push", "--set-upstream", "origin", branchName]);

  if (!repoFullName || !ghToken) {
    writeReport("final-status.json", JSON.stringify({ status: "failed", reason: "missing_github_context", gatesPass }, null, 2));
    throw new Error("GITHUB_REPOSITORY and GITHUB_TOKEN are required to create PRs.");
  }

  const prBody = [
    "Autonomous OpenCode Go run.",
    "",
    `Run ID: ${runId}`,
    `Planner model: ${plannerModel}`,
    `Auditor model: ${auditorModel}`,
    `Policy pass: ${policy.pass}`,
    `Test status: ${test.status}`,
    `Audit verdict: ${audit.verdict}`,
    `Gates pass: ${gatesPass}`,
    "",
    "Reports are committed under `.nabla-agent/runs/`.",
  ].join("\n");

  const prCreate = mustRun("gh", [
    "pr", "create",
    "--repo", repoFullName,
    "--base", baseBranch,
    "--head", branchName,
    "--title", `Agent: ${planner.title || "autonomous change"}`,
    "--body", prBody,
  ]);

  const prUrl = prCreate.stdout.trim();
  writeReport("pr-url.txt", prUrl);

  let finalAction = "pr_created_no_merge";
  if (gatesPass && allowAutoMerge) {
    mustRun("gh", ["pr", "merge", prUrl, "--repo", repoFullName, "--squash", "--delete-branch"]);
    finalAction = "merged";
  }

  writeReport("final-status.json", JSON.stringify({
    status: "completed",
    gatesPass,
    finalAction,
    prUrl,
    policy,
    audit,
  }, null, 2));
}

main().catch((error) => {
  writeReport("fatal-error.txt", error.stack || String(error));
  console.error(error);
  process.exit(1);
});
