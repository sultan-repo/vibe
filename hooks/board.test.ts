import { test, expect } from 'claude-code/testing'

// Uses Claude Code's own element-tree validation rather than the Node test mock.
// This is still not a human-observed terminal pane, which remains a release gate.
test('Vibe board renders an empty state in the native mod host', async ($, on) => {
  // Underlying engine placeholder; our Pane hook must replace it.
  on('ui.render', () => ({ type: 'Text', props: {}, children: ['engine fallback'] }))
  const pane = await $.ui.mount({
    plugin: 'vibe',
    surface: 'terminal',
    component: 'Pane',
    requestId: 'vibe-board',
    viewport: { columns: 160, rows: 45, isFullscreen: true },
    props: {
      title: 'Vibe · Progress',
      isFocused: true,
      bodyColumns: 48,
      placement: 'dock',
      scroll: { offset: 0, bodyRows: 35 },
      view: {},
    },
  })
  const rendered = await pane.drawn()
  expect(JSON.stringify(rendered)).toContain('No tracked plan yet')
  await pane.unmount()
})
