#!/usr/bin/env node
import { run } from '../src/cli.js';

const code = run(process.argv.slice(2), {
  file: process.env.TASKLOG_FILE || 'tasklog.json',
  out: (line) => console.log(line),
  err: (line) => console.error(line),
});
process.exitCode = code;
