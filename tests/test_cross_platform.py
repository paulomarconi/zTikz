"""Behaviour that must hold on Windows, Linux and macOS alike."""
import glob
import os
import re
import stat
import sys
import tempfile
import unittest
from unittest import mock

from PyQt6.QtCore import QProcess, QSettings
from PyQt6.QtWidgets import QDialog, QLineEdit, QPushButton

import qt_support
from qt_support import ROOT, WindowTestCase, requires_pdflatex

from zTikz.utils import latex
from zTikz.utils.latex import find_pdflatex


def make_executable(path, content=b"#!/bin/sh\n"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


class TempDirCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = os.path.realpath(tmp.name)


class FindPdflatexTests(TempDirCase):
    def test_configured_file_is_used(self):
        exe = make_executable(os.path.join(self.tmp, "bin", "pdflatex"))
        self.assertEqual(find_pdflatex(configured=exe), exe)

    def test_configured_folder_is_searched_for_pdflatex(self):
        exe = make_executable(os.path.join(self.tmp, "texbin", "pdflatex"))
        self.assertEqual(find_pdflatex(configured=os.path.dirname(exe)), exe)

    def test_quotes_around_a_configured_path_are_ignored(self):
        exe = make_executable(os.path.join(self.tmp, "bin", "pdflatex"))
        self.assertEqual(find_pdflatex(configured=f'"{exe}"'), exe)

    def test_wrong_configured_path_is_never_silently_replaced(self):
        # Even when a working pdflatex is on PATH, a bad setting must be reported, not hidden.
        on_path = make_executable(os.path.join(self.tmp, "path", "pdflatex"))
        with mock.patch("shutil.which", return_value=on_path):
            self.assertIsNone(find_pdflatex(configured=os.path.join(self.tmp, "nope", "pdflatex")))

    @unittest.skipIf(sys.platform == "win32", "Windows has no executable permission bit")
    def test_non_executable_file_is_rejected(self):
        path = os.path.join(self.tmp, "pdflatex")
        with open(path, "wb") as f:
            f.write(b"not executable")
        os.chmod(path, 0o644)
        self.assertIsNone(find_pdflatex(configured=path))

    def test_path_is_searched_first(self):
        exe = make_executable(os.path.join(self.tmp, "onpath", "pdflatex"))
        with mock.patch("shutil.which", return_value=exe):
            self.assertEqual(find_pdflatex(), exe)

    def test_usual_install_folders_are_searched_when_path_has_nothing(self):
        # e.g. a Finder-launched macOS app, whose PATH does not include /Library/TeX/texbin
        old = make_executable(os.path.join(self.tmp, "texlive", "2023", "bin", "x86_64", "pdflatex"))
        new = make_executable(os.path.join(self.tmp, "texlive", "2025", "bin", "x86_64", "pdflatex"))
        pattern = os.path.join(self.tmp, "texlive", "*", "bin", "*", "pdflatex")
        with mock.patch("shutil.which", return_value=None), \
                mock.patch.object(latex, "known_location_patterns", return_value=[pattern]):
            self.assertEqual(find_pdflatex(), new)                  # newest year wins
        self.assertNotEqual(old, new)

    def test_nothing_found_returns_none(self):
        with mock.patch("shutil.which", return_value=None), \
                mock.patch.object(latex, "known_location_patterns", return_value=[os.path.join(self.tmp, "x*")]):
            self.assertIsNone(find_pdflatex())


class KnownLocationTests(unittest.TestCase):
    def test_macos_includes_mactex(self):
        patterns = latex.known_location_patterns(platform="darwin")
        self.assertIn("/Library/TeX/texbin/pdflatex", patterns)

    def test_linux_includes_system_and_user_texlive(self):
        patterns = latex.known_location_patterns(platform="linux")
        self.assertIn("/usr/bin/pdflatex", patterns)
        self.assertTrue(any(os.path.join("texlive", "*", "bin", "*", "pdflatex") in p for p in patterns))
        self.assertFalse(any(p.endswith(".exe") for p in patterns))

    def test_windows_includes_miktex_and_texlive(self):
        env = {"LOCALAPPDATA": "C:\\Users\\u\\AppData\\Local", "PROGRAMFILES": "C:\\Program Files",
               "USERPROFILE": "C:\\Users\\u"}
        patterns = latex.known_location_patterns(platform="win32", environ=env)
        self.assertTrue(any("MiKTeX" in p and p.endswith("pdflatex.exe") for p in patterns))
        self.assertTrue(any("texlive" in p and p.endswith("pdflatex.exe") for p in patterns))

    def test_windows_patterns_skip_missing_environment_variables(self):
        patterns = latex.known_location_patterns(platform="win32", environ={})
        self.assertTrue(patterns)
        self.assertTrue(all(os.path.isabs(p) or re.match(r"^[A-Za-z]:\\", p) for p in patterns))


class SubprocessEnvTests(unittest.TestCase):
    def test_pdflatex_folder_comes_first_on_path(self):
        exe = os.path.join(tempfile.gettempdir(), "somewhere", "pdflatex")
        env = latex.subprocess_env(exe)
        self.assertEqual(env["PATH"].split(os.pathsep)[0], os.path.dirname(os.path.abspath(exe)))

    def test_the_processs_own_environment_is_not_modified(self):
        before = os.environ.get("PATH")
        latex.subprocess_env(os.path.join(tempfile.gettempdir(), "x", "pdflatex"))
        self.assertEqual(os.environ.get("PATH"), before)


class PlatformHintTests(unittest.TestCase):
    def test_only_windows_filters_executables_by_extension(self):
        self.assertIn("*.exe", latex.executable_file_filter("win32"))
        self.assertNotIn("*.exe", latex.executable_file_filter("linux"))
        self.assertNotIn("*.exe", latex.executable_file_filter("darwin"))

    def test_every_platform_can_still_pick_any_file(self):
        for platform in ("win32", "linux", "darwin"):
            self.assertIn("All Files (*)", latex.executable_file_filter(platform))

    def test_placeholders_use_the_platforms_own_path_style(self):
        self.assertIn("pdflatex.exe", latex.pdflatex_placeholder("win32"))
        self.assertIn("/Library/TeX/texbin", latex.pdflatex_placeholder("darwin"))
        self.assertNotIn("\\", latex.pdflatex_placeholder("linux"))
        self.assertIn(".app", latex.pdf_viewer_placeholder("darwin"))
        self.assertNotIn("\\", latex.pdf_viewer_placeholder("linux"))
        self.assertIn("SumatraPDF", latex.pdf_viewer_placeholder("win32"))


class PortabilityLintTests(unittest.TestCase):
    """Windows-only APIs must not creep back into code that runs everywhere."""

    def sources(self):
        for path in glob.glob(os.path.join(ROOT, "zTikz", "**", "*.py"), recursive=True):
            if os.sep + "antlr" + os.sep in path:
                continue
            with open(path, encoding="utf-8") as f:
                yield os.path.relpath(path, ROOT), f.read()

    def test_no_winreg_or_startfile(self):
        offenders = [name for name, text in self.sources()
                     if re.search(r"\bimport winreg\b|\bwinreg\.|os\.startfile", text)]
        self.assertEqual(offenders, [])

    def test_windll_only_behind_a_platform_check(self):
        for name, text in self.sources():
            if "windll" in text:
                self.assertIn('sys.platform == "win32"', text, name)

    def test_pdflatex_is_never_hardcoded_in_the_app(self):
        # The app must go through find_pdflatex so Settings and install-folder lookup apply.
        for name, text in self.sources():
            if name.endswith("generate_snippet_thumbnails.py"):           # standalone developer script
                continue
            self.assertNotRegex(text, r"\[\s*[\"']pdflatex[\"']", name)


class SettingsDialogTests(WindowTestCase):
    """The Settings dialog opens on every OS (it used to import winreg) and its values are used."""

    def setUp(self):
        super().setUp()
        self.addCleanup(self.reset_settings)

    def reset_settings(self):
        w = self.window
        w._pdflatex_path = None
        w._pdf_viewer_path = None
        w._pdflatex_missing_reported = None
        w.settings.remove("pdflatex_path")
        w.settings.remove("pdf_viewer_path")

    def run_dialog(self, edit=None, press_ok=False):
        from zTikz.ui.menu import _show_settings_dialog
        seen = {}

        def fake_exec(dialog):
            edits = dialog.findChildren(QLineEdit)
            seen["latex_text"], seen["viewer_text"] = edits[0].text(), edits[1].text()
            seen["viewer_placeholder"] = edits[1].placeholderText()
            if edit:
                edit(edits)
            if press_ok:
                next(b for b in dialog.findChildren(QPushButton) if b.text() == "OK").click()
            return 0

        # winreg is blocked to reproduce what Linux and macOS do: it does not exist there.
        with mock.patch.object(QDialog, "exec", fake_exec), mock.patch.dict(sys.modules, {"winreg": None}):
            _show_settings_dialog(self.window)
        return seen

    def test_opens_without_winreg(self):
        self.run_dialog()                                            # would raise ImportError before

    def test_shows_the_detected_pdflatex_and_an_empty_viewer(self):
        seen = self.run_dialog()
        self.assertEqual(seen["latex_text"], find_pdflatex() or "")
        self.assertEqual(seen["viewer_text"], "")
        self.assertIn("system default", seen["viewer_placeholder"].lower())

    def test_leaving_the_detected_path_stores_no_override(self):
        self.run_dialog(press_ok=True)
        self.assertIsNone(self.window._pdflatex_path)
        self.assertEqual(self.window.settings.value("pdflatex_path", ""), "")

    def test_a_custom_pdflatex_path_is_applied_and_persisted(self):
        custom = os.path.join(tempfile.gettempdir(), "definitely-not-installed", "pdflatex")
        self.run_dialog(edit=lambda edits: edits[0].setText(custom), press_ok=True)
        self.assertEqual(self.window._pdflatex_path, custom)
        self.assertEqual(self.window.settings.value("pdflatex_path"), custom)

    def test_a_custom_viewer_is_applied_and_persisted(self):
        self.run_dialog(edit=lambda edits: edits[1].setText("/opt/viewer"), press_ok=True)
        self.assertEqual(self.window._pdf_viewer_path, "/opt/viewer")
        self.assertEqual(self.window.settings.value("pdf_viewer_path"), "/opt/viewer")

    def test_cancel_changes_nothing(self):
        self.run_dialog(edit=lambda edits: edits[1].setText("/opt/viewer"), press_ok=False)
        self.assertIsNone(self.window._pdf_viewer_path)

    def test_settings_survive_a_restart(self):
        self.window.settings.setValue("pdflatex_path", "/somewhere/pdflatex")
        self.window.settings.setValue("pdf_viewer_path", "/somewhere/viewer")
        self.window.settings.sync()
        from zTikz.main import main_window
        again = main_window()
        self.addCleanup(lambda: (again.editor.document().setModified(False), again.close()))
        self.assertEqual(again._pdflatex_path, "/somewhere/pdflatex")
        self.assertEqual(again._pdf_viewer_path, "/somewhere/viewer")


class CompileWithPdflatexSettingTests(WindowTestCase):
    def setUp(self):
        super().setUp()
        self.window._pdflatex_path = None
        self.window._pdflatex_missing_reported = None
        self.addCleanup(self.reset)

    def reset(self):
        self.window._pdflatex_path = None
        self.window._pdflatex_missing_reported = None
        self.window._last_compiled_hash = ''

    @requires_pdflatex
    def test_the_configured_pdflatex_is_the_one_that_runs(self):
        real = find_pdflatex()
        self.window._pdflatex_path = real                       # explicit location, as set in Settings
        with mock.patch("zTikz.utils.functions.find_pdflatex", wraps=find_pdflatex) as finder, \
                qt_support.recorded_tex_runs() as runs:
            self.compile_code(r"\draw (0,0)--(1,1);")
        finder.assert_any_call(real)                            # the setting is what the compile asks for
        self.assertTrue(runs)
        self.assertEqual(runs[-1]["program"], real)             # ...and what it then runs

    @requires_pdflatex
    def test_pdflatex_folder_is_put_first_on_the_compile_path(self):
        real = find_pdflatex()
        self.window._pdflatex_path = real
        with qt_support.recorded_tex_runs() as runs:
            self.compile_code(r"\draw (0,0)--(2,2);")
        env = runs[-1]["env"]
        self.assertEqual(env["PATH"].split(os.pathsep)[0], os.path.dirname(os.path.abspath(real)))

    def test_missing_pdflatex_is_explained_once_not_on_every_keystroke(self):
        with mock.patch("zTikz.utils.functions.find_pdflatex", return_value=None):
            first = self.compile_code(r"\draw (0,0)--(5,5);")
            second = self.compile_code(r"\draw (0,0)--(6,6);")
        self.assertIn("pdflatex was not found", first)
        self.assertIn("TeX Live, MiKTeX or MacTeX", first)
        self.assertEqual(second, "")

    def test_wrong_configured_path_is_named_in_the_message(self):
        bad = os.path.join(tempfile.gettempdir(), "no-such-dir", "pdflatex")
        self.window._pdflatex_path = bad
        out = self.compile_code(r"\draw (0,0)--(7,7);")
        self.assertIn(bad, out)
        self.assertIn("Settings", out)

    @requires_pdflatex
    def test_compiling_works_again_once_pdflatex_is_available(self):
        with mock.patch("zTikz.utils.functions.find_pdflatex", return_value=None):
            self.compile_code(r"\draw (0,0)--(8,8);")
        self.assertIsNotNone(self.window._pdflatex_missing_reported)        # the problem was reported

        out = self.compile_code(r"\draw (0,0)--(8,8);")                     # same code: nothing was cached

        self.assertIn("Compilation successful", out)
        self.assertIsNone(self.window._pdflatex_missing_reported)


class ExternalViewerSettingTests(WindowTestCase):
    """'Show PDF' honours the viewer chosen in Settings and falls back to the system default."""

    def setUp(self):
        super().setUp()
        self.window._pdf_viewer_path = None
        self.addCleanup(lambda: setattr(self.window, "_pdf_viewer_path", None))
        self.temp_pdf = os.path.join(self.window.temp_dir, "temp.pdf")
        with open(self.temp_pdf, "wb") as f:
            f.write(b"%PDF-1.4 fake")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def show_pdf(self, start_result=(True, 4242)):
        from PyQt6.QtGui import QDesktopServices
        from zTikz.ui.menu import _open_pdf_externally
        with mock.patch.object(QDesktopServices, "openUrl", return_value=True) as open_url, \
                mock.patch.object(QProcess, "startDetached", return_value=start_result) as start:
            _open_pdf_externally(self.window)
        return open_url, start

    def test_default_uses_the_system_viewer(self):
        open_url, start = self.show_pdf()
        open_url.assert_called_once()
        start.assert_not_called()

    def test_configured_viewer_is_started_on_the_copy(self):
        viewer = make_executable(os.path.join(self.tmp.name, "myviewer"))
        self.window._pdf_viewer_path = viewer
        open_url, start = self.show_pdf()
        open_url.assert_not_called()
        program, arguments = start.call_args[0][0], start.call_args[0][1]
        self.assertEqual(program, viewer)
        self.assertEqual(len(arguments), 1)
        self.assertNotEqual(os.path.basename(arguments[0]), "temp.pdf")       # a copy, not the live file
        self.assertTrue(os.path.exists(arguments[0]))

    def test_missing_viewer_falls_back_to_the_system_default_with_a_message(self):
        self.window._pdf_viewer_path = os.path.join(self.tmp.name, "not-there")
        self.window.output.clear()
        open_url, start = self.show_pdf()
        start.assert_not_called()
        open_url.assert_called_once()
        self.assertIn("system default", self.window.output.toPlainText())

    def test_viewer_that_fails_to_start_falls_back_too(self):
        self.window._pdf_viewer_path = make_executable(os.path.join(self.tmp.name, "broken"))
        open_url, start = self.show_pdf(start_result=(False, 0))
        open_url.assert_called_once()

    def test_macos_app_bundles_are_opened_with_open_dash_a(self):
        app = os.path.join(self.tmp.name, "Skim.app")
        os.makedirs(app)
        self.window._pdf_viewer_path = app
        with mock.patch.object(sys, "platform", "darwin"):
            open_url, start = self.show_pdf()
        program, arguments = start.call_args[0][0], start.call_args[0][1]
        self.assertEqual(program, "open")
        self.assertEqual(arguments[:2], ["-a", app])


if __name__ == "__main__":
    unittest.main()
