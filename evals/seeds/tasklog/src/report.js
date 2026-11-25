// Builds the per-project summary shown by `tasklog report`.

export function summarize(entries) {
  const totals = new Map();
  for (const entry of entries) {
    totals.set(entry.project, (totals.get(entry.project) || 0) + entry.minutes);
  }
  const projects = [...totals.entries()]
    .map(([project, minutes]) => ({ project, minutes }))
    .sort((a, b) => b.minutes - a.minutes || a.project.localeCompare(b.project));
  const total = projects.reduce((sum, p) => sum + p.minutes, 0);
  return { projects, total };
}

export function formatDuration(minutes) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h ? `${h}h ${String(m).padStart(2, '0')}m` : `${m}m`;
}

export function renderReport(summary) {
  if (summary.projects.length === 0) return ['No entries yet.'];
  const width = Math.max(...summary.projects.map((p) => p.project.length), 'TOTAL'.length);
  const lines = summary.projects.map(
    (p) => `${p.project.padEnd(width)}  ${formatDuration(p.minutes)}`
  );
  lines.push(`${'TOTAL'.padEnd(width)}  ${formatDuration(summary.total)}`);
  return lines;
}
