"""Where zTikz keeps its files: nothing inside the installed package, one temp folder per session."""
import os
import shutil
import tempfile
import unittest
from unittest import mock

import qt_support
from qt_support import ROOT, WindowTestCase, requires_pdflatex, save_dialog_returns

from PyQt6.QtCore import QStandardPaths

from zTikz.utils import paths as app_paths
from zTikz.utils.functions import read_text_file

PACKAGE_DIR = os.path.join(ROOT, "zTikz")


def snapshot(folder):
    """(relative path, size, mtime) of every file in a tree, ignoring compiled caches."""
    result = {}
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in files:
            path = os.path.join(root, name)
            stat = os.stat(path)
            result[os.path.relpath(path, folder)] = (stat.st_size, stat.st_mtime_ns)
    return result


class DataDirTests(unittest.TestCase):
    def setUp(self):
        qt_support.get_app()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = os.path.realpath(tmp.name)

    def use_data_dir(self, path):
        patcher = mock.patch.dict(os.environ, {app_paths.DATA_DIR_ENV: path})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_environment_variable_overrides_the_location(self):
        self.use_data_dir(self.tmp)
        self.assertEqual(app_paths.user_data_dir(), self.tmp)
        self.assertEqual(app_paths.user_preamble_path(), os.path.join(self.tmp, "preamble.tex"))

    def test_default_location_is_the_platforms_per_user_data_folder(self):
        with mock.patch.dict(os.environ):
            os.environ.pop(app_paths.DATA_DIR_ENV, None)
            path = app_paths.user_data_dir()
        base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericDataLocation)
        self.assertEqual(os.path.normcase(path), os.path.normcase(os.path.join(os.path.normpath(base), "zTikz")))
        self.assertFalse(os.path.normcase(path).startswith(os.path.normcase(PACKAGE_DIR)))

    def test_finding_the_data_dir_does_not_create_it(self):
        target = os.path.join(self.tmp, "not-created")
        self.use_data_dir(target)
        app_paths.user_data_dir()
        app_paths.user_preamble_path()
        self.assertFalse(os.path.exists(target))

    def test_first_use_copies_the_shipped_default(self):
        self.use_data_dir(os.path.join(self.tmp, "data"))
        path = app_paths.ensure_user_preamble()
        self.assertEqual(path, app_paths.user_preamble_path())
        self.assertEqual(read_text_file(path), read_text_file(app_paths.default_preamble_path()))

    def test_an_existing_user_preamble_is_never_overwritten(self):
        self.use_data_dir(os.path.join(self.tmp, "data"))
        path = app_paths.ensure_user_preamble()
        with open(path, "w", encoding="utf-8") as f:
            f.write("% my edits\n")
        app_paths.ensure_user_preamble()
        self.assertEqual(read_text_file(path), "% my edits\n")

    def test_an_edited_legacy_preamble_is_migrated(self):
        # Older versions kept the editable copy inside the package folder.
        self.use_data_dir(os.path.join(self.tmp, "data"))
        legacy = os.path.join(self.tmp, "legacy_preamble.tex")
        with open(legacy, "w", encoding="utf-8") as f:
            f.write("% edited in an old version\n")
        path = app_paths.ensure_user_preamble(legacy_path=legacy)
        self.assertEqual(read_text_file(path), "% edited in an old version\n")

    def test_an_unedited_legacy_preamble_gives_the_default(self):
        self.use_data_dir(os.path.join(self.tmp, "data"))
        legacy = os.path.join(self.tmp, "legacy_preamble.tex")
        shutil.copyfile(app_paths.default_preamble_path(), legacy)
        path = app_paths.ensure_user_preamble(legacy_path=legacy)
        self.assertEqual(read_text_file(path), read_text_file(app_paths.default_preamble_path()))

    def test_unwritable_data_dir_raises_oserror(self):
        blocker = os.path.join(self.tmp, "a-file")
        with open(blocker, "w") as f:
            f.write("x")
        self.use_data_dir(os.path.join(blocker, "data"))          # a folder can't be created below a file
        with self.assertRaises(OSError):
            app_paths.ensure_user_preamble()

    def test_session_temp_dirs_are_unique_and_private_to_the_system_temp_area(self):
        a, b = app_paths.new_session_temp_dir(), app_paths.new_session_temp_dir()
        self.addCleanup(shutil.rmtree, a, True)
        self.addCleanup(shutil.rmtree, b, True)
        self.assertNotEqual(a, b)
        self.assertTrue(os.path.isdir(a) and os.path.isdir(b))
        self.assertTrue(os.path.basename(a).startswith("ztikz-"))
        self.assertEqual(os.path.realpath(os.path.dirname(a)), os.path.realpath(tempfile.gettempdir()))


class UserPreambleTests(WindowTestCase):
    def setUp(self):
        super().setUp()
        qt_support.preserve_preamble(self)

    def test_saving_writes_to_the_user_folder_only(self):
        w = self.window
        w.preamble_editor.setPlainText("% saved from the tab\n" + read_text_file(app_paths.default_preamble_path()))
        w.save_preamble()
        self.assertTrue(read_text_file(qt_support.user_preamble_path()).startswith("% saved from the tab"))
        self.assertFalse(os.path.exists(app_paths.legacy_preamble_path()))            # nothing in the package
        self.assertNotIn("% saved from the tab", read_text_file(app_paths.default_preamble_path()))

    def test_the_editor_starts_with_the_user_preamble(self):
        with open(qt_support.user_preamble_path(), "w", encoding="utf-8") as f:
            f.write("% distinctive user preamble\n")
        from zTikz.main import main_window
        w2 = main_window()
        self.addCleanup(lambda: (w2.editor.document().setModified(False), w2.close()))
        self.assertTrue(w2.preamble_editor.toPlainText().startswith("% distinctive user preamble"))

    def test_first_run_creates_the_user_preamble_from_the_default(self):
        fresh = tempfile.mkdtemp(prefix="ztikz-fresh-")
        self.addCleanup(shutil.rmtree, fresh, True)
        with mock.patch.dict(os.environ, {app_paths.DATA_DIR_ENV: os.path.join(fresh, "data")}):
            from zTikz.main import main_window
            w2 = main_window()
            self.addCleanup(lambda: (w2.editor.document().setModified(False), w2.close()))
            created = app_paths.user_preamble_path()
            self.assertTrue(os.path.exists(created))
            self.assertEqual(read_text_file(created), read_text_file(app_paths.default_preamble_path()))

    def test_an_unwritable_data_dir_does_not_stop_the_app(self):
        blocker = os.path.join(tempfile.mkdtemp(prefix="ztikz-block-"), "file")
        self.addCleanup(shutil.rmtree, os.path.dirname(blocker), True)
        with open(blocker, "w") as f:
            f.write("x")
        with mock.patch.dict(os.environ, {app_paths.DATA_DIR_ENV: os.path.join(blocker, "data")}):
            from zTikz.main import main_window
            w2 = main_window()                                                  # must not raise
            self.addCleanup(lambda: (w2.editor.document().setModified(False), w2.close()))
            self.assertIn(r"\begin{document}", w2.preamble_editor.toPlainText())    # shipped default in use
            w2.output.clear()
            w2.preamble_editor.setPlainText("% cannot be saved\n")
            w2.save_preamble()                                                  # reports instead of crashing
            self.assertIn("Could not save the preamble", w2.output.toPlainText())


class SessionTempDirTests(WindowTestCase):
    def test_temp_dir_is_a_private_folder_outside_the_package(self):
        temp = os.path.realpath(self.window.temp_dir)
        self.assertTrue(os.path.basename(temp).startswith("ztikz-"))
        self.assertEqual(os.path.dirname(temp), os.path.realpath(tempfile.gettempdir()))
        self.assertFalse(os.path.normcase(temp).startswith(os.path.normcase(os.path.realpath(PACKAGE_DIR))))

    def test_two_running_windows_do_not_share_a_folder(self):
        from zTikz.main import main_window
        other = main_window()
        self.addCleanup(lambda: (other.editor.document().setModified(False), other.close()))
        self.assertNotEqual(os.path.realpath(other.temp_dir), os.path.realpath(self.window.temp_dir))

    def test_closing_a_window_removes_only_its_own_folder(self):
        from zTikz.main import main_window
        other = main_window()
        mine, theirs = self.window.temp_dir, other.temp_dir
        other.editor.document().setModified(False)
        other.close()
        self.assertFalse(os.path.exists(theirs))
        self.assertTrue(os.path.isdir(mine))

    @requires_pdflatex
    def test_both_windows_can_compile_at_the_same_time(self):
        from zTikz.main import main_window
        other = main_window()
        self.addCleanup(lambda: (other.editor.document().setModified(False), other.close()))
        other.editor.setPlainText(r"\draw (0,0) circle (1);")
        mine = self.compile_code(r"\draw (0,0) rectangle (1,1);")
        other.output.clear()
        other.compile_and_wait()
        self.assertIn("Compilation successful", mine)
        self.assertIn("Compilation successful", other.output.toPlainText())
        self.assertTrue(os.path.exists(os.path.join(self.window.temp_dir, "temp.pdf")))
        self.assertTrue(os.path.exists(os.path.join(other.temp_dir, "temp.pdf")))

    @requires_pdflatex
    def test_a_temp_folder_deleted_mid_session_is_recreated(self):
        shutil.rmtree(self.window.temp_dir)
        out = self.compile_code(r"\draw (0,0)--(9,9);")
        self.assertTrue(os.path.isdir(self.window.temp_dir))
        self.assertIn("Compilation successful", out)


@requires_pdflatex
class PackageFolderIsNeverWrittenTests(WindowTestCase):
    """After pip install the package folder can be read-only, so a whole session must leave it untouched."""

    def test_a_full_session_leaves_the_package_folder_untouched(self):
        from PyQt6.QtGui import QDesktopServices
        from zTikz.main import main_window

        before = snapshot(PACKAGE_DIR)
        with tempfile.TemporaryDirectory() as out_dir, mock.patch.object(QDesktopServices, "openUrl", return_value=True):
            w = main_window()                                              # startup compiles once
            try:
                w.editor.setPlainText(r"\draw (0,0) -- (2,1); \node at (1,1) {\'e};")
                w.compile_and_wait()
                w.preamble_editor.setPlainText(read_text_file(app_paths.default_preamble_path()) + "\n% edit\n")
                w.save_preamble()
                w.compile_and_wait()
                w.restore_preamble()
                for name, flt in (("a.png", "PNG Files (*.png)"), ("a.pdf", "PDF Files (*.pdf)"), ("a.svg", "SVG Files (*.svg)")):
                    with save_dialog_returns(os.path.join(out_dir, name), flt):
                        w.export_image()
                from zTikz.ui.menu import _open_pdf_externally
                _open_pdf_externally(w)
                temp_dir = w.temp_dir
            finally:
                w.editor.document().setModified(False)
                w.close()

        self.assertEqual(snapshot(PACKAGE_DIR), before)
        self.assertFalse(os.path.exists(temp_dir))                          # ...and the session's temp folder is gone


if __name__ == "__main__":
    unittest.main()
