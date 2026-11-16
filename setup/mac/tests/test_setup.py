"""Offline installer regression: only a temporary HOME is written."""
import os
import contextlib
from datetime import datetime
import importlib.util
import io
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest import mock


KIT = Path(__file__).resolve().parents[3]


class InstallerPreservesEdits(unittest.TestCase):
    def test_same_second_backups_never_replace_an_earlier_revision(self):
        spec = importlib.util.spec_from_file_location('mac_setup', KIT / 'setup/mac/setup_support.py')
        setup = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(setup)
        with tempfile.TemporaryDirectory(prefix='ck-mac-backup-') as temporary:
            home = Path(temporary)
            argv = ['setup', '--yes', '--mac-user', 'test-user', '--phd-root', str(home / 'PhD'),
                    '--no-plugins', '--no-tests']
            with mock.patch.dict(os.environ, {'HOME': str(home)}), mock.patch('sys.argv', argv), \
                    mock.patch.object(setup, 'datetime') as clock, \
                    mock.patch.object(setup.subprocess, 'run'), contextlib.redirect_stdout(io.StringIO()):
                clock.now.return_value = datetime(2026, 1, 1)
                setup.main()
                target = home / '.ck_shortcuts.zsh'
                for text in ('earlier edit', 'later edit'):
                    target.write_text(text)
                    setup.main()
                backups = sorted(target.parent.glob(target.name + '.bak-*'))
                self.assertEqual([p.read_text() for p in backups], ['earlier edit', 'later edit'])
                self.assertEqual([p.name for p in backups], [target.name + '.bak-20260101-000000',
                                                           target.name + '.bak-20260101-000000-1'])

    def test_install_edit_reinstall_preserves_or_backs_up_every_revision(self):
        with tempfile.TemporaryDirectory(prefix='ck-mac-install-') as temporary:
            home = Path(temporary)
            env = {**os.environ, 'HOME': str(home), 'PYTHONDONTWRITEBYTECODE': '1'}
            command = ['bash', str(KIT / 'setup/mac/setup.sh'), '--yes',
                       '--mac-user', 'test-user', '--phd-root', str(home / 'PhD files'),
                       '--no-plugins', '--no-tests']

            def install():
                result = subprocess.run(command, env=env, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout

            herdr = home / '.config/herdr-app'
            user_files = [herdr / relative for relative in (
                'keys.json', 'settings.json', 'layouts/ck-main.json',
                'themes/win98.json', 'mods/ck-tabs/main.js')]
            # Include a file that predates the very first installation.
            user_files[0].parent.mkdir(parents=True)
            user_files[0].write_text('preexisting user shortcuts\n')
            first = install()
            self.assertEqual(user_files[0].read_text(), 'preexisting user shortcuts\n')
            self.assertIn(f'kept yours: {user_files[0]}', first)

            replaced = [home / '.ck_shortcuts.zsh',
                        home / 'PhD_local/ck-dispatch/bin/ck-run',
                        home / '.zshrc', home / '.claude/settings.json']
            for path in replaced:
                path.with_name(path.name + '.bak').write_text('older backup\n')
            for revision in ('first edit', 'second edit'):
                edits = {}
                for path in user_files + replaced:
                    # Valid JSON lets the settings merge run and exercise its backup.
                    text = ('{"theme": "' + revision + '"}\n'
                            if path.suffix == '.json' else revision + '\n')
                    path.write_text(text)
                    edits[path] = text
                output = install()
                for path in user_files:
                    self.assertEqual(path.read_text(), edits[path])
                    self.assertIn(f'kept yours: {path}', output)
                for path in replaced:
                    backups = list(path.parent.glob(path.name + '.bak-*'))
                    self.assertTrue(any(p.read_text() == edits[path] for p in backups), path)
                    self.assertTrue(all(re.fullmatch(
                        re.escape(path.name) + r'\.bak-\d{8}-\d{6}(?:-\d+)?', p.name)
                                        for p in backups), backups)
                    self.assertEqual(path.with_name(path.name + '.bak').read_text(), 'older backup\n')

            def snapshot():
                return {str(p.relative_to(home)): (os.readlink(p) if p.is_symlink() else p.read_bytes())
                        for p in home.rglob('*') if p.is_file() or p.is_symlink()}

            before = snapshot()
            install()
            self.assertEqual(snapshot(), before, 'Unchanged repeat must not make more backups')


if __name__ == '__main__':
    unittest.main()
