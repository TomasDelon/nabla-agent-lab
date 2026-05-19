import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";

const promptPath = ".nabla-agent/prompts/next.md";

if (!existsSync(promptPath)) {
  throw new Error(`Missing prompt file: ${promptPath}`);
}

const prompt = await readFile(promptPath, "utf8");
const runId = new Date().toISOString().replace(/[:.]/g, "-");
const runDir = join(".nabla-agent", "runs", runId);

await mkdir(runDir, { recursive: true });

await writeFile(join(runDir, "prompt.md"), prompt, "utf8");

await writeFile(
  join(runDir, "output.md"),
  [
    "# Dry Run Output",
    "",
    "This is a fake runner output.",
    "",
    "No AI model was called.",
    "No source code was modified.",
    "",
    "A later stage may ask an agent to add `subtract(a, b)`, but this dry run only verifies the orchestration path.",
    ""
  ].join("\n"),
  "utf8"
);

await writeFile(
  join(runDir, "status.json"),
  JSON.stringify(
    {
      runId,
      stage: "dry-run",
      status: "completed",
      aiCalled: false,
      sourceModified: false,
      promptPath
    },
    null,
    2
  ) + "\n",
  "utf8"
);

console.log(`Created dry-run report at ${runDir}`);
