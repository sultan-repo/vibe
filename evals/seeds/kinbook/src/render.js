'use strict';

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function page(entries, numbers, user) {
  const items = entries
    .map((e) => `<li id="${esc(e.id)}"><p>${esc(e.text)}</p><small>${esc(e.author)}, ${esc(e.createdAt.slice(0, 10))}</small></li>`)
    .join('\n');
  const latest = numbers.latest
    ? `<p class="latest">Latest: ${esc(numbers.latest.author)} wrote "${esc(numbers.latest.preview)}"</p>`
    : '';
  const who = user
    ? `<p>Signed in as ${esc(user.name)}.</p>
<form method="post" action="/entries"><textarea name="text" required></textarea><button>Add entry</button></form>`
    : `<form method="post" action="/signin"><input name="code" placeholder="Invite code" required><button>Sign in</button></form>`;
  return `<!doctype html>
<html><head><meta charset="utf-8"><title>Kinbook</title></head>
<body>
<h1>Kinbook</h1>
<div class="stats"><p>${numbers.total} entries so far.</p>${latest}</div>
${who}
<ul>
${items}
</ul>
<p><a href="/export.csv">Download as spreadsheet</a></p>
</body></html>
`;
}

module.exports = { page, esc };
