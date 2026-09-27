from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtGui import QPainter, QColor, QTextFormat, QFont, QTextCursor
from PyQt6.QtCore import QRect, QSize, Qt
from zTikz.utils.theme import is_dark_mode

class line_number_area(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class code_editor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shape_highlight_intervals = []
        self.line_number_area = line_number_area(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def set_shape_highlight_intervals(self, intervals):
        self.shape_highlight_intervals = intervals
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = 1
        maxBlocks = max(1, self.blockCount())
        while maxBlocks >= 10:
            maxBlocks //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        
        # Background color
        bg_color = QColor(30, 30, 30) if is_dark_mode() else Qt.GlobalColor.white
        painter.fillRect(event.rect(), bg_color)
        
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        # Text color
        text_color = QColor(133, 133, 133) if is_dark_mode() else Qt.GlobalColor.gray

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(text_color)
                painter.drawText(0, top, self.line_number_area.width()-2, 
                                 self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlight_current_line(self):
        extraSelections = []
        if not self.isReadOnly(): 
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(45, 45, 45) if is_dark_mode() else QColor(232, 232, 255)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
            
        # Add shape highlights
        for start, stop in self.shape_highlight_intervals:
            selection = QTextEdit.ExtraSelection()
            shape_color = QColor(80, 80, 0, 150) if is_dark_mode() else QColor(255, 255, 0, 150)
            selection.format.setBackground(shape_color)
            
            cursor = self.textCursor()
            cursor.setPosition(max(0, start))
            cursor.setPosition(min(len(self.toPlainText()), stop + 1), QTextCursor.MoveMode.KeepAnchor)
            selection.cursor = cursor
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn(1)
            elif delta < 0:
                self.zoomOut(1)
            # Clamp font size to a reasonable range
            font = self.font()
            size = font.pointSize()
            if size < 6:
                font.setPointSize(6)
                self.setFont(font)
            elif size > 72:
                font.setPointSize(72)
                self.setFont(font)
            self.update_line_number_area_width(0)
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Slash:
            self.toggle_comment()
            return
        super().keyPressEvent(event)

    def toggle_comment(self):
        cursor = self.textCursor()
        
        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()
        
        cursor.setPosition(start_pos)
        start_block = cursor.blockNumber()
        cursor.setPosition(end_pos)
        end_block = cursor.blockNumber()
        
        # If the cursor is exactly at the start of the next block but there is a selection,
        # we don't want to comment that empty line
        if cursor.positionInBlock() == 0 and end_block > start_block:
            end_block -= 1

        cursor.beginEditBlock()

        # First pass: check if all selected lines are already commented
        all_commented = True
        for i in range(start_block, end_block + 1):
            block = self.document().findBlockByNumber(i)
            text = block.text().lstrip()
            # Ignore completely empty lines when determining "all commented" state
            if text and not text.startswith('%'):
                all_commented = False
                break

        # Second pass: toggle the comments
        for i in range(start_block, end_block + 1):
            block = self.document().findBlockByNumber(i)
            text = block.text()
            cursor.setPosition(block.position())
            
            if all_commented:
                # Uncomment
                stripped = text.lstrip()
                if stripped.startswith('%'):
                    idx = text.find('%')
                    cursor.setPosition(block.position() + idx)
                    cursor.deleteChar()
            else:
                # Comment
                cursor.insertText('%')

        cursor.endEditBlock()