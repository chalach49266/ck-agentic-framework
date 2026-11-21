"""Exercise agent talk with a fake hc backend and an isolated ledger."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

from ckdispatch import asks, cli, herdr, ledger, live, patterns, runner, talk, views
from ckdispatch.errors import Refused


class AgentTalkTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.runs = self.root / "runs"
        self.runs.mkdir()
        self.cfg = SimpleNamespace(runs_dir=str(self.runs), home=str(self.root), asks_budgets={},
                                   herdr_doorbell="auto", herdr_say_cap=3,
                                   workspace=lambda name: SimpleNamespace(key=name))
        self.panes = {}
        self.sent = []
        self.fail_send = False
        self.closed = []
        self.enterContext(mock.patch.dict(os.environ, {"HC_TERMINAL_ID": "t1"}, clear=True))
        self.enterContext(mock.patch.object(herdr, "transport", return_value="mac"))
        self.enterContext(mock.patch.object(herdr, "calling_parent", return_value="t1"))
        self.enterContext(mock.patch.object(herdr, "call", side_effect=self.hc))
        self.enterContext(mock.patch.object(herdr, "close_pane", side_effect=self.close))
        self.ask = asks.open_ask(self.cfg, words="Check the change", size="M", title="Check")
        self.aid = self.ask["ask_id"]
        self.rd = self.worker("worker", "t2")
        self.base = {"run_id": self.rd.name, "ask_id": self.aid, "agent": "codex", "workspace": "devfab"}

    def worker(self, slug, target):
        rid = runner.new_run_id("devfab", "general", "codex")
        rd = self.runs / rid
        rd.mkdir()
        (rd / "live.pid").write_text(str(os.getpid()))
        (rd / "task.md").write_text("Worker task")
        (rd / herdr.STATE_FILE).write_text(json.dumps({"host": "herdr:t1", "terminal": target}))
        with mock.patch.dict(os.environ, {"CK_RUN_SLUG": slug, "CK_RUN_OUT": str(self.runs / f"{slug}.out")}):
            herdr.prepare_doorbell(self.cfg, rid, rd)
        self.panes[target] = {"address": target, "state": "live", "status": {"state": "idle"},
                              "labels": {"ck-run": "true", "ck.run": rid}}
        ledger.append(self.cfg.runs_dir, event="dispatch", run_id=rid, ask_id=self.aid, agent="codex",
                      workspace="devfab", title=slug)
        return rd

    def hc(self, cfg, command, target, *args, **kwargs):
        if command == "get":
            return self.panes[target]
        if command == "send":
            self.sent.append((target, args[0]))
            if self.fail_send:
                raise ValueError("fake hc refused blocked pane")
            return {"status": "ok"}
        self.fail(f"unexpected fake hc command {command}")

    def close(self, cfg, target, log):
        self.closed.append(target)
        self.panes[target]["state"] = "finished"
        return True

    def events(self, event):
        return [e for e in ledger.load(self.cfg.runs_dir) if e["event"] == event]

    def poll(self):
        talk.poll_question(self.cfg, self.rd.name, self.rd, self.base)

    def needs(self):
        return [r for r in views.Snapshot(self.cfg).needs_you() if r["kind"] == "question"]

    def ring(self):
        herdr.doorbell(self.cfg, self.rd, self.base, 0)

    def test_doorbell_is_at_most_once_and_keeps_original_parent(self):
        with mock.patch.dict(os.environ, {"HC_TERMINAL_ID": "t9"}):
            with ThreadPoolExecutor(2) as workers:
                list(workers.map(lambda _: self.ring(), range(2)))
        self.assertEqual(len(self.sent), 1)
        self.assertEqual(self.sent[0][0], "t1")
        self.assertIn("worker finished", self.sent[0][1])
        self.assertEqual(self.events("doorbell")[0]["status"], "sent")

    def test_mod_owns_completion_but_worker_question_is_delivered(self):
        store = self.root / ".claude/plugins/store/grokbot_ck-grokbot-test.json"
        store.parent.mkdir(parents=True)
        store.write_text(json.dumps({"pending": [{"out": str(self.runs / "worker.out")}]}))
        self.ring()
        self.assertFalse(self.sent)
        self.assertEqual(self.events("doorbell")[0]["status"], "skipped")
        (self.rd / "question.md").write_text("Select the input?\nBackground.")
        live.wait_done(str(self.rd), time.time() - 1, 0.01, watch={"question_only": True, "question": self.poll})
        self.poll()
        self.assertEqual(len(self.sent), 1)
        self.assertIn("worker asks: Select the input?", self.sent[0][1])
        self.assertIn("Select the input?", self.needs()[0]["text"])
        talk.say(self.cfg, "worker", "Use the ask file")
        self.assertEqual(self.sent[-1], ("t2", "Use the ask file"))
        self.assertFalse(self.needs())

    def test_question_symlink_ignored_and_failed_reply_counts_against_cap(self):
        src = self.rd / "other.md"
        src.write_text("Question?")
        question = self.rd / "question.md"
        question.symlink_to(src)
        self.poll()
        self.assertFalse(self.events("question"))
        question.unlink()
        question.write_text("Question?")
        self.poll()
        self.cfg.herdr_say_cap = 1
        self.fail_send = True
        with self.assertRaisesRegex(Refused, "not confirmed"):
            talk.say(self.cfg, "worker", "Answer")
        with self.assertRaises(asks.OverBudget):
            talk.say(self.cfg, "worker", "Answer")
        self.assertEqual(len(self.events("say")), 1)
        self.assertTrue(self.needs())

    def test_say_rejects_wrong_run_label_blocked_remote_and_shell_after_exit(self):
        pane = self.panes["t2"]
        pane["labels"]["ck.run"] = "another-run"
        with self.assertRaisesRegex(Refused, "does not match"):
            talk.say(self.cfg, "worker", "Answer")
        pane["labels"]["ck.run"] = self.rd.name
        pane["status"]["state"] = "blocked"
        with self.assertRaisesRegex(Refused, "blocked"):
            talk.say(self.cfg, "worker", "Answer")
        pane["status"]["state"] = "idle"
        (self.rd / "live.exit").write_text("0")
        with self.assertRaises(talk.PaneGone):
            talk.say(self.cfg, "worker", "Answer")
        (self.rd / herdr.STATE_FILE).write_text(json.dumps({"host": "herdr:t1", "terminal": "pc/t2"}))
        with self.assertRaisesRegex(talk.PaneGone, "local"):
            talk.say(self.cfg, "worker", "Answer")
        self.assertFalse(self.sent)

    def test_review_live_cli_is_explicit_and_steers_one_fix(self):
        parser = cli._parser()
        for mode in ("--live", "--interactive", "--no-live"):
            with self.subTest(mode=mode):
                args = parser.parse_args(["review", self.rd.name, "--by", "claude", mode])
                self.assertEqual(args.steer, mode == "--live")
        kwargs = dict(blind=False, focus=None, title=None, model=None, timeout_s=None, trigger="you-asked")
        with self.assertRaisesRegex(Refused, "no result"):
            runner.review_spec(self.cfg, self.rd.name, "claude", **kwargs)
        spec = runner.review_spec(self.cfg, self.rd.name, "claude", live=True, **kwargs)
        self.assertTrue(spec.review["in_progress"])
        self.assertIn(str(self.rd / "task.md"), spec.task_text)
        (self.rd / "question.md").write_text("Question?")
        self.poll()
        result = {"findings": [{"claim": f"Finding {i}", "evidence": "Proof"} for i in range(4)]}
        self.assertIn("one fix round", talk.review_steer(self.cfg, "review-1", spec.review, result))
        self.assertIn("already sent", talk.review_steer(self.cfg, "review-1", spec.review, result))
        self.assertEqual(asks.usage(self.cfg, self.aid)["fixes"], 1)
        self.assertNotIn("Finding 3", self.sent[-1][1])
        self.assertTrue(self.needs())
        with self.assertRaises(asks.OverBudget):
            talk.review_steer(self.cfg, "review-2", spec.review, result)

    def test_race_stop_only_recorded_losing_panes(self):
        loser = self.worker("loser", "t3")
        self.worker("unrelated", "t4")
        # A stopped racer can be waiting for approval.
        self.panes["t3"]["status"]["state"] = "blocked"
        ledger.append(self.cfg.runs_dir, event="race", ask_id=self.aid, note="slugs=worker,loser; models=sol,opus")
        with self.assertRaises(Refused):
            patterns.race_stop(self.cfg, SimpleNamespace(ask=self.aid, keep="unrelated"))
        self.assertEqual(patterns.race_stop(self.cfg, SimpleNamespace(ask=self.aid, keep="worker")), 0)
        self.assertEqual(self.closed, ["t3"])
        self.assertTrue(any(e["run_id"] == loser.name and e["status"] == "stopped" for e in self.events("race_stop")))
