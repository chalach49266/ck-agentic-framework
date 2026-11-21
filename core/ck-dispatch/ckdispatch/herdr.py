"""Herdr transport and local control for ck-run's saved pane identities."""
from functools import lru_cache
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys

from .config import REPO

STATE_FILE = "live-host.json"
LOCAL_ADDRESS = re.compile(r"t[0-9a-z]+")


def local_address(value):
    return isinstance(value, str) and LOCAL_ADDRESS.fullmatch(value) is not None


def transport(cfg):
    path = Path(cfg.live_osascript).resolve()
    platform = Path(REPO, "platform")
    if sys.platform == "darwin" and path == platform / "mac/osascript":
        return "mac"
    if sys.platform == "linux" and path in (platform / "auto/osascript", platform / "herdr/osascript"):
        return "herdr"
    return None


@lru_cache(maxsize=2)
def adapter(side):
    entry = "herdr.py" if side == "mac" else "osascript"
    path = Path(REPO, "platform", side, entry)
    loader = SourceFileLoader(f"_ckdispatch_{side}_herdr", str(path))
    spec = spec_from_loader(loader.name, loader)
    module = module_from_spec(spec)
    loader.exec_module(module)
    return module


def call(cfg, command, target, *args, timeout=20):
    side = transport(cfg)
    if not side or not local_address(target):
        raise ValueError("Herdr requires a local terminal address and configured adapter")
    backend = adapter(side)
    if command == "send":
        # End option parsing before worker or user text, even when it looks like an hc flag.
        if side == "mac":
            return backend.invoke([backend.hc_path(), "send", "--json", "--", target, *args], timeout=timeout)
        proc = backend.hc("send", "--json", "--", target, *args, timeout=timeout)
        return _json_reply(proc, command)
    elif side == "mac":
        return backend.invoke([backend.hc_path(), command, "--json", target, *args], timeout=timeout)
    else:
        rc, info = backend.hc_json(command, target, *args, timeout=timeout)
    if rc or not isinstance(info, dict) or "error" in info:
        raise ValueError(f"local hc {command} failed (exit {rc})")
    return info


def _json_reply(proc, command):
    try:
        info = json.loads(proc.stdout)
    except ValueError:
        info = None
    if proc.returncode or not isinstance(info, dict) or "error" in info:
        detail = info.get("error") if isinstance(info, dict) else None
        raise ValueError(str(detail or proc.stderr.strip() or f"hc {command} failed (exit {proc.returncode})"))
    return info


def message_call(*args, timeout=10):
    """Run an explicit bot-message RPC independently of the worker launch transport."""
    if sys.platform == "darwin":
        backend = adapter("mac")
        return backend.invoke([backend.hc_path(), *args], timeout=timeout)
    if sys.platform == "linux":
        proc = adapter("herdr").hc(*args, timeout=timeout)
    else:
        hc = os.environ.get("CK_HERDR_HC") or os.environ.get("CK_HC") or shutil.which("hc.exe")
        if not hc:
            local = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
            hc = str(local / "Programs" / "herdr-core" / "hc.exe")
        proc = subprocess.run([hc, *args], stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return _json_reply(proc, args[0])


def saved(run_dir):
    try:
        data = json.loads((Path(run_dir) / STATE_FILE).read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def calling_parent(cfg):
    # On the PC the adapter discovers the parent during launch. A tmux launch has no parent.
    if transport(cfg) != "mac":
        return ""
    try:
        host = adapter("mac").detect_host(cfg.live_terminal)
    except ValueError:
        return ""
    return host.partition(":")[2] if host.startswith("herdr:") else ""


def parent_target(run_dir, context):
    pane = saved(run_dir)
    host = str(pane.get("host") or "")
    target = host.partition(":")[2] if host.startswith("herdr:") else context.get("parent")
    return target if local_address(target) else ""


def close_pane(cfg, target, log):
    if not local_address(target):
        return False
    side = transport(cfg)
    if side == "mac":
        return adapter(side).close_pane(target, log)
    if side == "herdr":
        # Reuse the PC's existing exact-address close and layout cleanup.
        from . import live
        return live.close_session(cfg.live_osascript, os.environ.copy(), session_id=target)
    return False


DOORBELL_CONTEXT = "doorbell-context.json"
DOORBELL_RECEIPT = "doorbell-receipt.json"


def prepare_doorbell(cfg, run_id, run_dir):
    """Persist the original destination for reattach; never infer it from a worker's terminal."""
    slug = os.environ.get("CK_RUN_SLUG") or run_id
    out = os.environ.get("CK_RUN_OUT")
    if not out:
        # Older documented .sh launches export only the host. Recover their .out from stdout's
        # file identity so the mod's existing watcher still owns the wake. No file contents are read.
        try:
            output_stat = os.fstat(1)
            if stat.S_ISREG(output_stat.st_mode):
                for candidate in Path(cfg.runs_dir).glob("*.out"):
                    try:
                        candidate_stat = candidate.stat()
                    except OSError:
                        continue
                    if os.path.samestat(candidate_stat, output_stat):
                        out, slug = str(candidate), candidate.stem
                        break
        except OSError:
            pass
    out = out or str(Path(run_dir) / "summary.md")
    context = {"slug": slug, "out": out, "parent": calling_parent(cfg)}
    (Path(run_dir) / DOORBELL_CONTEXT).write_text(json.dumps(context) + "\n")


def _mod_owns(cfg, context):
    """Read only the Grokbot plugin's pending store, never session transcripts or credentials.

    The mod retains a pending entry until its .out has the final exit marker. Our completion runs
    before that marker. An unreadable store suppresses auto delivery rather than risking a double wake.
    """
    stores = (Path(cfg.home) / ".claude/plugins/store").glob("grokbot_ck-grokbot-*.json")
    for path in stores:
        try:
            data = json.loads(path.read_text())
            if not isinstance(data, dict):
                return True, f"watcher ownership unknown: malformed {path}"
            pending = data["pending"] if "pending" in data else []
            if not isinstance(pending, list) or any(not isinstance(p, dict) for p in pending):
                return True, f"watcher ownership unknown: malformed {path}"
            if any(p.get("out") == context["out"] for p in pending):
                return True, f"Grokbot watcher owns output ({path})"
        except (OSError, ValueError, TypeError):
            return True, f"watcher ownership unknown: cannot read {path}"
    return False, "no Grokbot watcher owns output"


def parent_note_skip(cfg):
    """Shared parent-note policy. Completion ownership is checked only for completion notes."""
    if cfg.herdr_doorbell == "off":
        return "herdr.doorbell=off"
    return ""


def send_note(cfg, run_dir, target, text):
    with (Path(run_dir) / "herdr.log").open("a") as log:
        try:
            reply = call(cfg, "send", target, text, timeout=120)
            log.write(f"hc send to {target}: {reply.get('status', 'accepted')}\n")
            return "sent", ""
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            log.write(f"hc send to {target} failed: {exc}\n")
            return "failed", str(exc)


def doorbell(cfg, run_dir, base, exit_code):
    """One durable attempt per run. Never retry ambiguous sends or bypass hc draft/blocked guards."""
    from . import ledger

    try:
        context = json.loads((Path(run_dir) / DOORBELL_CONTEXT).read_text())
    except (OSError, ValueError):
        return  # old runs have no reliable original launch context
    if not isinstance(context, dict) or not isinstance(context.get("slug"), str) or not isinstance(context.get("out"), str):
        return
    target = parent_target(run_dir, context)
    if not target:
        return
    mode = cfg.herdr_doorbell
    skip = parent_note_skip(cfg)
    if mode == "auto":
        owned, reason = _mod_owns(cfg, context)
        if owned:
            skip = reason
    receipt = Path(run_dir) / DOORBELL_RECEIPT
    try:
        fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return  # includes attempts interrupted after submission; no automatic retry
    text = f"[ck-run] {context['slug']} finished (exit {exit_code}). Read {context['out']}"
    record = {"target": target, "text": text, "status": "skipped" if skip else "attempting", "reason": skip}
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps(record) + "\n")
        f.flush()
        os.fsync(f.fileno())
    if not skip:
        record["status"], record["reason"] = send_note(cfg, run_dir, target, text)
    receipt.write_text(json.dumps(record, indent=2) + "\n")
    fields = dict(base, event="doorbell", status=record["status"], exit_code=exit_code,
                  slug=context["slug"], response_path=context["out"],
                  note=f"target={target}; {text}; {record['reason']}")
    fields.update({"from": "ck-run", "to": "CK"})
    ledger.append(cfg.runs_dir, **fields)
