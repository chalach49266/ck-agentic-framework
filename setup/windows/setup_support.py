"""Portable installer. Dry-run never creates files or starts external commands."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

WINDOWS = Path(__file__).resolve().parent
KIT = WINDOWS.parent.parent
COMMON = KIT / 'setup/common'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--yes', action='store_true', help='Use the supplied paths without prompts; requires --phd-root')
    ap.add_argument('--win-user', default=os.environ.get('WIN_USER') or os.environ.get('CK_WIN_USER') or os.environ.get('USERNAME') or os.environ.get('USER', 'user'))
    ap.add_argument('--phd-root', help='Full PhD parent folder as an absolute WSL path')
    ap.add_argument('--no-plugins', action='store_true', help='Offline: skip marketplace and plugin commands; bundled skills still install')
    ap.add_argument('--no-tests', action='store_true')
    args = ap.parse_args()
    home = Path.home().absolute()
    win_user = args.win_user
    if not args.phd_root and (args.yes or not sys.stdin.isatty()):
        ap.error('Pass --phd-root "/full/WSL/path/to/PhD" when running without a terminal or with --yes. No PhD folder was guessed; no files were changed.')
    phd = args.phd_root
    if not args.yes and sys.stdin.isatty():
        win_user = input(f'Windows user [{win_user}]: ').strip() or win_user
        candidate = os.environ.get('PHD_ROOT') or f'/mnt/c/Users/{win_user}/Documents/PhD'
        phd_default = args.phd_root or (candidate if Path(candidate).is_dir() else '')
        suffix = f' [{phd_default}]' if phd_default else ''
        phd = input(f'Full PhD folder (WSL path){suffix}: ').strip() or phd_default
        if not phd:
            ap.error('PhD folder is required. Pass --phd-root "/full/WSL/path/to/PhD". No files were changed.')
    if not re.fullmatch(r'[A-Za-z0-9_. -]+', win_user):
        ap.error('Windows user must contain letters, digits, spaces, dots, underscores or hyphens.')
    # Templates contain shell/Python strings. Reject shell metacharacters instead of evaluating input.
    if not phd.startswith('/') or any(c in str(home) + phd for c in '\n\r\0"\'`$\\{}'):
        ap.error('HOME and PHD_ROOT must be absolute WSL paths without quotes or shell metacharacters.')
    local = home / 'PhD_local'
    for name, target in (('ck-dispatch', 'ck-dispatch'), ('ckstack', 'ckstack'),
                         ('grokbot-mod', 'grokbot-mod'), ('skills', 'grok-bot-skills')):
        source, destination = KIT / 'core' / name, local / target
        if source.is_relative_to(destination) or destination.is_relative_to(source):
            ap.error(f'Keep the source {source} separate from the install destination {destination}.')
    values = {'WIN_USER': win_user, 'PHD_ROOT': phd, 'WSL_HOME': str(home),
              'LOCAL_ROOT': str(local), 'ONEDRIVE_ROOT': str(Path(phd).parent.parent)}

    def action(text):
        print(('DRY-RUN ' if args.dry_run else '') + text, flush=True)

    def safe(path):
        if path != home and not path.is_relative_to(home):
            raise RuntimeError(f'Destination outside HOME: {path}')
        for p in [path, *path.parents]:
            if p == home:
                break
            if p.is_symlink() and not args.dry_run:
                raise RuntimeError(f'Refusing existing symlink destination: {p}; move it aside yourself first.')

    def mkdir(path):
        safe(path)
        action(f'MKDIR {path}')
        if not args.dry_run:
            path.mkdir(parents=True, exist_ok=True)

    def render(text):
        for key, val in values.items():
            text = text.replace('{{' + key + '}}', val)
        return text

    def install(src, dst):
        safe(dst)
        action(f'COPY + fill placeholders {src.relative_to(KIT)} -> {dst}')
        if args.dry_run:
            return
        text = src.read_text()
        if src.suffix == '.json':
            def walk(v):
                if isinstance(v, str): return render(v)
                if isinstance(v, list): return [walk(x) for x in v]
                if isinstance(v, dict): return {k: walk(x) for k, x in v.items()}
                return v
            text = json.dumps(walk(json.loads(text)), indent=2) + '\n'
        else:
            text = render(text)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.read_text() != text:
            dst.write_text(text)
        dst.chmod(src.stat().st_mode & 0o777)

    def command(argv, cwd=None):
        action('RUN ' + (f'(in {cwd}) ' if cwd else '') + shlex.join(map(str, argv)))
        if not args.dry_run:
            subprocess.run(list(map(str, argv)), cwd=cwd, check=True)

    action(f'USE Windows user {win_user}; PHD_ROOT={phd}; COPY mode into {local}')
    for path in (local, home / '.local/bin', local / 'agent_runs', local / 'grokbot_router'):
        mkdir(path)
    for name, target in (('ck-dispatch', 'ck-dispatch'), ('ckstack', 'ckstack'),
                         ('grokbot-mod', 'grokbot-mod'), ('skills', 'grok-bot-skills')):
        source = KIT / 'core' / name
        mkdir(local / target)
        for src in sorted(source.rglob('*')):
            if src.is_file() and not any(part in ('.git', '__pycache__') for part in src.parts) and src.suffix != '.pyc':
                install(src, local / target / src.relative_to(source))
    install(WINDOWS / 'wsl/ck_shortcuts.sh', home / '.ck_shortcuts.sh')
    install(WINDOWS / 'wsl/ck-open', home / '.local/bin/ck-open')
    dst = home / '.local/bin/ck-run'
    safe(dst.parent)
    action(f'LINK {dst} -> {local / "ck-dispatch/bin/ck-run"}')
    if not args.dry_run:
        if dst.is_symlink():
            if dst.resolve() != (local / 'ck-dispatch/bin/ck-run').resolve():
                raise RuntimeError(f'Existing unrelated link: {dst}')
        elif dst.exists():
            raise RuntimeError(f'Existing file: {dst}; move it aside first.')
        else:
            dst.symlink_to(local / 'ck-dispatch/bin/ck-run')
    bashrc = home / '.bashrc'
    safe(bashrc)
    line = '[ -f "$HOME/.ck_shortcuts.sh" ] && . "$HOME/.ck_shortcuts.sh"'
    action(f'ENSURE {line} at start of {bashrc}')
    if not args.dry_run:
        old = bashrc.read_text() if bashrc.exists() else ''
        if line not in old.splitlines():
            bashrc.write_text(line + '\n' + old)
    if args.no_plugins:
        action('SKIP network: marketplaces and plugin installs (--no-plugins); skills copied from core/skills')
    else:
        markets = json.loads((COMMON / 'claude/marketplaces.json').read_text())
        known = {}
        action('READ claude plugin marketplace list --json (local registry)')
        if not args.dry_run:
            registered = subprocess.run(['claude', 'plugin', 'marketplace', 'list', '--json'],
                                        check=True, capture_output=True, text=True)
            known = {item['name']: item for item in json.loads(registered.stdout)}
        for name, info in markets.items():
            source = render(info.get('path', info.get('repo', '')))
            if name in known:
                previous = known[name].get('path', known[name].get('repo', ''))
                if previous != source:
                    raise RuntimeError(f'Marketplace {name} already uses another source: {previous}')
                action(f'KEEP registered marketplace {name} ({source})')
            else:
                command(['claude', 'plugin', 'marketplace', 'add', source])
        for row in (COMMON / 'claude/plugins.txt').read_text().splitlines():
            if not row or row.startswith('#'):
                continue
            plugin, scope, folder = row.split(' ', 2)
            cwd = Path(phd) / folder if scope == 'local' else home
            if scope == 'local' and not cwd.is_dir():
                action(f'WARNING: SKIP {plugin}: project folder is missing: {cwd}. Restore it, then rerun setup to install this local plugin.')
                continue
            command(['claude', 'plugin', 'install', plugin, '--scope', scope], cwd=cwd)
    mkdir(home / '.claude/plugins/store')
    for src in sorted((COMMON / 'claude/store').glob('*.json')):
        install(src, home / '.claude/plugins/store' / src.name)
    settings = home / '.claude/settings.json'
    safe(settings)
    action(f'MERGE theme, modelSettings, agentPushNotifEnabled into {settings}; preserve other keys and original .bak')
    if not args.dry_run:
        old = json.loads(settings.read_text()) if settings.exists() else {}
        if not isinstance(old, dict):
            raise RuntimeError('Claude settings must be a JSON object')
        extra = json.loads((COMMON / 'claude/settings.json').read_text())

        def merge(base, changes):
            result = dict(base)
            for key, val in changes.items():
                if isinstance(val, dict) and isinstance(result.get(key), dict):
                    result[key] = merge(result[key], val)
                else:
                    result[key] = val
            return result

        updated = merge(old, extra)
        if not settings.exists() or updated != old:
            backup = settings.with_name(settings.name + '.bak')
            safe(backup)
            if settings.exists() and not backup.exists():
                shutil.copy2(settings, backup)
            settings.write_text(json.dumps(updated, indent=2) + '\n')
    if args.no_tests:
        action('SKIP offline tests (--no-tests)')
    else:
        command(['python3', '-I', local / 'ck-dispatch/tests/run_all.py'])
    action('DONE. Open a new terminal for the PATH and shortcuts.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as e:
        print(f'Setup failed: {e}', file=sys.stderr)
        sys.exit(1)
