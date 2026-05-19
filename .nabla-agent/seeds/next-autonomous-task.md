# Next Autonomous Task

Add a JavaScript ESM function named `mod(a, b)` to the fake math module.

Requirements:

- Edit `src/math.js`.
- Export `mod`.
- Add tests in `tests/math.test.mjs` using `node:test` and `node:assert/strict`.
- Keep the project JavaScript/Node/ESM only.
- Do not use Python.
- Do not add dependencies.
- Do not edit workflow files.
- Do not edit package.json unless strictly necessary.

Expected behavior:

- `mod(10, 3)` returns `1`.
- `mod(12, 4)` returns `0`.
- `mod(-10, 3)` follows JavaScript `%` semantics and returns `-1`.
