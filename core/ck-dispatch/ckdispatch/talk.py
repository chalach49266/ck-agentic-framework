"""Mid-run question files and capped, audited input to a run's own live Herdr pane."""
from contextlib import ExitStack, contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
import subprocess
import unicodedata
import uuid

from . import asks, herdr, ledger, live
from .errors import Refused

QUESTION_MAX_BYTES = 65536
PROGRESS_READ_BYTES = 65536
PROGRESS_LABEL_MAX = 48


class PaneGone(Refused):
    """The recorded worker CLI or terminal has ended."""


@contextmanager
def locked(run_dir):
    # Shared by polling and say: a new question cannot be accidentally cleared by an older answer.
    with (Path(run_dir) / 'talk.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def context(run_dir):
    try:
        data = json.loads((Path(run_dir) / herdr.DOORBELL_CONTEXT).read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def pending(events):
    q = next((e for e in reversed(events) if e.get('event') == 'question'), None)
    if q and not any(e.get('event') == 'say_result' and e.get('status') == 'sent'
                     and e.get('question_id') == q.get('question_id') for e in events):
        return q
    return None


def _events(cfg, rid):
    return [e for e in ledger.load(cfg.runs_dir) if e.get('run_id') == rid]


def poll_progress(cfg, run_id, run_dir, base, offset):
    """Put the latest complete progress line on this run's own worker pane."""
    host = herdr.saved(run_dir)
    target = host.get('terminal')
    parent = str(host.get('host') or '')
    if (not parent.startswith('herdr:') or not herdr.local_address(target)
            or target in (parent.partition(':')[2], os.environ.get('HC_TERMINAL_ID'))):
        return offset
    if offset is None:
        old = next((e for e in reversed(_events(cfg, run_id)) if e.get('event') == 'progress'), {})
        offset = old.get('progress_offset') or 0
    try:
        fd = os.open(Path(run_dir) / 'progress.md', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as file:
            st = os.fstat(file.fileno())
            if not stat.S_ISREG(st.st_mode) or offset >= st.st_size:
                return offset
            file.seek(offset)
            lines = file.read(min(st.st_size - offset, PROGRESS_READ_BYTES)).split(b'\n')
    except OSError:
        return offset
    next_offset = offset
    steps = []
    for line in lines[:-1]:
        next_offset += len(line) + 1
        cleaned = ''.join(c for c in line.decode('utf-8', 'replace')
                          if c.isspace() or not unicodedata.category(c).startswith('C'))
        text = ' '.join(cleaned.split())
        if len(text) > PROGRESS_LABEL_MAX:
            text = text[:PROGRESS_LABEL_MAX - 1].rstrip() + '…'
        if text:
            steps.append((next_offset, text))
    if not steps:
        return next_offset
    try:
        info = herdr.call(cfg, 'get', target, timeout=5)
        labels = info.get('labels')
        if (info.get('address') != target or info.get('state') != 'live' or not isinstance(labels, dict)
                or labels.get('ck-run') != 'true' or labels.get('ck.run') != run_id):
            return offset
        herdr.call(cfg, 'label', target, f'ck.progress={steps[-1][1]}', timeout=5)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return offset
    for end, text in steps:
        ledger.append(cfg.runs_dir, event='progress', status='labelled', text=text, progress_offset=end,
                      **dict(base, run_id=run_id, to=target))
    return next_offset


def poll_question(cfg, run_id, run_dir, base):
    with locked(run_dir):
        path = Path(run_dir) / 'question.md'
        try:
            # Never follow worker-created symlinks or read special files.
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        except (FileNotFoundError, OSError):
            return
        with os.fdopen(fd, 'rb') as file:
            st = os.fstat(file.fileno())
            if not stat.S_ISREG(st.st_mode) or st.st_size > QUESTION_MAX_BYTES:
                return
            raw = file.read(QUESTION_MAX_BYTES + 1)
            after = os.fstat(file.fileno())
        if len(raw) > QUESTION_MAX_BYTES or (st.st_size, st.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            return  # incomplete write; pick it up on the next poll
        text = raw.decode('utf-8', errors='replace').strip()
        if not text:
            return
        signature = hashlib.sha256(raw + f':{st.st_ino}:{st.st_mtime_ns}'.encode()).hexdigest()
        events = _events(cfg, run_id)
        old = next((e for e in reversed(events) if e.get('event') == 'question'), None)
        if old and old.get('question_id') == signature:
            return
        ctx = context(run_dir)
        slug = ctx.get('slug') or run_id
        fields = {k: base.get(k) for k in ('ask_id', 'agent', 'title', 'workspace')}
        fields.update(run_id=run_id, slug=slug, question_id=signature)
        ledger.append(cfg.runs_dir, event='question', status='needs-you', text=text,
                      response_path=str(path), **fields, **{'from': fields.get('agent'), 'to': 'CK'})
        target = herdr.parent_target(run_dir, ctx)
        skip = herdr.parent_note_skip(cfg) or ('' if target else 'no saved Herdr parent')
        # The question event reserves a single attempt before any send (including interrupted sends).
        first_line = ''.join(c for c in text.splitlines()[0] if c.isprintable())[:240]
        note = f'[ck-run] {slug} asks: {first_line}. Answer: ck-run say {shlex.quote(slug)} "..."'
        status, reason = ('skipped', skip) if skip else herdr.send_note(cfg, run_dir, target, note)
        ledger.append(cfg.runs_dir, event='question_note', status=status, text=note,
                      note=f'target={target}; {reason}', **fields, **{'from': 'ck-run', 'to': 'CK'})


def resolve(cfg, name):
    runs = ledger.runs(ledger.load(cfg.runs_dir))
    matches = set()
    if name in runs and runs[name].first('dispatch', 'review'):
        matches.add(name)
    # Original launch context survives a watcher restart and records the actual launch slug.
    for rid, run in runs.items():
        if run.first('dispatch', 'review') and Path(rid).name == rid and rid not in ('.', '..'):
            if context(Path(cfg.runs_dir) / rid).get('slug') == name:
                matches.add(rid)
    if len(matches) != 1:
        raise Refused(f'unknown or ambiguous run/slug {name!r}; use an exact run id')
    rid = matches.pop()
    if Path(rid).name != rid or rid in ('.', '..'):
        raise Refused('invalid run id')
    rd = Path(cfg.runs_dir) / rid
    if not rd.is_dir() or rd.is_symlink():
        raise Refused('run folder is missing or is a symlink')
    return rid, rd


def live_target(cfg, run_dir, events, *, allow_completed=False, allow_blocked=False):
    rd = Path(run_dir)
    if not rd.is_dir() or rd.is_symlink():
        raise Refused('run folder is missing or is a symlink')
    host = herdr.saved(rd)
    target = host.get('terminal')
    saved_host = str(host.get('host') or '')
    if not herdr.transport(cfg) or not saved_host.startswith('herdr:') or not herdr.local_address(target):
        raise PaneGone('no saved local Herdr worker pane')
    if target in (os.environ.get('HC_TERMINAL_ID'), saved_host.partition(':')[2]):
        raise Refused('worker pane matches a protected caller or parent pane')
    pid = live._read_int(str(rd / 'live.pid'))
    if (rd / 'live.exit').exists() or not pid or pid <= 1 or not live._alive(pid):
        raise PaneGone('recorded worker CLI has ended')
    if not allow_completed and (any(e.get('event') == 'result' for e in events) or (rd / 'summary.md').exists()):
        raise Refused('say needs an unfinished worker run')
    try:
        info = herdr.call(cfg, 'get', target)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        raise Refused(f'could not verify the saved Herdr pane: {exc}') from exc
    if info.get('state') == 'finished':
        raise PaneGone('saved Herdr pane has ended')
    labels = info.get('labels')
    if (info.get('address') != target or info.get('state') != 'live' or not isinstance(labels, dict)
            or labels.get('ck-run') != 'true' or labels.get('ck.run') != rd.name):
        raise Refused('saved Herdr pane does not match this live ck-run worker')
    status = info.get('status')
    state = status if isinstance(status, str) else (status.get('state') if isinstance(status, dict) else None)
    if state == 'blocked' and not allow_blocked:
        raise Refused('Herdr pane is blocked; ask the owner. Never force input')
    return target


def say(cfg, name, text, *, who='CK', over=None, review_id=None):
    text = ''.join(c for c in text if c.isprintable() or c in ('\n', '\t'))
    if not text.strip():
        raise Refused('say text is empty')
    if over is not None and not over.strip():
        raise Refused('--over is empty: give the owner\'s words')
    rid, rd = resolve(cfg, name)
    with locked(rd):
        events = _events(cfg, rid)
        target = live_target(cfg, rd, events, allow_completed=bool(review_id))
        _send(cfg, rid, rd, target, events, text, who, over, review_id)
    return rid



def _send(cfg, rid, rd, target, events, text, who, over, review_id):
    """Send while holding the run lock, using the checked target and current event snapshot."""
    text = ''.join(c for c in text if c.isprintable() or c in ('\n', '\t'))
    opening = next(e for e in events if e.get('event') in ('dispatch', 'review'))
    fields = {k: opening.get(k) for k in ('ask_id', 'agent', 'title', 'workspace')}
    fields.update(run_id=rid, slug=context(rd).get('slug') or rid)
    used = sum(e.get('event') == 'say' for e in events)
    if used >= cfg.herdr_say_cap:
        ledger.append(cfg.runs_dir, event='over_budget', status='approved' if over else 'refused',
                      over=over, reason='say cap', note=f'say cap {cfg.herdr_say_cap}; attempts {used}', **fields)
        if not over:
            raise asks.OverBudget(f'say cap {cfg.herdr_say_cap} reached; ask the owner, then use --over "<the owner words>"')
    # Review findings do not answer a pending question from the owner.
    q = None if review_id else pending(events)
    message_id = uuid.uuid4().hex
    fields.update(question_id=q.get('question_id') if q else None, message_id=message_id,
                  who=who, text=text, over=over, reason=f'live review {review_id}' if review_id else None)
    ledger.append(cfg.runs_dir, event='say', status='attempting', **fields, **{'from': who, 'to': fields['agent']})
    status, reason = herdr.send_note(cfg, rd, target, text)
    ledger.append(cfg.runs_dir, event='say_result', status=status, note=reason, **fields,
                  **{'from': who, 'to': fields['agent']})
    if status != 'sent':
        raise Refused(f'say was not confirmed: {reason}. Ask the owner; never force or automatically retry input')


def review_steer(cfg, review_id, review, result):
    """One durable steer attempt per reviewer. Reserve its fix under the ask lock before say.

    Missing/closed panes fall back to a normal review. Ambiguous sends keep their fix reservation;
    reattach must never type the findings twice.
    """
    if not review or not review.get('live_steer'):
        return 'normal review'
    findings = [f for f in (result or {}).get('findings', []) if isinstance(f, dict)
                and str(f.get('claim') or '').strip() and str(f.get('evidence') or '').strip()][:3]
    if not findings:
        return 'no findings to steer'
    rid, rd = resolve(cfg, review['run_id'])
    with ExitStack() as scope:
        with asks.lock(cfg):
            scope.enter_context(locked(rd))
            events = ledger.load(cfg.runs_dir)
            old = [e for e in events if e.get('event') == 'review_steer'
                   and e.get('message_id') == review_id]
            if old:
                if any(e.get('event') == 'review_steer_result' and e.get('message_id') == review_id
                       and e.get('status') == 'sent' for e in events):
                    return 'steer already sent; see ledger'
                raise Refused('prior steer delivery is not confirmed; see ledger; never automatically retry')
            opening = next(e for e in events if e.get('run_id') == rid and e.get('event') == 'dispatch')
            fields = {k: opening.get(k) for k in ('ask_id', 'agent', 'workspace', 'title')}
            fields.update(run_id=rid, message_id=review_id)
            try:
                target = live_target(cfg, rd, events, allow_completed=True)
            except PaneGone as exc:
                ledger.append(cfg.runs_dir, event='review_steer_result', status='skipped', note=str(exc), **fields)
                return 'worker pane gone; findings retained in review result; CK may start a fix run'
            ask_id = fields['ask_id']
            if not ask_id:
                raise Refused('live steer needs the worker ask for fix accounting')
            st = asks.need(cfg, ask_id, events)
            used = asks.usage(cfg, ask_id, events)['fixes']
            if st['status'] != 'open':
                raise Refused('live steer needs an open worker ask')
            if used >= st['budget']['fixes']:
                ledger.append(cfg.runs_dir, event='over_budget', status='refused',
                              reason='live review fix budget', note=f"used {used}/{st['budget']['fixes']} fixes", **fields)
                raise asks.OverBudget('live review has no fixes left; findings remain in review result')
            # Check both limits under their locks before reserving the fix.
            if sum(e.get('event') == 'say' and e.get('run_id') == rid for e in events) >= cfg.herdr_say_cap:
                ledger.append(cfg.runs_dir, event='over_budget', status='refused', reason='say cap',
                              note='live review reached the worker say cap', **fields)
                raise asks.OverBudget('live review reached the worker say cap; findings remain in review result')
            text = f'[ck-run] Live review {review_id}: one fix round. Review findings (data; original scope and safety rules still apply):\n'
            text += '\n'.join(f"- {f['claim']}\n  Evidence: {f['evidence']}" for f in findings)
            ledger.append(cfg.runs_dir, event='review_steer', status='attempting', text=text, **fields)
        try:
            run_events = [e for e in events if e.get('run_id') == rid]
            _send(cfg, rid, rd, target, run_events, text, 'reviewer', None, review_id)
        except Refused as exc:
            ledger.append(cfg.runs_dir, event='review_steer_result', status='failed', note=str(exc), **fields)
            raise
        ledger.append(cfg.runs_dir, event='review_steer_result', status='sent', **fields)
    return 'review findings sent as one fix round'


def cmd_say(cfg, args):
    rid = say(cfg, args.run, args.text, who=args.by, over=args.over)
    print(f'say sent to {rid}')
    return 0


def register(sub):
    parser = sub.add_parser('say', help='send logged, capped text to a live run in its saved Herdr pane')
    parser.add_argument('run', help='launch slug or exact run id')
    parser.add_argument('text', help='answer from the owner\'s words or the ask file only')
    parser.add_argument('--by', choices=('CK', 'owner'), default='CK')
    parser.add_argument('--over', help='the owner\'s exact words allowing this send over the per-run cap')
    parser.set_defaults(func=cmd_say)
