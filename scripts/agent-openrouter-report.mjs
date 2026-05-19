import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";

const promptPath = ".nabla-agent/prompts/next.md";
const apiKey = process.env.OPENROUTER_API_KEY;
const model = process.env.OPENROUTER_MODEL || "deepseek/deepseek-chat-v3.1:free";

if (!existsSync(promptPath)) {
  throw new Error(`Missing prompt file: ${promptPath}`);
}

if (!apiKey) {
  throw new Error("Missing OPENROUTER_API_KEY secret");
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
      { role: "system", content: systemPrompt },
      { role: "user", content: prompt }
    ],
    temperature: 0.2
  })
});

const responseText = await response.text();
let data;
try {
  data = JSON.parse(responseText);
} catch {
  data = null;
}

if (!response.ok) {
  const message = data?.error?.message || responseText;
  throw new Error(`OpenRouter request failed with ${response.status}: ${message}`);
}

const output = data?.choices?.[0]?.message?.content;
if (!output) {
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

console.log(`Created OpenRouter report at ${runDir}`);
