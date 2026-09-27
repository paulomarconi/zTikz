"""Compiling runs in the background: the window stays responsive and the newest text wins."""
import contextlib
import os
import sys
import time
import unittest
from unittest import mock

from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest

import qt_support
from qt_support import WindowTestCase, requires_pdflatex

from zTikz.utils import functions

SLEEP_30S = "import time; time.sleep(30)"        # a "pdflatex" that hangs until it is killed
QUICK = "pass"                                   # a "pdflatex" that exits at once without producing a PDF


@contextlib.contextmanager
def fake_tex(codes):
    """Replace the next TeX runs by small Python programs (later runs use the real thing).

    Yields the list of programs that were started, in order.
    """
    real = functions._new_process
    remaining = list(codes)
    started = []

    def replacement(window, program, arguments, cwd, env):
        if remaining:
            code = remaining.pop(0)
            started.append(code)
            if code is None:                                             # a program that cannot start
                return real(window, os.path.join(cwd, "no-such-program-zz"), [], cwd, env)
            return real(window, sys.executable, ["-c", code], cwd, env)
        return real(window, program, arguments, cwd, env)

    with mock.patch.object(functions, "_new_process", replacement):
        yield started


def wait_until(condition, timeout_s=30):
    """Run the Qt event loop until condition() is true; returns whether it became true."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if condition():
            return True
        QTest.qWait(10)
    return condition()


class StandInCase(WindowTestCase):
    """Compile with a stand-in for pdflatex, so these tests need no TeX installation."""

    def setUp(self):
        super().setUp()
        for patcher in (mock.patch("zTikz.utils.functions.find_pdflatex", return_value=sys.executable),
                        mock.patch("zTikz.utils.functions._split_preamble", return_value=None)):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.stop_everything)
        self.window.output.clear()

    def stop_everything(self):
        w = self.window
        w.cancel_compilation()
        w.timer.stop()
        w.wait_for_compile(10_000)

    def set_code(self, code):
        self.window.editor.setPlainText(code)
        self.window.timer.stop()                      # editing starts the debounce timer; we compile explicitly

    def running_job(self):
        return self.window._compile_job


class LifecycleTests(StandInCase):
    def test_compile_returns_at_once_and_the_ui_keeps_running(self):
        ticks = []
        heartbeat = QTimer()
        heartbeat.setInterval(10)
        heartbeat.timeout.connect(lambda: ticks.append(1))
        self.set_code(r"\draw (0,0)--(1,1);")

        with fake_tex(["import time; time.sleep(0.8)"]):
            heartbeat.start()
            self.window.compile_tikz()
            self.assertFalse(self.window.is_compile_idle())                 # started, not finished
            self.assertEqual(self.window.output.toPlainText(), "")
            QTest.qWait(500)                                                # the UI thread is free meanwhile
            still_running = not self.window.is_compile_idle()
            heartbeat.stop()
            self.assertTrue(self.window.wait_for_compile(10_000))

        self.assertTrue(still_running)
        self.assertGreater(len(ticks), 15, "the event loop was blocked while compiling")
        self.assertIn("Compilation failed", self.window.output.toPlainText())    # the stand-in makes no PDF

    def test_cancel_stops_the_run_and_says_so_once(self):
        self.set_code(r"\draw (0,0)--(2,2);")
        before = self.window._last_compiled_hash
        with fake_tex([SLEEP_30S]):
            self.window.compile_tikz()
            QTest.qWait(150)
            started = time.monotonic()
            self.window.cancel_compilation()
            self.assertTrue(self.window.wait_for_compile(10_000))
        out = self.window.output.toPlainText()
        self.assertLess(time.monotonic() - started, 5)                      # not the 30 s the program wanted
        self.assertEqual(out.count("cancelled by user"), 1)
        self.assertNotIn("Compilation failed", out)
        self.assertEqual(self.window._last_compiled_hash, before)
        self.assertIsNone(self.window.compilation_process)

    def test_cancel_with_nothing_running_does_nothing(self):
        self.window.cancel_compilation()
        self.assertEqual(self.window.output.toPlainText(), "")

    def test_the_same_request_while_running_does_not_restart_it(self):
        self.set_code(r"\draw (0,0)--(3,3);")
        with fake_tex([SLEEP_30S]) as started:
            self.window.compile_tikz()
            QTest.qWait(100)
            job, process = self.running_job(), self.running_job().process
            self.window.compile_tikz()                                      # identical text
            self.assertIs(self.running_job(), job)
            self.assertIs(job.process, process)
            self.assertIsNone(job.cancel_reason)
            self.assertEqual(len(started), 1)

    def test_newer_text_supersedes_the_running_compile(self):
        self.set_code(r"\draw (0,0)--(4,4);")
        with fake_tex([SLEEP_30S, QUICK]) as started:
            self.window.compile_tikz()
            QTest.qWait(150)
            self.set_code(r"\draw (0,0)--(5,5);")
            t0 = time.monotonic()
            self.window.compile_tikz()
            self.assertTrue(self.window.wait_for_compile(10_000))
        self.assertLess(time.monotonic() - t0, 8)                           # the hung run was killed, not awaited
        self.assertEqual(started, [SLEEP_30S, QUICK])                       # a second run for the newer text
        out = self.window.output.toPlainText()
        self.assertEqual(out.count("Compilation failed"), 1)                # only the newest run reports

    def test_going_back_to_the_compiled_text_discards_the_running_job(self):
        self.set_code(r"\draw (0,0)--(6,6);")
        self.window._last_compiled_hash = functions._prepare_compile_job(self.window, time.time()).content_hash
        self.set_code(r"\draw (0,0)--(7,7);")
        with fake_tex([SLEEP_30S]) as started:
            self.window.compile_tikz()
            QTest.qWait(150)
            self.set_code(r"\draw (0,0)--(6,6);")                          # back to what is already shown
            self.window.compile_tikz()
            self.assertTrue(self.window.wait_for_compile(10_000))
        self.assertEqual(len(started), 1)                                   # nothing new had to be compiled
        self.assertEqual(self.window.output.toPlainText(), "")

    def test_a_hung_run_is_stopped_by_the_timeout(self):
        self.set_code(r"\draw (0,0)--(8,8);")
        with mock.patch.object(functions, "COMPILE_TIMEOUT_MS", 300), fake_tex([SLEEP_30S]):
            self.window.compile_tikz()
            self.assertTrue(self.window.wait_for_compile(10_000))
        self.assertIn("timed out", self.window.output.toPlainText())

    def test_a_pdflatex_that_cannot_start_is_reported(self):
        self.set_code(r"\draw (0,0)--(9,9);")
        with fake_tex([None]):
            self.window.compile_tikz()
            self.assertTrue(self.window.wait_for_compile(10_000))
        self.assertIn("Could not start pdflatex", self.window.output.toPlainText())
        self.assertIsNone(self.window.compilation_process)

    def test_every_job_uses_its_own_file_names_and_cleans_up(self):
        import glob
        self.set_code(r"\draw (0,0)--(1,2);")
        with fake_tex([QUICK]):
            self.window.compile_and_wait()
        self.set_code(r"\draw (0,0)--(2,1);")
        with fake_tex([QUICK]):
            self.window.compile_and_wait()
        self.assertGreaterEqual(self.window._job_counter, 2)
        self.assertEqual(glob.glob(os.path.join(self.window.temp_dir, "build*")), [])


class BusyIndicatorTests(StandInCase):
    MATRIX = '\\draw (0,0) -- (1,1);\n\\matrix {\\node{a};&\\node{b};\\\\};\n'

    def test_slow_compile_shows_compiling_and_then_restores_the_previous_status(self):
        self.set_code(self.MATRIX)                                          # leaves a canvas-overlay message
        bar = self.window.statusBar()
        overlay_message = bar.currentMessage()
        self.assertIn("line 2", overlay_message)

        with mock.patch.object(functions, "BUSY_INDICATOR_DELAY_MS", 50), fake_tex(["import time; time.sleep(0.6)"]):
            self.window.compile_tikz()
            self.assertTrue(wait_until(lambda: bar.currentMessage() == "Compiling...", 5))
            self.assertFalse(bar.isHidden())
            self.assertTrue(self.window.wait_for_compile(10_000))

        self.assertEqual(bar.currentMessage(), overlay_message)

    def test_fast_compile_never_flashes_the_indicator(self):
        self.set_code(r"\draw (0,0)--(1,1);")
        with mock.patch.object(functions, "BUSY_INDICATOR_DELAY_MS", 5000), fake_tex([QUICK]):
            self.window.compile_and_wait()
        self.assertFalse(getattr(self.window, "_busy_message_shown", False))
        self.assertNotEqual(self.window.statusBar().currentMessage(), "Compiling...")


class ShutdownTests(StandInCase):
    def test_closing_the_window_stops_a_running_compile_and_removes_its_folder(self):
        from zTikz.main import main_window
        with fake_tex([SLEEP_30S]):
            other = main_window()                                           # its startup compile now hangs
            QTest.qWait(150)
        self.assertFalse(other.is_compile_idle())
        temp_dir = other.temp_dir
        other.editor.document().setModified(False)

        started = time.monotonic()
        other.close()

        self.assertLess(time.monotonic() - started, 8)
        self.assertTrue(other.is_compile_idle())
        self.assertFalse(os.path.exists(temp_dir))                          # nothing kept it locked

    def test_a_request_after_closing_is_ignored(self):
        self.window._closing = True                                         # setUp of the next test resets this
        self.window.compile_tikz()
        self.assertTrue(self.window.is_compile_idle())


@requires_pdflatex
class RealPdflatexTests(WindowTestCase):
    def setUp(self):
        super().setUp()
        self.window.output.clear()

    def test_compile_returns_before_pdflatex_has_finished(self):
        self.window.editor.setPlainText(r"\draw (0,0)--(1,1);")
        self.window.timer.stop()
        self.window.compile_tikz()
        self.assertFalse(self.window.is_compile_idle())
        self.assertNotIn("Compilation successful", self.window.output.toPlainText())
        self.assertTrue(self.window.wait_for_compile())
        self.assertIn("Compilation successful", self.window.output.toPlainText())

    def test_the_format_build_runs_in_the_background_too(self):
        self.window._fmt_static_hash = None
        self.window._fmt_failed_hash = None
        self.window.editor.setPlainText(r"\draw (0,0)--(2,2);")
        self.window.timer.stop()
        self.window.compile_tikz()
        self.assertEqual(self.window._compile_job.stage, "format")
        self.assertTrue(self.window.wait_for_compile())
        out = self.window.output.toPlainText()
        self.assertIn("Compilation successful", out)
        self.assertIn("fmt: yes", out)

    def test_a_burst_of_edits_ends_with_the_last_text_shown(self):
        w = self.window
        for n in (3, 4, 5):
            w.editor.setPlainText(rf"\draw (0,0) -- ({n},{n});")
            w.compile_tikz()                                                # no waiting, like fast typing
        expected = functions._prepare_compile_job(w, time.time()).content_hash
        self.assertTrue(w.wait_for_compile())

        out = w.output.toPlainText()
        self.assertNotIn("Compilation failed", out)
        self.assertEqual(w._last_compiled_hash, expected)
        with open(os.path.join(w.temp_dir, "temp.tex"), encoding="utf-8") as f:
            self.assertIn("(5,5)", f.read())                                # the published tex is the last text

    def test_the_last_good_pdf_stays_available_while_a_new_compile_runs(self):
        w = self.window
        self.compile_code(r"\draw (0,0)--(1,1);")
        temp_pdf = os.path.join(w.temp_dir, "temp.pdf")
        self.assertTrue(os.path.exists(temp_pdf))

        w.editor.setPlainText(r"\draw (0,0)--(6,6);")
        w.compile_tikz()
        self.assertFalse(w.is_compile_idle())
        self.assertTrue(os.path.exists(temp_pdf))                           # Export / Show PDF still work
        self.assertTrue(w.wait_for_compile())

    def test_typing_triggers_a_compile_by_itself(self):
        w = self.window
        w.editor.setPlainText(r"\draw (0,0)--(7,7);")                      # starts the 100 ms debounce timer
        self.assertTrue(wait_until(lambda: "Compilation successful" in w.output.toPlainText(), 30))
        self.assertTrue(w.wait_for_compile())

    def test_cancelling_a_format_build_leaves_no_partial_format(self):
        w = self.window
        fmt = os.path.join(w.temp_dir, "tikz_preamble.fmt")
        w._fmt_static_hash = None
        w._fmt_failed_hash = None
        w.editor.setPlainText(r"\draw (0,0)--(8,8);")
        w.timer.stop()
        partial = f"import time; open(r'{fmt}', 'w').write('half written'); time.sleep(30)"
        with fake_tex([partial]):
            w.compile_tikz()
            self.assertTrue(wait_until(lambda: os.path.exists(fmt), 10))     # the "build" has begun writing
            w.cancel_compilation()
            self.assertTrue(w.wait_for_compile(10_000))
        self.assertFalse(os.path.exists(fmt))
        self.assertIsNone(w._fmt_static_hash)
        # ...and the next compile rebuilds it properly.
        self.assertIn("Compilation successful", self.compile_code(r"\draw (0,0)--(9,9);"))


if __name__ == "__main__":
    unittest.main()
