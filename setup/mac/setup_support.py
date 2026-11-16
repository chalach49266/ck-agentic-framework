"""Portable installer. Dry-run never creates files or starts external commands."""
from __future__ import annotations
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

MAC = Path(__file__).resolve().parent
KIT = MAC.parent.parent
COMMON = KIT / 'setup/common'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--yes', action='store_true', help='Use the supplied paths without prompts; requires --phd-root')
    ap.add_argument('--mac-user', default=os.environ.get('MAC_USER') or os.environ.get('USER') or Path.home().name)
    ap.add_argument('--phd-root', help='Full PhD parent folder as an absolute Mac path')
    ap.add_argument('--no-plugins', action='store_true', help='Offline: skip marketplace and plugin commands; bundled skills still install')
    ap.add_argument('--no-tests', action='store_true')
    ap.add_argument('--coursework-root', help='Optional full coursework workspace path; defaults to ~/Downloads/WashU HW')
    args = ap.parse_args()
    home = Path.home().absolute()
    mac_user = args.mac_user
    if not args.phd_root and (args.yes or not sys.stdin.isatty()):
        ap.error('Pass --phd-root "/full/Mac/path/to/PhD" when running without a terminal or with --yes. No PhD folder was guessed; no files were changed.')
    phd = args.phd_root
    if not args.yes and sys.stdin.isatty():
        mac_user = input(f'Mac user [{mac_user}]: ').strip() or mac_user
        candidate = os.environ.get('PHD_ROOT') or str(home / 'Documents/PhD')
        phd_default = args.phd_root or (candidate if Path(candidate).is_dir() else '')
        suffix = f' [{phd_default}]' if phd_default else ''
        phd = input(f'Full PhD folder (Mac path){suffix}: ').strip() or phd_default
        if not phd:
            ap.error('PhD folder is required. Pass --phd-root "/full/Mac/path/to/PhD". No files were changed.')
    if not re.fullmatch(r'[A-Za-z0-9_. -]+', mac_user):
        ap.error('Mac user must contain letters, digits, spaces, dots, underscores or hyphens.')
    # Templates contain shell/Python strings. Reject shell metacharacters instead of evaluating input.
    if not phd.startswith('/') or any(c in str(home) + phd for c in '\n\r\0"\'`$\\{}'):
        ap.error('HOME and PHD_ROOT must be absolute Mac paths without quotes or shell metacharacters.')
    coursework = args.coursework_root or str(home / 'Downloads/WashU HW')
    if not coursework.startswith('/') or any(c in coursework for c in '\n\r\0\"\'`$\\{}'):
        ap.error('Coursework root must be an absolute path without quotes or shell metacharacters.')
    local = home / 'PhD_local'
    for name, target in (('ck-dispatch', 'ck-dispatch'), ('ckstack', 'ckstack'),
                         ('grokbot-mod', 'grokbot-mod'), ('skills', 'grok-bot-skills')):
        source, destination = KIT / 'core' / name, local / target
        if source.is_relative_to(destination) or destination.is_relative_to(source):
            ap.error(f'Keep the source {source} separate from the install destination {destination}.')
    values = {'MAC_USER': mac_user, 'MAC_HOME': str(home), 'PHD_ROOT': phd, 'WSL_HOME': str(home),
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

    def backup_existing(path):
        if not path.exists():
            return
        stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        base = path.with_name(path.name + '.bak-' + stamp)
        backup, suffix = base, 0
        while True:
            safe(backup)
            try:
                # Exclusive creation also protects backups made in the same second.
                with backup.open('xb') as target, path.open('rb') as source:
                    shutil.copyfileobj(source, target)
                shutil.copystat(path, backup)
                action(f'BACKUP {path} -> {backup}')
                return
            except FileExistsError:
                suffix += 1
                backup = base.with_name(base.name + f'-{suffix}')

    def mkdir(path):
        safe(path)
        action(f'MKDIR {path}')
        if not args.dry_run:
            path.mkdir(parents=True, exist_ok=True)

    def render(text):
        for key, val in values.items():
            text = text.replace('{{' + key + '}}', val)
        return text

    def install(src, dst, *, only_if_absent=False):
        safe(dst)
        if only_if_absent and dst.exists():
            action(f'kept yours: {dst}')
            return
        rule = 'copy only if absent' if only_if_absent else 'changed existing file gets timestamped .bak-YYYYMMDD-HHMMSS'
        action(f'COPY + fill placeholders {src.relative_to(KIT)} -> {dst}; {rule}')
        if args.dry_run:
            return
        text = src.read_text()
        if src.suffix == '.json':
            def walk(v):
                if isinstance(v, str): return render(v)
                if isinstance(v, list): return [walk(x) for x in v]
                if isinstance(v, dict): return {k: walk(x) for k, x in v.items()}
                return v
            data = walk(json.loads(text))
            if src == KIT / 'core/ck-dispatch/config/workspaces.json':
                data['live'].update(osascript=str(local / 'ck-dispatch/platform/mac/osascript'), caffeinate='/usr/bin/caffeinate', terminal='iTerm2')
                data['bin_dirs'] = ['~/.local/bin', '/opt/homebrew/bin', '/usr/local/bin', '/usr/bin', '/bin', '/usr/sbin', '/sbin']
                data['workspaces']['washu']['root'] = coursework
            text = json.dumps(data, indent=2) + '\n'
        else:
            text = render(text)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.read_text() != text:
            backup_existing(dst)
            dst.write_text(text)
        dst.chmod(src.stat().st_mode & 0o777)

    def command(argv, cwd=None):
        action('RUN ' + (f'(in {cwd}) ' if cwd else '') + shlex.join(map(str, argv)))
        if not args.dry_run:
            subprocess.run(list(map(str, argv)), cwd=cwd, check=True)

    action(f'USE Mac user {mac_user}; PHD_ROOT={phd}; COPY mode into {local}')
    for path in (local, home / '.local/bin', local / 'agent_runs', local / 'grokbot_router'):
        mkdir(path)
    for name, target in (('ck-dispatch', 'ck-dispatch'), ('ckstack', 'ckstack'),
                         ('grokbot-mod', 'grokbot-mod'), ('skills', 'grok-bot-skills')):
        source = KIT / 'core' / name
        mkdir(local / target)
        for src in sorted(source.rglob('*')):
            if src.is_file() and not any(part in ('.git', '__pycache__') for part in src.parts) and src.suffix != '.pyc':
                install(src, local / target / src.relative_to(source))
    install(MAC / 'ck_shortcuts.zsh', home / '.ck_shortcuts.zsh')
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
    bashrc = home / '.zshrc'
    safe(bashrc)
    line = '[ -f "$HOME/.ck_shortcuts.zsh" ] && . "$HOME/.ck_shortcuts.zsh"'
    action(f'ENSURE {line} at end of {bashrc}')
    if not args.dry_run:
        old = bashrc.read_text() if bashrc.exists() else ''
        if line not in old.splitlines():
            backup_existing(bashrc)
            bashrc.write_text(old + ('\n' if old and not old.endswith('\n') else '') + line + '\n')
    # Herdr files are portable preferences, never the app's view, machine list or live documents.
    for src in sorted((MAC / 'herdr').rglob('*')):
        if src.is_file():
            install(src, home / '.config/herdr-app' / src.relative_to(MAC / 'herdr'), only_if_absent=True)
    icon = local / 'ck-dispatch/bin/herdr-icons/agent'
    safe(icon.parent)
    action(f'LINK {icon} -> /bin/bash (native Cursor pane icon shell)')
    if not args.dry_run:
        icon.parent.mkdir(parents=True, exist_ok=True)
        if icon.is_symlink() and os.readlink(icon) == '/bin/bash':
            pass
        elif icon.exists() or icon.is_symlink():
            raise RuntimeError(f'Existing unrelated icon shell: {icon}')
        else:
            icon.symlink_to('/bin/bash')
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
        target = home / '.claude/plugins/store' / src.name
        if target.exists():
            action(f'KEEP existing plugin preferences {target}')
        else:
            install(src, target)
    settings = home / '.claude/settings.json'
    safe(settings)
    action(f'MERGE common settings then Mac portable settings into {settings}; preserve other keys and timestamp each changed backup')
    action('MERGE iTerm cc-status hooks only if the installed app supplies the helper; keep other hooks')
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

        extra = merge(extra, json.loads((MAC / 'claude.json').read_text()))
        updated = merge(old, extra)
        helper = next((p for p in (home / 'Applications/iTerm.app/Contents/Resources/utilities/cc-status', Path('/Applications/iTerm.app/Contents/Resources/utilities/cc-status')) if p.is_file()), None)
        if helper:
            hooks = updated.setdefault('hooks', {})
            for event in ('Notification', 'PermissionRequest', 'PostToolUse', 'PreToolUse', 'SessionEnd', 'SessionStart', 'Stop', 'StopFailure', 'SubagentStop', 'UserPromptSubmit'):
                rows = hooks.setdefault(event, [])
                entry = {'hooks': [{'type': 'command', 'command': shlex.quote(str(helper))}]}
                if entry not in rows:
                    rows.append(entry)
        if not settings.exists() or updated != old:
            backup_existing(settings)
            settings.write_text(json.dumps(updated, indent=2) + '\n')
    command(['bash', COMMON / 'smoke.sh'])
    if args.no_tests:
        action('SKIP offline tests (--no-tests)')
    else:
        command(['python3', '-I', local / 'ck-dispatch/tests/run_all.py'])
        command(['python3', '-I', '-m', 'unittest', 'discover', '-s', local / 'ck-dispatch/platform/mac/tests'])
    action('DONE. Open a new terminal for the PATH and shortcuts.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as e:
        print(f'Setup failed: {e}', file=sys.stderr)
        sys.exit(1)
