"""Offline Mac host tests. Real subprocesses talk only to the copied fake hc/app."""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

MAC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MAC))
sys.path.insert(0, str(MAC.parents[1]))
loader = importlib.machinery.SourceFileLoader('mac_transport', str(MAC / 'osascript'))
spec = importlib.util.spec_from_loader(loader.name, loader)
transport = importlib.util.module_from_spec(spec)
loader.exec_module(transport)
herdr = transport.herdr
from ckdispatch import live


class MacTransport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ck-mac-host-')
        self.home = Path(self.temp.name)
        self.run = self.home / 'agent_runs/a run'
        self.run.mkdir(parents=True)
        self.script = self.run / 'live.sh'
        self.script.write_text('#!/bin/bash\nexit 0\n')
        self.fixture = self.home / 'herdr-fixture.json'
        self.fixture.write_text('{}')
        code = Path(__file__).with_name('fake_herdr.py').read_text()
        for name in ('hc', 'herdr-app'):
            p = self.home / name
            p.write_text(f'#!{sys.executable}\n' + code)
            p.chmod(0o755)
        self.env = mock.patch.dict(os.environ, {'HOME': str(self.home), 'HC_TERMINAL_ID': 't-main',
            'CK_HERDR_HC': str(self.home / 'hc'), 'CK_HERDR_APP': str(self.home / 'herdr-app'),
            'CK_HERDR_LAUNCH_GAP_S': '0'}, clear=True)
        self.env.start()
        self.state_patch = mock.patch.object(transport, 'STATE', self.home / 'host-state')
        self.state_patch.start()
        self.watch_patch = mock.patch.object(transport, 'spawn_watch')
        self.watch_patch.start()

    def tearDown(self):
        self.watch_patch.stop()
        self.state_patch.stop()
        self.env.stop()
        self.temp.cleanup()

    def call(self, kind='window', args=None):
        if args is None:
            import shlex
            args = ['/bin/bash ' + shlex.quote(str(self.script)), 'CK · codex · Test', '']
        out = io.StringIO()
        lines = live.ITERM_APPLESCRIPT if kind == 'window' else ['-- ck-run:' + kind]
        argv = [v for ln in lines for v in ('-e', ln)] + args
        with contextlib.redirect_stdout(out):
            rc = transport.main(argv)
        return rc, out.getvalue().strip()

    def state(self):
        return json.loads((self.home / 'herdr-state.json').read_text())

    def test_host_override_and_default(self):
        self.assertEqual(herdr.detect_host('iTerm2', {}), 'iTerm2')
        self.assertEqual(herdr.detect_host('iTerm2', {'HC_TERMINAL_ID': 't-main'}), 'herdr:t-main')
        self.assertEqual(herdr.detect_host('iTerm2', {'CK_RUN_HOST': 'iterm', 'HC_TERMINAL_ID': 'x'}), 'iterm')
        self.assertEqual(herdr.detect_host('iTerm2', {'CK_RUN_HOST': 'herdr:t-original'}), 'herdr:t-original')
        with self.assertRaises(ValueError):
            herdr.detect_host('iTerm2', {'CK_RUN_HOST': 'invalid'})

    def test_pane_names_use_job_title_and_run_suffix(self):
        title = "Port the agent talk changes to the framework!"
        name = herdr.job_name(title, "run-1")
        self.assertTrue(name.startswith("port-the-agent-talk-changes"))
        self.assertRegex(name, r"^[a-z0-9-]{1,32}$")
        self.assertNotEqual(name, herdr.job_name(title, "run-2"))
        self.assertEqual(herdr.job_name("", "run-1"), herdr.safe_name("run-1"))

    def test_native_forwards_arguments_unchanged(self):
        os.environ['CK_RUN_HOST'] = 'iterm'
        with mock.patch.object(transport, 'native', return_value=0) as native:
            self.call()
        self.assertIn(str(self.script), native.call_args.args[0][-3])
        self.assertFalse((self.home / 'herdr-state.json').exists())

    def test_launch_returns_persistent_session_and_equal_layout(self):
        rc, reply = self.call()
        self.assertEqual(rc, 0)
        wid, _, sid = reply.split('|')
        self.assertTrue(sid.startswith('ckmac-'))
        run = next(c['argv'] for c in self.state()['calls'] if c['argv'][0] == 'run')
        self.assertIn('--no-notify', run)
        self.assertEqual(run[run.index('--parent') + 1], 't-main')
        self.assertIn(f'ck.run={self.run.name}', run)
        self.assertRegex(run[run.index('--name') + 1], r'^test-[0-9a-f]{4}$')
        self.assertIn('ck.title=Test', run)
        self.assertEqual(herdr.saved(self.run)['adapter_session'], sid)
        self.assertEqual(self.call('exists', [wid, 'CK'])[1], 'yes')
        self.assertEqual(self.call('tail', [sid, ''])[1][:4], 'CKOK')
        self.assertEqual(self.call('write', [sid, '', 'resume'])[1], 'CKOK')
        self.assertEqual(self.call('close', [sid, ''])[1], 'CKNOTFOUND')
        self.assertFalse(any(c['argv'][0] == 'kill' for c in self.state()['calls']))
        left, right = self.state()['doc']['spaces'][0]['tabs'][0]['root']['children']
        self.assertEqual(left['size'], right['size'])
        self.assertEqual([x['content']['terminal'] for x in herdr._leaves(left)], ['t-main', 't-other'])

    def test_saved_window_retains_herdr_after_host_changes(self):
        _, reply = self.call()
        wid = reply.split('|')[0]
        os.environ['CK_RUN_HOST'] = 'iterm'
        rc, reply = self.call('tab', ['/bin/bash ' + __import__('shlex').quote(str(self.script)), 'CK · codex · Test', '', wid])
        self.assertEqual(rc, 0)
        self.assertTrue(reply.endswith('ckmac-t-run-2'))

    def test_hc_failure_uses_native_and_app_failure_creates_no_agent(self):
        self.fixture.write_text('{"fail":"app"}')
        with mock.patch.object(transport, 'native', return_value=0) as native:
            self.assertEqual(self.call()[0], 0)
            native.assert_called_once()
        self.assertFalse(any(c['argv'][0] == 'run' for c in self.state()['calls']))

    def test_layout_failure_never_duplicates_started_agent(self):
        self.fixture.write_text('{"fail":"connect"}')
        self.assertEqual(self.call()[0], 0)
        self.assertEqual(len(self.state()['terminals']), 1)
        self.assertIn('terminal retained', (self.run / 'herdr.log').read_text())

    def test_missing_parent_uses_ck_space(self):
        self.fixture.write_text('{"main_missing":true}')
        self.assertEqual(self.call()[0], 0)
        calls = self.state()['calls']
        argv = next(c['argv'] for c in calls if c['argv'][0] == 'run')
        self.assertIn('herdr.space=space-ck', argv)
        self.assertFalse(any(x.startswith('herdr.tab=') for x in argv))

    def test_conflict_rereads_document(self):
        self.fixture.write_text('{"conflict":true}')
        self.assertEqual(self.call()[0], 0)
        self.assertIn('t-concurrent', [p['content']['terminal'] for p in herdr._leaves(self.state()['doc']['spaces'][0]['tabs'][0]['root'])])

    def test_partial_is_labeled_but_never_auto_closes(self):
        self.call()
        (self.run / 'result.json').write_text('{"status":"partial"}')
        with mock.patch.object(herdr, '_closer_main') as close:
            transport.watch(self.run, 't-run-1')
            close.assert_not_called()
        self.assertEqual(self.state()['terminals'][0]['labels']['ck.state'], 'needs')

    def test_clean_result_uses_live_busy_turn_closer(self):
        self.call()
        (self.run / 'result.json').write_text('{"status":"ok"}')
        with mock.patch.object(herdr, '_closer_main', return_value=0) as close:
            transport.watch(self.run, 't-run-1')
            self.assertEqual(close.call_args.args[0][0], 't-run-1')
        self.assertEqual(self.state()['terminals'][0]['labels']['ck.state'], 'done')

    def test_busy_or_followup_never_closes(self):
        for final in ({'status': {'state': 'working'}, 'turn': 1}, {'status': {'state': 'idle'}, 'turn': 2}):
            with mock.patch.object(herdr, '_get', side_effect=[{'turn': 1}, final]), mock.patch.object(herdr.time, 'sleep'), mock.patch.object(herdr, 'close_pane') as close:
                herdr._closer_main(['t-run', '0.001', ''])
                close.assert_not_called()

    def test_core_only_passes_host_settings_to_mac_adapter_on_darwin(self):
        path = str(MAC / 'osascript')
        env = {'HOME': str(self.home), 'PATH': '/usr/bin:/bin'}
        for platform in ('darwin', 'linux'):
            with mock.patch.object(sys, 'platform', platform), mock.patch.object(live.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '', '')) as run:
                live._osa(path, [], [], env)
                actual = run.call_args.kwargs['env']
                self.assertEqual('HC_TERMINAL_ID' in actual, platform == 'darwin')
        self.assertNotIn('HC_TERMINAL_ID', env)

    def test_live_wrapper_passes_new_pane_identity_without_other_host_variables(self):
        with mock.patch.object(sys, 'platform', 'darwin'):
            text = live.script_text(run_dir=str(self.run), cwd=str(self.home),
                env={'HOME': str(self.home), 'PATH': '/usr/bin:/bin'}, argv=['/usr/bin/env'],
                prompt_path=str(self.run / 'prompt.md'), title='Fixture')
        self.script.write_text(text)
        proc = subprocess.run(['/bin/bash', str(self.script)],
            env={'HOME': str(self.home), 'HC_TERMINAL_ID': 'new-pane', 'UNRELATED_HOST_VALUE': 'fixture'},
            text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('HC_TERMINAL_ID=new-pane', proc.stdout)
        self.assertNotIn('UNRELATED_HOST_VALUE', proc.stdout)


if __name__ == '__main__':
    unittest.main()
