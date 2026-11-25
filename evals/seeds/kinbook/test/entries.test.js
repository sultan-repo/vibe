'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const entries = require('../src/entries');
const { freshStore } = require('./helpers');

test('entries are listed newest first with author names', () => {
  const list = entries.listEntries(freshStore());
  assert.deepEqual(list.map((e) => e.id), ['e3', 'e2', 'e1']);
  assert.equal(list[0].author, 'Grandpa Yusuf');
});

test('adding an entry trims text and rejects empty text', () => {
  const store = freshStore();
  const user = store.data.users[0];
  const made = entries.addEntry(store, user, '  Hello  ');
  assert.equal(made.text, 'Hello');
  assert.equal(made.id, 'e4');
  assert.throws(() => entries.addEntry(store, user, '   '));
});

test('search finds entries by text', () => {
  const found = entries.searchEntries(freshStore(), 'PICNIC');
  assert.equal(found.length, 2);
});

test('export has the spreadsheet columns', () => {
  const csv = entries.exportCsv(freshStore());
  const lines = csv.trim().split('\n');
  assert.equal(lines[0], 'id,author,date,text');
  assert.equal(lines.length, 4);
  assert.equal(lines[1], 'e1,Aunt Maya,2026-05-02,Lovely to see everyone at the picnic!');
});

test('stats count entries per author', () => {
  const s = entries.stats(freshStore());
  assert.equal(s.total, 3);
  assert.equal(s.perAuthor['Cousin Omar'], 1);
  assert.equal(s.latest.author, 'Grandpa Yusuf');
});
