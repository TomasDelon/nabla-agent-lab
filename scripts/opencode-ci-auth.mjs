import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { homedir } from "node:os";

const key = process.env.OPENCODE_GO_KEY;

if (!key) {
  throw new Error("Missing OPENCODE_GO_KEY secret");
}

const authDir = join(homedir(), ".local", "share", "opencode");
const authPath = join(authDir, "auth.json");

await mkdir(authDir, { recursive: true });
await writeFile(
  authPath,
  JSON.stringify({
    "opencode-go": {
      type: "api",
      key
    }
  }, null, 2) + "\n",
  "utf8"
);

console.log(`Wrote OpenCode auth file at ${authPath}`);
