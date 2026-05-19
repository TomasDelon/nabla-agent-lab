import { readFile, writeFile } from "node:fs/promises";

const mathPath = "src/math.js";
const testPath = "tests/math.test.mjs";

let math = await readFile(mathPath, "utf8");
let tests = await readFile(testPath, "utf8");

if (!math.includes("export function multiply")) {
  math = `${math.trim()}\n\nexport function multiply(a, b) {\n  return a * b;\n}\n`;
}

if (!tests.includes("multiply")) {
  tests = tests.replace(
    'import { add, subtract } from "../src/math.js";',
    'import { add, subtract, multiply } from "../src/math.js";'
  );
  tests = `${tests.trim()}\n\ntest("multiply returns the product of two numbers", () => {\n  assert.equal(multiply(2, 3), 6);\n  assert.equal(multiply(-2, 3), -6);\n  assert.equal(multiply(-2, -3), 6);\n  assert.equal(multiply(0, 10), 0);\n});\n`;
}

await writeFile(mathPath, math, "utf8");
await writeFile(testPath, tests, "utf8");
console.log("Prepared multiply implementation and tests.");
