'use strict';

function authorName(store, userId) {
  const user = store.data.users.find((u) => u.id === userId);
  return user ? user.name : 'Someone';
}

function decorate(store, entry) {
  return { ...entry, author: authorName(store, entry.userId) };
}

function addEntry(store, user, text) {
  const clean = String(text || '').trim();
  if (!clean) throw new Error('An entry needs some text.');
  if (clean.length > 2000) throw new Error('That entry is too long.');
  const entry = {
    id: 'e' + store.data.nextEntry++,
    userId: user.id,
    text: clean,
    createdAt: new Date().toISOString(),
  };
  store.data.entries.push(entry);
  store.save();
  return decorate(store, entry);
}

// Newest first.
function listEntries(store) {
  return store.data.entries
    .slice()
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
    .map((e) => decorate(store, e));
}

function getEntry(store, id) {
  const entry = store.data.entries.find((e) => e.id === id);
  return entry ? decorate(store, entry) : null;
}

function searchEntries(store, query) {
  const q = String(query || '').trim().toLowerCase();
  if (!q) return [];
  return store.data.entries
    .filter((e) => e.text.toLowerCase().includes(q))
    .map((e) => decorate(store, e));
}

// Numbers for the little box at the top of the page.
function stats(store) {
  const perAuthor = {};
  for (const e of store.data.entries) {
    const name = authorName(store, e.userId);
    perAuthor[name] = (perAuthor[name] || 0) + 1;
  }
  const newest = store.data.entries
    .slice()
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt))[0];
  return {
    total: store.data.entries.length,
    perAuthor,
    latest: newest ? { author: authorName(store, newest.userId), preview: newest.text.slice(0, 60) } : null,
  };
}

function csvCell(value) {
  const s = String(value);
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

// The monthly spreadsheet export. Columns: id,author,date,text
function exportCsv(store) {
  const rows = [['id', 'author', 'date', 'text']];
  for (const e of store.data.entries) {
    rows.push([e.id, authorName(store, e.userId), e.createdAt.slice(0, 10), e.text]);
  }
  return rows.map((r) => r.map(csvCell).join(',')).join('\n') + '\n';
}

module.exports = { addEntry, listEntries, getEntry, searchEntries, stats, exportCsv };
