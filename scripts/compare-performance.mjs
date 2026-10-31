#!/usr/bin/env node
// Run matched Claude Code coding tasks only when invoked by the user.
import { spawnSync } from 'node:child_process'
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const plugin=resolve(dirname(fileURLToPath(import.meta.url)),'..')
const args=process.argv.slice(2)
const flag=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1]}
const rounds=Number(flag('--rounds','3'))
const model=flag('--model','sonnet')
const output=resolve(flag('--output','vibe-benchmark-results.json'))
if(!Number.isInteger(rounds)||rounds<1||rounds>10)throw Error('rounds must be 1..10')
const tasks=[
 {id:'unique-words',source:"export function uniqueWords(text) { return text.trim().split(/\\s+/) }\n",
 test:"import test from 'node:test';import assert from 'node:assert/strict';import {uniqueWords} from './lib.js';test('normalizes unique words',()=>{assert.deepEqual(uniqueWords('Hi, hi! THERE there'),['hi','there']);assert.deepEqual(uniqueWords(''),[]);assert.deepEqual(uniqueWords('Red blue red'),['red','blue'])})\n",
 prompt:"Fix uniqueWords in lib.js to pass the existing tests. Ignore punctuation, normalize case, keep the first occurrence. Run node --test. Do not edit tests."},
 {id:'chunk',source:"export function chunk(items,size) { return [items] }\n",
 test:"import test from 'node:test';import assert from 'node:assert/strict';import {chunk} from './lib.js';test('chunks and validates',()=>{assert.deepEqual(chunk([1,2,3,4,5],2),[[1,2],[3,4],[5]]);assert.deepEqual(chunk([],3),[]);assert.throws(()=>chunk([1],0),RangeError);assert.throws(()=>chunk([1],1.2),RangeError)})\n",
 prompt:"Fix chunk in lib.js to pass the existing tests, reject invalid sizes with RangeError and avoid empty chunks. Run node --test. Do not edit tests."}
]
const plan=[]
for(let r=0;r<rounds;r++)for(const task of tasks)for(const arm of (r%2?['vibe','plain']:['plain','vibe']))plan.push({round:r+1,task:task.id,arm})
if(args.includes('--dry-run')){console.log(JSON.stringify({model,rounds,invocations:plan.length,plan,warning:'No model calls made. Actual runs consume Claude usage.'},null,2));process.exit(0)}
const version=spawnSync('claude',['--version'],{encoding:'utf8'})
if(version.status!==0)throw Error('Claude Code is not installed/authenticated on PATH')
const results=[]
for(const run of plan){
 const task=tasks.find(t=>t.id===run.task)
 const dir=mkdtempSync(join(tmpdir(),'vibe-compare-'))
 try{
  mkdirSync(dir,{recursive:true})
  writeFileSync(join(dir,'package.json'),'{"type":"module"}\n')
  writeFileSync(join(dir,'lib.js'),task.source)
  writeFileSync(join(dir,'lib.test.js'),task.test)
  const argv=['-p',task.prompt,'--output-format','json','--model',model,'--max-turns','12',
    '--permission-mode','acceptEdits','--setting-sources','project,local',
    '--allowedTools','Read','Edit','Write','Bash(node --test:*)']
  if(run.arm==='vibe')argv.unshift('--plugin-dir',plugin)
  const started=process.hrtime.bigint()
  const r=spawnSync('claude',argv,{cwd:dir,encoding:'utf8',timeout:180000,maxBuffer:8000000,
    env:{...process.env,CLAUDE_CODE_SKIP_PROMPT_HISTORY:'1'}})
  const wall_ms=Number((process.hrtime.bigint()-started)/1000000n)
  let data={};try{data=JSON.parse(r.stdout)}catch{}
  const checked=spawnSync('node',['--test'],{cwd:dir,encoding:'utf8',timeout:15000})
  const row={...run,wall_ms,turns:data.num_turns??null,
    input_tokens:data.usage?.input_tokens??null,output_tokens:data.usage?.output_tokens??null,
    cache_read_tokens:data.usage?.cache_read_input_tokens??null,
    total_cost_usd:data.total_cost_usd??null,
    passed:r.status===0&&data.is_error!==true&&checked.status===0,
    cli_exit:r.status,test_exit:checked.status,error:String(r.error?.message??r.stderr??'').slice(0,300)}
  results.push(row)
  console.log(run.arm,run.task,'#'+run.round,wall_ms+'ms',row.passed?'PASS':'FAIL')
 }finally{rmSync(dir,{recursive:true,force:true})}
}
const median=values=>{if(!values.length)return null;const v=[...values].sort((a,b)=>a-b);return(v[(v.length-1)>>1]+v[v.length>>1])/2}
const summary=Object.fromEntries(['plain','vibe'].map(arm=>{
 const subset=results.filter(r=>r.arm===arm)
 return[arm,{attempts:subset.length,passed:subset.filter(r=>r.passed).length,
   median_wall_ms:median(subset.map(r=>r.wall_ms)),
   median_turns:median(subset.map(r=>r.turns).filter(Number.isFinite)),
   median_output_tokens:median(subset.map(r=>r.output_tokens).filter(Number.isFinite))}]
}))
const delta=summary.plain.median_wall_ms?Math.round((summary.vibe.median_wall_ms/summary.plain.median_wall_ms-1)*1000)/10:null
writeFileSync(output,JSON.stringify({created_at:new Date().toISOString(),model,rounds,cli_version:version.stdout.trim(),
 summary,vibe_wall_time_change_percent:delta,results,
 note:'Positive change means Vibe slower. Headless runs do not test graphical UI. Confirm plain arm has no Vibe settings.'},null,2)+'\n')
console.log('Saved:',output,' Vibe relative wall time:',delta===null?'unavailable':delta+'%')
