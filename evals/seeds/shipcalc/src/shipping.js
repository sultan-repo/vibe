const FREE_FROM = 50;
const FLAT_CHARGE = 4.95;
const EXPRESS_EXTRA = 6;

export function deliveryCharge(orderTotal, { express = false } = {}) {
  if (typeof orderTotal !== 'number' || Number.isNaN(orderTotal) || orderTotal < 0) {
    throw new RangeError('order total must be a number, zero or more');
  }
  const base = orderTotal >= FREE_FROM ? 0 : FLAT_CHARGE;
  return express ? base + EXPRESS_EXTRA : base;
}
