import os
import json
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression

class tikz_highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlighting_rules = []
        self.load_highlighting_settings()
        
    def load_highlighting_settings(self):
        from zTikz.utils.theme import is_dark_mode
        
        config_name = 'highlighting_config_dark.json' if is_dark_mode() else 'highlighting_config.json'
        config_path = os.path.join(os.path.dirname(__file__), '..', 'resources', config_name)
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
        
        # TikZ/LaTeX command format (e.g., \draw, \node)
        command_format = QTextCharFormat()
        command_format.setForeground(QColor(config["commands"]["color"]))
        if config["commands"].get("bold", False):
            command_format.setFontWeight(QFont.Weight.Bold)
        self._highlighting_rules.append((QRegularExpression(r"\\[a-zA-Z]+"), command_format))
        
        # Braces format (e.g., {content})
        brace_format = QTextCharFormat()
        brace_format.setForeground(QColor(config["braces"]["color"]))
        self._highlighting_rules.append((QRegularExpression(r"[{}]"), brace_format))

        # Numbers (coordinates)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(config["numbers"]["color"]))
        self._highlighting_rules.append((QRegularExpression(r"-?\b\d+(\.\d+)?\b"), number_format))

        # Comments (e.g., % comment)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(config["comments"]["color"]))
        if config["comments"].get("italic", False):
            comment_format.setFontItalic(True)
        self._highlighting_rules.append((QRegularExpression(r"%[^\n]*"), comment_format))

        # Keywords (e.g., \begin, \end)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(config["keywords"]["color"]))
        if config["keywords"].get("bold", False):
            keyword_format.setFontWeight(QFont.Weight.Bold)
        self._highlighting_rules.append((QRegularExpression(r"\\begin|\\end"), keyword_format))

        # Node content format — the text inside {…} after node[…]
        # Color is configurable in highlighting_config.json → "node_content" → "color"
        self._node_content_format = QTextCharFormat()
        node_color = config.get("node_content", {}).get("color", "#CC6600")
        self._node_content_format.setForeground(QColor(node_color))

    def highlightBlock(self, text):
        # 1) Apply normal regex rules
        for pattern, format in self._highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        # 2) Highlight node label content: node  or  node[...]{content}
        #    Scan for the word "node", skip optional whitespace + [...], then
        #    colour everything inside the matching {…} pair.
        self._highlight_node_content(text)

    def _highlight_node_content(self, text):
        """Find every ``node`` token and colour the brace-delimited label that follows."""
        node_re = QRegularExpression(r'\bnode\b')
        it = node_re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            pos = m.capturedEnd()           # position right after "node"

            # Skip optional whitespace
            while pos < len(text) and text[pos] in ' \t':
                pos += 1

            # Skip optional [options] block (handle nested brackets)
            if pos < len(text) and text[pos] == '[':
                depth = 1
                pos += 1
                while pos < len(text) and depth > 0:
                    if text[pos] == '[':
                        depth += 1
                    elif text[pos] == ']':
                        depth -= 1
                    pos += 1

            # Skip optional whitespace between ] and {
            while pos < len(text) and text[pos] in ' \t':
                pos += 1

            # Skip optional "at (x,y)" clause
            if pos < len(text) and text[pos:pos+2] == 'at':
                pos += 2
                while pos < len(text) and text[pos] in ' \t':
                    pos += 1
                if pos < len(text) and text[pos] == '(':
                    while pos < len(text) and text[pos] != ')':
                        pos += 1
                    if pos < len(text):
                        pos += 1  # skip ')'
                while pos < len(text) and text[pos] in ' \t':
                    pos += 1

            # Now we expect the opening brace
            if pos < len(text) and text[pos] == '{':
                brace_start = pos
                depth = 1
                pos += 1
                while pos < len(text) and depth > 0:
                    if text[pos] == '{':
                        depth += 1
                    elif text[pos] == '}':
                        depth -= 1
                    pos += 1
                # Highlight everything between the braces (exclusive of braces themselves)
                inner_start = brace_start + 1
                inner_len = pos - brace_start - 2  # -2 for both { and }
                if inner_len > 0:
                    self.setFormat(inner_start, inner_len, self._node_content_format)
