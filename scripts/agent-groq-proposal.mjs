import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";

const promptPath = ".nabla-agent/prompts/next.md";
const apiKey = process.env.GROQ_API_KEY;
const requestedModel = process.env.GROQ_MODEL || "llama-3.3-70b-versatile";

const fallbackModels = [
  "llama-3.3-70b-versatile",
  "openai/gpt-oss-20b",
  "llama-3.1-8b-instant"
];

function getText(data) {
  const msg = data?.choices?.[0]?.message;
  if (typeof msg?.content === "string" && msg.content.trim()) return msg.content.trim();
  return null;
}

function modelsFor(input) {
  if (input === "auto-groq") return fallbackModels;
  return [input, ...fallbackModels.filter((m) => m !== input)];
}

async function writeReport(runDir, prompt, proposal, status) {
  await mkdir(runDir, { recursive: true });
  await writeFile(join(runDir, "prompt.md"), prompt, "utf8");
  await writeFile(join(runDir, "proposal.md"), proposal.trim() + "\n", "utf8");
  await writeFile(join(runDir, "status.json"), JSON.stringify(status, null, 2) + "\n", "utf8");
}

async function ask(model, system, prompt) {
  const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
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
  const body = await response.text();
  let data = null;
  try { data = JSON.parse(body); } catch { data = null; }
  if (!response.ok) return { ok: false, model, httpStatus: response.status, error: data?.error?.message || `HTTP ${response.status}` };
  const text = getText(data);
  if (!text) return { ok: false, model, httpStatus: response.status, error: "missing assistant content" };
  return { ok: true, model, text };
}

if (!existsSync(promptPath)) throw new Error(`Missing prompt file: ${promptPath}`);
const prompt = await readFile(promptPath, "utf8");
const runId = new Date().toISOString().replace(/[:.]/g, "-");
const runDir = join(".nabla-agent", "runs", runId);
const candidates = modelsFor(requestedModel);

if (!apiKey) {
  await writeReport(runDir, prompt, "GROQ_API_KEY was not available.", {
    runId,
    stage: "groq-proposal-only",
    status: "failed",
    aiCalled: false,
    requestedModel,
    sourceModified: false
  });
  process.exit(0);
}

const system = [
  "You are in a safe lab workflow.",
  "Do not modify files. Generate a proposal only.",
  "Return a concise file-by-file proposal for adding subtract(a, b) and tests.",
  "No markdown fences. No credentials."
].join("\n");

const attempts = [];
let winner = null;
for (const model of candidates) {
  console.log(`Trying Groq model: ${model}`);
  try {
    const result = await ask(model, system, prompt);
    attempts.push(result.ok ? { model, ok: true } : { model, ok: false, httpStatus: result.httpStatus, error: result.error });
    if (result.ok) {
      winner = result;
      break;
    }
  } catch (error) {
    attempts.push({ model, ok: false, error: error.message });
  }
}

if (!winner) {
  await writeReport(runDir, prompt, [
    "# Groq Proposal Failed",
    "",
    "All configured Groq models failed.",
    "",
    ...attempts.map((a) => `- ${a.model}: ${a.ok ? "ok" : `failed${a.httpStatus ? ` HTTP ${a.httpStatus}` : ""}${a.error ? ` — ${a.error}` : ""}`}`)
  ].join("\n"), {
    runId,
    stage: "groq-proposal-only",
    status: "failed",
    aiCalled: true,
    requestedModel,
    modelsTried: attempts,
    sourceModified: false
  });
  process.exit(0);
}

await writeReport(runDir, prompt, winner.text, {
  runId,
  stage: "groq-proposal-only",
  status: "completed",
  aiCalled: true,
  requestedModel,
  selectedModel: winner.model,
  modelsTried: attempts,
  sourceModified: false
});
console.log(`Created Groq proposal report at ${runDir}`);
