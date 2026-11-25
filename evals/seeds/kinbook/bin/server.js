#!/usr/bin/env node
'use strict';
const path = require('node:path');
const { openStore } = require('../src/store');
const { createApp } = require('../src/server');

const file = process.env.KINBOOK_DATA || path.join(__dirname, '..', 'data', 'kinbook.json');
const port = Number(process.env.PORT || 3000);
const store = openStore(file);
createApp(store).listen(port, () => {
  console.log(`kinbook listening on http://localhost:${port}`);
});
