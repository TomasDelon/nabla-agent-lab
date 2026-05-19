import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";

const promptPath = ".nabla-agent/prompts/next.md";
const apiKey = process.env.OPENROUTER_API_KEY;
const model = process.env.OPENROUTER_MODEL || "deepseek/deepseek-v4-flash:free";

function contentOf(data) {
  const msg = data?.choices?.[0]?.message;
  if (typeof msg?.content === "string" && msg.content.trim()) return msg.content.trim();
  return null;
}

async function writeReport(runDir, prompt, proposal, status) {
  await mkdir(runDir, { recursive: true });
  await writeFile(join(runDir, "prompt.md"), prompt, "utf8");
  await writeFile(join(runDir, "proposal.md"), proposal.trim() + "\n", "utf8");
  await writeFile(join(runDir, "status.json"), JSON.stringify(status, null, 2) + "\n", "utf8");
}

if (!existsSync(promptPath)) throw new Error(`Missing prompt file: ${promptPath}`);
const prompt = await readFile(promptPath, "utf8");
const runId = new Date().toISOString().replace(/[:.]/g, "-");
const runDir = join(".nabla-agent", "runs", runId);

if (!apiKey) {
  await writeReport(runDir, prompt, "OPENROUTER_API_KEY was not available.", {
    runId, stage: "proposal-only", status: "failed", aiCalled: false, model, sourceModified: false
  });
  process.exit(0);
}

const system = [
  "You are in a safe lab workflow.",
  "Do not modify files. Generate a proposal only.",
  "Return a concise file-by-file change proposal for adding subtract(a, b) and tests.",
  "No markdown fences. No secrets."
].join("\n");

let responseText = "";
let data = null;
try {
  const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://github.com/TomasDelon/nabla-agent-lab",
      "X-Title": "Nabla Agent Lab"
    },
    body: JSON.stringify({
      model,
      messages: [
        { role: "system", content: system },
        { role: "user", content: prompt }
      ],
      temperature: 0.1
    })
  });
  responseText = await response.text();
  try { data = JSON.parse(responseText); } catch { data = null; }
  if (!response.ok) {
    await writeReport(runDir, prompt, `OpenRouter request failed with HTTP ${response.status}.`, {
      runId, stage: "proposal-only", status: "failed", aiCalled: true, model, sourceModified: false, httpStatus: response.status
    });
    process.exit(0);
  }
} catch (error) {
  await writeReport(runDir, prompt, `Network request failed: ${error.message}`, {
    runId, stage: "proposal-only", status: "failed", aiCalled: true, model, sourceModified: false, error: error.message
  });
  process.exit(0);
}

const proposal = contentOf(data);
if (!proposal) {
  await writeReport(runDir, prompt, "Provider returned no assistant content.", {
    runId, stage: "proposal-only", status: "failed", aiCalled: true, model, sourceModified: false, error: "missing assistant content"
  });
  process.exit(0);
}

await writeReport(runDir, prompt, proposal, {
  runId, stage: "proposal-only", status: "completed", aiCalled: true, model, sourceModified: false
});
console.log(`Created proposal report at ${runDir}`);
