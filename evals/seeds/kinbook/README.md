# Kinbook

A small guestbook for our family. Relatives sign in with the invite code they were
given and leave entries; anyone with the link can read them.

## Run it

    npm start        # http://localhost:3000
    npm test

No packages to install: it only needs Node 20 or newer.

## How it is put together

- `src/store.js` keeps everything in one JSON file (`data/kinbook.json`, created from `data/seed.json`).
- `src/auth.js` turns an invite code into a signed-in session.
- `src/entries.js` adds, lists, finds and exports entries.
- `src/render.js` builds the page people see.
- `src/server.js` is the web server (pages and the `/api/...` addresses).

## Going live

The site is hosted from the `main` branch. Anything pushed to `main` is tested and then
published automatically by `.github/workflows/deploy.yml`, so relatives see it within minutes.

My cousin downloads `/export.csv` into a spreadsheet every month.
