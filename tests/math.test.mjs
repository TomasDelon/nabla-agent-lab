import test from "node:test";
import assert from "node:assert/strict";
import { add, subtract, multiply, divide } from "../src/math.js";

test("add returns the sum of two numbers", () => {
  assert.equal(add(2, 3), 5);
});

test("subtract returns the difference of two numbers", () => {
  assert.equal(subtract(10, 5), 5);
  assert.equal(subtract(-10, -5), -5);
  assert.equal(subtract(10, -5), 15);
  assert.equal(subtract(10, 10), 0);
});

test("multiply returns the product of two numbers", () => {
  assert.equal(multiply(2, 3), 6);
  assert.equal(multiply(-2, 3), -6);
  assert.equal(multiply(-2, -3), 6);
  assert.equal(multiply(0, 10), 0);
});

test("divide returns the quotient of two numbers", () => {
  assert.equal(divide(10, 5), 2);
  assert.equal(divide(-10, 5), -2);
  assert.equal(divide(-10, -5), 2);
  assert.equal(divide(5, 2), 2.5);
});
