import test from 'node:test';
import assert from 'node:assert/strict';
import { summarize, renderReport, formatDuration } from '../src/report.js';

const entries = [
  { project: 'site', minutes: 50, note: '' },
  { project: 'api', minutes: 90, note: 'auth' },
  { project: 'site', minutes: 25, note: 'css' },
];

test('summarize totals minutes per project, largest first', () => {
  assert.deepEqual(summarize(entries), {
    projects: [
      { project: 'api', minutes: 90 },
      { project: 'site', minutes: 75 },
    ],
    total: 165,
  });
});

test('formatDuration', () => {
  assert.equal(formatDuration(45), '45m');
  assert.equal(formatDuration(125), '2h 05m');
});

test('renderReport aligns columns and adds a total', () => {
  assert.deepEqual(renderReport(summarize(entries)), [
    'api    1h 30m',
    'site   1h 15m',
    'TOTAL  2h 45m',
  ]);
});

test('renderReport handles an empty log', () => {
  assert.deepEqual(renderReport(summarize([])), ['No entries yet.']);
});
