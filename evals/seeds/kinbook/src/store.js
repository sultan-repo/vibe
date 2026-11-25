'use strict';
const fs = require('node:fs');
const path = require('node:path');

const SEED = path.join(__dirname, '..', 'data', 'seed.json');

// Everything lives in one JSON file. `file` may be null for an in-memory store (tests).
function openStore(file, seed) {
  let data;
  if (file && fs.existsSync(file)) {
    data = JSON.parse(fs.readFileSync(file, 'utf8'));
  } else {
    data = seed ? JSON.parse(JSON.stringify(seed)) : JSON.parse(fs.readFileSync(SEED, 'utf8'));
  }
  function save() {
    if (!file) return;
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, JSON.stringify(data, null, 2));
  }
  return { data, save };
}

module.exports = { openStore };
