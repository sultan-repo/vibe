import test from 'node:test'
import assert from 'node:assert/strict'
import { register, clean, normalizeSteps, progressOf, taskIdFromResult } from '../hooks/board.mjs'

function harness() {
  const hooks = []
  const calls = { opened: [], invalidated: 0, registered: [] }
  const ui = {
    open: async opts => { calls.opened.push(opts); return { isPlaced: true } },
    close: async () => {},
    invalidate: () => { calls.invalidated++ },
    resolve: () => Object.fromEntries(['Box','Text','Button'].map(name => [name, props => ({type:name,...props})]))
  }
  const $ = { ui, command: { register: async v => calls.registered.push(v) },
    tool: { register: async v => calls.registered.push(v) } }
  register((event, matcher, fn) => {
    if (typeof matcher === 'function') { fn = matcher; matcher = null }
    hooks.push({ event, matcher, fn })
  })
  async function fire(name, e = {}, nextResult = {}) {
    const h = hooks.find(h => h.event === name &&
      (!h.matcher || Object.entries(h.matcher).every(([k, v]) => e[k] === v)))
    assert.ok(h, 'hook not found: ' + name)
    return h.fn($, e, async () => nextResult)
  }
  const render = async () => fire('ui.render', {component:'Pane',requestId:'vibe-board'})
  return { $, calls, fire, render }
}
const text = tree => JSON.stringify(tree)
test('sanitization and status counts do not invent a plan', () => {
  assert.equal(clean('Hello\nworld'), 'Hello world')
  assert.deepEqual(normalizeSteps(null), [])
  assert.equal(progressOf([]).percent, null)
  assert.deepEqual(progressOf([{status:'completed'},{status:'pending'}]),
    {done:1,total:2,percent:50})
})
test('registers optional command and progress tool', async () => {
  const h = harness()
  await h.fire('session.start')
  assert.equal(h.calls.registered[0].name,'progress')
  assert.equal(h.calls.registered[0].isDeferred,true)
  assert.equal(h.calls.registered[1].name,'vibe-board')
  assert.equal(h.calls.registered[1].immediate,true)
})
test('tracks native todos and does not count denied changes', async () => {
  const h = harness()
  const todo = {tool:'TodoWrite',todos:[
    {content:'Build login',status:'completed'},
    {content:'Test login',status:'in_progress'}
  ]}
  await h.fire('tool.call',todo,{result:{ok:true}})
  assert.ok(text(await h.render()).includes('1 of 2 planned steps finished'))
  assert.equal(h.calls.opened.length,1)
  await h.fire('tool.call',{tool:'TodoWrite',todos:[{content:'Bad',status:'completed'}]},
    {deny:'permission denied'})
  assert.match(text(await h.render()),/Build login/)
  assert.doesNotMatch(text(await h.render()),/Bad/)
})
test('tracks native task create and update by returned id', async () => {
  const h = harness()
  await h.fire('tool.call',{tool:'TaskCreate',subject:'Write tests'},
    {result:{taskId:'7',success:true}})
  await h.fire('tool.call',{tool:'TaskUpdate',taskId:'7',status:'completed'},
    {result:{success:true}})
  assert.ok(text(await h.render()).includes('1 of 1 planned steps finished'))
  await h.fire('tool.call',{tool:'TaskUpdate',taskId:'7',status:'deleted'},
    {result:{success:true}})
  assert.match(text(await h.render()),/Your plan will appear here/)
})
test('native TaskList reconciles the plan and preserves the goal and tool result', async () => {
  for (const wrap of [tasks => ({result:{tasks}}), tasks => ({tasks})]) {
    const h = harness()
    await h.fire('tool.call',{tool:'mcp__vibe__progress',goal:'Account settings',steps:[
      {id:'old',label:'Outdated step',status:'pending'} ]})
    const result = wrap([
      {id:'1',subject:'Build settings UI',status:'completed'},
      {id:'2',subject:'Verify settings API',status:'in_progress'}
    ])
    assert.equal(await h.fire('tool.call',{tool:'TaskList'},result),result)
    const rendered = text(await h.render())
    assert.match(rendered,/Account settings/)
    assert.match(rendered,/1 of 2 planned steps finished/)
    assert.match(rendered,/Verify settings API/)
    assert.doesNotMatch(rendered,/Outdated step/)
    assert.equal(h.calls.opened.length,1)
  }
})
test('an empty successful TaskList clears stale progress without opening the board', async () => {
  const h = harness()
  await h.fire('tool.call',{tool:'TaskList'},{result:{tasks:[]}})
  assert.equal(h.calls.opened.length,0)
  await h.fire('tool.call',{tool:'TaskCreate',subject:'Old task'},{result:{taskId:'1'}})
  await h.fire('tool.call',{tool:'TaskList'},{result:{tasks:[]}})
  const rendered = text(await h.render())
  assert.match(rendered,/Your plan will appear here/)
  assert.doesNotMatch(rendered,/Old task|\/build/)
  assert.equal(h.calls.opened.length,1)
})
test('native empty todos clear the plan while invalid fallback snapshots do not', async () => {
  const h = harness()
  await h.fire('tool.call',{tool:'TodoWrite',todos:[{content:'Existing task',status:'pending'}]})
  const result = await h.fire('tool.call',{tool:'mcp__vibe__progress',goal:'Invalid',steps:[]})
  assert.equal(result.result.accepted,false)
  assert.match(text(await h.render()),/Existing task/)
  await h.fire('tool.call',{tool:'TodoWrite',todos:[]})
  assert.match(text(await h.render()),/Your plan will appear here/)
})
test('failed or malformed TaskList results leave the last valid plan intact', async () => {
  const h = harness()
  await h.fire('tool.call',{tool:'TaskCreate',subject:'Keep this task'},{result:{taskId:'1'}})
  const results = [
    {deny:'denied',result:{tasks:[]}},
    {isError:true,result:{tasks:[]}},
    {success:false,tasks:[]},
    {result:{success:false,tasks:[]}},
    {result:{isError:true,tasks:[]}},
    {result:{deny:'denied',tasks:[]}},
    {result:{tasks:'invalid'}}
  ]
  for (const result of results) {
    assert.equal(await h.fire('tool.call',{tool:'TaskList'},result),result)
    assert.match(text(await h.render()),/Keep this task/)
  }
})
test('multiple tasks remain visibly in progress after the coordinator turn ends', async () => {
  const h = harness()
  for (const [id,subject] of [['1','Build UI'],['2','Build API']]) {
    await h.fire('tool.call',{tool:'TaskCreate',subject},{result:{taskId:id}})
  }
  await h.fire('turn.start')
  await Promise.all(['1','2'].map(taskId =>
    h.fire('tool.call',{tool:'TaskUpdate',taskId,status:'in_progress'},{result:{success:true}})))
  await h.fire('turn.complete')
  const rendered = text(await h.render())
  assert.match(rendered,/In progress/)
  assert.match(rendered,/◉ In progress: Build UI/)
  assert.match(rendered,/◉ In progress: Build API/)
  assert.match(rendered,/0 of 2 planned steps finished/)
  await h.fire('tool.call',{tool:'TaskUpdate',taskId:'1',status:'completed'})
  assert.match(text(await h.render()),/In progress/)
  await h.fire('tool.call',{tool:'TaskUpdate',taskId:'2',status:'completed'})
  assert.match(text(await h.render()),/Planned steps finished/)
  assert.match(text(await h.render()),/what was checked and what is ready to use/)
  assert.doesNotMatch(text(await h.render()),/100%|VIBE  ·  Ready/)
})
test('native task tracking opens automatically and respects a dismissed board', async () => {
  const h = harness()
  const result = {result:{tasks:[{id:'1',subject:'Build profile',status:'in_progress'}]}}
  await h.fire('tool.call',{tool:'TaskList'},result)
  assert.equal(h.calls.opened.length,1)
  await h.fire('ui.close',{id:'vibe-board',origin:{kind:'person'}})
  await h.fire('tool.call',{tool:'TaskList'},result)
  assert.equal(h.calls.opened.length,1)
})
test('progress fallback updates a single snapshot without modifying tool calls', async () => {
  const h = harness()
  const result = await h.fire('tool.call',{tool:'mcp__vibe__progress',goal:'User profile',steps:[
    {id:'a',label:'Build UI',status:'completed'},
    {id:'b',label:'Run tests',status:'pending'} ]})
  assert.equal(result.result.accepted,true)
  assert.match(text(await h.render()),/User profile/)
  assert.match(text(await h.render()),/1 of 2 planned steps finished/)
  assert.doesNotMatch(text(await h.render()),/50%/)
  assert.match(text(await h.render()),/Run tests/)
})
test('opens on request and details can be expanded', async () => {
  const h = harness()
  await h.fire('command.run',{command:'vibe-board'})
  assert.equal(h.calls.opened.length,1)
  const tree = await h.render()
  const detailsButton = tree.children.at(-1).children[0]
  detailsButton.onPress()
  assert.match(text(await h.render()),/Check results and availability are reported separately/)
  await h.fire('turn.complete')
  assert.match(text(await h.render()),/Ready to start/)
})
test('default activity stays plain and technical details remain optional', async () => {
  const h = harness()
  await h.fire('command.run',{command:'vibe-board'})
  await h.fire('turn.start')
  await h.fire('tool.call',{tool:'Read'})
  assert.match(text(await h.render()),/Reading project details/)
  await h.fire('tool.call',{tool:'mcp__private__run_step'})
  const tree = await h.render()
  assert.match(text(tree),/Working on the next step/)
  assert.doesNotMatch(text(tree),/mcp__private|Source:|Observed calls/)
  tree.children.at(-1).children[0].onPress()
  assert.match(text(await h.render()),/mcp__private__run_step/)
})
test('current outcome labels retain the user language and blocked work is not ready', async () => {
  const h = harness()
  await h.fire('tool.call',{tool:'mcp__vibe__progress',goal:'تسجيل أفراد العائلة',steps:[
    {id:'internal-42',label:'إضافة فرد إلى العائلة',status:'in_progress'}
  ]})
  await h.fire('turn.start')
  await h.fire('tool.call',{tool:'Bash'})
  assert.match(text(await h.render()),/Current: إضافة فرد إلى العائلة/)
  assert.doesNotMatch(text(await h.render()),/internal-42|Bash|%/)
  await h.fire('tool.call',{tool:'TaskUpdate',taskId:'internal-42',status:'blocked'})
  await h.fire('turn.complete')
  const rendered = text(await h.render())
  assert.match(rendered,/Needs attention/)
  assert.match(rendered,/! Waiting: إضافة فرد إلى العائلة/)
  assert.doesNotMatch(rendered,/Ready|waiting for you/i)
})
test('extraction supports structured and legacy task result', () => {
  assert.equal(taskIdFromResult({result:{taskId:'11'}}),'11')
  assert.equal(taskIdFromResult({result:'Task #12 created successfully'}),'12')
})
