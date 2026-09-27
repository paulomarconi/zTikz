import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zTikz.parser.parser import tikz_parser


class ParserUpdateCodeTests(unittest.TestCase):
    def test_overlay_model_extracts_coordinate_nodes(self):
        parser = tikz_parser()
        code = r'''\begin{tikzpicture}
\draw (0,0) -- (1,1);
\node at (2,2) {A};
\end{tikzpicture}
'''

        parser.parse_to_canvas_shapes(code, incremental=False)
        overlay = parser.last_overlay_model

        self.assertEqual(len(overlay['nodes']), 3)
        self.assertEqual(len(overlay['scopes']), 0)

    def test_overlay_model_extracts_nested_scopes(self):
        parser = tikz_parser()
        code = r'''\begin{tikzpicture}
\begin{scope}
  \draw (0,0) -- (1,1);
  \begin{scope}
    \node at (2,2) {A};
  \end{scope}
\end{scope}
\end{tikzpicture}
'''

        parser.parse_to_canvas_shapes(code, incremental=False)
        overlay = parser.last_overlay_model

        self.assertEqual(len(overlay['scopes']), 2)
        self.assertTrue(all(scope.rect is not None for scope in overlay['scopes']))
        inner_scopes = [scope for scope in overlay['scopes'] if scope.parent_id is not None]
        self.assertEqual(len(inner_scopes), 1)
        self.assertEqual(len(inner_scopes[0].node_intervals), 1)

    def test_named_inline_node_in_path_is_parsed(self):
        parser = tikz_parser()
        code = r'''\begin{tikzpicture}
\draw (-7.5,1.2) node (v1) {} rectangle (-6.7,0.8) node[midway,align=center]{$z^{-1}$};
\draw (v1) -- (-6.7,1.2);
\end{tikzpicture}
'''

        shapes = parser.parse_to_canvas_shapes(code, incremental=False)
        overlay = parser.last_overlay_model

        self.assertGreaterEqual(len(shapes), 3)
        path_shapes = [shape for shape in shapes if shape[-1] == 'path']
        self.assertTrue(any(len(shape[:-1]) == 2 for shape in path_shapes))
        self.assertGreaterEqual(len(overlay['nodes']), 2)

    def test_circle_radius_parentheses_preserved_when_updating_code(self):
        parser = tikz_parser()
        code = r'''\begin{tikzpicture}
\draw (0,0) circle (10);
\end{tikzpicture}
'''

        shapes = parser.parse_to_canvas_shapes(code, incremental=False)
        updated_code = parser.update_code(code, shapes)

        self.assertIn('circle (10)', updated_code)
        self.assertNotIn('circle 10;', updated_code)

    def test_ellipse_parentheses_preserved_when_updating_code(self):
        parser = tikz_parser()
        code = r'''\begin{tikzpicture}
\draw (0,0) ellipse (5 and 3);
\end{tikzpicture}
'''

        shapes = parser.parse_to_canvas_shapes(code, incremental=False)
        updated_code = parser.update_code(code, shapes)

        self.assertIn('ellipse (5 and 3)', updated_code)
        self.assertNotIn('ellipse 5 and 3;', updated_code)

        # Ensure the updated code still parses back into an ellipse shape
        parsed_shapes = parser.parse_to_canvas_shapes(updated_code, incremental=False)
        self.assertEqual(len(parsed_shapes), 1)
        self.assertEqual(parsed_shapes[0][-1], 'ellipse')

    def test_arc_parentheses_preserved_when_updating_code(self):
        parser = tikz_parser()
        code = r'''\begin{tikzpicture}
\draw (0,0) arc (0:90:10);
\end{tikzpicture}
'''

        shapes = parser.parse_to_canvas_shapes(code, incremental=False)
        updated_code = parser.update_code(code, shapes)

        self.assertIn('arc (0:90:10)', updated_code)
        self.assertNotIn('arc 0:90:10', updated_code)

        # Ensure the updated code still parses back into an arc shape
        parsed_shapes = parser.parse_to_canvas_shapes(updated_code, incremental=False)
        self.assertEqual(len(parsed_shapes), 1)
        self.assertEqual(parsed_shapes[0][-1], 'arc')

    def test_rectangle_parentheses_preserved_when_updating_code(self):
        parser = tikz_parser()
        code = r'''\begin{tikzpicture}
\draw (0,0) rectangle (10,10);
\end{tikzpicture}
'''

        shapes = parser.parse_to_canvas_shapes(code, incremental=False)
        updated_code = parser.update_code(code, shapes)

        self.assertIn('rectangle (10, 10)', updated_code)
        self.assertNotIn('rectangle 10, 10', updated_code)

        # Ensure the updated code still parses back into a rectangle shape
        parsed_shapes = parser.parse_to_canvas_shapes(updated_code, incremental=False)
        self.assertEqual(len(parsed_shapes), 1)
        self.assertEqual(parsed_shapes[0][-1], 'rectangle')

    def test_path_coordinates_preserved_when_updating_code(self):
        parser = tikz_parser()
        code = r'''\begin{tikzpicture}
\draw (0,0) -- (10,10);
\end{tikzpicture}
'''

        shapes = parser.parse_to_canvas_shapes(code, incremental=False)
        updated_code = parser.update_code(code, shapes)

        self.assertIn('(0, 0)', updated_code)
        self.assertIn('(10, 10)', updated_code)
        self.assertIn(' -- ', updated_code)

        # Ensure the updated code still parses back into a path shape
        parsed_shapes = parser.parse_to_canvas_shapes(updated_code, incremental=False)
        self.assertEqual(len(parsed_shapes), 1)
        self.assertEqual(parsed_shapes[0][-1], 'path')
        self.assertEqual(len(parsed_shapes[0]), 3)  # 2 points + type


class ParserErrorReportingTests(unittest.TestCase):
    """last_errors tells the UI which lines the canvas overlay could not interpret."""

    MATRIX = '\\matrix {\\node{a};&\\node{b};\\\\};'   # valid TikZ the grammar doesn't cover

    def test_valid_code_has_no_errors(self):
        parser = tikz_parser()
        parser.parse(r'\draw (0,0) -- (1,1);', incremental=False)
        self.assertEqual(parser.last_errors, [])

    def test_error_line_refers_to_the_users_code_for_bare_snippets(self):
        # Bare code is wrapped in \begin{tikzpicture}, which must not shift the reported line.
        parser = tikz_parser()
        parser.parse('\\draw (0,0) -- (1,1);\n' + self.MATRIX + '\n\\draw (2,2) -- (3,3);', incremental=False)
        self.assertEqual(parser.last_errors[0][0], 2)

    def test_error_line_is_correct_for_code_with_its_own_tikzpicture(self):
        parser = tikz_parser()
        parser.parse('\\begin{tikzpicture}\n\\draw (0,0) -- (1,1);\n' + self.MATRIX + '\n\\end{tikzpicture}',
                     incremental=False)
        self.assertEqual(parser.last_errors[0][0], 3)

    def test_errors_never_point_past_the_last_line(self):
        parser = tikz_parser()
        code = '\\draw (0,0) -- (1,1);\n' + self.MATRIX + '\n\\draw (2,2) -- (3,3);'
        parser.parse(code, incremental=False)
        user_lines = code.count('\n') + 1
        self.assertTrue(parser.last_errors)
        self.assertTrue(all(1 <= line <= user_lines for line, _col, _msg in parser.last_errors))

    def test_cached_parse_keeps_the_errors(self):
        parser = tikz_parser()
        code = self.MATRIX
        parser.parse(code, incremental=False)
        first = list(parser.last_errors)
        parser.parse(code, incremental=True)                 # served from the hash cache
        self.assertEqual(parser.last_errors, first)
        self.assertTrue(first)

    def test_errors_clear_once_the_code_is_valid_again(self):
        parser = tikz_parser()
        parser.parse(self.MATRIX, incremental=False)
        self.assertTrue(parser.last_errors)
        parser.parse(r'\draw (0,0) -- (1,1);', incremental=False)
        self.assertEqual(parser.last_errors, [])

    def test_invalidate_cache_clears_errors(self):
        parser = tikz_parser()
        parser.parse(self.MATRIX, incremental=False)
        parser.invalidate_cache()
        self.assertEqual(parser.last_errors, [])


if __name__ == '__main__':
    unittest.main()
