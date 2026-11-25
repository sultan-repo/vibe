import { addEntry, loadEntries } from './store.js';
import { summarize, renderReport, formatDuration } from './report.js';

const USAGE = [
  'Usage:',
  '  tasklog add <project> <minutes> [note...]',
  '  tasklog list',
  '  tasklog report',
];

export function run(argv, { file, out, err }) {
  const [command, ...args] = argv;
  try {
    switch (command) {
      case 'add': {
        const [project, minutesText, ...note] = args;
        const minutes = Number(minutesText);
        if (!project || !Number.isInteger(minutes) || minutes <= 0) {
          err('add needs a project and a positive whole number of minutes');
          return 2;
        }
        const count = addEntry(file, { project, minutes, note: note.join(' ') });
        out(`Recorded ${formatDuration(minutes)} on ${project} (${count} entries)`);
        return 0;
      }
      case 'list': {
        for (const e of loadEntries(file)) {
          out(`${e.project}\t${e.minutes}\t${e.note || ''}`);
        }
        return 0;
      }
      case 'report': {
        for (const line of renderReport(summarize(loadEntries(file)))) out(line);
        return 0;
      }
      default:
        USAGE.forEach(err);
        return command ? 2 : 1;
    }
  } catch (e) {
    err(`tasklog: ${e.message}`);
    return 1;
  }
}
