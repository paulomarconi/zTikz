# =============================================================================
# tikz_visitor.py — ANTLR4 Visitor for the TikZ parse tree
#
# This module implements the shape-extraction visitor that walks the parse
# tree produced by TikzParser.py (generated from TikzParser.g4 + TikzLexer.g4).
#
# Architecture:#   - TikzVisitor extends TikzParserVisitor (auto-generated).
#   - visit* methods correspond to parser rule contexts.
#   - Each method extracts coordinates, styles, and shape types, then appends
#     a shape-dict to self.shapes.
#   - The final self.shapes list is consumed by tikz_parser.py (parser.py).
#
# Shape dict format (same as the old regex-based parser):
#   {
#       'type'  : str,           # 'rectangle', 'circle', 'ellipse', 'arc',
#                                #   'line', 'path', 'node', 'bezier',
#                                #   'polygon', 'grid', 'parabola'
#       'points': [QPointF, ...],
#       'style' : dict,          # output of parse_style()
#       # extra keys depending on type:
#       'rx', 'ry'               # ellipse radii (canvas pixels)
#       'start_angle', 'end_angle', 'radius'   # arc parameters
#       'text'                   # node label string
#   }
# =============================================================================

import math
import re

from PyQt6.QtCore import QPointF, QPoint
from PyQt6.QtGui import QColor, QFont

# Generated ANTLR4 classes

from zTikz.antlr.TikzParser import TikzParser
from zTikz.antlr.TikzParserVisitor import TikzParserVisitor


class TikzVisitor(TikzParserVisitor):
    """
    Walks the ANTLR4 parse tree produced by TikzParser and collects all
    drawable shapes into self.shapes.

    Usage:
        visitor = TikzVisitor(scaling=10, canvas_height=800)
        visitor.visit(parse_tree)
        shapes = visitor.shapes   # list of shape dicts
    """

    # ------------------------------------------------------------------
    # Construction & configuration
    # ------------------------------------------------------------------

    def __init__(self, scaling: float = 10.0, canvas_height: float = 800.0):
        """
        :param scaling:       Pixels per TikZ unit (default 10 → 1cm = 10px).
        :param canvas_height: Canvas height in pixels (used for y-flip).
        """
        super().__init__()

        self.scaling = scaling
        self.canvas_height = canvas_height
        self.tikz_scale = 1.0    # updated when [scale=…] is found in tikzpicture opts
        self.global_styles: dict = {}

        # Accumulated list of shape dicts — filled during tree walk
        self.shapes: list = []
        self.named_nodes: dict[str, QPointF] = {}

        # Default style values (same as old regex parser for consistency)
        self.default_line_width = 1.0
        self.default_color = QColor(0, 0, 0)          # black
        self.default_fill = QColor(255, 255, 255, 0)  # transparent
        self.default_font = QFont("Arial", 12)

        # Running "current path": accumulates coordinates connected by --
        # This is reset each time a path_cmd starts.
        self._current_path_points: list = []
        self._current_style: dict = {}

    # ------------------------------------------------------------------
    # Coordinate conversion  (TikZ → canvas pixels)
    # Convert mathematical coordinate to canvas pixels
    # ------------------------------------------------------------------

    def _to_canvas(self, x: float, y: float) -> QPointF:
        """
        Convert a TikZ coordinate (x, y) to a canvas QPointF.
        TikZ y-axis points up; canvas y-axis points down → negate y.
        """
        cx = float(x) * self.tikz_scale * self.scaling
        cy = -float(y) * self.tikz_scale * self.scaling
        return QPointF(cx, cy)

    def _to_canvas_pt(self, x: float, y: float) -> QPoint:
        """Integer version of _to_canvas (for shapes that need QPoint)."""
        p = self._to_canvas(x, y)
        return QPoint(int(p.x()), int(p.y()))


    # ------------------------------------------------------------------
    # Number-with-unit extraction
    # ------------------------------------------------------------------

    def _get_number(self, ctx) -> float:
        """
        Extract a plain float from a numberunit context.
        Ignores the unit (cm, pt, etc.) — TikZ default unit is cm.
        """
        if ctx is None:
            return 0.0
        try:
            return float(ctx.NUMBER().getText())
        except Exception:
            return 0.0

    # ------------------------------------------------------------------
    # Parse inline style options
    # ------------------------------------------------------------------

    def _parse_options_ctx(self, ctx) -> dict:
        """
        Parse a tikz_options context into a style dict.
        Delegates to self.parse_style() after reconstructing the string.
        """
        if ctx is None:
            return self._default_style()
        raw = self._options_to_string(ctx)
        return self.parse_style(raw)

    def _options_to_string(self, ctx) -> str:
        """
        Reconstruct the raw option string from an option context tree.
        e.g. [draw=red, line width=2pt]  →  "draw=red, line width=2pt"
        """
        if ctx is None:
            return ""
        parts = []
        if ctx.option_list():
            for item in ctx.option_list().option_item():
                key_text = self._atom_text(item.option_atom(0)) if item.option_atom() else ""
                if len(item.option_atom()) > 1:
                    val_text = self._atom_text(item.option_atom(1))
                    parts.append(f"{key_text}={val_text}")
                else:
                    parts.append(key_text)
        return ", ".join(parts)

    def _atom_text(self, ctx) -> str:
        """Return raw text of an option_atom."""
        if ctx is None:
            return ""
        return ctx.getText()

    def _default_style(self) -> dict:
        return {
            'line_width': self.default_line_width,
            'line_color': self.default_color,
            'fill_color': self.default_fill,
            'font': self.default_font,
            'dashed': False,
            'dotted': False,
            'arrow': False,
            'align': 'left',
            'midway': False,
        }

    def parse_style(self, style_str: str) -> dict:
        """
        Parse TikZ style options string into a style dict.
        Kept identical to the old regex-based parser for compatibility.
        """
        style = self._default_style()
        if not style_str:
            return style

        style_str = style_str.strip().strip('[]')

        # Split on commas, respecting nested braces/brackets
        options = []
        for opt in style_str.split(','):
            opt = opt.strip()
            if not opt:
                continue
            if '=' in opt:
                key, value = opt.split('=', 1)
                options.append((key.strip(), value.strip()))
            else:
                options.append((opt.strip(), 'true'))

        for key, value in options:
            if key == 'midway':
                style['midway'] = True
            elif key == 'align':
                style['align'] = value
            elif key == 'line width':
                style['line_width'] = float(value.replace('pt', '').replace('cm', ''))
            elif key == 'draw':
                style['line_color'] = self._parse_color(value)
            elif key == 'fill':
                style['fill_color'] = self._parse_color(value)
            elif key == 'dashed':
                style['dashed'] = True
            elif key == 'dotted':
                style['dotted'] = True
            elif key == 'font':
                style['font'] = self._parse_font(value)
            elif key in ('->', 'latex', '-latex'):
                style['arrow'] = True
            elif key == 'scale':
                try:
                    self.tikz_scale = float(value)
                except Exception:
                    pass
        return style

    def _parse_color(self, color_str: str) -> QColor:
        """Map TikZ color names / rgb(...) to QColor."""
        color_map = {
            'red':     QColor(255, 0, 0),
            'green':   QColor(0, 200, 0),
            'blue':    QColor(0, 0, 255),
            'yellow':  QColor(255, 255, 0),
            'cyan':    QColor(0, 255, 255),
            'magenta': QColor(255, 0, 255),
            'black':   QColor(0, 0, 0),
            'white':   QColor(255, 255, 255),
            'gray':    QColor(128, 128, 128),
            'orange':  QColor(255, 165, 0),
            'violet':  QColor(238, 130, 238),
            'brown':   QColor(165, 42, 42),
            'teal':    QColor(0, 128, 128),
            'olive':   QColor(128, 128, 0),
        }
        cs = color_str.strip().lower()
        if cs in color_map:
            return color_map[cs]
        rgb = re.match(r'rgb\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)', cs)
        if rgb:
            r, g, b = [int(float(v) * 255) for v in rgb.groups()]
            return QColor(r, g, b)
        op = re.match(r'([a-z]+)!(\d+)', cs)
        if op and op.group(1) in color_map:
            c = QColor(color_map[op.group(1)])
            c.setAlpha(int(op.group(2)) * 255 // 100)
            return c
        return QColor(0, 0, 0)

    def _parse_font(self, font_str: str) -> QFont:
        """Map TikZ font size commands to QFont."""
        font = QFont(self.default_font)
        size_map = {
            '\\tiny': 8, '\\scriptsize': 9, '\\footnotesize': 10,
            '\\small': 11, '\\normalsize': 12, '\\large': 14,
            '\\Large': 17, '\\LARGE': 20, '\\huge': 24, '\\Huge': 28
        }
        for cmd, sz in size_map.items():
            if cmd in font_str:
                font.setPointSize(sz)
                break
        if 'bold' in font_str.lower():
            font.setBold(True)
        if 'italic' in font_str.lower():
            font.setItalic(True)
        return font

    # ------------------------------------------------------------------
    # Node text extraction
    # ------------------------------------------------------------------

    def _brace_text_content(self, ctx) -> str:
        """
        Recursively collect raw text from a brace_text context.
        e.g. {Hello $x^2$} → "Hello $x^2$"
        """
        if ctx is None:
            return ""
        parts = []
        for item in ctx.brace_item():
            if item.BRACE_CONTENT():
                parts.append(item.BRACE_CONTENT().getText())
            elif item.BRACE_LBRACE():
                # Nested braces — recurse (only one child brace_text here)
                inner = item  # brace_item contains BRACE_LBRACE brace_item* BRACE_RBRACE
                inner_parts = []
                for sub in inner.brace_item():
                    inner_parts.append(self._collect_brace_item(sub))
                parts.append("{" + "".join(inner_parts) + "}")
        return "".join(parts)

    def _collect_brace_item(self, ctx) -> str:
        if ctx.BRACE_CONTENT():
            return ctx.BRACE_CONTENT().getText()
        inner_parts = []
        for sub in ctx.brace_item():
            inner_parts.append(self._collect_brace_item(sub))
        return "{" + "".join(inner_parts) + "}"

    # ------------------------------------------------------------------
    # Coordinate context helpers
    # ------------------------------------------------------------------

    def _get_coord(self, ctx, last_coord: QPointF | None = None) -> QPointF | None:
        """
        Extract a QPointF from a coordinate context.
        Returns None if the coordinate is a node name (not numeric).
        """
        if ctx is None:
            return None
        cv = ctx.coord_value()
        if cv is None:
            return None
            
        is_relative = ctx.PLUS() is not None and len(ctx.PLUS()) > 0
        
        # Numeric coordinate
        nums = cv.numberunit()
        if nums and len(nums) == 2:
            if cv.COLON():
                angle = self._get_number(nums[0])
                radius = self._get_number(nums[1])
                rad = math.radians(angle)
                x = radius * math.cos(rad)
                y = radius * math.sin(rad)
            else:
                x = self._get_number(nums[0])
                y = self._get_number(nums[1])
                
            if is_relative and last_coord is not None:
                dx = x * self.tikz_scale * self.scaling
                dy = -y * self.tikz_scale * self.scaling
                return QPointF(last_coord.x() + dx, last_coord.y() + dy)
            return self._to_canvas(x, y)
            
        if cv.ID():
            return self.named_nodes.get(cv.ID().getText())
        return None

    def _get_coord_interval(self, ctx) -> tuple[int, int] | None:
        """Get the (start, stop) character indices of an editable numeric coordinate."""
        if ctx is None:
            return None
        cv = ctx.coord_value()
        if cv is None or not cv.numberunit() or len(cv.numberunit()) != 2:
            return None
        return (ctx.start.start, ctx.stop.stop)

    def visitStandalone_node(self, ctx: TikzParser.Standalone_nodeContext):
        """
        Handle a standalone node command:  \node [opts] at (x,y) {text} ;
        """
        style = self._parse_options_ctx(
            ctx.tikz_options() if ctx.tikz_options() else None
        )

        # Position from  at (x,y)
        pt = None
        if ctx.coordinate():
            pt = self._get_coord(ctx.coordinate())

        text = ""
        if ctx.brace_text():
            text = self._brace_text_content(ctx.brace_text())

        if pt is not None:
            if ctx.node_name():
                self.named_nodes[ctx.node_name().ID().getText()] = pt
            self.shapes.append({
                'type':   'node',
                'points': [pt],
                'intervals': [self._get_coord_interval(ctx.coordinate())] if ctx.coordinate() else [],
                'text':   text,
                'style':  style,
                'cmd_interval': (ctx.start.start, ctx.stop.stop)
            })

    # ------------------------------------------------------------------
    # Document / picture level
    # ------------------------------------------------------------------

    def visitDocument(self, ctx: TikzParser.DocumentContext):
        """Entry point — visit all tikzpicture children."""
        return self.visitChildren(ctx)

    def visitTikzpicture(self, ctx: TikzParser.TikzpictureContext):
        """
        Visit the tikzpicture environment.
        Parse global options (scale, etc.) then visit the body.
        """
        # Parse global tikzpicture options (e.g. [scale=2])
        if ctx.tikz_options():
            style = self._parse_options_ctx(ctx.tikz_options())
            # tikz_scale is updated inside parse_style if 'scale' key is present

        # Visit the body
        if ctx.tikzbody():
            self.visitTikzbody(ctx.tikzbody())
        

    def visitTikzbody(self, ctx: TikzParser.TikzbodyContext):
        """Visit each statement in the body."""
        return self.visitChildren(ctx)

    def visitTikz_stmt(self, ctx: TikzParser.Tikz_stmtContext):
        return self.visitChildren(ctx)

    # ------------------------------------------------------------------
    # PATH COMMAND  (\draw, \fill, \path, \node, …)
    # ------------------------------------------------------------------

    def visitPath_cmd(self, ctx: TikzParser.Path_cmdContext):
        """
        Process a full path command.

        Strategy:
          1. Parse the inline options (line width, color, fill, arrow, …).
          2. Walk path_elements, collecting:
               - coordinates  → path points
               - shape_spec   → emit shape immediately
               - arc_spec     → emit arc
               - control_spec → emit bezier
               - node_inline  → emit node
               - edge_op      → just a connector, no shape emitted
        """
        num_shapes_before = len(self.shapes)
        # ---- 1. Style from the options block right after the path start ----
        opt_ctx = None
        for child in ctx.children or []:
            if isinstance(child, TikzParser.Tikz_optionsContext):
                opt_ctx = child
                break
        style = self._parse_options_ctx(opt_ctx)

        # ---- 2. Walk path elements ----
        # We accumulate points for polylines; when we see a shape_spec we
        # emit the accumulated points (if any) plus the new shape.
        path_points: list[QPointF] = []
        path_intervals: list[tuple[int, int]] = []
        last_coord: QPointF | None = None
        last_interval: tuple[int, int] | None = None
        is_plot = False

        elements = ctx.path_element() or []
        i = 0
        while i < len(elements):
            elem = elements[i]

            # ---- coordinate ----
            if elem.coordinate():
                pt = self._get_coord(elem.coordinate(), last_coord)
                if pt is not None:
                    path_points.append(pt)
                    interval = self._get_coord_interval(elem.coordinate())
                    if interval: path_intervals.append(interval)
                    last_coord = pt
                    last_interval = interval

            # ---- shape_spec  (rectangle / circle / ellipse / grid / parabola) ----
            elif elem.shape_spec():
                ss = elem.shape_spec()
                self._emit_shape_spec(ss, last_coord, last_interval, style)

            # ---- arc ----
            elif elem.arc_spec():
                is_relative = False
                prev_elem = elements[i-1] if i > 0 else None
                if prev_elem and prev_elem.coordinate() and prev_elem.coordinate().PLUS():
                    is_relative = True
                
                center_interval = None
                typed_center_pt = None
                if is_relative and len(path_intervals) >= 2:
                    center_interval = path_intervals[-2]
                elif not is_relative and i >= 2 and elements[i-2].coordinate():
                    # If absolute arc is immediately preceded by two coordinates (e.g. `(c) (s) arc`),
                    # map the first coordinate as the intended center to allow auto-correction.
                    center_interval = self._get_coord_interval(elements[i-2].coordinate())
                    if len(path_points) >= 2:
                        typed_center_pt = path_points[-2]
                    
                self._emit_arc(elem.arc_spec(), last_coord, last_interval, is_relative, center_interval, typed_center_pt, style)

            # ---- bezier controls ----
            elif elem.control_spec():
                self._emit_control(elem.control_spec(), path_points, style) # TODO: bezier intervals

            # ---- inline node (node [opts] {text}) ----
            elif elem.node_inline():
                self._emit_node_inline(elem.node_inline(), last_coord, style)

            # ---- brace_text directly on path (label without 'node' keyword) ----
            elif elem.brace_text():
                text = self._brace_text_content(elem.brace_text())
                if is_plot:
                    import re
                    pts = []
                    intervals = []
                    # elem.brace_text().start.start gives the index of '{'
                    base_offset = elem.brace_text().start.start + 1
                    matches = re.finditer(r'\(([^,]+),([^)]+)\)', text)
                    for m in matches:
                        try:
                            x = float(m.group(1).strip())
                            y = float(m.group(2).strip())
                            px = x * self.tikz_scale * self.scaling
                            py = -y * self.tikz_scale * self.scaling
                            pts.append(QPointF(px, py))
                            intervals.append((base_offset + m.start(), base_offset + m.end() - 1))
                        except ValueError:
                            pass
                    if pts:
                        self.shapes.append({
                            'type': 'smooth_curve',
                            'points': pts,
                            'intervals': intervals,
                            'style': style,
                        })
                    is_plot = False
                elif last_coord is not None and text:
                    self.shapes.append({
                        'type':   'node',
                        'points': [last_coord],
                        'text':   text,
                        'style':  style,
                    })

            # ---- AT coordinate (node placement override) ----
            elif elem.AT() if hasattr(elem, 'AT') else False:
                if elem.coordinate():
                    pt = self._get_coord(elem.coordinate())
                    if pt is not None:
                        last_coord = pt

            # ---- PLOT / edge_op / CYCLE — no shape emitted ----
            elif hasattr(elem, 'PLOT') and elem.PLOT():
                is_plot = True
            elif elem.edge_op():
                pass  # just a connector

            i += 1

        # ---- 3. If we accumulated 2+ points connected by --, emit a path ----
        if len(path_points) >= 2:
            self.shapes.append({
                'type':      'path',
                'points':    list(path_points),
                'intervals': list(path_intervals),
                'style':     style,
            })
        elif len(path_points) == 1:
            # Single point with no shape → emit a small node dot
            pass

        for i in range(num_shapes_before, len(self.shapes)):
            self.shapes[i]['cmd_interval'] = (ctx.start.start, ctx.stop.stop)

    # ------------------------------------------------------------------
    # Shape spec emission helpers
    # ------------------------------------------------------------------

    def _emit_shape_spec(self, ctx: TikzParser.Shape_specContext,
                         origin: QPointF | None, origin_interval: tuple[int, int] | None, style: dict):
        """
        Convert a shape_spec context into one or more shape dicts.
        """
        if ctx is None or origin is None:
            return

        # ---- RECTANGLE  (p1) rectangle (p2) ----
        if ctx.RECTANGLE():
            p2 = self._get_coord(ctx.coordinate())
            p2_int = self._get_coord_interval(ctx.coordinate())
            if p2 is not None:
                self.shapes.append({
                    'type':      'rectangle',
                    'points':    [origin, p2],
                    'intervals': [origin_interval, p2_int] if origin_interval and p2_int else [],
                    'style':     style,
                })

        # ---- CIRCLE  circle (r) ----
        elif ctx.CIRCLE():
            radius = 0.0
            r_int = None
            if ctx.circle_size():
                radius = self._get_number(ctx.circle_size().numberunit()) * self.tikz_scale * self.scaling
                r_int = (ctx.circle_size().start.start, ctx.circle_size().stop.stop)
            radius_pt = QPointF(origin.x() + radius, origin.y())
            self.shapes.append({
                'type':      'circle',
                'points':    [origin, radius_pt],
                'intervals': [origin_interval, r_int] if origin_interval and r_int else [],
                'style':     style,
            })

        # ---- ELLIPSE  ellipse (rx and ry) ----
        elif ctx.ELLIPSE():
            rx, ry = 0.0, 0.0
            e_int = None
            if ctx.ellipse_size():
                nums = ctx.ellipse_size().numberunit()
                if len(nums) >= 1:
                    rx = self._get_number(nums[0]) * self.tikz_scale * self.scaling
                if len(nums) >= 2:
                    ry = self._get_number(nums[1]) * self.tikz_scale * self.scaling
                e_int = (ctx.ellipse_size().start.start, ctx.ellipse_size().stop.stop)
            self.shapes.append({
                'type':      'ellipse',
                'points':    [origin],
                'intervals': [origin_interval, e_int] if origin_interval and e_int else [],
                'rx':        rx,
                'ry':        ry,
                'style':     style,
            })

        # ---- GRID  grid (corner) ----
        elif ctx.GRID():
            p2 = self._get_coord(ctx.coordinate())
            p2_int = self._get_coord_interval(ctx.coordinate())
            if p2 is not None:
                self.shapes.append({
                    'type':      'grid',
                    'points':    [origin, p2],
                    'intervals': [origin_interval, p2_int] if origin_interval and p2_int else [],
                    'style':     style,
                })

        # ---- PARABOLA  parabola (endpoint) ----
        elif ctx.PARABOLA():
            p2 = self._get_coord(ctx.coordinate())
            p2_int = self._get_coord_interval(ctx.coordinate())
            if p2 is not None:
                self.shapes.append({
                    'type':      'parabola',
                    'points':    [origin, p2],
                    'intervals': [origin_interval, p2_int] if origin_interval and p2_int else [],
                    'style':     style,
                })

    # ------------------------------------------------------------------
    # Arc emission
    # ------------------------------------------------------------------

    def _emit_arc(self, ctx: TikzParser.Arc_specContext,
                  start_pt: QPointF | None, start_interval: tuple[int, int] | None, 
                  is_relative: bool, center_interval: tuple[int, int] | None,
                  typed_center_pt: QPointF | None, style: dict):
        """
        Emit an arc shape.
        TikZ arc syntax: arc(start_angle : end_angle : radius)
        The given coordinate is the START point on the arc, NOT the centre.
        """
        if ctx is None or start_pt is None:
            return
        params = ctx.arc_params()
        if params is None:
            return

        nums = params.numberunit()
        if len(nums) < 3:
            return

        start_angle = self._get_number(nums[0])
        end_angle   = self._get_number(nums[1])
        radius_tikz = self._get_number(nums[2])
        radius_px   = radius_tikz * self.tikz_scale * self.scaling

        # Convert start point back to TikZ units so we can compute the centre
        sx = start_pt.x() / (self.tikz_scale * self.scaling)
        sy = -start_pt.y() / (self.tikz_scale * self.scaling)   # un-flip y

        # Centre = start point − r*(cos, sin) of start angle
        rad_start = math.radians(start_angle)
        cx_tikz = sx - radius_tikz * math.cos(rad_start)
        cy_tikz = sy - radius_tikz * math.sin(rad_start)
        center = self._to_canvas(cx_tikz, cy_tikz)

        # End point
        rad_end = math.radians(end_angle)
        ex_tikz = cx_tikz + radius_tikz * math.cos(rad_end)
        ey_tikz = cy_tikz + radius_tikz * math.sin(rad_end)
        end_pt  = self._to_canvas(ex_tikz, ey_tikz)

        intervals = []
        if center_interval:
            intervals.append(center_interval)
        if start_interval:
            intervals.append(start_interval)
        
        arc_interval = (ctx.start.start, ctx.stop.stop) if ctx else None
        if arc_interval:
            intervals.append(arc_interval)

        pts = [center, start_pt, end_pt]
        if typed_center_pt:
            pts.append(typed_center_pt)

        self.shapes.append({
            'type':        'arc',
            'points':      pts,
            'intervals':   intervals,
            'start_angle': start_angle,
            'end_angle':   end_angle,
            'radius':      radius_px,
            'style':       style,
            'is_relative': is_relative,
        })
    # Bezier control emission
    # ------------------------------------------------------------------

    def _emit_control(self, ctx: TikzParser.Control_specContext,
                      path_points: list, style: dict):
        """
        Emit a bezier curve from .. controls (p1) and (p2) ..
        Requires that path_points has at least one point (start).
        """
        if ctx is None or not path_points:
            return
        start = path_points[-1]
        coords = ctx.coordinate()
        if not coords:
            return
        ctrl1 = self._get_coord(coords[0])
        ctrl2 = self._get_coord(coords[1]) if len(coords) > 1 else ctrl1
        # The end point comes as the NEXT coordinate in the parent path,
        # but for now we emit with what we have (end = ctrl2 if no further point)
        if ctrl1 and ctrl2:
            self.shapes.append({
                'type':   'bezier',
                'points': [start, ctrl1, ctrl2, ctrl2],  # end updated if next coord exists
                'style':  style,
            })

    # ------------------------------------------------------------------
    # Inline node emission
    # ------------------------------------------------------------------

    def _emit_node_inline(self, ctx: TikzParser.Node_inlineContext,
                          position: QPointF | None, style: dict):
        """
        Emit an inline node  node [opts] {label}.
        """
        if ctx is None:
            return
        # Position: from  at (x,y)  if present, else the accumulated path point
        pt = position
        if ctx.AT() and ctx.coordinate():
            pt = self._get_coord(ctx.coordinate())

        if pt is None:
            return

        if ctx.node_name():
            self.named_nodes[ctx.node_name().ID().getText()] = pt

        # Merge node-specific options
        node_style = dict(style)
        if ctx.tikz_options():
            node_style.update(self._parse_options_ctx(ctx.tikz_options()))

        # Extract text content
        text = ""
        if ctx.brace_text():
            text = self._brace_text_content(ctx.brace_text())

        self.shapes.append({
            'type':   'node',
            'points': [pt],
            'intervals': [self._get_coord_interval(ctx.coordinate())] if ctx.coordinate() else [],
            'text':   text,
            'style':  node_style,
        })

    # ------------------------------------------------------------------
    # Standalone node command  (\node [opts] at (x,y) {label};)
    # Already handled by path_cmd when path_start is NODE_CMD.
    # But if the visitor encounters a node_inline at stmt level, handle it.
    # ------------------------------------------------------------------

    def visitNode_inline(self, ctx: TikzParser.Node_inlineContext):
        # Only called directly if the node appears outside a path_cmd.
        # In that case we have no position context.
        self._emit_node_inline(ctx, None, self._default_style())

    # ------------------------------------------------------------------
    # Default visitor: visit children for all other rules
    # ------------------------------------------------------------------

    def visitChildren(self, node):
        result = None
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                if hasattr(child, 'accept'):
                    result = child.accept(self)
        return result
