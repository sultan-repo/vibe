'use strict';
const http = require('node:http');
const { signIn, currentUser, signOut } = require('./auth');
const entries = require('./entries');
const { page } = require('./render');

function readBody(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    req.on('data', (c) => {
      raw += c;
      if (raw.length > 100000) reject(new Error('too large'));
    });
    req.on('end', () => {
      const type = req.headers['content-type'] || '';
      try {
        if (type.includes('application/json')) return resolve(raw ? JSON.parse(raw) : {});
        const out = {};
        for (const [k, v] of new URLSearchParams(raw)) out[k] = v;
        resolve(out);
      } catch (err) {
        reject(err);
      }
    });
    req.on('error', reject);
  });
}

function json(res, status, body) {
  res.writeHead(status, { 'content-type': 'application/json' });
  res.end(JSON.stringify(body));
}

function createApp(store) {
  return http.createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost');
    const user = currentUser(store, req);
    try {
      // ---- pages ----
      if (req.method === 'GET' && url.pathname === '/') {
        res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
        return res.end(page(entries.listEntries(store), entries.stats(store), user));
      }
      if (req.method === 'POST' && url.pathname === '/signin') {
        const body = await readBody(req);
        const result = signIn(store, body.code);
        if (!result) {
          res.writeHead(303, { location: '/?error=code' });
          return res.end();
        }
        res.writeHead(303, { location: '/', 'set-cookie': `session=${result.token}; HttpOnly; Path=/` });
        return res.end();
      }
      if (req.method === 'POST' && url.pathname === '/entries') {
        if (!user) {
          res.writeHead(303, { location: '/?error=signin' });
          return res.end();
        }
        const body = await readBody(req);
        entries.addEntry(store, user, body.text);
        res.writeHead(303, { location: '/' });
        return res.end();
      }
      if (req.method === 'GET' && url.pathname === '/export.csv') {
        res.writeHead(200, { 'content-type': 'text/csv; charset=utf-8' });
        return res.end(entries.exportCsv(store));
      }

      // ---- api ----
      if (req.method === 'POST' && url.pathname === '/api/signin') {
        const body = await readBody(req);
        const result = signIn(store, body.code);
        return result ? json(res, 200, result) : json(res, 401, { error: 'Unknown invite code.' });
      }
      if (req.method === 'POST' && url.pathname === '/api/signout') {
        signOut(store, req);
        return json(res, 200, { ok: true });
      }
      if (req.method === 'GET' && url.pathname === '/api/me') {
        return user ? json(res, 200, { id: user.id, name: user.name }) : json(res, 401, { error: 'Not signed in.' });
      }
      if (req.method === 'GET' && url.pathname === '/api/entries') {
        return json(res, 200, entries.listEntries(store));
      }
      if (req.method === 'POST' && url.pathname === '/api/entries') {
        if (!user) return json(res, 401, { error: 'Sign in first.' });
        const body = await readBody(req);
        try {
          return json(res, 201, entries.addEntry(store, user, body.text));
        } catch (err) {
          return json(res, 400, { error: err.message });
        }
      }
      if (req.method === 'GET' && url.pathname === '/api/search') {
        return json(res, 200, entries.searchEntries(store, url.searchParams.get('q')));
      }
      if (req.method === 'GET' && url.pathname === '/api/stats') {
        return json(res, 200, entries.stats(store));
      }
      const one = /^\/api\/entries\/(e\d+)$/.exec(url.pathname);
      if (req.method === 'GET' && one) {
        const entry = entries.getEntry(store, one[1]);
        return entry ? json(res, 200, entry) : json(res, 404, { error: 'No such entry.' });
      }

      json(res, 404, { error: 'Not found.' });
    } catch (err) {
      json(res, 500, { error: 'Something went wrong.' });
    }
  });
}

module.exports = { createApp };
