"""Report the initial ck-run task's status on the Cursor pane's output."""

from pathlib import Path
import signal
import subprocess
import sys
import time


POLL_S = 0.5


def report(state):
    sys.stdout.write(f"\x1b]7501;app=cursor:state={state}\x07")
    sys.stdout.flush()


def completion_signature(run_dir):
    try:
        summary = (run_dir / "summary.md").stat()
        if summary.st_size and (run_dir / "result.md").is_file():
            return summary.st_size, summary.st_mtime_ns
    except OSError:
        pass
    return None


def wait_for_task(child, run_dir):
    previous = None
    while True:
        current = completion_signature(run_dir)
        if current is not None and current == previous:
            report("done")
            return child.wait()
        code = child.poll()
        if code is not None:
            # The child may have finished writing its result just before exit.
            report("done" if completion_signature(run_dir) is not None else "error")
            return code
        previous = current
        time.sleep(POLL_S)


def main(run_dir, command):
    report("working")
    try:
        child = subprocess.Popen(command)  # Cursor inherits the pane and its foreground process group.
    except OSError:
        report("error")
        raise

    def terminate(signum, _frame):
        child.send_signal(signum)

    # Ctrl-C goes to the foreground group. A targeted stop must also reach the child.
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, terminate)
    code = wait_for_task(child, run_dir)
    return 128 - code if code < 0 else code


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), sys.argv[2:]))
