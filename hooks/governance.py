#!/usr/bin/env python3
"""Read-only project conflict discovery and explicit owner decision recording.

Never executes project hooks or changes test/release enforcement. This is a
conservative advisory, not a general-purpose natural-language rule engine.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

START = '<!-- vibe:governance:start -->'
END = '<!-- vibe:governance:end -->'
DECISIONS = 'docs/DECISIONS.md'
CHOICES = ('keep-project', 'align-vibe', 'defer')
MAX_BYTES = 65536
RULES = (
    ('testing.full-on-commit', 'Routine full-suite commit gate', re.compile(r'\b(?:every|each|per|before)\b.{0,22}\bcommit\b.{0,90}\b(?:full|complete|entire|all)\b.{0,35}\b(?:test|suite|e2e|browser|verification)\b|\b(?:full|complete|entire|all)\b.{0,35}\b(?:test|suite|e2e|browser|verification)\b.{0,55}\b(?:every|each|per|before)\b.{0,25}\bcommit\b', re.I)),
    ('testing.full-on-push', 'Routine full-suite push gate', re.compile(r'\b(?:every|each|per|before)\b.{0,22}\bpush\b.{0,90}\b(?:full|complete|entire|all)\b.{0,35}\b(?:test|suite|e2e|browser|verification)\b|\b(?:full|complete|entire|all)\b.{0,35}\b(?:test|suite|e2e|browser|verification)\b.{0,55}\b(?:every|each|per|before)\b.{0,25}\bpush\b', re.I)),
    ('review.every-change', 'Independent review on every change', re.compile(r'\b(?:every|each|all)\b.{0,22}\b(?:change|commit|edit)\b.{0,40}\b(?:must|require|needs?)\b.{0,35}\b(?:independent|codex|external)\b.{0,25}\breview\b|\breview\b.{0,45}\b(?:every|each|all)\b.{0,20}\b(?:change|commit|edit)\b', re.I)),
    ('workflow.slash-required', 'Mandatory workflow slash command', re.compile(r'\b(?:must|required|always)\b.{0,50}/(?:vibe:)?(?:build|discover|reassess)\b', re.I)),
    ('continuity.no-checkpoint', 'Durable handoff forbidden', re.compile(r'\b(?:never|do not|don.t)\b.{0,35}\b(?:save|update|commit|push)\b.{0,35}\b(?:status|handoff|checkpoint)\b', re.I)),
)
NEGATE = re.compile(r'\b(?:avoid|skip|do not|don.t|never|without|not required)\b', re.I)

class GovernanceError(Exception):
    pass

def read_file(path, limit=MAX_BYTES):
    if path.is_symlink():
        raise GovernanceError('symlink')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise GovernanceError('nonregular file')
        data = os.read(fd, limit + 1)
        if len(data) > limit:
            raise GovernanceError('oversized file')
        return data.decode('utf-8')
    finally:
        os.close(fd)

def prose(text):
    marker = re.compile(r'^ {0,3}(' + chr(96) + r'{3,}|~{3,})')
    fence = None
    managed = False
    for number, line in enumerate(text.splitlines(), 1):
        if '<!-- vibe:project:start -->' in line or START in line:
            managed = True
        if managed:
            if '<!-- vibe:project:end -->' in line or END in line:
                managed = False
            continue
        m = marker.match(line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and not line[m.end():].strip():
                fence = None
            continue
        if m:
            fence = (m.group(1)[0], len(m.group(1)))
        elif not line.startswith(('    ', '\t', '>')):
            yield number, line

def scan(root):
    root = root.resolve(strict=True)
    findings, warnings = {}, []
    def record(key, title, source, evidence):
        item = findings.setdefault(key, {'id': key, 'summary': title, 'sources': [], '_evidence': []})
        if len(item['sources']) < 4:
            item['sources'].append(source)
        item['_evidence'].append((source.split(':')[0], evidence))
    for name in ('CLAUDE.md', '.claude/CLAUDE.md', 'AGENTS.md', 'AGENTS.override.md'):
        path = root / name
        try:
            if not path.resolve().is_relative_to(root):
                raise GovernanceError('outside project')
            contents = read_file(path)
        except FileNotFoundError:
            continue
        except (OSError, GovernanceError, UnicodeError):
            warnings.append(name + ': incomplete inspection')
            continue
        for number, line in prose(contents):
            for key, title, pattern in RULES:
                if (key == 'continuity.no-checkpoint' or not NEGATE.search(line)) and pattern.search(line):
                    record(key, title, name + ':' + str(number), line.strip())
    # Resolve the active Git hooks directory, including core.hooksPath.
    try:
        result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--path-format=absolute',
                                 '--git-path', 'hooks'], capture_output=True, text=True, timeout=1,
                                env={**os.environ, 'GIT_NO_LAZY_FETCH':'1', 'GIT_ALLOW_PROTOCOL':'',
                                     'GIT_OPTIONAL_LOCKS':'0'})
        if result.returncode == 0:
            for name, key in (('pre-commit','testing.full-on-commit'), ('pre-push','testing.full-on-push')):
                path = Path(result.stdout.strip()) / name
                try:
                    contents = read_file(path, 8192)
                except FileNotFoundError:
                    continue
                except (OSError, GovernanceError, UnicodeError):
                    warnings.append(name + ': incomplete hook inspection')
                    continue
                if os.access(path, os.X_OK) and re.search(r'\b(?:playwright\s+test|cypress\s+run|npm\s+(?:run\s+)?test:e2e|verify.{0,12}full)\b', contents, re.I):
                    record(key, 'Possible broad tests in active ' + name, 'active:' + name,
                           hashlib.sha256(contents.encode()).hexdigest())
    except (OSError, subprocess.TimeoutExpired):
        warnings.append('Git hooks unavailable')
    result = []
    for key in sorted(findings):
        item = findings[key]
        evidence = json.dumps([key, sorted(item.pop('_evidence'))], sort_keys=True)
        item['fingerprint'] = hashlib.sha256(evidence.encode()).hexdigest()
        result.append(item)
    return result[:8], warnings[:4]

def records(text):
    if START not in text and END not in text:
        return {}, None
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
        raise GovernanceError('ambiguous decision markers')
    begin, end = text.index(START), text.index(END) + len(END)
    output = {}
    for line in text[begin + len(START):text.index(END)].splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'- ([a-z][\w.-]+) \| ([a-f0-9]{64}) \| (keep-project|align-vibe|defer)', line.strip())
        if not match or match.group(1) in output:
            raise GovernanceError('invalid or repeated decision')
        output[match.group(1)] = (match.group(2), match.group(3))
    return output, (begin, end)

def report(root):
    conflicts, warnings = scan(root)
    try:
        prior, _ = records(read_file(root / DECISIONS, 131072))
    except FileNotFoundError:
        prior = {}
    except (OSError, GovernanceError, UnicodeError):
        prior = {}
        warnings.append('decision record ambiguous; no choice inferred')
    for item in conflicts:
        choice = prior.get(item['id'])
        item['decision'] = choice[1] if choice and choice[0] == item['fingerprint'] else None
        item['state'] = 'unresolved' if item['decision'] is None else (
            'alignment-pending' if item['decision'] == 'align-vibe' else
            'accepted-exception' if item['decision'] == 'keep-project' else 'deferred')
    return {'schema': 1, 'conflicts': conflicts, 'warnings': warnings}

def decide(root, key, fingerprint, choice, confirmed):
    if not confirmed or choice not in CHOICES:
        raise GovernanceError('explicit owner choice required')
    check = report(root)
    if check['warnings'] or not any(i['id'] == key and i['fingerprint'] == fingerprint for i in check['conflicts']):
        raise GovernanceError('conflict changed or inspection incomplete')
    path = root / DECISIONS
    if path.parent.is_symlink():
        raise GovernanceError('symlinked decision directory')
    try:
        before = read_file(path, 131072)
    except FileNotFoundError:
        before = ''
    prior, span = records(before)
    prior[key] = fingerprint, choice
    block = START + '\n' + '\n'.join('- %s | %s | %s' % (k, *v) for k, v in sorted(prior.items())) + '\n' + END
    after = before[:span[0]] + block + before[span[1]:] if span else (
        before + ('' if not before else '\n' if before.endswith('\n') else '\n\n') +
        ('## Vibe governance decisions\n' if '## Vibe governance decisions' not in before else '') + block + '\n')
    if len(after.encode()) > 131072:
        raise GovernanceError('decision record too large')
    if before == after:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as out:
            temp = Path(out.name)
            out.write(after.encode())
            os.fchmod(out.fileno(), (path.stat().st_mode & 0o777) if path.exists() else 0o644)
        try:
            current = read_file(path, 131072)
        except FileNotFoundError:
            current = ''
        if current != before or path.is_symlink():
            raise GovernanceError('decision file changed concurrently')
        os.replace(temp, path)
        return True
    finally:
        if temp:
            temp.unlink(missing_ok=True)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('scan','decide'))
    p.add_argument('--project-dir', required=True, type=Path)
    p.add_argument('--id')
    p.add_argument('--fingerprint')
    p.add_argument('--choice', choices=CHOICES)
    p.add_argument('--owner-confirmed', action='store_true')
    args = p.parse_args()
    try:
        root = args.project_dir.resolve(strict=True)
        if args.action == 'scan':
            print(json.dumps(report(root), ensure_ascii=False))
        else:
            if not args.id or not args.fingerprint or not args.choice:
                p.error('decide needs --id, --fingerprint, --choice')
            print(json.dumps({'recorded': decide(root,args.id,args.fingerprint,args.choice,args.owner_confirmed)}))
        return 0
    except (GovernanceError, OSError, UnicodeError) as error:
        print('Vibe governance: ' + str(error), file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
