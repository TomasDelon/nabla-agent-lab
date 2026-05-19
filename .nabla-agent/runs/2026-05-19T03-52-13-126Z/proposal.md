Update src/math.js to include the following code:
export function subtract(a, b) {
  return a - b;
}

Update tests/math.test.mjs to include the following code:
import { add, subtract } from '../src/math.js';

Add the following tests to tests/math.test.mjs:
test('subtract positive numbers', () => {
  assert.strictEqual(subtract(10, 5), 5);
});

test('subtract negative numbers', () => {
  assert.strictEqual(subtract(-10, -5), -5);
});

test('subtract mixed numbers', () => {
  assert.strictEqual(subtract(10, -5), 15);
});

test('subtract same numbers', () => {
  assert.strictEqual(subtract(10, 10), 0);
});
