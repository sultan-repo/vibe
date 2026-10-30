import test from 'node:test'
import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { resolve } from 'node:path'

const runner=resolve('scripts/compare-performance.mjs')
test('dry run alternates identical tasks across both conditions without model calls',()=>{
 const proc=spawnSync(process.execPath,[runner,'--dry-run','--rounds','2'],{encoding:'utf8'})
 assert.equal(proc.status,0,proc.stderr)
 const data=JSON.parse(proc.stdout)
 assert.equal(data.invocations,8)
 assert.equal(data.plan[0].arm,'plain')
 assert.equal(data.plan[1].arm,'vibe')
 assert.equal(data.plan[4].arm,'vibe')
 assert.equal(data.plan[5].arm,'plain')
 assert.equal(data.plan.filter(x=>x.arm==='plain').length,4)
 assert.equal(data.plan.filter(x=>x.arm==='vibe').length,4)
})
test('invalid rounds fail before invoking Claude',()=>{
 const proc=spawnSync(process.execPath,[runner,'--dry-run','--rounds','0'],{encoding:'utf8'})
 assert.notEqual(proc.status,0)
})
