'use strict';
const crypto = require('node:crypto');

// Sign in with an invite code. Returns { token, user } or null.
function signIn(store, code) {
  const wanted = String(code || '').trim().toUpperCase();
  const user = store.data.users.find((u) => u.inviteCode === wanted);
  if (!user) return null;
  const token = crypto.randomBytes(16).toString('hex');
  store.data.sessions.push({ token, userId: user.id, createdAt: new Date().toISOString() });
  store.save();
  return { token, user: { id: user.id, name: user.name } };
}

// Who is making this request? Looks at "Authorization: Bearer <token>" and the "session" cookie.
function currentUser(store, req) {
  let token = null;
  const header = req.headers['authorization'];
  if (header && header.startsWith('Bearer ')) token = header.slice(7).trim();
  if (!token && req.headers.cookie) {
    const m = /(?:^|;\s*)session=([a-f0-9]+)/.exec(req.headers.cookie);
    if (m) token = m[1];
  }
  if (!token) return null;
  const session = store.data.sessions.find((s) => s.token === token);
  if (!session) return null;
  return store.data.users.find((u) => u.id === session.userId) || null;
}

function signOut(store, req) {
  const header = req.headers['authorization'] || '';
  const token = header.startsWith('Bearer ') ? header.slice(7).trim() : null;
  store.data.sessions = store.data.sessions.filter((s) => s.token !== token);
  store.save();
}

module.exports = { signIn, currentUser, signOut };
