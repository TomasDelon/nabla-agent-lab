import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";

const promptPath = ".nabla-agent/prompts/next.md";
const apiKey = process.env.OPENROUTER_API_KEY;
const model = process.env.OPENROUTER_MODEL || "deepseek/deepseek-v4-flash:free";

function sanitize(value) {
  return String(value)
    .replace(/sk-or-v1-[A-Za-z0-9_-]+/g, "[REDACTED_OPENROUTER_KEY]")
    .replace(/Bearer\s+[A-Za-z0-9._~+/-]+/g, "Bearer [REDACTED]");
}

async function fetchModelCandidates() {
  try {
    const response = await fetch("https://openrouter.ai/api/v1/models");
    const text = await response.text();
    const data = JSON.parse(text);
    const models = Array.isArray(data?.data) ? data.data : [];
    return models
      .filter((entry) => {
        const id = String(entry?.id || "").toLowerCase();
        const name = String(entry?.name || "").toLowerCase();
        return (id.includes("deepseek") || name.includes("deepseek")) && (id.includes(":free") || name.includes("free"));
      })
      .map((entry) => `${entry.id}${entry.name ? ` — ${entry.name}` : ""}`)
      .slice(0, 20);
  } catch (error) {
    return [`Could not fetch model candidates: ${sanitize(error.message)}`];
  }
}

if (!existsSync(promptPath)) {
  throw new Error(`Missing prompt file: ${promptPath}`);
}

console.log(`Prompt path: ${promptPath}`);
console.log(`Selected OpenRouter model: ${model}`);
console.log(`OPENROUTER_API_KEY present: ${apiKey ? "yes" : "no"}`);
console.log(`OPENROUTER_API_KEY length: ${apiKey ? apiKey.length : 0}`);

if (!apiKey) {
  throw new Error("Missing OPENROUTER_API_KEY secret. Add it under repository Settings > Secrets and variables > Actions.");
}

const prompt = await readFile(promptPath, "utf8");
const runId = new Date().toISOString().replace(/[:.]/g, "-");
const runDir = join(".nabla-agent", "runs", runId);

const systemPrompt = [
  "You are running inside Nabla Agent Lab Stage 2.",
  "You must not modify code.",
  "You must answer with a concise implementation plan only.",
  "Do not include secrets, credentials, or hidden chain-of-thought.",
  "The requested output is for a lab report, not for direct execution."
].join("\n");

let response;
try {
  response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
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
        { role: "system", content: systemPrompt },
        { role: "user", content: prompt }
      ],
      temperature: 0.2
    })
  });
} catch (error) {
  throw new Error(`OpenRouter network request failed: ${sanitize(error.message)}`);
}

const responseText = await response.text();
let data;
try {
  data = JSON.parse(responseText);
} catch {
  data = null;
}

if (!response.ok) {
  const message = sanitize(data?.error?.message || responseText);
  console.log(`OpenRouter status: ${response.status}`);
  console.log(`OpenRouter error: ${message}`);
  const candidates = await fetchModelCandidates();
  console.log("Available DeepSeek free model candidates:");
  for (const candidate of candidates) {
    console.log(`- ${candidate}`);
  }
  throw new Error(`OpenRouter request failed with ${response.status}. See sanitized diagnostics above.`);
}

const output = data?.choices?.[0]?.message?.content;
if (!output) {
  console.log(`OpenRouter raw response: ${sanitize(responseText).slice(0, 2000)}`);
  throw new Error("OpenRouter response did not contain choices[0].message.content");
}

await mkdir(runDir, { recursive: true });
await writeFile(join(runDir, "prompt.md"), prompt, "utf8");
await writeFile(join(runDir, "output.md"), output.trim() + "\n", "utf8");
await writeFile(
  join(runDir, "status.json"),
  JSON.stringify(
    {
      runId,
      stage: "openrouter-report-only",
      status: "completed",
      aiCalled: true,
      model,
      sourceModified: false,
      promptPath
    },
    null,
    2
  ) + "\n",
  "utf8"
);

console.log(`OpenRouter status: ${response.status}`);
console.log(`Created OpenRouter report at ${runDir}`);
