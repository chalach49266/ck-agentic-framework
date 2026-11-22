"""Exercise the Windows Herdr launcher with a local Bash pane in place of WSL."""

import contextlib
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import io
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import time
import unittest
from unittest import mock


loader = SourceFileLoader("windows_herdr", str(Path(__file__).resolve().parents[1] / "osascript"))
transport = module_from_spec(spec_from_loader(loader.name, loader))
loader.exec_module(transport)


class WindowsHerdr(unittest.TestCase):
    def test_cursor_status_with_quoted_run_path(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run_dir = root / "agent_runs" / "cursor run"
            run_dir.mkdir(parents=True)
            ready, release = run_dir / "ready", run_dir / "release"
            script = run_dir / "live.sh"
            script.write_text(f': > {shlex.quote(str(ready))}\n'
                              f'while [ ! -f {shlex.quote(str(release))} ]; do sleep 0.05; done\n')
            state_dir = root / "windows-adapter"
            with mock.patch.multiple(transport, STATE_DIR=str(state_dir), RUNS_DIR=str(state_dir / "runs"),
                                     ensure_app=mock.Mock(return_value="no Herdr window"),
                                     grokbot_parent=mock.Mock(return_value=None),
                                     hc_path=mock.Mock(return_value="/bin/false"),
                                     hc_json=mock.Mock(return_value=(0, {"address": "t-fixture"})),
                                     close_after_s=mock.Mock(return_value=0)), contextlib.redirect_stdout(io.StringIO()):
                rc = transport.start(shlex.join(["/bin/bash", str(script)]), "CK · cursor · Test", "5000", 1, True)
                argv = transport.hc_json.call_args.args
            self.assertEqual(rc, 0)
            self.assertEqual(argv[0], "run")

            pane_log = root / "pane.log"
            with pane_log.open("wb") as out:
                pane = subprocess.Popen(argv[argv.index("--exec") + 1:], env=dict(os.environ, HOME=folder),
                                        stdin=subprocess.DEVNULL, stdout=out, stderr=out, start_new_session=True)
            working = b"\x1b]7501;app=cursor:state=working\x07"
            done = b"\x1b]7501;app=cursor:state=done\x07"
            try:
                deadline = time.monotonic() + 5
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertTrue(ready.is_file())
                self.assertIn(working, pane_log.read_bytes())
                (run_dir / "result.json").write_text('{"status":"ok"}')
                deadline = time.monotonic() + 5
                while done not in pane_log.read_bytes() and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertIn(done, pane_log.read_bytes())
                self.assertIsNone(pane.poll())
            finally:
                release.touch()
                pane.wait(timeout=5)
