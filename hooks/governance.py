#!/usr/bin/env python3
"""Read-only project conflict discovery and explicit owner decision recording.

Never executes project hooks or changes test/release enforcement. This is a
conservative advisory, not a general-purpose natural-language rule engine.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import sys

START = '<!-- vibe:governance:start -->'
END = '<!-- vibe:governance:end -->'
DECISIONS = 'docs/DECISIONS.md'
CHOICES = ('keep-project', 'align-vibe', 'defer')
MAX_BYTES = 65536

def test_gate(action):
    suite = r'\b(?:full|complete|entire|all)\b.{0,35}\b(?:tests?|suite|e2e|browser|verification)\b'
    cadence = rf'\b(?:every|each|per|before)\b.{{0,25}}\b{action}\b'
    return re.compile(rf'{cadence}.{{0,90}}{suite}|{suite}.{{0,55}}{cadence}', re.I)

RULES = (
    ('testing.full-on-commit', 'Routine full-suite commit gate', test_gate('commit')),
    ('testing.full-on-push', 'Routine full-suite push gate', test_gate('push')),
    ('review.every-change', 'Independent review on every change', re.compile(r'\b(?:every|each|all)\b.{0,22}\b(?:change|commit|edit)\b.{0,40}\b(?:must|require|needs?)\b.{0,35}\b(?:independent|codex|external)\b.{0,25}\breview\b|\breview\b.{0,45}\b(?:every|each|all)\b.{0,20}\b(?:change|commit|edit)\b', re.I)),
    ('workflow.slash-required', 'Mandatory workflow slash command', re.compile(r'\b(?:must|required|always)\b.{0,50}/(?:vibe:)?(?:build|discover|reassess)\b', re.I)),
    ('continuity.no-checkpoint', 'Durable handoff forbidden', re.compile(r'\b(?:never|do not|don.t)\b.{0,35}\b(?:save|update|commit|push)\b.{0,35}\b(?:status|handoff|checkpoint)\b', re.I)),
)
NEGATE = re.compile(r'\b(?:avoid|skip|do not|don.t|never|without|not required)\b', re.I)

class GovernanceError(Exception):
    pass

def read_file(path, limit=MAX_BYTES, *, dir_fd=None):
    if dir_fd is None and Path(path).is_symlink():
        raise GovernanceError('symlink')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
                 | getattr(os, 'O_BINARY', 0), dir_fd=dir_fd)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise GovernanceError('nonregular file')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(limit + 1)
        if len(data) > limit:
            raise GovernanceError('oversized file')
        return data.decode('utf-8')
    finally:
        os.close(fd)

def prose(text):
    marker = re.compile(r'^ {0,3}(' + chr(96) + r'{3,}|~{3,})')
    fence = None
    closing = None
    blocks = {'<!-- vibe:project:start -->': '<!-- vibe:project:end -->', START: END}
    for number, line in enumerate(text.splitlines(), 1):
        m = marker.match(line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and not line[m.end():].strip():
                fence = None
            continue
        if m:
            fence = (m.group(1)[0], len(m.group(1)))
            continue
        if line.startswith(('    ', '\t')) or line.lstrip().startswith('>'):
            continue
        token = line.strip().lstrip('\ufeff')
        if token in blocks:
            if closing:
                raise GovernanceError('nested managed block')
            closing = blocks[token]
        elif token in blocks.values():
            if token != closing:
                raise GovernanceError('unmatched managed delimiter')
            closing = None
        elif not closing:
            yield number, line
    if closing:
        raise GovernanceError('unclosed managed block')

def instruction_dirs(root, scope):
    scope = Path(scope)
    if scope.anchor or '..' in scope.parts or len(scope.parts) > 16:
        raise GovernanceError('scope must be a project-relative directory, at most 16 levels deep')
    current = root
    yield current
    for part in scope.parts:
        current = current / part
        if current.is_symlink() or not current.is_dir() or current.resolve() != current:
            raise GovernanceError('scope must be an existing project directory without symlinks')
        yield current

def scan(root, scope=Path('.')):
    root = root.resolve(strict=True)
    findings, warnings = {}, []
    def record(key, title, source, identity, evidence, directory=None):
        item = findings.setdefault(key, {'id': key, 'summary': title, 'sources': [], '_evidence': set(),
                                         'record_key': key})
        if len(item['sources']) < 4:
            item['sources'].append(source)
        item['_evidence'].add((identity, evidence))
        if directory is not None and directory != root:
            # Independent subprojects can keep different choices for the same rule.
            item['record_key'] = key + '.' + hashlib.sha256(directory.relative_to(root).as_posix().encode()).hexdigest()
    paths = ((directory, directory / name) for directory in instruction_dirs(root, scope)
             for name in ('CLAUDE.md', '.claude/CLAUDE.md', 'AGENTS.md', 'AGENTS.override.md'))
    for directory, path in paths:
        name = path.relative_to(root).as_posix()
        try:
            if path.parent.resolve() != path.parent:
                raise GovernanceError('symlinked instruction directory')
            contents = read_file(path)
            lines = list(prose(contents))
        except FileNotFoundError:
            continue
        except (OSError, GovernanceError, UnicodeError):
            warnings.append(name + ': incomplete inspection')
            continue
        # Qualifiers can precede or follow a match, including in Markdown headings.
        context = hashlib.sha256('\n'.join(line.rstrip() for _, line in lines).encode()).hexdigest()
        for number, line in lines:
            for key, title, pattern in RULES:
                if (key == 'continuity.no-checkpoint' or not NEGATE.search(line)) and pattern.search(line):
                    record(key, title, name + ':' + str(number), name, context, directory)
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
                    hook_source = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
                    record(key, 'Possible broad tests in active ' + name, 'active:' + name, hook_source,
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

@contextmanager
def open_directory(path, parent=None):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
    try:
        yield fd
    finally:
        os.close(fd)

PIN_DIRECTORIES = hasattr(os, 'O_DIRECTORY') and hasattr(os, 'O_NOFOLLOW') and os.open in os.supports_dir_fd
RECORD = Path(DECISIONS).name
RECORD_LIMIT = 131072

def read_decisions(root):
    if PIN_DIRECTORIES:
        with open_directory(root) as project, open_directory('docs', project) as docs:
            return read_file(RECORD, RECORD_LIMIT, dir_fd=docs)
    path = root / DECISIONS
    if path.parent.resolve() != path.parent:
        raise GovernanceError('redirected decision directory')
    return read_file(path, RECORD_LIMIT)

def report(root, scope=Path('.')):
    root = root.resolve(strict=True)
    conflicts, warnings = scan(root, scope)
    try:
        prior, _ = records(read_decisions(root))
    except FileNotFoundError:
        prior = {}
    except (OSError, GovernanceError, UnicodeError):
        prior = {}
        warnings.append('decision record ambiguous; no choice inferred')
    for item in conflicts:
        choice = prior.get(item['record_key'])
        item['decision'] = choice[1] if choice and choice[0] == item['fingerprint'] else None
        item['state'] = 'unresolved' if item['decision'] is None else (
            'alignment-pending' if item['decision'] == 'align-vibe' else
            'accepted-exception' if item['decision'] == 'keep-project' else 'deferred')
    return {'schema': 1, 'conflicts': conflicts, 'warnings': warnings}

def decision_text(before, key, fingerprint, choice):
    prior, span = records(before)
    prior[key] = fingerprint, choice
    block = START + '\n' + '\n'.join('- %s | %s | %s' % (k, *v) for k, v in sorted(prior.items())) + '\n' + END
    after = before[:span[0]] + block + before[span[1]:] if span else (
        before + ('' if not before else '\n' if before.endswith('\n') else '\n\n') +
        ('## Vibe governance decisions\n' if '## Vibe governance decisions' not in before else '') + block + '\n')
    if len(after.encode()) > RECORD_LIMIT:
        raise GovernanceError('decision record too large')
    return after

def snapshot(docs):
    try:
        info = os.stat(RECORD, dir_fd=docs, follow_symlinks=False)
    except FileNotFoundError:
        return None, None, ''
    return ((info.st_dev, info.st_ino, info.st_mtime_ns, info.st_ctime_ns),
            info.st_mode & 0o777, read_file(RECORD, RECORD_LIMIT, dir_fd=docs))

def decide(root, key, fingerprint, choice, confirmed, scope=Path('.')):
    if not confirmed or choice not in CHOICES:
        raise GovernanceError('explicit owner choice required')
    if not PIN_DIRECTORIES:
        raise GovernanceError('safe decision writes require POSIX directory handles; run the helper in WSL on Windows')
    import fcntl
    root = root.resolve(strict=True)
    with open_directory(root) as project:
        conflicts, warnings = scan(root, scope)
        item = next((i for i in conflicts if i['id'] == key and i['fingerprint'] == fingerprint), None)
        if warnings or item is None:
            raise GovernanceError('conflict changed or inspection incomplete')
        try:
            os.mkdir('docs', dir_fd=project)
        except FileExistsError:
            pass
        with open_directory('docs', project) as docs:
            # Serialize cooperating writers without leaving a lock file in the project.
            fcntl.flock(docs, fcntl.LOCK_EX)
            before = snapshot(docs)
            _, mode, original = before
            after = decision_text(original, item['record_key'], fingerprint, choice)
            def check_directory():
                if (not os.path.samestat(os.fstat(project), os.stat(root, follow_symlinks=False))
                        or not os.path.samestat(os.fstat(docs), os.stat('docs', dir_fd=project, follow_symlinks=False))):
                    raise GovernanceError('decision directory changed concurrently')
            check_directory()
            if original == after:
                return False
            name = '.vibe-decision-' + secrets.token_hex(16)
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=docs)
            try:
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(after.encode())
                    if mode is not None:
                        os.fchmod(stream.fileno(), mode)
                if snapshot(docs) != before:
                    raise GovernanceError('decision file changed concurrently')
                check_directory()
                os.replace(name, RECORD, src_dir_fd=docs, dst_dir_fd=docs)
                check_directory()
                return True
            finally:
                try:
                    os.unlink(name, dir_fd=docs)
                except FileNotFoundError:
                    pass

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('scan','decide'))
    p.add_argument('--project-dir', required=True, type=Path)
    p.add_argument('--scope', type=Path, default=Path('.'), help='project-relative work directory')
    p.add_argument('--id')
    p.add_argument('--fingerprint')
    p.add_argument('--choice', choices=CHOICES)
    p.add_argument('--owner-confirmed', action='store_true')
    args = p.parse_args()
    try:
        root = args.project_dir.resolve(strict=True)
        if args.action == 'scan':
            print(json.dumps(report(root, args.scope), ensure_ascii=False))
        else:
            if not args.id or not args.fingerprint or not args.choice:
                p.error('decide needs --id, --fingerprint, --choice')
            print(json.dumps({'recorded': decide(root,args.id,args.fingerprint,args.choice,args.owner_confirmed,args.scope)}))
        return 0
    except (GovernanceError, OSError, UnicodeError) as error:
        print('Vibe governance: ' + str(error), file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
