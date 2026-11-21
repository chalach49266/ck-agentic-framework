"""Audited Herdr messages between Grok Bot panes."""
import hashlib
import html
import json
import os
import re
import subprocess
import uuid
from xml.etree import ElementTree

from . import asks, herdr, ledger
from .errors import Refused

MACHINE = r"[A-Za-z0-9][A-Za-z0-9_.-]*"
PANE = r"t[0-9a-z]+"
ADDRESS = rf"{MACHINE}/{PANE}"
MESSAGE_ID = r"[A-Za-z0-9][A-Za-z0-9_.-]*"
ROLE = "ck.role=grokbot"
NATIVE = re.compile(r'<hc(?=\s|>)([^>]*)>(.*)</hc>\s*\Z', re.DOTALL)
NATIVE_FROM = re.compile(r'(?:^|\s)from="([^"]*)"')


def _hc(*args):
    try:
        return herdr.message_call(*args)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        raise Refused(f'Herdr {args[0]} unavailable: {exc}') from exc


def _machine():
    core = _hc('server', 'status', '--json').get('core')
    name = core.get('name') if isinstance(core, dict) else None
    if not isinstance(name, str) or not re.fullmatch(MACHINE, name):
        raise Refused('Herdr could not identify this machine')
    return name


def _qualified(address, machine):
    return f'{machine}/{address}' if re.fullmatch(PANE, address) else address


def _is_bot(pane):
    return (isinstance(pane, dict) and pane.get('state') == 'live'
            and isinstance(pane.get('labels'), dict) and pane['labels'].get('ck.role') == 'grokbot')


def _peer_name(host):
    peers = _hc('machine', 'ls', '--json').get('machines')
    if not isinstance(peers, list):
        raise Refused('Herdr returned no machine list')
    if any(isinstance(peer, dict) and peer.get('name') == host for peer in peers):
        return host
    names = {peer['name'] for peer in peers
             if isinstance(peer, dict) and peer.get('host') == host
             and isinstance(peer.get('name'), str) and re.fullmatch(MACHINE, peer['name'])}
    if len(names) > 1:
        raise Refused(f'Herdr host {host!r} has multiple routing names')
    return names.pop() if names else host


def _target(to, machine):
    explicit = '/' in to
    if re.fullmatch(MACHINE, to):
        panes = _hc('ls', '--json', '--label', ROLE).get('terminals')
        if not isinstance(panes, list):
            raise Refused('Herdr returned no terminal list')
        matches = set()
        # hc ls applies the label filter but its summary rows omit labels.
        for pane in panes:
            if isinstance(pane, dict) and pane.get('state') == 'live' and isinstance(pane.get('address'), str):
                address = _qualified(pane['address'], machine)
                if re.fullmatch(ADDRESS, address) and address.partition('/')[0] == to:
                    matches.add(address)
        if len(matches) != 1:
            raise Refused(f'{to} must have exactly one live Herdr pane labelled {ROLE}; found {len(matches)}')
        to = matches.pop()
    if not re.fullmatch(ADDRESS, to):
        raise Refused('message target must be a machine name or machine/tN')
    host, _, pane_id = to.partition('/')
    if host == machine:
        return to, pane_id
    canonical = f'{_peer_name(host)}/{pane_id}' if explicit else to
    return canonical, canonical


def _escape(text):
    return (html.escape(text).replace('\t', '&#9;').replace('\r', '&#13;')
            .replace('\n', '&#10;'))


def _check_text(text, name):
    if not text.strip():
        raise Refused(f'{name} is empty')
    if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\ufffe\uffff]', text):
        raise Refused(f'{name} contains a terminal control character')


def send(cfg, to, text, ask=None, words=None):
    _check_text(text, 'message')
    if ask is not None and not asks.ASK_ID_RE.fullmatch(ask):
        raise Refused('message ask must be an ask id')
    if words is not None:
        _check_text(words, '--words')
    pane = os.environ.get('HC_TERMINAL_ID', '')
    if not re.fullmatch(PANE, pane):
        raise Refused('send from your own Herdr pane (HC_TERMINAL_ID is missing or invalid)')
    machine = _machine()
    to, target = _target(to, machine)
    message_id = uuid.uuid4().hex
    sender = f'{machine}/{pane}'
    fields = {'from': sender, 'to': to, 'message_id': message_id, 'ask_id': ask, 'words': words, 'text': text}
    opening = f'<ck-msg from="{sender}" id="{message_id}" ask="{_escape(ask or "")}"'
    if words is not None:
        opening += f' words="{_escape(words)}"'
    raw = f'{opening}>{_escape(text)}</ck-msg>'
    info = _hc('get', '--json', target)
    if not _is_bot(info) or info.get('address') != target:
        raise Refused(f'{to} is absent, finished, or missing {ROLE}')
    ledger.append(cfg.runs_dir, event='msg_out', status='attempting', **fields)
    reason = None
    try:
        receipt = herdr.message_call('send', '--json', '--', target, raw, timeout=120)
        if receipt.get('sent') is False:
            reason = str(receipt.get('reason') or 'Herdr did not send')
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        reason = str(exc) or type(exc).__name__
    ledger.append(cfg.runs_dir, event='msg_out_result', status='unconfirmed' if reason else 'sent',
                  note=reason, **fields)
    if reason:
        raise Refused(f'message {message_id} delivery is unconfirmed: {reason}. Check the ledger before retrying')
    return message_id


def _native_sender(header):
    from_attr = NATIVE_FROM.search(header)
    sender = html.unescape(from_attr[1]).split(maxsplit=1) if from_attr else []
    address = sender[0] if sender else ''
    if re.fullmatch(PANE, address):
        try:
            address = _qualified(address, _machine())
        except Refused:
            pass  # the note is still received, with no route for a reply
    return address if re.fullmatch(ADDRESS, address) else None


def _receipt_id(raw):
    return 'hc-' + hashlib.sha256(raw.encode()).hexdigest()


def _ck_message(raw, *, native_header=None, raw_envelope=None):
    try:
        node = ElementTree.fromstring(raw)
    except ElementTree.ParseError as exc:
        raise Refused('invalid ck-msg envelope') from exc
    allowed = {'from', 'id', 'ask', 'words'}
    legacy_reply = (native_header is not None and 'id' not in node.attrib
                    and re.fullmatch(MESSAGE_ID, node.get('reply-to', '')))
    if legacy_reply:
        allowed.update(('kind', 'reply-to'))
    if node.tag != 'ck-msg' or len(node) or set(node.attrib) - allowed:
        raise Refused('invalid ck-msg envelope')
    sender, message_id = node.get('from', ''), node.get('id', '')
    if native_header is not None:
        # A Herdr wrapper may use a hostname where the inner message uses a peer alias.
        wrapped_sender = _native_sender(native_header)
        sender = wrapped_sender or ('' if legacy_reply else sender)
    if legacy_reply:
        # reply-to identifies the earlier message, so generate an ID for this receipt.
        message_id = _receipt_id(raw_envelope)
    ask, words, text = node.get('ask') or None, node.get('words'), node.text or ''
    if not re.fullmatch(ADDRESS, sender) or not re.fullmatch(MESSAGE_ID, message_id):
        raise Refused('invalid ck-msg sender or id')
    if ask is not None and not asks.ASK_ID_RE.fullmatch(ask):
        raise Refused('invalid ck-msg ask id')
    _check_text(text, 'message')
    if words is not None:
        _check_text(words, 'words')
    return dict(message_id=message_id, ask_id=ask, words=words, text=text, **{'from': sender})


def log_in(cfg, raw):
    envelope = raw.strip()
    native = NATIVE.fullmatch(envelope)
    payload = native[2].strip() if native else envelope
    if payload.startswith('<ck-msg'):
        fields = _ck_message(payload, native_header=native[1] if native else None, raw_envelope=raw)
    elif native:
        fields = dict(message_id=_receipt_id(raw), text=native[2], **{'from': _native_sender(native[1])})
    else:
        raise Refused('incoming message must be a ck-msg or hc envelope')
    ledger.append(cfg.runs_dir, event='msg_in', status='received', note=raw, **fields)
    return {k: fields.get(k) for k in ('from', 'message_id', 'words')}


def reply(cfg, message_id, text):
    earlier = {(e.get('from'), e.get('ask_id'), e.get('words'), e.get('text'))
               for e in ledger.load(cfg.runs_dir)
               if e.get('event') == 'msg_in' and e.get('message_id') == message_id}
    if len(earlier) != 1:
        raise Refused(f'unknown or ambiguous received message id {message_id!r}')
    sender, ask, _, _ = earlier.pop()
    if not sender:
        raise Refused('received message has no routable sender')
    return send(cfg, sender, text, ask=ask)


def cmd_msg(cfg, args):
    if args.target == 'log' and args.raw is not None and all(
            x is None for x in (args.value, args.reply_text, args.ask, args.words)):
        print(json.dumps(log_in(cfg, args.raw)))
        return 0
    if args.target == 'reply' and args.value is not None and args.reply_text is not None and all(
            x is None for x in (args.raw, args.ask, args.words)):
        message_id = reply(cfg, args.value, args.reply_text)
    elif args.target not in ('log', 'reply') and args.value is not None and args.reply_text is None and args.raw is None:
        message_id = send(cfg, args.target, args.value, args.ask, args.words)
    else:
        raise Refused('use msg <machine|machine/tN> <text>, msg reply <id> <text>, or msg log --in <raw>')
    print(f'message {message_id} sent')
    return 0


def register(sub):
    p = sub.add_parser('msg', help='send, reply to, or log an audited Herdr bot message', allow_abbrev=False)
    p.add_argument('target', help='machine name, machine/tN, reply, or log')
    p.add_argument('value', nargs='?', help='message text or received id')
    p.add_argument('reply_text', nargs='?', help='reply text')
    p.add_argument('--ask', help='related ask id')
    p.add_argument('--words', help="the owner's exact words")
    p.add_argument('--in', dest='raw', help='raw incoming Herdr envelope (msg log only)')
    p.set_defaults(func=cmd_msg)
