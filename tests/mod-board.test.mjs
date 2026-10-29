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
  assert.ok(text(await h.render()).includes('1/2 steps reported complete'))
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
  assert.ok(text(await h.render()).includes('1/1 steps reported complete'))
  await h.fire('tool.call',{tool:'TaskUpdate',taskId:'7',status:'deleted'},
    {result:{success:true}})
  assert.match(text(await h.render()),/No tracked plan yet/)
})
test('progress fallback updates a single snapshot without modifying tool calls', async () => {
  const h = harness()
  const result = await h.fire('tool.call',{tool:'mcp__vibe__progress',goal:'User profile',steps:[
    {id:'a',label:'Build UI',status:'completed'},
    {id:'b',label:'Run tests',status:'pending'} ]})
  assert.equal(result.result.accepted,true)
  assert.match(text(await h.render()),/User profile/)
  assert.match(text(await h.render()),/50%/)
  assert.match(text(await h.render()),/Run tests/)
})
test('opens on request and details can be expanded', async () => {
  const h = harness()
  await h.fire('command.run',{command:'vibe-board'})
  assert.equal(h.calls.opened.length,1)
  const tree = await h.render()
  const detailsButton = tree.children.at(-1).children[0]
  detailsButton.onPress()
  assert.match(text(await h.render()),/Task status is not test/)
  await h.fire('turn.complete')
  assert.match(text(await h.render()),/Ready/)
})
test('extraction supports structured and legacy task result', () => {
  assert.equal(taskIdFromResult({result:{taskId:'11'}}),'11')
  assert.equal(taskIdFromResult({result:'Task #12 created successfully'}),'12')
})
