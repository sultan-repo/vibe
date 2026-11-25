import test from 'node:test';
import assert from 'node:assert/strict';
import { deliveryCharge } from '../src/shipping.js';

test('small order pays the flat charge', () => {
  assert.equal(deliveryCharge(20), 4.95);
});

test('order just under 50', () => {
  assert.equal(deliveryCharge(49.99), 4.95);
});

test('order of exactly 50', () => {
  assert.equal(deliveryCharge(50), 4.95);
});

test('large order is delivered free', () => {
  assert.equal(deliveryCharge(120), 0);
});

test('express adds 6.00 to a small order', () => {
  assert.equal(deliveryCharge(20, { express: true }), 10.95);
});

test('express adds 6.00 to a free-delivery order', () => {
  assert.equal(deliveryCharge(120, { express: true }), 6);
});

test('negative totals are refused', () => {
  assert.throws(() => deliveryCharge(-1), RangeError);
});
