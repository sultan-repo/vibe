#!/usr/bin/env node
import { deliveryCharge } from '../src/shipping.js';

const args = process.argv.slice(2);
const express = args.includes('--express');
const total = Number(args.find((a) => !a.startsWith('--')));
try {
  console.log(deliveryCharge(total, { express }).toFixed(2));
} catch (err) {
  console.error(err.message);
  process.exit(2);
}
