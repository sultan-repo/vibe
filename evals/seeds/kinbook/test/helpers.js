'use strict';
const { openStore } = require('../src/store');
const seed = require('../data/seed.json');

function freshStore() {
  return openStore(null, seed);
}

module.exports = { freshStore };
