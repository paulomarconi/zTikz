"""Shared helpers for the GUI tests: headless Qt, a real main window, safe dialog stubs."""
import atexit
import contextlib
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

# Must be set before the first QApplication is created so tests run without a display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# The tests must never touch the developer's real preamble or settings: give this run
# its own throwaway user-data folder and settings file (removed when the run ends).
_SANDBOX = tempfile.mkdtemp(prefix="ztikz-test-sandbox-")
atexit.register(shutil.rmtree, _SANDBOX, ignore_errors=True)
os.environ["ZTIKZ_DATA_DIR"] = os.path.join(_SANDBOX, "data")

from PyQt6.QtCore import QSettings  # noqa: E402
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox  # noqa: E402

QSettings.setDefaultFormat(QSettings.Format.IniFormat)
QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, os.path.join(_SANDBOX, "settings"))

from zTikz.utils import paths as app_paths  # noqa: E402
from zTikz.utils.latex import find_pdflatex  # noqa: E402

DEFAULT_PREAMBLE_PATH = app_paths.default_preamble_path()

requires_pdflatex = unittest.skipUnless(find_pdflatex(), "pdflatex is not installed")


def user_preamble_path():
    return app_paths.user_preamble_path()


_app = None  # the QApplication must stay referenced, or Python destroys it and Qt crashes


def get_app():
    global _app
    _app = QApplication.instance() or QApplication(["ztikz-tests"])
    return _app


def preserve_preamble(testcase):
    """Put the user preamble back after the test (tests call save_preamble)."""
    path = app_paths.ensure_user_preamble()
    with open(path, "rb") as f:
        original = f.read()

    def restore():
        with open(user_preamble_path(), "wb") as f:
            f.write(original)

    testcase.addCleanup(restore)
    return original.decode("utf-8")


@contextlib.contextmanager
def save_dialog_returns(path, selected_filter=""):
    with mock.patch.object(QFileDialog, "getSaveFileName",
                           staticmethod(lambda *a, **k: (path, selected_filter))):
        yield


@contextlib.contextmanager
def open_dialog_returns(path):
    with mock.patch.object(QFileDialog, "getOpenFileName",
                           staticmethod(lambda *a, **k: (path, ""))):
        yield


@contextlib.contextmanager
def message_box_answers(button):
    """Make QMessageBox.question return `button`; yields the list of calls made."""
    calls = []

    def fake(*args, **kwargs):
        calls.append(args)
        return button

    with mock.patch.object(QMessageBox, "question", staticmethod(fake)):
        yield calls


@contextlib.contextmanager
def recorded_tex_runs():
    """Record every pdflatex run the app starts (program, arguments, cwd, env) while still running it."""
    from zTikz.utils import functions
    runs = []
    real = functions._new_process

    def recorder(window, program, arguments, cwd, env):
        runs.append({"program": program, "arguments": list(arguments), "cwd": cwd, "env": dict(env)})
        return real(window, program, arguments, cwd, env)

    with mock.patch.object(functions, "_new_process", recorder):
        yield runs


class WindowTestCase(unittest.TestCase):
    """One real main_window per test class (creating it compiles once, so it is not free)."""

    @classmethod
    def setUpClass(cls):
        get_app()
        from zTikz.main import main_window
        cls.window = main_window()
        cls.window.wait_for_compile()       # the startup compile runs in the background

    @classmethod
    def tearDownClass(cls):
        # Let closeEvent run its cleanup without an unsaved-changes prompt.
        cls.window.editor.document().setModified(False)
        cls.window.close()

    def setUp(self):
        # The window is shared by a class's tests. Compiles run in the background, so first
        # let anything left over by the previous test finish (and stop the debounce timer that
        # editing the text started), then forget the "unchanged, skip compile" cache so one
        # test's compile can't make another test's identical compile a silent no-op.
        # Subclasses that define setUp must call super().setUp().
        w = self.window
        w._closing = False                 # a test may have run closeEvent on the shared window
        w.timer.stop()
        w.wait_for_compile()
        w._last_compiled_hash = ''

    def compile_code(self, code):
        """Put `code` in the editor, compile (waiting for the background run), and return the output it produced."""
        w = self.window
        w.editor.setPlainText(code)
        w.output.clear()
        w.compile_and_wait()
        return w.output.toPlainText()
