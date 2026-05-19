# LAB-002 JavaScript Proposal Only

Goal: generate a proposal for adding subtract(a, b) to this JavaScript Node ESM lab project.

Current project facts:
- package.json has type module and test script node --test.
- src/math.js exports add(a, b).
- tests/math.test.mjs uses node:test and node:assert/strict.
- tests/math.test.mjs imports add from ../src/math.js.

Required proposal:
- update src/math.js to export subtract(a, b);
- update tests/math.test.mjs to import subtract;
- add subtract tests using node:test and node:assert/strict.

Rules:
- proposal only;
- JavaScript only;
- existing files only;
- no Python;
- no new files.
