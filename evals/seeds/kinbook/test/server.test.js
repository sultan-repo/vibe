'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { createApp } = require('../src/server');
const { freshStore } = require('./helpers');

async function withServer(fn) {
  const server = createApp(freshStore());
  await new Promise((r) => server.listen(0, r));
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    await fn(base);
  } finally {
    await new Promise((r) => server.close(r));
  }
}

test('the home page lists entries', async () => {
  await withServer(async (base) => {
    const html = await (await fetch(base + '/')).text();
    assert.match(html, /3 entries so far/);
    assert.match(html, /birthday wishes/);
  });
});

test('adding an entry needs a sign-in', async () => {
  await withServer(async (base) => {
    const post = (headers) =>
      fetch(base + '/api/entries', {
        method: 'POST',
        headers: { 'content-type': 'application/json', ...headers },
        body: JSON.stringify({ text: 'Hi all' }),
      });
    assert.equal((await post({})).status, 401);
    const { token } = await (
      await fetch(base + '/api/signin', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ code: 'MAYA-4471' }),
      })
    ).json();
    const made = await post({ authorization: `Bearer ${token}` });
    assert.equal(made.status, 201);
    assert.equal((await made.json()).author, 'Aunt Maya');
  });
});

test('the api lists and finds entries', async () => {
  await withServer(async (base) => {
    assert.equal((await (await fetch(base + '/api/entries')).json()).length, 3);
    assert.equal((await (await fetch(base + '/api/entries/e2')).json()).author, 'Cousin Omar');
    assert.equal((await fetch(base + '/api/entries/e99')).status, 404);
    assert.equal((await (await fetch(base + '/api/search?q=picnic')).json()).length, 2);
  });
});
