import { existsSync, readFileSync, writeFileSync } from 'node:fs';

export function loadEntries(file) {
  if (!existsSync(file)) return [];
  const data = JSON.parse(readFileSync(file, 'utf8'));
  if (!Array.isArray(data)) throw new Error(`${file} is not a tasklog file`);
  return data;
}

export function saveEntries(file, entries) {
  writeFileSync(file, JSON.stringify(entries, null, 2) + '\n');
}

export function addEntry(file, entry) {
  const entries = loadEntries(file);
  entries.push(entry);
  saveEntries(file, entries);
  return entries.length;
}
