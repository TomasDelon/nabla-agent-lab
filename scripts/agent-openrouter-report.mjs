import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";

const promptPath = ".nabla-agent/prompts/next.md";
const apiKey = process.env.OPENROUTER_API_KEY;
const requestedModel = process.env.OPENROUTER_MODEL || "auto-deepseek-free";

function sanitize(value) {
  return String(value)
    .replace(/sk-or-v1-[A-Za-z0-9_-]+/g, "[REDACTED_OPENROUTER_KEY]")
    .replace(/Bearer\s+[A-Za-z0-9._~+/-]+/g, "Bearer [REDACTED]");
}

async function fetchModels() {
  const response = await fetch("https://openrouter.ai/api/v1/models");
  const text = await response.text();
  const data = JSON.parse(text);
  return Array.isArray(data?.data) ? data.data : [];
}

function isFreeDeepSeek(entry) {
  const id = String(entry?.id || "").toLowerCase();
  const name = String(entry?.name || "").toLowerCase();
  return (id.includes("deepseek") || name.includes("deepseek")) && (id.includes(":free") || name.includes("free"));
}

function rankDeepSeek(entry) {
  const text = `${entry?.id || ""} ${entry?.name || ""}`.toLowerCase();
  let score = 0;
  if (text.includes("chat")) score += 100;
  if (text.includes("v3")) score += 50;
  if (text.includes("v4")) score += 40;
  if (text.includes("flash")) score += 20;
  if (text.includes("r1")) score -= 20;
  return score;
}

async function resolveModel(inputModel) {
  if (inputModel !== "auto-deepseek-free") {
    return { selectedModel: inputModel, candidates: [] };
  }

  try {
    const models = await fetchModels();
    const candidates = models
      .filter(isFreeDeepSeek)
      .sort((a, b) => rankDeepSeek(b) - rankDeepSeek(a));

    return {
      selectedModel: candidates[0]?.id || "deepseek/deepseek-chat:free",
      candidates: candidates.map((entry) => `${entry.id}${entry.name ? ` — ${entry.name}` : ""}`).slice(0, 20)
    };
  } catch (error) {
    return {
      selectedModel: "deepseek/deepseek-chat:free",
      candidates: [`Could not fetch model list: ${sanitize(error.message)}`]
    };
  }
}

async function writeRunReport({ runDir, prompt, output, status }) {
  await mkdir(runDir, { recursive: true });
  await writeFile(join(runDir, "prompt.md"), prompt, "utf8");
  await writeFile(join(runDir, "output.md"), output.trim() + "\n", "utf8");
  await writeFile(join(runDir, "status.json"), JSON.stringify(status, null, 2) + "\n", "utf8");
}

function getAssistantContent(data) {
  const message = data?.choices?.[0]?.message;
  if (typeof message?.content === "string" && message.content.trim()) {
    return message.content;
  }
  if (Array.isArray(message?.content)) {
    const text = message.content
      .map((part) => typeof part?.text === "string" ? part.text : "")
      .join("\n")
      .trim();
    if (text) return text;
  }
  return null;
}

if (!existsSync(promptPath)) {
  throw new Error(`Missing prompt file: ${promptPath}`);
}

const prompt = await readFile(promptPath, "utf8");
const runId = new Date().toISOString().replace(/[:.]/g, "-");
const runDir = join(".nabla-agent", "runs", runId);
const { selectedModel, candidates } = await resolveModel(requestedModel);

console.log(`Prompt path: ${promptPath}`);
console.log(`Requested OpenRouter model: ${requestedModel}`);
console.log(`Selected OpenRouter model: ${selectedModel}`);
console.log(`OPENROUTER_API_KEY present: ${apiKey ? "yes" : "no"}`);
console.log(`OPENROUTER_API_KEY length: ${apiKey ? apiKey.length : 0}`);
if (candidates.length) {
  console.log("DeepSeek free candidates discovered:");
  for (const candidate of candidates) console.log(`- ${candidate}`);
}

if (!apiKey) {
  await writeRunReport({
    runDir,
    prompt,
    output: "# OpenRouter Report Failed\n\nOPENROUTER_API_KEY was not available to the workflow.\n",
    status: {
      runId,
      stage: "openrouter-report-only",
      status: "failed",
      aiCalled: false,
      requestedModel,
      selectedModel,
      sourceModified: false,
      promptPath,
      error: "Missing OPENROUTER_API_KEY secret"
    }
  });
  console.log(`Created failed report at ${runDir}`);
  process.exit(0);
}

const systemPrompt = [
  "You are running inside Nabla Agent Lab Stage 2.",
  "You must not modify code.",
  "You must answer with a concise implementation plan only.",
  "Do not include secrets, credentials, or hidden chain-of-thought.",
  "The requested output is for a lab report, not for direct execution."
].join("\n");

let response;
let responseText = "";
let data = null;
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
      model: selectedModel,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: prompt }
      ],
      temperature: 0.2
    })
  });
  responseText = await response.text();
  try {
    data = JSON.parse(responseText);
  } catch {
    data = null;
  }
} catch (error) {
  const message = sanitize(error.message);
  await writeRunReport({
    runDir,
    prompt,
    output: `# OpenRouter Report Failed\n\nNetwork request failed.\n\n${message}\n`,
    status: {
      runId,
      stage: "openrouter-report-only",
      status: "failed",
      aiCalled: true,
      requestedModel,
      selectedModel,
      sourceModified: false,
      promptPath,
      error: message
    }
  });
  console.log(`Created failed report at ${runDir}`);
  process.exit(0);
}

if (!response.ok) {
  const message = sanitize(data?.error?.message || responseText);
  await writeRunReport({
    runDir,
    prompt,
    output: [
      "# OpenRouter Report Failed",
      "",
      `HTTP status: ${response.status}`,
      "",
      `Error: ${message}`,
      "",
      `Requested model: ${requestedModel}`,
      `Selected model: ${selectedModel}`,
      "",
      "DeepSeek free candidates discovered:",
      ...(candidates.length ? candidates.map((candidate) => `- ${candidate}`) : ["- none"]),
      ""
    ].join("\n"),
    status: {
      runId,
      stage: "openrouter-report-only",
      status: "failed",
      aiCalled: true,
      requestedModel,
      selectedModel,
      sourceModified: false,
      promptPath,
      httpStatus: response.status,
      error: message,
      candidates
    }
  });
  console.log(`OpenRouter status: ${response.status}`);
  console.log(`OpenRouter error: ${message}`);
  console.log(`Created failed report at ${runDir}`);
  process.exit(0);
}

const output = getAssistantContent(data);
if (!output) {
  await writeRunReport({
    runDir,
    prompt,
    output: [
      "# OpenRouter Report Failed",
      "",
      "The provider returned a response without assistant content.",
      "",
      `Requested model: ${requestedModel}`,
      `Selected model: ${selectedModel}`,
      "",
      "The raw provider response was intentionally not persisted because it may contain reasoning-only fields.",
      "Use a chat/content model or rerun with auto-deepseek-free.",
      ""
    ].join("\n"),
    status: {
      runId,
      stage: "openrouter-report-only",
      status: "failed",
      aiCalled: true,
      requestedModel,
      selectedModel,
      sourceModified: false,
      promptPath,
      error: "Missing assistant content"
    }
  });
  console.log("OpenRouter response had no assistant content. Raw response was not persisted.");
  console.log(`Created failed report at ${runDir}`);
  process.exit(0);
}

await writeRunReport({
  runDir,
  prompt,
  output,
  status: {
    runId,
    stage: "openrouter-report-only",
    status: "completed",
    aiCalled: true,
    requestedModel,
    selectedModel,
    sourceModified: false,
    promptPath
  }
});

console.log(`OpenRouter status: ${response.status}`);
console.log(`Created OpenRouter report at ${runDir}`);
