import os
import tempfile
import unittest
from unittest import mock

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMessageBox

import qt_support
from qt_support import WindowTestCase, requires_pdflatex, save_dialog_returns, message_box_answers

Button = QMessageBox.StandardButton


class LeftPanelTabTests(WindowTestCase):
    def setUp(self):
        super().setUp()
        self.window.preamble_editor.hide()
        self.window.preamble_buttons_widget.hide()

    def test_preamble_editor_is_hidden_at_startup(self):
        self.assertTrue(self.window.preamble_editor.isHidden())

    def test_opening_the_preamble_tab_shows_its_editor(self):
        self.window.toggle_left_panel(2)                     # tabs: 0 Files, 1 Snippets, 2 Preamble
        self.assertFalse(self.window.preamble_editor.isHidden())
        self.assertFalse(self.window.preamble_buttons_widget.isHidden())

    def test_opening_the_snippets_tab_does_not_show_the_preamble_editor(self):
        self.window.toggle_left_panel(1)
        self.assertTrue(self.window.preamble_editor.isHidden())


@requires_pdflatex
class ExportTests(WindowTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.window.editor.setPlainText(r"\draw (0,0) -- (1,1);")
        cls.window.compile_and_wait()

    def setUp(self):
        super().setUp()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name

    def export(self, name, selected_filter=""):
        path = os.path.join(self.dir, name)
        with save_dialog_returns(path, selected_filter):
            self.window.export_image()
        return path

    def read_head(self, path, n=200):
        with open(path, "rb") as f:
            return f.read(n)

    def test_png_export_is_a_png(self):
        self.assertTrue(self.read_head(self.export("out.png", "PNG Files (*.png)")).startswith(b"\x89PNG"))

    def test_pdf_export_is_a_pdf(self):
        self.assertTrue(self.read_head(self.export("out.pdf", "PDF Files (*.pdf)")).startswith(b"%PDF"))

    def test_svg_export_is_an_svg(self):
        path = self.export("out.svg", "SVG Files (*.svg)")
        self.assertIn(b"<svg", self.read_head(path, 2000))

    def test_exporting_twice_still_works(self):
        # The old implementation moved the PNG, so a second export failed.
        self.export("a.png", "PNG Files (*.png)")
        self.export("b.png", "PNG Files (*.png)")
        self.assertTrue(os.path.exists(os.path.join(self.dir, "b.png")))
        self.assertTrue(os.path.exists(self.window.image_path))

    def test_missing_extension_uses_the_selected_filter(self):
        self.export("noext", "PDF Files (*.pdf)")
        self.assertTrue(os.path.exists(os.path.join(self.dir, "noext.pdf")))

    def test_cancelled_dialog_writes_nothing(self):
        with save_dialog_returns("", ""):
            self.window.export_image()
        self.assertEqual(os.listdir(self.dir), [])


class UnsavedChangesTests(WindowTestCase):
    def setUp(self):
        super().setUp()
        w = self.window
        w.editor.setPlainText("MARKER")
        w.editor.document().setModified(True)
        w.current_file_path = None
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name

    def close_window(self):
        """Fire closeEvent without letting its cleanup delete the shared temp folder."""
        event = QCloseEvent()
        with mock.patch("shutil.rmtree"):
            self.window.closeEvent(event)
        return event

    def test_new_file_cancel_keeps_the_text(self):
        with message_box_answers(Button.Cancel) as calls:
            self.window.new_file()
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.window.editor.toPlainText(), "MARKER")

    def test_new_file_discard_resets_the_text(self):
        with message_box_answers(Button.Discard):
            self.window.new_file()
        self.assertNotEqual(self.window.editor.toPlainText(), "MARKER")

    def test_close_cancel_ignores_the_event(self):
        with message_box_answers(Button.Cancel):
            self.assertFalse(self.close_window().isAccepted())

    def test_save_with_cancelled_save_dialog_aborts_close(self):
        with message_box_answers(Button.Save), save_dialog_returns("", ""):
            self.assertFalse(self.close_window().isAccepted())
        self.assertTrue(self.window.editor.document().isModified())

    def test_save_writes_the_file_and_then_closes(self):
        path = os.path.join(self.dir, "saved.tex")
        with message_box_answers(Button.Save), save_dialog_returns(path, ""):
            event = self.close_window()
        self.assertTrue(event.isAccepted())
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "MARKER")

    def test_unmodified_document_closes_without_prompt(self):
        self.window.editor.document().setModified(False)
        with message_box_answers(Button.Cancel) as calls:
            self.assertTrue(self.close_window().isAccepted())
        self.assertEqual(calls, [])


class ParseStatusTests(WindowTestCase):
    """The status bar tells the user when the canvas overlay can't follow part of the code."""
    MATRIX = '\\draw (0,0) -- (1,1);\n\\matrix {\\node{a};&\\node{b};\\\\};\n'

    def test_valid_code_shows_no_message_and_hides_the_bar(self):
        self.window.editor.setPlainText(r"\draw (0,0) -- (1,1);")
        bar = self.window.statusBar()
        self.assertEqual(bar.currentMessage(), "")
        self.assertTrue(bar.isHidden())

    def test_uninterpretable_line_is_reported_with_its_line_number(self):
        self.window.editor.setPlainText(self.MATRIX)
        bar = self.window.statusBar()
        self.assertFalse(bar.isHidden())
        self.assertIn("line 2", bar.currentMessage())

    def test_message_goes_away_when_the_code_is_fixed(self):
        self.window.editor.setPlainText(self.MATRIX)
        self.window.editor.setPlainText(r"\draw (0,0) -- (1,1);")
        self.assertEqual(self.window.statusBar().currentMessage(), "")
        self.assertTrue(self.window.statusBar().isHidden())


class OpenFileGuardTests(WindowTestCase):
    """Opening another file must not silently discard unsaved changes."""

    def setUp(self):
        super().setUp()
        w = self.window
        w.editor.setPlainText("MARKER")
        w.editor.document().setModified(True)
        w.current_file_path = None
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.new_file_path = os.path.join(tmp.name, "other.tex")
        with open(self.new_file_path, "w", encoding="utf-8") as f:
            f.write("OTHER")

    def open_via_dialog(self):
        picker = mock.Mock(return_value=(self.new_file_path, ""))
        with mock.patch.object(qt_support.QFileDialog, "getOpenFileName", staticmethod(picker)):
            self.window.open_file()
        return picker

    def open_via_tree(self):
        w = self.window
        with mock.patch.object(w.file_model, "isDir", return_value=False), \
                mock.patch.object(w.file_model, "filePath", return_value=self.new_file_path):
            w.open_file_from_tree(None)

    def test_cancel_keeps_the_current_text_and_never_shows_the_file_dialog(self):
        with message_box_answers(Button.Cancel):
            picker = self.open_via_dialog()
        picker.assert_not_called()
        self.assertEqual(self.window.editor.toPlainText(), "MARKER")

    def test_save_with_cancelled_save_dialog_does_not_open_the_file(self):
        # The old code went on to open the file after a cancelled Save As, losing the changes.
        with message_box_answers(Button.Save), save_dialog_returns("", ""):
            picker = self.open_via_dialog()
        picker.assert_not_called()
        self.assertEqual(self.window.editor.toPlainText(), "MARKER")
        self.assertTrue(self.window.editor.document().isModified())

    def test_discard_opens_the_file(self):
        with message_box_answers(Button.Discard):
            self.open_via_dialog()
        self.assertEqual(self.window.editor.toPlainText(), "OTHER")

    def test_file_tree_cancel_keeps_the_current_text(self):
        with message_box_answers(Button.Cancel):
            self.open_via_tree()
        self.assertEqual(self.window.editor.toPlainText(), "MARKER")

    def test_file_tree_save_with_cancelled_save_dialog_does_not_open_the_file(self):
        with message_box_answers(Button.Save), save_dialog_returns("", ""):
            self.open_via_tree()
        self.assertEqual(self.window.editor.toPlainText(), "MARKER")

    def test_file_tree_discard_opens_the_file(self):
        with message_box_answers(Button.Discard):
            self.open_via_tree()
        self.assertEqual(self.window.editor.toPlainText(), "OTHER")

    def test_unmodified_document_opens_without_prompt(self):
        self.window.editor.document().setModified(False)
        with message_box_answers(Button.Cancel) as calls:
            self.open_via_dialog()
        self.assertEqual(calls, [])
        self.assertEqual(self.window.editor.toPlainText(), "OTHER")


class ExternalViewerTests(WindowTestCase):
    """'Show PDF' opens a copy, so a viewer locking it can't block the next compile."""

    def setUp(self):
        super().setUp()
        self.temp_pdf = os.path.join(self.window.temp_dir, "temp.pdf")
        self.temp_pdf_backup = None
        if os.path.exists(self.temp_pdf):
            with open(self.temp_pdf, "rb") as f:
                self.temp_pdf_backup = f.read()
        self.addCleanup(self.restore_temp_pdf)

    def restore_temp_pdf(self):
        if self.temp_pdf_backup is None:
            if os.path.exists(self.temp_pdf):
                os.remove(self.temp_pdf)
        else:
            with open(self.temp_pdf, "wb") as f:
                f.write(self.temp_pdf_backup)

    def write_temp_pdf(self, data=b"%PDF-1.4 fake"):
        with open(self.temp_pdf, "wb") as f:
            f.write(data)

    def show_pdf(self):
        from PyQt6.QtGui import QDesktopServices
        from zTikz.ui.menu import _open_pdf_externally
        with mock.patch.object(QDesktopServices, "openUrl", return_value=True) as open_url:
            _open_pdf_externally(self.window)
        return open_url

    def opened_path(self, open_url):
        return open_url.call_args[0][0].toLocalFile()

    def test_without_a_compiled_pdf_it_says_so(self):
        if os.path.exists(self.temp_pdf):
            os.remove(self.temp_pdf)
        self.window.output.clear()
        open_url = self.show_pdf()
        open_url.assert_not_called()
        self.assertIn("No compiled PDF found", self.window.output.toPlainText())

    def test_opens_a_copy_not_the_live_pdf(self):
        self.write_temp_pdf(b"%PDF-1.4 snapshot")
        open_url = self.show_pdf()
        opened = self.opened_path(open_url)
        self.assertNotEqual(os.path.normcase(opened), os.path.normcase(os.path.abspath(self.temp_pdf)))
        with open(opened, "rb") as f:
            self.assertEqual(f.read(), b"%PDF-1.4 snapshot")

    def test_live_pdf_can_still_be_replaced_while_the_copy_is_open(self):
        # On Windows a viewer holds its file open; the live temp.pdf must stay replaceable.
        self.write_temp_pdf(b"first")
        open_url = self.show_pdf()
        with open(self.opened_path(open_url), "rb"):          # "viewer" keeps the copy open
            self.write_temp_pdf(b"second")                     # the next compile's output
            os.remove(self.temp_pdf)

    def test_falls_back_to_a_new_name_when_the_previous_copy_is_locked(self):
        import shutil
        self.write_temp_pdf(b"payload")
        real_copy = shutil.copyfile
        calls = []

        def copy_but_first_is_locked(src, dst, *a, **k):
            calls.append(dst)
            if len(calls) == 1:
                raise PermissionError("locked by viewer")
            return real_copy(src, dst, *a, **k)

        with mock.patch("shutil.copyfile", side_effect=copy_but_first_is_locked):
            open_url = self.show_pdf()
        opened = self.opened_path(open_url)
        self.assertEqual(len(calls), 2)
        self.assertNotEqual(os.path.basename(opened), "viewer_copy.pdf")
        with open(opened, "rb") as f:
            self.assertEqual(f.read(), b"payload")

    def test_reports_when_no_copy_can_be_made(self):
        self.write_temp_pdf()
        self.window.output.clear()
        with mock.patch("shutil.copyfile", side_effect=PermissionError("nope")):
            open_url = self.show_pdf()
        open_url.assert_not_called()
        self.assertIn("Could not open the PDF", self.window.output.toPlainText())


if __name__ == "__main__":
    unittest.main()
