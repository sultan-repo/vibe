'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { signIn, currentUser } = require('../src/auth');
const { freshStore } = require('./helpers');

test('a valid invite code signs in', () => {
  const store = freshStore();
  const result = signIn(store, 'maya-4471');
  assert.equal(result.user.name, 'Aunt Maya');
  assert.match(result.token, /^[a-f0-9]{32}$/);
});

test('an unknown code is refused', () => {
  assert.equal(signIn(freshStore(), 'NOPE-0000'), null);
});

test('currentUser reads the bearer token and the cookie', () => {
  const store = freshStore();
  const { token } = signIn(store, 'OMAR-9020');
  assert.equal(currentUser(store, { headers: { authorization: `Bearer ${token}` } }).id, 'u2');
  assert.equal(currentUser(store, { headers: { cookie: `a=b; session=${token}` } }).id, 'u2');
  assert.equal(currentUser(store, { headers: {} }), null);
});
