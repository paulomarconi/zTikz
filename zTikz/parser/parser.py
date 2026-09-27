# =============================================================================
# parser.py — TikZ parser using ANTLR4
#
# This module replaces the old regex-based parser with an ANTLR4-powered one.
# The public API is identical to the old tikz_parser class, so main.py and
# canvas.py need no changes.
#
# Architecture:
#   tikz_parser.parse()
#       → feeds code to TikzLexer + TikzParser (ANTLR4 generated)
#       → walks the parse tree with TikzVisitor
#       → returns a list of shape-dicts  (same format as the old regex parser)
#
#   tikz_parser.parse_to_canvas_shapes()
#       → calls parse() and converts shape-dicts to the flat list format
#         expected by drawing_canvas  ([p1, p2, "rectangle"] etc.)
#
# Incremental parsing:
#   A simple MD5-hash cache avoids re-parsing if the TikZ code hasn't changed.
#   The old "incremental parse by command" logic is preserved as a fast path
#   for small edits.
#
# Error handling:
#   ANTLR4 parse errors are caught and silently ignored so the UI stays
#   responsive even when the user is mid-sentence in the editor.
# =============================================================================

import re
import math
import hashlib
import logging
from dataclasses import dataclass, field

from PyQt6.QtCore import QPoint, QPointF
from PyQt6.QtGui import QColor, QFont

# ---------- ANTLR4 runtime ----------
from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

# ---------- Generated ANTLR4 classes (in same directory) ----------
from zTikz.antlr.TikzLexer import TikzLexer
from zTikz.antlr.TikzParser import TikzParser

# ---------- Our custom visitor ----------
from zTikz.parser.tikz_visitor import TikzVisitor


class CanvasShapeList(list):
    """
    A custom list subclass that behaves exactly like a regular Python list
    (so canvas.py can iterate and modify it without issues), but secretly
    carries the AST character intervals for the coordinates.
    """
    def __init__(self, elements, intervals=None, is_new=False, cmd_interval=None):
        super().__init__(elements)
        self.intervals = intervals or []
        self.is_new = is_new
        self.cmd_interval = cmd_interval


@dataclass
class OverlayNode:
    interval: tuple[int, int]
    point: QPointF
    shape_index: int
    point_index: int
    scope_ids: list[int] = field(default_factory=list)


@dataclass
class OverlayScope:
    id: int
    start: int
    end: int
    parent_id: int | None = None
    child_scope_ids: list[int] = field(default_factory=list)
    node_intervals: list[tuple[int, int]] = field(default_factory=list)
    rect: tuple[int, int, int, int] | None = None


# ---------------------------------------------------------------------------
# Silent error listener — suppresses ANTLR console output while the user
# is still typing incomplete TikZ code.
# ---------------------------------------------------------------------------
class _SilentErrorListener(ErrorListener):
    """Swallows all ANTLR4 parse/lex errors; stores the last message."""

    def __init__(self):
        super().__init__()
        self.errors: list[str] = []
        self.details: list[tuple[int, int, str]] = []   # (line, column, message)

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Log at DEBUG level so developers can see them, but not the user
        logging.debug(f"ANTLR TikZ parse error at {line}:{column} — {msg}")
        self.errors.append(f"Line {line}:{column} {msg}")
        self.details.append((line, column, msg))


# ---------------------------------------------------------------------------
# Main parser class — drop-in replacement for the old regex-based parser
# ---------------------------------------------------------------------------
class tikz_parser:
    """
    ANTLR4-based TikZ parser.

    Public API (unchanged from old regex parser):
        parse(tikz_code, incremental=False)  → list of shape dicts
        parse_to_canvas_shapes(code, incremental=True) → canvas shape list
        invalidate_cache()
    """

    def __init__(self, scaling: float = 10.0, canvas_height: float = 800.0):
        """
        :param scaling:       Pixels per TikZ unit (1 cm = scaling px).
        :param canvas_height: Canvas height used for y-axis flip.
        """
        self.scaling = scaling
        self.canvas_height = canvas_height

        # ----- incremental parse cache -----
        # We hash the TikZ code; if the hash matches we return cached shapes.
        self._last_hash: str = ""
        self._cached_shapes: list = []

        # Legacy attributes kept so existing code that accesses them doesn't break
        self.tikz_scale = 1.0
        self.global_styles: dict = {}
        self.last_code: str = ""
        self.cached_shapes: list = []  # alias for _cached_shapes
        self.shape_lookup: dict = {}
        
        # Store parsed shapes for matching with newly drawn shapes
        self.last_parsed_shapes: list = []
        self.last_overlay_model: dict = {'nodes': [], 'scopes': []}

        # (line, column, message) for the constructs the last parse could not interpret.
        # Lines refer to the code as passed in (1-based). The grammar doesn't cover all of
        # valid TikZ, so these are "the overlay can't follow this", not LaTeX errors.
        self.last_errors: list[tuple[int, int, str]] = []
        self._pending_errors: list[tuple[int, int, str]] = []

        # Default style helpers (kept for backward compat with canvas.py)
        self.default_line_width = 1.0
        self.default_color = QColor(0, 0, 0)
        self.default_fill = QColor(255, 255, 255, 0)
        self.default_font = QFont("Arial", 12)

    # ------------------------------------------------------------------
    # Core parsing method
    # ------------------------------------------------------------------

    def parse(self, tikz_code: str, incremental: bool = False) -> list:
        """
        Parse TikZ code and return a list of shape dicts.

        :param tikz_code:   Full TikZ document or tikzpicture snippet.
        :param incremental: If True, return cached result when code is unchanged.
        :return:            List of shape dicts (see tikz_visitor.py for format).
        """
        # ---- Fast path: identical code ----
        code_hash = hashlib.md5(tikz_code.encode()).hexdigest()
        if incremental and code_hash == self._last_hash:
            return list(self._cached_shapes)

        # ---- Wrap bare content in tikzpicture if needed ----
        is_wrapped = r'\begin{tikzpicture}' not in tikz_code
        code_to_parse = self._ensure_tikzpicture(tikz_code)
        code_to_parse = self._sanitize_for_parser(code_to_parse)

        # ---- ANTLR4 lexer + parser ----
        try:
            shapes = self._antlr_parse(code_to_parse)

            # The wrapper adds a line at the top and bottom; report lines of the code the
            # user wrote (errors cascading onto the wrapper are attributed to the last line).
            line_offset = 1 if is_wrapped else 0
            user_lines = tikz_code.count("\n") + 1
            self.last_errors = [(min(max(1, line - line_offset), user_lines), col, msg)
                                for line, col, msg in self._pending_errors]

            # If wrapped, subtract the offset from all intervals to match the original unwrapped code
            if is_wrapped:
                offset = len(r'\begin{tikzpicture}') + 1 # +1 for the newline
                for shape in shapes:
                    if 'intervals' in shape:
                        new_intervals = []
                        for interval in shape['intervals']:
                            if interval:
                                new_intervals.append((interval[0] - offset, interval[1] - offset))
                            else:
                                new_intervals.append(None)
                        shape['intervals'] = new_intervals
        except Exception as exc:
            # If parsing completely fails (very malformed code), return cached
            logging.warning(f"tikz_parser.parse() failed: {exc}")
            shapes = list(self._cached_shapes)
            self.last_errors = [(1, 0, str(exc))]

        # ---- Update cache ----
        self._last_hash = code_hash
        self._cached_shapes = list(shapes)
        self.cached_shapes = self._cached_shapes  # keep legacy alias in sync
        self.last_code = tikz_code

        return list(shapes)

    def _ensure_tikzpicture(self, code: str) -> str:
        """
        If the code already contains \\begin{tikzpicture} leave it as-is.
        Otherwise wrap it so the parser always sees a complete environment.
        """
        if r'\begin{tikzpicture}' in code:
            return code
        return r'\begin{tikzpicture}' + '\n' + code + '\n' + r'\end{tikzpicture}'

    def _sanitize_for_parser(self, code: str) -> str:
        """
        Replace scope wrappers with whitespace of equal length so ANTLR can still
        parse the contained draw statements while character intervals remain valid.
        """
        scope_pattern = re.compile(r'\\begin\{scope\}(?:\[[^\]]*\])?|\\end\{scope\}')

        def repl(match):
            text = match.group(0)
            return ''.join('\n' if ch == '\n' else ' ' for ch in text)

        return scope_pattern.sub(repl, code)

    def _antlr_parse(self, code: str) -> list:
        """
        Run the ANTLR4 lexer + parser and extract shapes via the visitor.
        Returns a list of shape dicts.
        """
        # Build the ANTLR4 input stream from the TikZ source string
        input_stream = InputStream(code)

        # Lex
        lexer = TikzLexer(input_stream)
        lexer.removeErrorListeners()
        lex_err_listener = _SilentErrorListener()
        lexer.addErrorListener(lex_err_listener)

        token_stream = CommonTokenStream(lexer)

        # Parse
        parser = TikzParser(token_stream)
        parser.removeErrorListeners()
        err_listener = _SilentErrorListener()
        parser.addErrorListener(err_listener)

        # Build parse tree — entry rule is  document
        tree = parser.document()

        # Walk tree with visitor
        visitor = TikzVisitor(
            scaling=self.scaling,
            canvas_height=self.canvas_height
        )
        visitor.visit(tree)

        # Propagate tikz_scale so callers can read it
        self.tikz_scale = visitor.tikz_scale

        # Lexer and parser errors, in source order
        self._pending_errors = sorted(lex_err_listener.details + err_listener.details)

        return visitor.shapes

    # ------------------------------------------------------------------
    # Incremental parsing (lightweight: just hash comparison)
    # ------------------------------------------------------------------

    def _incremental_parse(self, tikz_code: str) -> list:
        """Thin wrapper kept for API compatibility."""
        return self.parse(tikz_code, incremental=True)

    def invalidate_cache(self):
        """Force a full re-parse on the next call by clearing the hash cache."""
        self._last_hash = ""
        self._cached_shapes = []
        self.cached_shapes = []
        self.last_code = ""
        self.shape_lookup = {}
        self.last_overlay_model = {'nodes': [], 'scopes': []}
        self.last_errors = []

    # ------------------------------------------------------------------
    # Canvas-shape conversion
    # ------------------------------------------------------------------

    def parse_to_canvas_shapes(self, tikz_code: str,
                                incremental: bool = True) -> list:
        """
        Parse TikZ code and convert the shape dicts into the flat list format
        expected by drawing_canvas  ([p1, p2, "rectangle"], etc.).

        This is the method called by main.py's parse_tikz_and_update_canvas().
        """
        try:
            parsed_shapes = self.parse(tikz_code, incremental=incremental)
            # Store the parsed shapes for later matching with newly drawn shapes
            self.last_parsed_shapes = self._shapes_to_canvas(parsed_shapes)
            self.last_overlay_model = self.build_overlay_model(tikz_code, self.last_parsed_shapes)
            return self.last_parsed_shapes
        except Exception as exc:
            logging.error(f"parse_to_canvas_shapes failed: {exc}")
            self.last_overlay_model = {'nodes': [], 'scopes': []}
            return []

    def build_overlay_model(self, tikz_code: str, canvas_shapes: list) -> dict:
        """Build an overlay model from parsed coordinate intervals and scope ranges."""
        nodes: list[OverlayNode] = []
        seen_intervals: set[tuple[int, int]] = set()

        for shape_index, shape in enumerate(canvas_shapes):
            intervals = getattr(shape, 'intervals', [])
            if not intervals:
                continue
            
            point_indexes = self._overlay_point_indexes(shape, intervals)
            for interval_index, point_index in enumerate(point_indexes):
                if interval_index >= len(intervals):
                    break
                interval = intervals[interval_index]
                if not interval or interval in seen_intervals:
                    continue
                if point_index >= len(shape) - 1:
                    continue

                point = shape[point_index]
                if point is None:
                    continue

                seen_intervals.add(interval)
                nodes.append(
                    OverlayNode(
                        interval=interval,
                        point=QPointF(point.x(), point.y()),
                        shape_index=shape_index,
                        point_index=point_index,
                    )
                )

        scopes = self._extract_scope_ranges(tikz_code)
        for node in nodes:
            node.scope_ids = [
                scope.id for scope in scopes
                if scope.start <= node.interval[0] and node.interval[1] <= scope.end
            ]

        scope_lookup = {scope.id: scope for scope in scopes}
        for scope in scopes:
            containing_parents = [
                parent for parent in scopes
                if parent.id != scope.id and parent.start <= scope.start and scope.end <= parent.end
            ]
            if containing_parents:
                parent = min(containing_parents, key=lambda item: item.end - item.start)
                scope.parent_id = parent.id
                parent.child_scope_ids.append(scope.id)

        for node in nodes:
            if not node.scope_ids:
                continue
            target_scope_id = max(
                node.scope_ids,
                key=lambda scope_id: scope_lookup[scope_id].start
            )
            scope_lookup[target_scope_id].node_intervals.append(node.interval)

        node_lookup = {node.interval: node for node in nodes}
        for scope in sorted(scopes, key=lambda item: item.end - item.start):
            points = self._scope_points(scope, scope_lookup, node_lookup)
            if not points:
                continue

            min_x = min(point.x() for point in points) - 12
            max_x = max(point.x() for point in points) + 12
            min_y = min(point.y() for point in points) - 12
            max_y = max(point.y() for point in points) + 12
            scope.rect = (min_x, min_y, max_x, max_y)

        return {'nodes': nodes, 'scopes': scopes}

    def _overlay_point_indexes(self, shape: list, intervals: list = None) -> list[int]:
        """Map interval order to point indexes in the canvas shape representation."""
        shape_type = shape[-1]
        if shape_type == "arc":
            if intervals and len(intervals) >= 3:
                # If we appended typed_center_pt, shape is [center, start, end, typed_center, "arc"]
                if len(shape) >= 5:
                    return [3, 1]
                return [0, 1]
            return [1]
        if shape_type == "node":
            return [0]
        return list(range(max(0, len(shape) - 1)))

    def _extract_scope_ranges(self, tikz_code: str) -> list[OverlayScope]:
        """Find nested \\begin{scope}...\\end{scope} blocks by source offsets."""
        token_pattern = re.compile(r'\\begin\{scope\}(?:\[[^\]]*\])?|\\end\{scope\}')
        stack: list[tuple[int, int]] = []
        scopes: list[OverlayScope] = []

        for match in token_pattern.finditer(tikz_code):
            token_text = match.group(0)
            if token_text.startswith(r'\begin{scope}'):
                stack.append((match.start(), match.end()))
            elif stack:
                start, content_start = stack.pop()
                scopes.append(
                    OverlayScope(
                        id=len(scopes),
                        start=content_start,
                        end=match.start() - 1,
                    )
                )

        scopes.sort(key=lambda scope: (scope.start, -(scope.end - scope.start)))
        for index, scope in enumerate(scopes):
            scope.id = index
        return scopes

    def _scope_points(
        self,
        scope: OverlayScope,
        scope_lookup: dict[int, OverlayScope],
        node_lookup: dict[tuple[int, int], OverlayNode]
    ) -> list[QPoint]:
        points: list[QPoint] = []
        for interval in scope.node_intervals:
            node = node_lookup.get(interval)
            if node is not None:
                points.append(node.point)
        for child_scope_id in scope.child_scope_ids:
            child_scope = scope_lookup[child_scope_id]
            if child_scope.rect:
                x1, y1, x2, y2 = child_scope.rect
                points.extend([QPoint(int(x1), int(y1)), QPoint(int(x2), int(y2))])
        return points

    def _shapes_to_canvas(self, shapes: list) -> list:
        """
        Convert list of shape dicts → flat canvas list.
        Convert all QPointF to QPoint to prevent TypeError in canvas.py during drag/edit.
        """
        canvas_shapes = []
        for shape in shapes:
            t = shape.get('type')
            pts = shape.get('points', [])
            intervals = shape.get('intervals', [])
            cmd_interval = shape.get('cmd_interval')
            
            # Use QPointF to keep exact floating point precision from AST
            from PyQt6.QtCore import QPointF
            int_pts = [QPointF(p.x(), p.y()) for p in pts]

            if t == 'rectangle' and len(int_pts) >= 2:
                canvas_shapes.append(CanvasShapeList([int_pts[0], int_pts[1], "rectangle"], intervals, cmd_interval=cmd_interval))

            elif t == 'circle' and len(int_pts) >= 2:
                canvas_shapes.append(CanvasShapeList([int_pts[0], int_pts[1], "circle"], intervals, cmd_interval=cmd_interval))

            elif t == 'ellipse' and len(int_pts) >= 1:
                rx = shape.get('rx', 0)
                ry = shape.get('ry', 0)
                # Compute the radius point from the original float point to keep precision, then convert
                radius_pt_f = QPointF(pts[0].x() + rx, pts[0].y() + ry)
                radius_pt = radius_pt_f
                canvas_shapes.append(CanvasShapeList([int_pts[0], radius_pt, "ellipse"], intervals, cmd_interval=cmd_interval))

            elif t == 'arc' and len(int_pts) >= 3:
                # Order for canvas: [center, start, end, typed_center, "arc"]
                entry = list(int_pts) + ["arc"]
                
                csl = CanvasShapeList(entry, intervals, cmd_interval=cmd_interval)
                csl.is_relative = shape.get('is_relative', False)
                canvas_shapes.append(csl)

            elif t in ('path', 'line', 'parabola') and len(int_pts) >= 2:
                # Standardize to "path" for canvas logic
                entry = list(int_pts) + ["path"]
                canvas_shapes.append(CanvasShapeList(entry, intervals, cmd_interval=cmd_interval))

            elif t == 'smooth_curve' and len(int_pts) >= 2:
                entry = list(int_pts) + ["smooth_curve"]
                canvas_shapes.append(CanvasShapeList(entry, intervals, cmd_interval=cmd_interval))

            elif t == 'bezier' and len(int_pts) >= 4:
                # Represent bezier as a path for now
                entry = [int_pts[0], int_pts[3]] + ["path"]
                canvas_shapes.append(CanvasShapeList(entry, intervals, cmd_interval=cmd_interval))

            elif t == 'grid' and len(int_pts) >= 2:
                # Grids are currently drawn like rectangles
                canvas_shapes.append(CanvasShapeList([int_pts[0], int_pts[1], "rectangle"], intervals, cmd_interval=cmd_interval))

            elif t == 'arrow_path' and len(int_pts) >= 2:
                entry = list(int_pts) + ["arrow_path"]
                canvas_shapes.append(CanvasShapeList(entry, intervals, cmd_interval=cmd_interval))
                
            elif t == 'node' and len(int_pts) >= 1:
                # Nodes are represented by their center point
                # Canvas expected format: [center, center, "node"]
                entry = [int_pts[0], int_pts[0], "node"]
                canvas_shapes.append(CanvasShapeList(entry, intervals, cmd_interval=cmd_interval))

        return canvas_shapes
    def update_code(self, old_code: str, canvas_shapes: list, scale_factor: float = 1.0, deleted_cmd_intervals: list = None) -> str:
        """
        Updates the original TikZ code by replacing modified coordinates in-place 
        using AST character intervals, preserving all options and formatting.
        New shapes drawn by the user are appended before \\end{tikzpicture}.
        """
        import math
        replacements = []
        new_commands = []
        
        if deleted_cmd_intervals is None:
            deleted_cmd_intervals = []
            
        for start, stop in deleted_cmd_intervals:
            if stop + 1 < len(old_code) and old_code[stop + 1] == '\n':
                replacements.append((start, stop + 1, ""))
            else:
                replacements.append((start, stop, ""))
        
        # Effective scaling factor accounts for both TikZ [scale=] and base scaling.
        # scale_factor (zoom) is NOT used here because canvas points are already unscaled.
        eff_scale = self.scaling * self.tikz_scale

        def _fmt(val: float) -> str:
            """Format number up to 4 decimal places, stripping trailing zeros for cleaner code."""
            s = f"{val:.4f}"
            if '.' in s:
                s = s.rstrip('0').rstrip('.')
            return s

        def _format_replacement(start: int, stop: int, text: str) -> str:
            """Preserve outer parentheses around intervals when the original AST text had them."""
            if 0 <= start < len(old_code) and 0 <= stop < len(old_code):
                if old_code[start] == '(' and old_code[stop] == ')' and not (text.startswith('(') and text.endswith(')')):
                    return f'({text})'
            return text
        
        for shape in canvas_shapes:
            shape_type = shape[-1]
            
            # If the shape has intervals, it was parsed from the AST and can be updated in-place
            intervals = getattr(shape, 'intervals', [])
            if intervals:
                points = shape[:-1]

                if shape_type == "rectangle" and len(intervals) >= 2:
                    for i in range(2):
                        if i < len(points) and intervals[i]:
                            start, stop = intervals[i]
                            p_x = _fmt(points[i].x() / eff_scale)
                            p_y = _fmt(-points[i].y() / eff_scale)
                            replacements.append((start, stop, f"({p_x}, {p_y})"))

                elif shape_type == "circle" and len(intervals) >= 2:
                    # intervals[0] is center coord, intervals[1] is radius number
                    if intervals[0]:
                        c_x = _fmt(points[0].x() / eff_scale)
                        c_y = _fmt(-points[0].y() / eff_scale)
                        replacements.append((intervals[0][0], intervals[0][1], f"({c_x}, {c_y})"))
                    if intervals[1]:
                        # Recompute radius from center and edge point
                        p1_x, p1_y = points[0].x() / eff_scale, points[0].y() / eff_scale
                        p2_x, p2_y = points[1].x() / eff_scale, points[1].y() / eff_scale
                        radius = _fmt(math.hypot(p1_x - p2_x, p1_y - p2_y))
                        replacements.append((intervals[1][0], intervals[1][1], _format_replacement(intervals[1][0], intervals[1][1], f"{radius}")))

                elif shape_type == "ellipse" and len(intervals) >= 2:
                    # intervals[0] is center, intervals[1] is (rx and ry) numberunit block
                    if intervals[0]:
                        c_x = _fmt(points[0].x() / eff_scale)
                        c_y = _fmt(-points[0].y() / eff_scale)
                        replacements.append((intervals[0][0], intervals[0][1], f"({c_x}, {c_y})"))
                    if intervals[1]:
                        p1_x, p1_y = points[0].x() / eff_scale, points[0].y() / eff_scale
                        p2_x, p2_y = points[1].x() / eff_scale, points[1].y() / eff_scale
                        rx = _fmt(abs(p2_x - p1_x))
                        ry = _fmt(abs(p2_y - p1_y))
                        replacements.append((intervals[1][0], intervals[1][1], _format_replacement(intervals[1][0], intervals[1][1], f"{rx} and {ry}")))

                elif shape_type in ("path", "smooth_curve", "arrow_path", "node"):
                    # For paths and nodes, we have intervals for each coordinate/point
                    for i in range(min(len(intervals), len(points))):
                        if intervals[i]:
                            start, stop = intervals[i]
                            p_x = _fmt(points[i].x() / eff_scale)
                            p_y = _fmt(-points[i].y() / eff_scale)
                            replacements.append((start, stop, f"({p_x}, {p_y})"))

                elif shape_type == "arc" and len(intervals) >= 2:
                    # Canvas shapes: [center, start, end, "arc"]
                    c_x = points[0].x() / eff_scale
                    c_y = points[0].y() / eff_scale
                    s_x = points[1].x() / eff_scale
                    s_y = points[1].y() / eff_scale
                    e_x = points[2].x() / eff_scale
                    e_y = points[2].y() / eff_scale
                    
                    is_relative = getattr(shape, 'is_relative', False)
                    
                    # Determine intervals
                    if is_relative or len(intervals) >= 3:
                        c_int, s_int, a_int = intervals[0], intervals[1], intervals[2]
                    else:
                        c_int = None
                        s_int, a_int = intervals[0], intervals[1]
                        
                    # If the user provided a center, we always auto-format the start point as polar (++(angle:radius)) 
                    # so that it is editable in the polar grid just like the end point.
                    if c_int or is_relative:
                        if c_int:
                            # Use typed_center_pt (shape[3]) if available, else mathematical center (shape[0])
                            if len(points) >= 5:
                                c_x_c = points[3].x() / eff_scale
                                c_y_c = points[3].y() / eff_scale
                            else:
                                c_x_c, c_y_c = c_x, c_y
                            c_x_fmt = _fmt(c_x_c)
                            c_y_fmt = _fmt(-c_y_c)
                            replacements.append((c_int[0], c_int[1], f"({c_x_fmt}, {c_y_fmt})"))
                        
                        c_x_u, c_y_u = c_x, -c_y
                        s_x_u, s_y_u = s_x, -s_y
                        e_x_u, e_y_u = e_x, -e_y
                        
                        radius = _fmt(math.hypot(s_x_u - c_x_u, s_y_u - c_y_u))
                        start_angle = _fmt(math.degrees(math.atan2(s_y_u - c_y_u, s_x_u - c_x_u)))
                        end_angle = _fmt(math.degrees(math.atan2(e_y_u - c_y_u, e_x_u - c_x_u)))
                        
                        if s_int:
                            replacements.append((s_int[0], s_int[1], f"++({start_angle}:{radius})"))
                        if a_int:
                            replacements.append((a_int[0], a_int[1], f"arc ({start_angle}:{end_angle}:{radius})"))
                    else:
                        if s_int:
                            s_x_fmt = _fmt(s_x)
                            s_y_fmt = _fmt(-s_y)
                            replacements.append((s_int[0], s_int[1], f"({s_x_fmt}, {s_y_fmt})"))
                        
                        if a_int:
                            c_x_u, c_y_u = c_x, -c_y
                            s_x_u, s_y_u = s_x, -s_y
                            e_x_u, e_y_u = e_x, -e_y
                            
                            radius = _fmt(math.hypot(s_x_u - c_x_u, s_y_u - c_y_u))
                            start_angle = _fmt(math.degrees(math.atan2(s_y_u - c_y_u, s_x_u - c_x_u)))
                            end_angle = _fmt(math.degrees(math.atan2(e_y_u - c_y_u, e_x_u - c_x_u)))
                            
                            replacements.append((a_int[0], a_int[1], f"arc ({start_angle}:{end_angle}:{radius})"))

            else:
                # This is a brand new shape drawn on the canvas, missing AST metadata
                if shape_type == "rectangle":
                    p1_x, p1_y = _fmt(shape[0].x() / eff_scale), _fmt(-shape[0].y() / eff_scale)
                    p2_x, p2_y = _fmt(shape[1].x() / eff_scale), _fmt(-shape[1].y() / eff_scale)
                    new_commands.append(f"\\draw ({p1_x},{p1_y}) rectangle ({p2_x},{p2_y});\n")
                elif shape_type == "circle":
                    c_x, c_y = _fmt(shape[0].x() / eff_scale), _fmt(-shape[0].y() / eff_scale)
                    p1_x, p1_y = shape[1].x() / eff_scale, shape[1].y() / eff_scale
                    radius = _fmt(math.hypot(shape[0].x() / eff_scale - p1_x, shape[0].y() / eff_scale - p1_y))
                    new_commands.append(f"\\draw ({c_x},{c_y}) circle ({radius});\n")
                elif shape_type == "ellipse":
                    p1_x, p1_y = _fmt(shape[0].x() / eff_scale), _fmt(-shape[0].y() / eff_scale)
                    p2_x, p2_y = shape[1].x() / eff_scale, shape[1].y() / eff_scale
                    rx, ry = _fmt(abs(p2_x - shape[0].x() / eff_scale)), _fmt(abs(p2_y - shape[0].y() / eff_scale))
                    new_commands.append(f"\\draw ({p1_x},{p1_y}) ellipse ({rx} and {ry});\n")
                elif shape_type == "path":
                    pts = [f"({_fmt(p.x()/eff_scale)},{_fmt(-p.y()/eff_scale)})" for p in shape[:-1]]
                    cmd = r"\draw " + " -- ".join(pts) + ";\n"
                    new_commands.append(cmd)
                elif shape_type == "smooth_curve":
                    pts = [f"({_fmt(p.x()/eff_scale)},{_fmt(-p.y()/eff_scale)})" for p in shape[:-1]]
                    cmd = r"\draw plot[smooth, tension=.7] coordinates {" + " ".join(pts) + "};\n"
                    new_commands.append(cmd)
                elif shape_type == "arc":
                    c_x_u = shape[0].x() / eff_scale
                    c_y_u = -shape[0].y() / eff_scale
                    s_x_u = shape[1].x() / eff_scale
                    s_y_u = -shape[1].y() / eff_scale
                    e_x_u = shape[2].x() / eff_scale
                    e_y_u = -shape[2].y() / eff_scale
                    radius = _fmt(math.hypot(s_x_u - c_x_u, s_y_u - c_y_u))
                    start_angle = _fmt(math.degrees(math.atan2(s_y_u - c_y_u, s_x_u - c_x_u)))
                    end_angle = _fmt(math.degrees(math.atan2(e_y_u - c_y_u, e_x_u - c_x_u)))
                    c_x, c_y = _fmt(c_x_u), _fmt(c_y_u)
                    new_commands.append(f"\\draw ({c_x}, {c_y}) ++({start_angle}:{radius}) arc ({start_angle}:{end_angle}:{radius});\n")

        # Filter out replacements that fall completely within another replacement
        # (e.g. modifying a coordinate inside a command that is being deleted).
        # We only consider it "inside" if it is STRICTLY smaller in at least one dimension,
        # so identical intervals don't mutually destruct.
        valid_replacements = []
        for r in replacements:
            start, stop, text = r
            is_inside = False
            for other_r in replacements:
                if r is other_r:
                    continue
                ostart, ostop, _ = other_r
                if ostart <= start and ostop >= stop and (ostart != start or ostop != stop):
                    is_inside = True
                    break
            if not is_inside:
                valid_replacements.append(r)

        # Sort replacements: right-to-left (by start descending).
        # For tied starts, prioritize actual changes to the text over no-ops.
        # This handles cases where multiple shapes (e.g. arc and path) share intervals,
        # and one was modified while the other was not.
        valid_replacements.sort(key=lambda x: (x[0], 1 if old_code[x[0]:x[1]+1] != x[2] else 0), reverse=True)

        new_code = old_code
        applied_starts = set()
        for start, stop, text in valid_replacements:
            if start in applied_starts:
                continue
            applied_starts.add(start)
            new_code = new_code[:start] + text + new_code[stop + 1:]
            
        # Append new commands before \end{tikzpicture}
        if new_commands:
            end_tag = r"\end{tikzpicture}"
            idx = new_code.rfind(end_tag)
            if idx != -1:
                new_code = new_code[:idx] + "".join(new_commands) + new_code[idx:]
            else:
                new_code += "\n".join(new_commands)
                
        return new_code

    def match_intervals_for_drawn_shapes(self, canvas_shapes: list, parsed_shapes: list, newly_drawn_indices: set = None) -> list:
        """
        Match newly drawn shapes (without intervals) with existing parsed shapes.
        Copies intervals from parsed shapes to canvas shapes where they match.
        This ensures updates go to existing code instead of appending new commands.
        
        Matching is done by proximity: for each newly drawn shape, find the
        closest parsed shape of the same type and copy its intervals.
        
        :param canvas_shapes: List of shapes from the canvas
        :param parsed_shapes: List of shapes parsed from the current TikZ code
        :param newly_drawn_indices: Set of indices in canvas_shapes that are newly drawn
        """
        if newly_drawn_indices is None:
            newly_drawn_indices = set()
        
        # Create a mapping of shape type to list of parsed shapes with their intervals
        parsed_by_type = {}
        for shape in parsed_shapes:
            shape_type = shape[-1]
            if shape_type not in parsed_by_type:
                parsed_by_type[shape_type] = []
            parsed_by_type[shape_type].append(shape)
        
        # Only match shapes that are marked as newly drawn
        for i in newly_drawn_indices:
            if i >= len(canvas_shapes):
                continue
                
            canvas_shape = canvas_shapes[i]
            intervals = getattr(canvas_shape, 'intervals', [])
            
            # Skip if this shape already has intervals
            if intervals:
                continue
            
            shape_type = canvas_shape[-1]
            
            # Try to find the closest matching shape of the same type by proximity
            if shape_type in parsed_by_type and parsed_by_type[shape_type]:
                # Get the center/first point of the drawn shape
                drawn_center = canvas_shape[0] if canvas_shape else None
                
                best_match = None
                best_distance = float('inf')
                
                # Find the parsed shape with the same type that is closest to this drawn shape
                for parsed_shape in parsed_by_type[shape_type]:
                    parsed_center = parsed_shape[0] if parsed_shape else None
                    
                    if drawn_center and parsed_center:
                        # Calculate distance between centers
                        dx = drawn_center.x() - parsed_center.x()
                        dy = drawn_center.y() - parsed_center.y()
                        distance = (dx * dx + dy * dy) ** 0.5
                        
                        # Keep track of the closest match
                        if distance < best_distance:
                            best_distance = distance
                            best_match = parsed_shape
                
                # If we found a reasonably close match, copy its intervals
                if best_match is not None:
                    parsed_intervals = getattr(best_match, 'intervals', [])
                    if parsed_intervals:
                        # Copy intervals from parsed shape to canvas shape
                        canvas_shape_list = list(canvas_shape)  # Convert to regular list if needed
                        cmd_interval = getattr(best_match, 'cmd_interval', None)
                        
                        # Create a CanvasShapeList with intervals
                        new_canvas_shape = CanvasShapeList(canvas_shape_list, parsed_intervals, cmd_interval=cmd_interval)
                        canvas_shapes[i] = new_canvas_shape
                        
                        # Remove this parsed shape from consideration (mark as used)
                        parsed_by_type[shape_type].remove(best_match)
        
        return canvas_shapes

    # ------------------------------------------------------------------
    # Legacy helper methods kept for any code that imported them directly
    # ------------------------------------------------------------------

    def parse_style(self, style_str: str) -> dict:
        """Delegate to a temporary visitor for style parsing."""
        v = TikzVisitor(self.scaling, self.canvas_height)
        return v.parse_style(style_str)

    def parse_color(self, color_str: str) -> QColor:
        v = TikzVisitor(self.scaling, self.canvas_height)
        return v._parse_color(color_str)

    def to_coordinates(self, x, y, as_float: bool = False):
        """Legacy coordinate conversion kept for canvas.py compatibility."""
        cx = float(x) * self.tikz_scale * self.scaling
        cy = -float(y) * self.tikz_scale * self.scaling
        if as_float:
            return QPointF(cx, cy)
        return QPoint(round(cx), round(cy))
