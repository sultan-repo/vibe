// Vibe Board: optional native progress UI. No network, filesystem, model calls or polling.
const PANE = 'vibe-board'
const MAX_STEPS = 12
const MAX_LABEL = 96

export function clean(value, length = MAX_LABEL) {
  return String(value ?? '').replace(/[\x00-\x1f\x7f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, length)
}

export function normalizeSteps(value) {
  if (!Array.isArray(value)) return []
  const used = new Set()
  return value.slice(0, MAX_STEPS).map((step, index) => {
    const label = clean(step?.label ?? step?.content ?? step?.subject ?? step?.title)
    const id = clean(step?.id ?? step?.taskId ?? String(index + 1), 48)
    const raw = step?.status
    const status = raw === 'completed' || raw === 'in_progress' || raw === 'blocked' ? raw : 'pending'
    if (!label || used.has(id)) return null
    used.add(id)
    return { id, label, status, detail: clean(step?.detail ?? step?.description ?? '', 160) }
  }).filter(Boolean)
}

export function progressOf(steps) {
  const done = steps.filter(s => s.status === 'completed').length
  // These are reported task statuses, not independent acceptance verification.
  return { done, total: steps.length, percent: steps.length ? Math.round(done * 100 / steps.length) : null }
}

export function taskIdFromResult(result) {
  const value = result?.result ?? result
  const direct = value?.taskId ?? value?.task?.id ?? value?.result?.taskId
  if (direct !== undefined && direct !== null) return clean(direct, 48)
  const text = typeof value === 'string' ? value : typeof value?.content === 'string' ? value.content : ''
  const match = text.match(/(?:task(?:\s+|\s*#|\s*id\s*[:=]\s*))([0-9]+)/i)
  return match ? match[1] : null
}

async function openedWithPlan($, state) {
  if (!state.steps.length || state.autoOpenAttempted || state.dismissed) return
  state.autoOpenAttempted = true
  try {
    const result = await $.ui.open({ id: PANE, title: 'Vibe · Progress', columns: 48 })
    state.isOpen = result?.isPlaced !== false
  } catch { /* Non-visual surfaces continue normally. */ }
}

function redraw($, state) {
  if (state.isOpen) void $.ui.invalidate('ui.render')
}

async function setPlan($, state, name, rows, origin) {
  const normalized = normalizeSteps(rows)
  if (!normalized.length) return false
  state.goal = clean(name, 100) || state.goal
  state.steps = normalized
  state.source = origin
  await openedWithPlan($, state)
  redraw($, state)
  return true
}

export function register(on) {
  const state = { goal: '', steps: [], source: '', isOpen: false,
    autoOpenAttempted: false, dismissed: false }
  let working = false
  let action = ''
  let calls = 0
  let details = false
  let synthetic = 0
  const eventInput = e => e.input && typeof e.input === 'object' ? { ...e.input, ...e } : e
  const succeeded = result => !result?.deny && !result?.isError && result?.success !== false &&
    result?.result?.success !== false

  on('session.start', async ($, e, next) => {
    // Register tools first so the UI command works even when a tool isn't supported.
    try {
      await $.tool.register({
        name: 'progress',
        description: 'Optional Vibe visual board. For multi-step work only when no native Task/Todo tracking is available: send a concise goal and full step list, and update only when a step actually changes status. Never use for Fast fixes; completion reflects reported progress, not proof of testing.',
        isDeferred: true,
        inputSchema: {
          type: 'object',
          properties: {
            goal: { type: 'string' },
            steps: {
              type: 'array', minItems: 1, maxItems: MAX_STEPS,
              items: { type: 'object', properties: {
                id: { type: 'string' }, label: { type: 'string' },
                status: { type: 'string', enum: ['pending', 'in_progress', 'completed', 'blocked'] },
                detail: { type: 'string' }
              }, required: ['id', 'label', 'status'] }
            }
          }, required: ['goal', 'steps']
        }
      })
    } catch { /* Older clients can still use native task tracking. */ }
    await $.command.register({ name: 'vibe-board', description: 'Open the optional Vibe progress board', immediate: true })
    return next(e)
  })

  on('command.run', { command: 'vibe-board' }, async $ => {
    dismissed = false
    autoOpenAttempted = true
    const result = await $.ui.open({ id: PANE, title: 'Vibe · Progress', focus: true, columns: 48, closeOnEscape: true })
    isOpen = result?.isPlaced !== false
    redraw($, state)
    return {}
  })

  on('ui.close', async ($, e, next) => {
    if (e.id === PANE) {
      isOpen = false
      if (e.origin?.kind === 'person') dismissed = true
    }
    return next(e)
  })

  on('turn.start', async ($, e, next) => {
    working = true
    action = 'Thinking'
    redraw($, state)
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    working = false
    action = ''
    redraw($, state)
    return next(e)
  })

  on('tool.call', async ($, event, next) => {
    const e = eventInput(event)
    if (event.tool === 'mcp__vibe__progress') {
      const ok = await setPlan($, state, e.goal, e.steps, 'Claude-reported')
      return { result: { accepted: ok, message: ok ? 'Board updated' : 'No valid steps supplied' } }
    }

    const observed = ['TodoWrite', 'TaskCreate', 'TaskUpdate', 'TaskList'].includes(event.tool)
    if (isOpen) {
      action = event.tool === 'Bash' ? 'Running a command' :
        ['Edit', 'Write', 'MultiEdit', 'NotebookEdit'].includes(event.tool) ? 'Editing code' :
        observed ? 'Updating the plan' : 'Using ' + clean(event.tool, 32)
      calls++
      redraw($, state)
    }

    const result = await next(event)
    if (succeeded(result)) {
      if (event.tool === 'TodoWrite') {
        await setPlan($, state, goal, e.todos, 'Native task list')
      } else if (event.tool === 'TaskList') {
        const tasks = result?.result?.tasks ?? result?.tasks
        if (Array.isArray(tasks) && tasks.length) await setPlan($, state, goal, tasks, 'Native task list')
      } else if (event.tool === 'TaskCreate') {
        const label = clean(e.subject)
        if (label) {
          const id = taskIdFromResult(result) ?? 'unlinked-' + (++synthetic)
          const existing = steps.findIndex(s => s.id === id)
          const entry = { id, label, status: 'pending', detail: clean(e.description, 160) }
          if (existing >= 0) steps[existing] = entry
          else steps = [...steps, entry].slice(0, MAX_STEPS)
          source = 'Native task list'
          await openedWithPlan($, state)
          redraw($, state)
        }
      } else if (event.tool === 'TaskUpdate') {
        const id = clean(e.taskId, 48)
        const index = steps.findIndex(s => s.id === id)
        if (index !== -1) {
          if (e.status === 'deleted') steps.splice(index, 1)
          else {
            const current = steps[index]
            steps[index] = {
              ...current,
              label: clean(e.subject) || current.label,
              status: ['pending', 'in_progress', 'completed', 'blocked'].includes(e.status) ? e.status : current.status,
            }
          }
          redraw($, state)
        }
      }
    }
    // Never rewrite tool results or declare a failed/denied task complete.
    return result
  })

  on('ui.render', { component: 'Pane' }, async ($, e, next) => {
    if (e.requestId !== PANE) return next(e)
    const { Box, Text, Button } = $.ui.resolve(e)
    const { done, total, percent } = progressOf(steps)
    const width = 22
    const filled = percent === null ? 0 : Math.round(width * percent / 100)
    const text = value => Text({ children: [value] })
    const controls = Box({ flexDirection: 'row', columnGap: 2, children: [
      Button({ key: 'vibe-details', label: details ? 'Less' : 'Details', plain: true,
        onPress: () => { details = !details; redraw($, state) } }),
      Button({ key: 'vibe-close', label: 'Close', plain: true,
        onPress: async () => { dismissed = true; isOpen = false; await $.ui.close({ id: PANE }) } }),
    ] })
    const items = steps.map(s => {
      const symbol = s.status === 'completed' ? '✓' :
        s.status === 'in_progress' ? '◉' : s.status === 'blocked' ? '!' : '○'
      return text(symbol + ' ' + s.label)
    })
    return Box({ flexDirection: 'column', children: [
      text('VIBE  ·  ' + (working ? 'Working' : 'Ready')),
      text(goal || 'Current session'),
      text(total ? done + '/' + total + ' steps reported complete · ' + percent + '%' : 'No tracked plan yet'),
      text(total ? '▰'.repeat(filled) + '▱'.repeat(width - filled) : 'Run /build or report a plan to see steps'),
      ...items,
      ...(details ? [
        text('Source: ' + (source || 'No task source')),
        text('Activity: ' + (working ? (action || 'Working') : 'Not running')),
        text('Observed calls while open: ' + calls),
        text('Task status is not test or acceptance evidence.')
      ] : []),
      controls
    ] })
  })
}
