import random
import unittest

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QPlainTextEdit

import qt_support
from qt_support import WindowTestCase

from zTikz.utils.functions import _replace_editor_text


class ReplaceEditorTextTests(unittest.TestCase):
    def setUp(self):
        qt_support.get_app()

    def make_editor(self, text):
        editor = QPlainTextEdit()
        editor.setPlainText(text)
        return editor

    def test_result_equals_new_text_for_random_edits(self):
        # Includes a non-BMP character: QTextDocument positions are UTF-16 code units.
        rng = random.Random(1)
        alphabet = ["a", "b", " ", "\n", "(", ")", "\U0001F600", "é", "日"]
        for _ in range(300):
            old = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 40)))
            new = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 40)))
            editor = self.make_editor(old)
            _replace_editor_text(editor, new)
            self.assertEqual(editor.toPlainText(), new, (old, new))

    def test_each_replacement_is_one_undo_step(self):
        editor = self.make_editor("hello world")
        _replace_editor_text(editor, "hello brave new world")
        editor.document().undo()
        self.assertEqual(editor.toPlainText(), "hello world")

    def test_join_previous_merges_into_one_undo_step(self):
        editor = self.make_editor("0 0")
        _replace_editor_text(editor, "1 0")
        _replace_editor_text(editor, "1 2", join_previous=True)
        _replace_editor_text(editor, "3 2", join_previous=True)
        editor.document().undo()
        self.assertEqual(editor.toPlainText(), "0 0")

    def test_identical_text_is_a_no_op(self):
        editor = self.make_editor("same")
        editor.document().setUndoRedoEnabled(False)
        editor.document().setUndoRedoEnabled(True)
        _replace_editor_text(editor, "same")
        self.assertFalse(editor.document().isUndoAvailable())

    def test_cursor_and_undo_history_are_kept(self):
        editor = self.make_editor("aaa bbb ccc")
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        editor.setTextCursor(cursor)
        editor.insertPlainText("!")
        _replace_editor_text(editor, "aaa BBBBB ccc!")
        self.assertEqual(editor.textCursor().position(), len("aaa BBBBB ccc!"))
        editor.document().undo()                       # the replacement
        editor.document().undo()                       # the earlier typing is still there
        self.assertEqual(editor.toPlainText(), "aaa bbb ccc")


class CanvasDragTests(WindowTestCase):
    CODE = "\\draw (0,0) rectangle (2,1);\n\\node at (1,2) {é label};\n"

    def setUp(self):
        super().setUp()
        w = self.window
        w.editor.setPlainText(self.CODE)                  # also parses the code into canvas shapes
        w.editor.document().setModified(False)
        cursor = w.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        w.editor.setTextCursor(cursor)
        w.editor.insertPlainText("% typed by user\n")
        self.typed = w.editor.toPlainText()
        w.parse_tikz_and_update_canvas()
        self.addCleanup(self.reset_gesture_state)

    def reset_gesture_state(self):
        self.window.canvas.is_dragging = False
        self.window._canvas_edit_open = False

    def drag_rectangle(self):
        """Simulate a drag: three intermediate updates, then the final one on release."""
        w = self.window
        rect = next(s for s in w.canvas.shapes if s[-1] == "rectangle")
        w.canvas.is_dragging = True
        for dx in (10, 25, 40):
            for i in range(len(rect) - 1):
                rect[i] = QPointF(rect[i].x() + dx / 3.0, rect[i].y())
            w.update_tikz_code()
        w.canvas.is_dragging = False
        w.update_tikz_code()
        return w.editor.toPlainText()

    def test_drag_rewrites_the_code_and_marks_the_document_modified(self):
        after = self.drag_rectangle()
        self.assertNotEqual(after, self.typed)
        self.assertIn("rectangle", after)
        self.assertIn("% typed by user", after)            # everything else is untouched
        self.assertTrue(self.window.editor.document().isModified())

    def test_cursor_is_kept_not_reset_to_the_start(self):
        before_pos = self.window.editor.textCursor().position()
        before_len = len(self.window.editor.toPlainText())
        after = self.drag_rectangle()
        self.assertEqual(self.window.editor.textCursor().position(), before_pos + len(after) - before_len)

    def test_one_undo_reverts_the_whole_drag(self):
        self.drag_rectangle()
        self.window.editor.document().undo()
        self.assertEqual(self.window.editor.toPlainText(), self.typed)

    def test_undo_history_from_before_the_drag_survives(self):
        after = self.drag_rectangle()
        doc = self.window.editor.document()
        doc.undo()                                          # the drag
        self.assertTrue(doc.isUndoAvailable())
        doc.undo()                                          # the user's typing
        self.assertNotIn("typed by user", self.window.editor.toPlainText())
        doc.redo()
        doc.redo()
        self.assertEqual(self.window.editor.toPlainText(), after)

    def test_typing_after_a_drag_is_a_separate_undo_step(self):
        after = self.drag_rectangle()
        self.window.editor.insertPlainText("% later\n")
        self.window.editor.document().undo()
        self.assertEqual(self.window.editor.toPlainText(), after)


if __name__ == "__main__":
    unittest.main()
