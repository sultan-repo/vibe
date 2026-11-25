import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { run } from '../src/cli.js';

function harness() {
  const dir = mkdtempSync(join(tmpdir(), 'tasklog-'));
  const out = [];
  const err = [];
  const io = { file: join(dir, 'log.json'), out: (l) => out.push(l), err: (l) => err.push(l) };
  return { io, out, err, cleanup: () => rmSync(dir, { recursive: true, force: true }) };
}

test('add then report', () => {
  const h = harness();
  try {
    assert.equal(run(['add', 'api', '90', 'auth', 'work'], h.io), 0);
    assert.equal(run(['add', 'site', '30'], h.io), 0);
    h.out.length = 0;
    assert.equal(run(['report'], h.io), 0);
    assert.deepEqual(h.out, ['api    1h 30m', 'site   30m', 'TOTAL  2h 00m']);
  } finally {
    h.cleanup();
  }
});

test('add rejects bad minutes', () => {
  const h = harness();
  try {
    assert.equal(run(['add', 'api', 'lots'], h.io), 2);
    assert.equal(h.err.length, 1);
  } finally {
    h.cleanup();
  }
});

test('unknown command prints usage', () => {
  const h = harness();
  try {
    assert.equal(run(['frobnicate'], h.io), 2);
    assert.match(h.err[0], /Usage/);
  } finally {
    h.cleanup();
  }
});
