import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QPoint

class drawing_canvas(QWidget):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)   
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Enable transparent background
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Allow canvas to receive keyboard events
        
        self.editor = editor
        self.shapes = []         # List of committed shapes
        self.current_shape = []  # List of points for the shape being drawn
        self.drawing_mode = None # Default drawing mode
        
        # Arc drawing attributes
        self.arc_points = []     # Reset the arc points
        self.arc_selection_state = None  # For tracking arc drawing state: "selecting_arc_center", "selecting_arc_start_end"
        self.current_arc_end = None  # For arc preview when dragging    
        
        # Scaling attributes
        self.display_scale = 1.0  # Attribute for visual scaling only
        self.scale_factor = 1.0   # Initial scale factor 1.0
        self.content_scale = 1.0   # Initial content scale 1.0
        
        # Grid selection flags
        self.cartesian_grid_enabled = True
        self.polar_grid_enabled = False
        self.show_grid = True
        self.show_reference_points = True
        
        # Initial cartesian grid parameters
        self.cartesian_grid_step = 0.5     
        
        # Initial polar grid parameters
        self.polar_grid_angle_step = 10  # Angle increment for polar grid (degrees)
        self.polar_grid_radius_step = self.cartesian_grid_step  # Radius increment for polar grid
        
        # Selection and movement variables
        self.selection_start = None     # Start point of selection rectangle
        self.selection_end = None       # End point of selection rectangle
        self._selected_shape_indices = []  # Indices of the selected shapes
        self.is_selecting = False      # Flag for rectangle selection in progress
        self.is_dragging = False       # Flag for dragging selected shape
        self.drag_start_pos = None     # Start position for dragging
        self.last_drag_pos = None      # Last position during drag
            
        # Panning variables
        self.is_panning = False
        self.pan_start_pos = None
            
        # Selection and edition shape points
        self.is_editing_point = False       # Flag for editing a control point
        self.selected_point_index = None    # Index of the selected control point in the shape
            
        # Add an attribute to store the real cursor position
        self.real_cursor_pos = None
        
        # Track newly drawn shapes that need interval matching
        self.newly_drawn_indices = set()  # Set of shape indices that were just drawn and need matching

        # Parsed overlay model (coordinate crosses and scope boxes)
        self.overlay_model = {'nodes': [], 'scopes': []}
        self.selected_overlay_interval = None
        self.selected_overlay_scope_id = None
        self.is_dragging_overlay_node = False
        self.is_dragging_overlay_scope = False

    def update(self):
        super().update()
        if self.parent():
            self.parent().update()

    # Scale display only method
    def set_display_scale(self, scale):
        """
        Update the display scale factor without affecting shape dimensions.
        """
        self.display_scale = scale
        self.update()
            
    # updateCursorPosition method 
    def updateCursorPosition(self, global_pos):
        """
        Update cursor position display after zoom operations.
        No need to store any values as we'll use direct event positions.
        """
        # This is now just a visual update - we don't need to store anything
        # Just update the cursor to show it's in the right place
        self.setCursor(Qt.CursorShape.CrossCursor)
                    
    # --- Methods for cartesian and polar grids ---
    def set_cartesian_grid_step_value(self, value):
        self.cartesian_grid_step = value
        self.polar_grid_radius_step = value
        self.update()
        
    def set_polar_grid_angle_step_value(self, value):
        self.polar_grid_angle_step = value  
        self.update()
        
    def set_polar_grid_radius_step_value(self, value):
        self.polar_grid_radius_step = value  
        self.update()

    def snap_to_cartesian_grid(self, point):
        """
        Snap a given point to the nearest grid point.
        Point should be in canvas coordinates (origin at center).
        """
        if self.cartesian_grid_step == 0:
            return point
            
        effective_step = self.cartesian_grid_step * getattr(self.editor.parser, 'scaling', 38)
            
        # Point is already in canvas coordinates (origin at center, unscaled)
        # Snap to the nearest grid step in both directions
        snapped_x = round(point.x() / effective_step) * effective_step
        snapped_y = round(point.y() / effective_step) * effective_step
        

        from PyQt6.QtCore import QPointF
        return QPointF(snapped_x, snapped_y)
    
    def snap_to_polar_grid(self, point, center=None):
        """
        Snap a given point to the nearest polar grid intersection.
        Point should be in canvas coordinates.
        If center is not provided, uses the first arc point or origin.
        """
        if self.polar_grid_radius_step == 0 or self.polar_grid_angle_step == 0:
            return point
            
        # Use provided center, or the first arc point as center, or default to origin if not set
        if center is None:
            center = QPoint(0, 0)
            if self.arc_points:
                center = self.arc_points[0]
        
        # Calculate vector from center to point (invert Y because canvas Y is down)
        dx = point.x() - center.x()
        dy = -(point.y() - center.y())
        
        # Calculate radius and angle
        radius = math.sqrt(dx*dx + dy*dy)
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # Snap angle to nearest angle increment
        snapped_angle_deg = round(angle_deg / self.polar_grid_angle_step) * self.polar_grid_angle_step
        snapped_angle_rad = math.radians(snapped_angle_deg)
        
        # Snap radius to nearest radius increment
        effective_radius_step = self.polar_grid_radius_step * getattr(self.editor.parser, 'scaling', 38)
        snapped_radius = round(radius / effective_radius_step) * effective_radius_step
        
        # Convert back to Cartesian coordinates, relative to center (invert Y again)
        snapped_x = center.x() + snapped_radius * math.cos(snapped_angle_rad)
        snapped_y = center.y() - snapped_radius * math.sin(snapped_angle_rad)
        
        from PyQt6.QtCore import QPointF
        return QPointF(snapped_x, snapped_y)

    def transform_to_canvas_coords(self, screen_pos):
        """
        Transform screen/widget coordinates to canvas coordinates.
        Uses the same origin as paintEvent (logical canvas center) to
        guarantee mouse input aligns exactly with drawn grid and shapes.
        """
        # Use the same origin as paintEvent: logical canvas center, scaled
        center_x = self.editor.logical_canvas_width / 2.0 * self.display_scale
        center_y = self.editor.logical_canvas_height / 2.0 * self.display_scale
        
        # Calculate position relative to center in widget coordinates
        rel_x = screen_pos.x() - center_x
        rel_y = screen_pos.y() - center_y
        
        # Convert to canvas coordinates - divide by scale factor   
        canvas_x = rel_x / self.display_scale
        canvas_y = rel_y / self.display_scale
        
        from PyQt6.QtCore import QPointF
        return QPointF(canvas_x, canvas_y)

    def global_to_canvas_coords(self, global_pos):
        """
        Convert global screen coordinates to canvas coordinates
        accounting for scaling and translation.
        """
        # First convert global coordinates to widget coordinates
        local_pos = self.mapFromGlobal(global_pos)
        
        # Then convert widget coordinates to canvas coordinates
        return self.transform_to_canvas_coords(local_pos)
    
    def unscale_pos(self, pos):
        """Convert scaled coordinates back to original coordinates"""
        if self.scale_factor != 0:
            from PyQt6.QtCore import QPointF
            return QPointF(pos.x() / self.scale_factor, pos.y() / self.scale_factor)
        return pos
    
    # --- end methods for cartesian and polar grids ---

    # --- methods for selecting and moving shapes ---   
    # Add method to find the shape at a given position
    def find_shape_at_position(self, pos):
        """Find the index of a shape at the given position, or None if no shape is found."""
        # Check shapes in reverse order (top to bottom)
        for i in range(len(self.shapes) - 1, -1, -1):
            shape = self.shapes[i]
            shape_type = shape[-1]
            
            if shape_type == "rectangle":
                from PyQt6.QtCore import QRectF
                rect = QRectF(shape[0], shape[1]).normalized()
                if rect.contains(pos):
                    return i
                    
            elif shape_type == "circle":
                # Check if point is inside circle using Euclidean distance
                center = shape[0]
                # Radius is Euclidean distance between center and radius point
                dx = shape[0].x() - shape[1].x()
                dy = shape[0].y() - shape[1].y()
                radius = math.hypot(dx, dy)
                
                # Distance from mouse to center
                mouse_dx = pos.x() - center.x()
                mouse_dy = pos.y() - center.y()
                dist = math.hypot(mouse_dx, mouse_dy)
                
                if dist <= radius:
                    return i
                    
            elif shape_type == "ellipse":
                # Check if point is inside ellipse (approximate)
                center = shape[0]
                rx = abs(shape[0].x() - shape[1].x())
                ry = abs(shape[0].y() - shape[1].y())
                if rx > 0 and ry > 0:
                    dx = (pos.x() - center.x()) / rx
                    dy = (pos.y() - center.y()) / ry
                    if dx*dx + dy*dy <= 1:
                        return i
                        
            elif shape_type in ["path", "smooth_curve"]:
                # Check proximity to line segments
                points = shape[:-1]  # All points except mode marker
                for j in range(len(points) - 1):
                    # Calculate distance to line segment
                    p1, p2 = points[j], points[j+1]
                    dist = self.point_to_line_distance(pos, p1, p2)
                    if dist < 5:  # 5 pixel tolerance
                        return i
                        
            elif shape_type == "arc":
                # Check if near the arc using Euclidean distance
                center, start, end = shape[0], shape[1], shape[2]
                # Calculate radius
                dx = center.x() - start.x()
                dy = center.y() - start.y()
                radius = math.hypot(dx, dy)
                # Check if distance to center is approximately radius (on the arc)
                mouse_dx = pos.x() - center.x()
                mouse_dy = pos.y() - center.y()
                dist_to_center = math.hypot(mouse_dx, mouse_dy)
                if abs(dist_to_center - radius) < 5:  # 5 pixel tolerance
                    # Could add angle check for more precision
                    return i
        
        return None
   
    def find_shapes_in_selection(self, selection_rect):
        """Find all shapes that are inside or intersect the selection rectangle."""
        selected_shapes = []
        
        for i, shape in enumerate(self.shapes):
            shape_type = shape[-1]
            # Check different shape types
            if shape_type == "rectangle":
                # Check if rectangle intersects with selection
                from PyQt6.QtCore import QRectF
                shape_rect = QRectF(shape[0], shape[1]).normalized()
                if selection_rect.intersects(shape_rect):
                    selected_shapes.append(i)
                    
            elif shape_type == "circle":
                # Check if circle intersects with selection
                center = shape[0]
                dx = shape[0].x() - shape[1].x()
                dy = shape[0].y() - shape[1].y()
                radius = math.hypot(dx, dy)
                
                # Simple check: is the center in the selection or
                # is any corner of the selection within radius of center?
                if selection_rect.contains(center):
                    selected_shapes.append(i)
                else:
                    # Check corners of selection against circle
                    corners = [
                        selection_rect.topLeft(),
                        selection_rect.topRight(),
                        selection_rect.bottomLeft(),
                        selection_rect.bottomRight()
                    ]
                    for corner in corners:
                        corner_dx = corner.x() - center.x()
                        corner_dy = corner.y() - center.y()
                        if math.hypot(corner_dx, corner_dy) <= radius:
                            selected_shapes.append(i)
                            break
                            
            elif shape_type == "ellipse":
                # Check if ellipse intersects with selection (simplified)
                center = shape[0]
                if selection_rect.contains(center):
                    selected_shapes.append(i)
                    
            elif shape_type in ["path", "smooth_curve"]:
                # Check if any point of the path is in the selection
                points = shape[:-1]  # All points except mode marker
                for point in points:
                    if selection_rect.contains(point):
                        selected_shapes.append(i)
                        break
                        
            elif shape_type == "arc":
                # Special handling for arc shapes - check all control points
                if len(shape) >= 4:  # Make sure we have center, start, end, and mode
                    center = shape[0]
                    start = shape[1]
                    end = shape[2]
                    # Check if any control point is in the selection rectangle
                    for j in range(3):  # Check center, start, end points
                        if selection_rect.contains(shape[j]):
                            selected_shapes.append(i)
                            break
                    
                    # If control points aren't directly in the selection, check arc itself
                    if i not in selected_shapes:
                        # Check if center is in selection
                        if selection_rect.contains(center):
                            selected_shapes.append(i)
                        else:
                            # Also check if any part of the arc boundary is in the selection
                            dx = center.x() - start.x()
                            dy = center.y() - start.y()
                            radius = math.hypot(dx, dy)
                            # Simplified intersection check
                            if abs(math.hypot(selection_rect.center().x() - center.x(), 
                                              selection_rect.center().y() - center.y()) - radius) < 5:
                                selected_shapes.append(i)
        
        return selected_shapes
       
    def point_to_line_distance(self, point, line_start, line_end):
        """Calculate the shortest distance from a point to a line segment."""
        # Vector from line_start to line_end
        line_vec_x = line_end.x() - line_start.x()
        line_vec_y = line_end.y() - line_start.y()
        
        # Vector from line_start to point
        point_vec_x = point.x() - line_start.x()
        point_vec_y = point.y() - line_start.y()
        
        # Length squared of line segment
        line_len_sq = line_vec_x * line_vec_x + line_vec_y * line_vec_y
        
        # If line segment has zero length, return distance to start point
        if line_len_sq == 0:
            return math.sqrt(point_vec_x * point_vec_x + point_vec_y * point_vec_y)
        
        # Calculate projection of point_vec onto line_vec (dot product / length)
        t = max(0, min(1, (point_vec_x * line_vec_x + point_vec_y * line_vec_y) / line_len_sq))
        
        # Calculate closest point on line segment
        closest_x = line_start.x() + t * line_vec_x
        closest_y = line_start.y() + t * line_vec_y
        
        # Return distance to closest point
        dx = point.x() - closest_x
        dy = point.y() - closest_y
        return math.sqrt(dx * dx + dy * dy)

    def move_shape(self, current_pos):
        """Move the selected shape by the amount the mouse has moved since last position."""
        if not self.selected_shape_indices or self.last_drag_pos is None:
            return
        
        # Calculate movement delta
        delta_x = current_pos.x() - self.last_drag_pos.x()
        delta_y = current_pos.y() - self.last_drag_pos.y()
        
        # Apply movement to all points of all selected shapes
        from PyQt6.QtCore import QPointF
        for shape_idx in self.selected_shape_indices:
            shape = self.shapes[shape_idx]
            shape_type = shape[-1]
            
            if shape_type in ["rectangle", "circle", "ellipse"]:
                # For basic shapes (first two points)
                for i in range(len(shape) - 1):  # Skip the shape type marker
                    if shape[i] is not None:
                        shape[i] = QPointF(shape[i].x() + delta_x, shape[i].y() + delta_y)
                        
            elif shape_type in ["path", "smooth_curve"]:
                # For paths (all points except mode marker)
                for i in range(len(shape) - 1):
                    shape[i] = QPointF(shape[i].x() + delta_x, shape[i].y() + delta_y)
                    
            elif shape_type == "arc":
                # For arcs (center, start, end points)
                for i in range(min(3, len(shape) - 1)):
                    if shape[i] is not None:
                        shape[i] = QPointF(shape[i].x() + delta_x, shape[i].y() + delta_y)
        
        # Update the last drag position
        self.last_drag_pos = current_pos
        
        # Update the canvas
        self.update()
        
        # Update the TikZ code in the editor
        if hasattr(self.editor, "update_tikz_code"):
            self.editor.update_tikz_code()
        
    def reset_selection_state(self):
        """Reset selection and editing state for new tool actions."""
        self.selected_shape_indices = []
        self.selected_point_index = None
        self.clear_overlay_selection()
        self.is_editing_point = False
        self.is_dragging = False
        self.last_drag_pos = None
        self.drag_start_pos = None
        self.selection_start = None
        self.selection_end = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def find_control_point_at_position(self, pos, tolerance=5):
        """
        Find a control point of a shape at the given position.
        Returns (shape_index, point_index) if found, otherwise (None, None).
        Supports both QPoint and QPointF types.
        """
        from PyQt6.QtCore import QPointF
        
        # Convert pos to QPointF for consistent calculations
        if not isinstance(pos, QPointF):
            pos = QPointF(pos)
            
        best_shape_index = None
        best_point_index = None
        best_distance = float(tolerance) + 1.0

        for i, shape in enumerate(self.shapes):
            points = shape[:-1]  # All points except the mode marker

            for j, point in enumerate(points):
                # Skip None points
                if point is None:
                    continue

                # Convert point to QPointF for consistent calculations
                if not isinstance(point, QPointF):
                    point_f = QPointF(point)
                else:
                    point_f = point

                # Calculate Euclidean distance from cursor to point
                dx = pos.x() - point_f.x()
                dy = pos.y() - point_f.y()
                distance = math.hypot(dx, dy)

                # Check if the position is near this control point and is closer than any prior candidate
                if distance <= tolerance and distance < best_distance:
                    best_distance = distance
                    best_shape_index = i
                    best_point_index = j

        return best_shape_index, best_point_index

    def find_overlay_node_at_position(self, pos, tolerance=8):
        """Find a parsed overlay coordinate marker near the cursor."""
        best_node = None
        best_distance = float(tolerance) + 1.0
        for node in self.overlay_model.get('nodes', []):
            dx = pos.x() - node.point.x()
            dy = pos.y() - node.point.y()
            distance = math.hypot(dx, dy)
            if distance <= tolerance and distance < best_distance:
                best_distance = distance
                best_node = node
        return best_node

    def find_overlay_scope_at_position(self, pos, tolerance=8):
        """Find a scope box border near the cursor."""
        best_scope = None
        best_distance = float(tolerance) + 1.0
        for scope in self.overlay_model.get('scopes', []):
            if not scope.rect:
                continue
            x1, y1, x2, y2 = scope.rect
            if x1 > x2 or y1 > y2:
                continue
            on_horizontal = (x1 - tolerance <= pos.x() <= x2 + tolerance) and (
                abs(pos.y() - y1) <= tolerance or abs(pos.y() - y2) <= tolerance
            )
            on_vertical = (y1 - tolerance <= pos.y() <= y2 + tolerance) and (
                abs(pos.x() - x1) <= tolerance or abs(pos.x() - x2) <= tolerance
            )
            if not (on_horizontal or on_vertical):
                continue
            distance = min(
                abs(pos.x() - x1), abs(pos.x() - x2),
                abs(pos.y() - y1), abs(pos.y() - y2)
            )
            if distance < best_distance:
                best_distance = distance
                best_scope = scope
        return best_scope

    def move_overlay_node(self, overlay_node, new_pos):
        """Move a parsed overlay coordinate and propagate the change to the backing shape."""
        if overlay_node is None or overlay_node.shape_index >= len(self.shapes):
            return

        snapped_pos = self.snap_to_cartesian_grid(new_pos)
        shape = self.shapes[overlay_node.shape_index]
        if overlay_node.point_index >= len(shape) - 1:
            return

        delta_x = snapped_pos.x() - shape[overlay_node.point_index].x()
        delta_y = snapped_pos.y() - shape[overlay_node.point_index].y()
        shape[overlay_node.point_index] = snapped_pos

        # Preserve dependent geometry for circles and node convenience shapes.
        if shape[-1] == "circle" and overlay_node.point_index == 0 and len(shape) > 2 and shape[1] is not None:
            from PyQt6.QtCore import QPointF
            shape[1] = QPointF(shape[1].x() + delta_x, shape[1].y() + delta_y)
        if shape[-1] == "node" and len(shape) > 2:
            shape[1] = snapped_pos

    def _overlay_scope_intervals(self, scope_id):
        """Collect all overlay-node intervals that belong to a scope or its descendants."""
        intervals = set()
        scope_lookup = {scope.id: scope for scope in self.overlay_model.get('scopes', [])}

        def collect(current_scope_id):
            scope = scope_lookup.get(current_scope_id)
            if scope is None:
                return
            intervals.update(scope.node_intervals)
            for child_scope_id in scope.child_scope_ids:
                collect(child_scope_id)

        collect(scope_id)
        return intervals

    def move_overlay_scope(self, scope_id, delta_x, delta_y):
        """Move every parsed overlay coordinate within the scope."""
        target_intervals = self._overlay_scope_intervals(scope_id)
        interval_to_node = {node.interval: node for node in self.overlay_model.get('nodes', [])}
        for interval in target_intervals:
            node = interval_to_node.get(interval)
            if node is None:
                continue
            from PyQt6.QtCore import QPointF
            moved_pos = QPointF(node.point.x() + delta_x, node.point.y() + delta_y)
            self.move_overlay_node(node, moved_pos)

    def clear_overlay_selection(self):
        self.selected_overlay_interval = None
        self.selected_overlay_scope_id = None
        self.is_dragging_overlay_node = False
        self.is_dragging_overlay_scope = False
    
    # --- end for methods for select and move shapes ---


    # --- Mouse methods ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = True
            self.pan_start_pos = event.globalPosition().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        # Convert to canvas coordinates (origin at center, unscaled)
        canvas_pos = self.transform_to_canvas_coords(event.pos())
        
        # If we're in selection mode (drawing_mode is None)
        if self.drawing_mode is None and event.button() == Qt.MouseButton.LeftButton:
            if getattr(self.editor, "overlay_active", False):
                overlay_node = self.find_overlay_node_at_position(canvas_pos, 8 / self.display_scale)
                if overlay_node is not None:
                    self.clear_overlay_selection()
                    self.selected_overlay_interval = overlay_node.interval
                    self.is_dragging_overlay_node = True
                    self.drag_start_pos = canvas_pos
                    self.last_drag_pos = None
                    self.cartesian_grid_enabled = True
                    self.polar_grid_enabled = False
                    self.setCursor(Qt.CursorShape.CrossCursor)
                    self.update()
                    return

                overlay_scope = self.find_overlay_scope_at_position(canvas_pos, 8 / self.display_scale)
                if overlay_scope is not None:
                    self.clear_overlay_selection()
                    self.selected_overlay_scope_id = overlay_scope.id
                    self.is_dragging_overlay_scope = True
                    self.drag_start_pos = canvas_pos
                    self.last_drag_pos = None
                    self.cartesian_grid_enabled = True
                    self.polar_grid_enabled = False
                    self.setCursor(Qt.CursorShape.SizeAllCursor)
                    self.update()
                    return

            # First check if we clicked on a control point
            shape_index, point_index = self.find_control_point_at_position(canvas_pos)
            
            if shape_index is not None and point_index is not None:
                # We clicked on a control point - prepare for editing
                self.selected_shape_indices = [shape_index]
                self.selected_point_index = point_index
                self.is_editing_point = True
                self.drag_start_pos = canvas_pos
                self.last_drag_pos = None
                
                # Use appropriate grid based on shape type
                if self.shapes[shape_index][-1] == "arc":
                    # For arcs, use polar grid if editing start/end points
                    if point_index in (1, 2):  # Start or end point
                        self.cartesian_grid_enabled = False
                        self.polar_grid_enabled = True
                    else:
                        self.cartesian_grid_enabled = True
                        self.polar_grid_enabled = False
                else:
                    self.cartesian_grid_enabled = True
                    self.polar_grid_enabled = False
                
                self.setCursor(Qt.CursorShape.CrossCursor)
                self.update()
                return

            # If we clicked directly inside a shape, select it and begin dragging immediately
            direct_shape_index = self.find_shape_at_position(canvas_pos)
            if direct_shape_index is not None:
                # If the clicked shape is already in the selection, don't clear the selection!
                # This allows dragging a group of shapes by clicking on any one of them.
                if direct_shape_index not in self.selected_shape_indices:
                    self.selected_shape_indices = [direct_shape_index]
                self.selected_point_index = None
                self.is_selecting = False
                self.is_dragging = True
                self.drag_start_pos = canvas_pos
                self.last_drag_pos = None
                self.cartesian_grid_enabled = True
                self.polar_grid_enabled = False
                self.setCursor(Qt.CursorShape.SizeAllCursor)
                self.update()
                return

            # If not a control point or shape, start a selection rectangle
            self.is_selecting = True
            self.selection_start = canvas_pos
            self.selection_end = canvas_pos
            self.selected_shape_indices = []  # Clear previous selection
            self.is_editing_point = False
            self.selected_point_index = None
            self.cartesian_grid_enabled = True
            self.polar_grid_enabled = False
            self.update()
            return
        
        # For drawing operations, apply appropriate grid snapping based on mode
        if self.drawing_mode == "arc":           
            if self.arc_selection_state == "selecting_arc_center":
                # First click: select center using Cartesian grid
                point = self.snap_to_cartesian_grid(canvas_pos)
                self.arc_points = [point]  # Set center point
                
                # Switch to polar grid for the rest of the arc drawing
                self.cartesian_grid_enabled = False
                self.polar_grid_enabled = True
                self.arc_selection_state = "selecting_arc_start_end"
                
                self.update()
                return
            elif self.arc_selection_state == "selecting_arc_start_end":
                # After center is selected, snap to polar grid for start/end points
                point = self.snap_to_polar_grid(canvas_pos)
                self.arc_points.append(point)
                
                # Check if we have all points needed for an arc (center, start, end)
                if len(self.arc_points) == 3:
                    self.shapes.append(self.arc_points + ["arc"])
                    # Mark this shape as newly drawn (needs interval matching)
                    self.newly_drawn_indices.add(len(self.shapes) - 1)
                    
                    self.arc_points = [] # Reset arc points               
                    self.arc_selection_state = "selecting_arc_center" # restart the arc selection process
                    
                    # Reset grid visibility for next operation
                    self.cartesian_grid_enabled = True
                    self.polar_grid_enabled = False       
                                    
                    # Update the editor
                    self.update()
                    if hasattr(self.editor, "update_tikz_code"):
                        self.editor.update_tikz_code()
            
                self.update()
                return      
                    
        # For regular shapes, snap to cartesian grid
        if self.drawing_mode in ["rectangle", "circle", "ellipse", "path"]:
            point = self.snap_to_cartesian_grid(canvas_pos)
        else:
            point = canvas_pos

        # Draw shapes based on the current mode
        if self.drawing_mode in ["rectangle", "circle", "ellipse"]:
            if not self.current_shape: 
                self.current_shape = [point, point, self.drawing_mode]
            else:
                self.current_shape[1] = point
            self.update()
        elif self.drawing_mode == "path":
            if not self.current_shape:
                self.current_shape = [point, "path"]
            else:
                self.current_shape.insert(-1, point)
            self.update()
            event.accept()
        elif self.drawing_mode == "smooth_curve":
            if not self.current_shape:
                self.current_shape = [point, "smooth_curve"]
            else:
                self.current_shape.insert(-1, point)
            self.update()
        else:   
            super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.drawing_mode in ["path", "smooth_curve"] and self.current_shape and len(self.current_shape) > 1:
            # Commit the shape only if it has at least one point (other than the mode marker)
            self.shapes.append(self.current_shape)
            # Mark this shape as newly drawn (needs interval matching)
            self.newly_drawn_indices.add(len(self.shapes) - 1)
            self.current_shape = []
            self.update()
            # Update the TikZ code in the editor after committing a path
            if hasattr(self.editor, "update_tikz_code"):
                self.editor.update_tikz_code()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        if getattr(self, 'is_panning', False):
            current_pos = event.globalPosition().toPoint()
            delta = current_pos - self.pan_start_pos
            self.pan_start_pos = current_pos
            
            # Scroll the overlay_scroll_area
            h_bar = self.editor.overlay_scroll_area.horizontalScrollBar()
            v_bar = self.editor.overlay_scroll_area.verticalScrollBar()
            
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
            
            event.accept()
            return

        # Convert to canvas coordinates (origin at center, unscaled)
        canvas_pos = self.transform_to_canvas_coords(event.pos())

        if self.is_dragging_overlay_node and self.selected_overlay_interval is not None:
            overlay_node = next(
                (node for node in self.overlay_model.get('nodes', [])
                 if node.interval == self.selected_overlay_interval),
                None
            )
            if overlay_node is not None:
                self.move_overlay_node(overlay_node, canvas_pos)
                if hasattr(self.editor, "update_tikz_code"):
                    self.editor.update_tikz_code()
                    self.overlay_model = getattr(self.editor.parser, 'last_overlay_model', self.overlay_model)
                self.update()
            return

        if self.is_dragging_overlay_scope and self.selected_overlay_scope_id is not None:
            snapped_pos = self.snap_to_cartesian_grid(canvas_pos)
            
            if self.last_drag_pos is None:
                self.last_drag_pos = snapped_pos
                return
                
            delta_x = snapped_pos.x() - self.last_drag_pos.x()
            delta_y = snapped_pos.y() - self.last_drag_pos.y()
            if delta_x or delta_y:
                self.move_overlay_scope(self.selected_overlay_scope_id, delta_x, delta_y)
                self.last_drag_pos = snapped_pos
                if hasattr(self.editor, "update_tikz_code"):
                    self.editor.update_tikz_code()
                    self.overlay_model = getattr(self.editor.parser, 'last_overlay_model', self.overlay_model)
                self.update()
            return
            
        # If we're editing a control point
        if self.is_editing_point and self.selected_shape_indices and self.selected_point_index is not None:
            shape = self.shapes[self.selected_shape_indices[0]]
            shape_type = shape[-1]
            
            # Apply appropriate snapping based on shape type and point being edited
            if shape_type == "arc":
                if self.selected_point_index in (0, 3):
                    # Center point - use cartesian grid
                    snapped_pos = self.snap_to_cartesian_grid(canvas_pos)
                    
                    # Move the center to snapped_pos exactly, and update start/end points to maintain the arc geometry
                    center_idx = self.selected_point_index
                    if shape[center_idx] is not None:
                        delta_x = snapped_pos.x() - shape[center_idx].x()
                        delta_y = snapped_pos.y() - shape[center_idx].y()
                        
                        from PyQt6.QtCore import QPointF
                        shape[center_idx] = snapped_pos
                        if len(shape) > 1 and shape[1] is not None:
                            shape[1] = QPointF(shape[1].x() + delta_x, shape[1].y() + delta_y)
                        if len(shape) > 2 and shape[2] is not None:
                            shape[2] = QPointF(shape[2].x() + delta_x, shape[2].y() + delta_y)
                            
                        # If dragging math center, translate typed center too; if dragging typed center, translate math center too
                        other_center = 3 if center_idx == 0 else 0
                        if len(shape) >= 5 and shape[other_center] is not None:
                            shape[other_center] = QPointF(shape[other_center].x() + delta_x, shape[other_center].y() + delta_y)
                            
                    self.last_drag_pos = snapped_pos
                else:
                    # Start or end point - use polar grid relative to typed center if available
                    center = shape[3] if len(shape) >= 5 else shape[0]
                    snapped_pos = self.snap_to_polar_grid(canvas_pos, center)
                    
                    # Update the specific point (start or end)
                    shape[self.selected_point_index] = snapped_pos
            else:
                # For other shapes, use cartesian grid
                snapped_pos = self.snap_to_cartesian_grid(canvas_pos)
                
                # Update the specific control point
                shape[self.selected_point_index] = snapped_pos
                
                # For circles and ellipses, special handling
                if shape_type == "circle" and self.selected_point_index == 0:
                    # If moving center of circle, maintain radius by moving the radius point
                    if self.last_drag_pos is None:
                        self.last_drag_pos = snapped_pos
                        return
                        
                    delta_x = snapped_pos.x() - self.last_drag_pos.x()
                    delta_y = snapped_pos.y() - self.last_drag_pos.y()
                    
                    # Move radius point
                    if len(shape) > 1 and shape[1] is not None:
                        from PyQt6.QtCore import QPointF
                        shape[1] = QPointF(shape[1].x() + delta_x, shape[1].y() + delta_y)
                
                self.last_drag_pos = snapped_pos
            
            # Update the canvas and TikZ code
            self.update()
            if hasattr(self.editor, "update_tikz_code"):
                self.editor.update_tikz_code()
            
            return
        
        # If we're selecting with a rectangle
        if self.is_selecting:
            self.selection_end = canvas_pos
            self.update()
            return
            
        # If we're dragging selected shapes
        if self.is_dragging and self.selected_shape_indices:
            # Apply appropriate snapping based on shape type
            # If a single arc is selected, apply arc-specific snapping
            if len(self.selected_shape_indices) == 1 and self.shapes[self.selected_shape_indices[0]][-1] == "arc":
                shape = self.shapes[self.selected_shape_indices[0]]
                snapped_pos = self.snap_to_cartesian_grid(canvas_pos)
                
                if len(shape) >= 4:  # Ensure we have enough points
                    center, start, end = shape[0], shape[1], shape[2]
                    
                    if self.last_drag_pos is None:
                        self.last_drag_pos = snapped_pos
                        return
                    
                    delta_x = snapped_pos.x() - self.last_drag_pos.x()
                    delta_y = snapped_pos.y() - self.last_drag_pos.y()
                    
                    if delta_x != 0 or delta_y != 0:
                        from PyQt6.QtCore import QPointF
                        shape[0] = QPointF(center.x() + delta_x, center.y() + delta_y)
                        shape[1] = QPointF(start.x() + delta_x, start.y() + delta_y)
                        shape[2] = QPointF(end.x() + delta_x, end.y() + delta_y)
                        if len(shape) >= 5:
                            typed_center = shape[3]
                            shape[3] = QPointF(typed_center.x() + delta_x, typed_center.y() + delta_y)
                        
                        self.last_drag_pos = snapped_pos
                        self.update()
                        if hasattr(self.editor, "update_tikz_code"):
                            self.editor.update_tikz_code()
            else:
                # For other shapes or multiple shapes, use cartesian grid snapping
                snapped_pos = self.snap_to_cartesian_grid(canvas_pos)
                
                if self.last_drag_pos is None:
                    self.last_drag_pos = snapped_pos
                    return
                    
                delta_x = snapped_pos.x() - self.last_drag_pos.x()
                delta_y = snapped_pos.y() - self.last_drag_pos.y()
                
                if delta_x != 0 or delta_y != 0:
                    for shape_idx in self.selected_shape_indices:
                        shape = self.shapes[shape_idx]
                        shape_type = shape[-1]
                        
                        if shape_type in ["rectangle", "circle", "ellipse"]:
                            from PyQt6.QtCore import QPointF
                            for i in range(len(shape) - 1):
                                if shape[i] is not None:
                                    shape[i] = QPointF(shape[i].x() + delta_x, shape[i].y() + delta_y)
                                    
                        elif shape_type in ["path", "smooth_curve"]:
                            from PyQt6.QtCore import QPointF
                            for i in range(len(shape) - 1):
                                shape[i] = QPointF(shape[i].x() + delta_x, shape[i].y() + delta_y)
                                
                        elif shape_type == "arc":
                            from PyQt6.QtCore import QPointF
                            for i in range(len(shape) - 1):
                                if shape[i] is not None:
                                    shape[i] = QPointF(shape[i].x() + delta_x, shape[i].y() + delta_y)
                    
                    self.last_drag_pos = snapped_pos
                    self.update()
                    if hasattr(self.editor, "update_tikz_code"):
                        self.editor.update_tikz_code()
                
            # Show a visual indicator of the grid snapping
            if self.cartesian_grid_enabled:
                self.setCursor(Qt.CursorShape.SizeAllCursor)

            return
        
        # Reset cursor if not dragging
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        # Handle current shape drawing
        if self.current_shape:
            if self.drawing_mode in ["rectangle", "circle", "ellipse"]:
                # Snap to grid for these shapes
                point = self.snap_to_cartesian_grid(canvas_pos)
                self.current_shape[1] = point
                self.update()
        
        # For arc preview when we have center and start, but not yet end
        if self.drawing_mode == "arc" and self.arc_selection_state == "selecting_arc_start_end":
            # Ensure we have at least one point in arc_points (the center)
            if self.arc_points:
                if len(self.arc_points) == 1:  # We have the center, show the start point preview
                    self.current_arc_end = self.snap_to_polar_grid(canvas_pos)
                elif len(self.arc_points) == 2:  # We have center and start, show the end point preview
                    self.current_arc_end = self.snap_to_polar_grid(canvas_pos)
                
                self.update()
       
    def mouseReleaseEvent(self, event):
        if getattr(self, 'is_panning', False) and event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = False
            
            # Restore cursor based on current state
            if self.drawing_mode is not None or self.is_editing_point or self.is_selecting:
                self.setCursor(Qt.CursorShape.CrossCursor)
            elif self.is_dragging or self.is_dragging_overlay_node or self.is_dragging_overlay_scope:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
                
            event.accept()
            return

        # Always transform the current event position
        canvas_pos = self.transform_to_canvas_coords(event.pos())
        
        
        
        if event.button() == Qt.MouseButton.LeftButton:          
            if self.is_dragging_overlay_node or self.is_dragging_overlay_scope:
                self.clear_overlay_selection()
                self.last_drag_pos = None
                self.drag_start_pos = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                if hasattr(self.editor, "update_tikz_code"):
                    self.editor.update_tikz_code()
                    self.overlay_model = getattr(self.editor.parser, 'last_overlay_model', self.overlay_model)
                self.update()
                return

            # If we were editing a control point
            if self.is_editing_point:
                self.is_editing_point = False
                self.last_drag_pos = None
                self.selected_point_index = None
                
                # Reset cursor
                self.setCursor(Qt.CursorShape.ArrowCursor)
                
                # Update TikZ code
                if hasattr(self.editor, "update_tikz_code"):
                    self.editor.update_tikz_code()
                    
                self.update()
                return
            
            # If we were doing rectangle selection
            if self.is_selecting:
                self.is_selecting = False
                
                # Create selection rectangle (normalize to ensure positive width/height)
                x1, y1 = self.selection_start.x(), self.selection_start.y()
                x2, y2 = self.selection_end.x(), self.selection_end.y()
                
                # Normalize the rectangle (ensure top-left and bottom-right are correct)
                left = min(x1, x2)
                top = min(y1, y2)
                right = max(x1, x2)
                bottom = max(y1, y2)
                
                from PyQt6.QtCore import QRectF, QPointF
                selection_rect = QRectF(QPointF(left, top), QPointF(right, bottom))
                
                # Find shapes in the selection
                self.selected_shape_indices = self.find_shapes_in_selection(selection_rect)
                
                # If a shape is selected, do not automatically start dragging.
                # Just highlight the shape and wait for the user to explicitly click and drag it.
                if self.selected_shape_indices:
                    self.is_dragging = False
                    self.drag_start_pos = None
                    self.last_drag_pos = None
                    
                    # Determine appropriate grid for the selected shape
                    # For grid snapping, just use cartesian if multiple shapes are selected, else use shape specific
                    if len(self.selected_shape_indices) == 1:
                        shape_type = self.shapes[self.selected_shape_indices[0]][-1]
                        if shape_type == "arc":
                            # Use polar grid for arcs
                            self.cartesian_grid_enabled = False
                            self.polar_grid_enabled = True
                        else:
                            # Use cartesian grid for other shapes
                            self.cartesian_grid_enabled = True
                            self.polar_grid_enabled = False
                    else:
                        self.cartesian_grid_enabled = True
                        self.polar_grid_enabled = False
                                           
                    # Set appropriate cursor based on grid
                    if self.cartesian_grid_enabled:
                        self.setCursor(Qt.CursorShape.SizeAllCursor)
                
                else:
                    # No shape selected, reset cursor
                    self.setCursor(Qt.CursorShape.ArrowCursor)
                
                # Clear selection rectangle
                self.selection_start = None
                self.selection_end = None
                
                self.update()
                return
                
            # End dragging if we were dragging a shape
            if self.is_dragging:
                self.is_dragging = False
                self.last_drag_pos = None
                self.drag_start_pos = None
                
                # Keep appropriate grid visible based on selected shape
                if self.selected_shape_indices:
                    if len(self.selected_shape_indices) == 1:
                        shape_type = self.shapes[self.selected_shape_indices[0]][-1]
                        if shape_type == "arc":
                            self.cartesian_grid_enabled = False
                            self.polar_grid_enabled = True
                        else:
                            self.cartesian_grid_enabled = True
                            self.polar_grid_enabled = False
                    else:
                        self.cartesian_grid_enabled = True
                        self.polar_grid_enabled = False
                
                # Reset cursor
                self.setCursor(Qt.CursorShape.ArrowCursor)
                
                # Update TikZ code
                if hasattr(self.editor, "update_tikz_code"):
                    self.editor.update_tikz_code()
                    
                self.update()
                return
            
            if self.drawing_mode in ["rectangle", "circle", "ellipse"]:
                # Commit the current shape on mouse release
                if self.current_shape:
                    self.shapes.append(self.current_shape)
                    # Mark this shape as newly drawn (needs interval matching)
                    self.newly_drawn_indices.add(len(self.shapes) - 1)
                    self.current_shape = []
                    self.update()
                    self.editor.update_tikz_code()

    # --- end mouse methods ---
    
    
    # --- draw methods ----    
    @property
    def selected_shape_indices(self):
        return self._selected_shape_indices
        
    @selected_shape_indices.setter
    def selected_shape_indices(self, value):
        self._selected_shape_indices = value
        self.update_shape_highlights()
        
    def update_shape_highlights(self):
        """Updates the text editor to highlight the TikZ code of the selected shapes."""
        if not hasattr(self, 'editor') or not hasattr(self.editor, 'editor'):
            return
            
        intervals = []
        for idx in self._selected_shape_indices:
            if 0 <= idx < len(self.shapes):
                shape = self.shapes[idx]
                cmd_interval = getattr(shape, 'cmd_interval', None)
                if cmd_interval:
                    intervals.append(cmd_interval)
                    
        # Remove duplicates
        intervals = list(set(intervals))
        
        # Avoid redundant updates
        if getattr(self, '_last_highlight_intervals', None) == intervals:
            return
        self._last_highlight_intervals = intervals
        
        # Call the editor method
        if hasattr(self.editor.editor, 'set_shape_highlight_intervals'):
            self.editor.editor.set_shape_highlight_intervals(intervals)

    def set_drawing_mode(self, mode):
        self.drawing_mode = mode
        self.current_shape = []  # reset the temporary shape
        
        # Reset selection and edit state when switching to a draw mode
        if mode is not None:
            self.reset_selection_state()
        
        if mode == "arc":
            self.arc_points = []
            # Initialize the arc selection state when selecting arc mode
            self.arc_selection_state = "selecting_arc_center"
            # Set grid visibilities appropriate for arc drawing
            self.cartesian_grid_enabled = True
            self.polar_grid_enabled = False
        else:
            self.arc_points = []
            self.arc_selection_state = None
        self.current_arc_end = None  # Reset the arc end preview point
        
    def keyPressEvent(self, event):
        """Handle key press events for canceling operations."""
        if event.key() == Qt.Key.Key_Escape:
            if self.is_dragging_overlay_node or self.is_dragging_overlay_scope or self.selected_overlay_interval or self.selected_overlay_scope_id is not None:
                self.clear_overlay_selection()
                self.last_drag_pos = None
                self.drag_start_pos = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.update()
                event.accept()
                return

            # Cancel current editing operation
            if self.is_editing_point:
                # Cancel point editing
                self.is_editing_point = False
                self.selected_point_index = None
                self.last_drag_pos = None
                self.drag_start_pos = None
                
                # Reset cursor
                self.setCursor(Qt.CursorShape.ArrowCursor)
                
                # Reset grids to default state
                self.cartesian_grid_enabled = True
                self.polar_grid_enabled = False
                
                self.update()
                event.accept()
                return
            
            # Cancel shape selection
            if self.selected_shape_indices:
                self.selected_shape_indices = []
                self.update()
                event.accept()
                return
                
            # Cancel current drawing operation
            if getattr(self, 'drawing_mode', None) != "edit":
                self.drawing_mode = "edit"
                self.current_shape = []
                self.arc_points = []
                self.arc_selection_state = None
                self.current_arc_end = None
                
                # Reset grids
                self.cartesian_grid_enabled = True
                self.polar_grid_enabled = False
                
                self.update()
                event.accept()
                return
                
        elif event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            if getattr(self, 'drawing_mode', None) in ["edit", None] and self.selected_shape_indices:
                # Get cmd_intervals to delete
                intervals_to_delete = []
                for idx in self.selected_shape_indices:
                    shape = self.shapes[idx]
                    cmd_interval = getattr(shape, 'cmd_interval', None)
                    if cmd_interval:
                        intervals_to_delete.append(cmd_interval)
                
                # De-duplicate
                intervals_to_delete = list(set(intervals_to_delete))
                self.deleted_cmd_intervals = intervals_to_delete
                
                # Delete shapes
                for idx in sorted(self.selected_shape_indices, reverse=True):
                    if 0 <= idx < len(self.shapes):
                        del self.shapes[idx]
                
                self.selected_shape_indices = []
                self.update()
                
                # Update TikZ code
                if hasattr(self.editor, "update_tikz_code"):
                    self.editor.update_tikz_code()
                
                event.accept()
                return
        
        # Call parent implementation for other keys
        super().keyPressEvent(event)
    
    def draw_cartesian_grid(self, painter):
        if self.cartesian_grid_step == 0:
            return
            
        effective_step = self.cartesian_grid_step * getattr(self.editor.parser, 'scaling', 38)
            
        # Use a custom gray color (e.g., 245, 245, 245) for a very light grid
        # Make it even lighter (closer to 255) or darker (closer to 0)
        # Change the '1' to your desired thickness (e.g., 2, 0.5, etc.)
        grid_pen = QPen(QColor(245, 245, 245), 0.5, Qt.PenStyle.SolidLine)
        painter.setPen(grid_pen)
        
        # Compute visible extents in canvas coordinates
        half_width = self.width() / (2.0 * self.display_scale)
        half_height = self.height() / (2.0 * self.display_scale)
        
        # Calculate grid start/end to ensure we cover the visible area
        x_start = math.floor(-half_width / effective_step) * effective_step
        x_end = math.ceil(half_width / effective_step) * effective_step
        y_start = math.floor(-half_height / effective_step) * effective_step
        y_end = math.ceil(half_height / effective_step) * effective_step
        
        from PyQt6.QtCore import QPointF
        
        # Draw vertical grid lines
        x = x_start
        while x <= x_end + 1e-9:
            painter.drawLine(QPointF(x, y_start), QPointF(x, y_end))
            x += effective_step
        
        # Draw horizontal grid lines
        y = y_start
        while y <= y_end + 1e-9:
            painter.drawLine(QPointF(x_start, y), QPointF(x_end, y))
            y += effective_step

    def draw_polar_grid(self, painter):
        if self.polar_grid_radius_step == 0 or self.polar_grid_angle_step == 0:
            return
            
        # Use a custom gray color (e.g., 215, 215, 215) for a lower intensity polar grid
        # Make it even lighter (closer to 255) or darker (closer to 0)
        # Change the '1' to your desired thickness (e.g., 2, 0.5, etc.)
        grid_pen = QPen(QColor(215, 215, 215), 0.5, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        
        # Get the center point
        center_point = QPoint(0, 0)
        
        # If we're editing an arc, use the selected arc's center
        if self.selected_shape_indices and self.selected_shape_indices[0] < len(self.shapes):
            # Just use the first selected shape if it's an arc
            shape = self.shapes[self.selected_shape_indices[0]]
            if shape[-1] == "arc" and len(shape) >= 1:
                center_point = shape[3] if len(shape) >= 5 else shape[0]
        # Otherwise, for drawing new arcs, use the first point of arc_points
        elif self.drawing_mode == "arc" and self.arc_points:
            center_point = self.arc_points[0]
        
        # Calculate the diagonal distance from center to corner to ensure full coverage
        # This is the maximum possible distance in the canvas
        width = self.width() / self.display_scale
        height = self.height() / self.display_scale
        max_distance = math.sqrt((width/2)**2 + (height/2)**2)
        
        # Draw radial lines at polar_grid_angle_step intervals from the center point
        for angle in range(0, 360, self.polar_grid_angle_step):
            radians = math.radians(angle)
            # Use the max_distance to ensure lines extend to edges
            x_end = center_point.x() + max_distance * math.cos(radians)
            y_end = center_point.y() - max_distance * math.sin(radians)
            
            from PyQt6.QtCore import QPointF
            painter.drawLine(QPointF(center_point), QPointF(x_end, y_end))

        from PyQt6.QtCore import QPointF
        
        effective_radius_step = self.polar_grid_radius_step * getattr(self.editor.parser, 'scaling', 38)
        
        # Draw concentric circles centered at the selected point
        # Start from the first radius increment and go up to the max_distance
        # Add an extra polar_grid_radius_step to ensure we draw past the corner
        radius = effective_radius_step
        while radius <= max_distance + effective_radius_step:
            painter.drawEllipse(QPointF(center_point), radius, radius)
            radius += effective_radius_step
              
    def draw_origin(self, painter):
        # Set pen for the cross
        cross_pen = QPen(Qt.GlobalColor.blue, 0.2, Qt.PenStyle.SolidLine)
        painter.setPen(cross_pen)
        length = 1  # Length of the cross lines
        
        # Draw vertical line of the cross
        painter.drawLine(-length, 0, length, 0)  # Adjust lengths as needed

        # Draw horizontal line of the cross
        painter.drawLine(0, -length, 0, length)  # Adjust lengths as needed

    def draw_overlay_model(self, painter):
        """Draw parsed overlay nodes and scope boxes properly."""
        if not getattr(self.editor, "overlay_active", False):
            return

        for scope in self.overlay_model.get('scopes', []):
            if not scope.rect:
                continue
            x1, y1, x2, y2 = scope.rect
            is_selected = scope.id == self.selected_overlay_scope_id
            pen = QPen(
                QColor(210, 60, 60) if is_selected else QColor(180, 50, 50, 180),
                3 if is_selected else 2,
                Qt.PenStyle.DashLine
            )
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            from PyQt6.QtCore import QRectF, QPointF
            painter.drawRect(QRectF(QPointF(x1, y1), QPointF(x2, y2)))

        for node in self.overlay_model.get('nodes', []):
            point = node.point
            
            # An overlay node is "selected" if either its interval is explicitly selected (via overlay tool)
            # OR if its parent geometric shape is currently selected (via main edit tool).
            is_selected = (node.interval == self.selected_overlay_interval) or \
                          (getattr(node, 'shape_index', None) in self.selected_shape_indices)
                          
            pen = QPen(
                QColor(30, 220, 30) if is_selected else QColor(200, 0, 0, 220),
                3 if is_selected else 2, # the 3 is the green pen thickness, 2 is the red pen thickness
                Qt.PenStyle.SolidLine
            )
            pen.setCosmetic(True)
            painter.setPen(pen)
            length = 1 if is_selected else 1 # the 1 is the green arm length, 1 is the red arm length
            from PyQt6.QtCore import QPointF
            painter.drawLine(QPointF(point.x() - length, point.y() - length), QPointF(point.x() + length, point.y() + length))
            painter.drawLine(QPointF(point.x() + length, point.y() - length), QPointF(point.x() - length, point.y() + length))

    # Drawing specific shapes
    def draw_rectangle(self, painter, shape, is_preview=False, draw_lines=True, is_selected=False):
        """Draw a rectangle shape."""
        if draw_lines:
            # Set pen for the shape
            painter.setPen(QPen(Qt.GlobalColor.black, 0.5, Qt.PenStyle.SolidLine))
            
            # Draw the rectangle
            from PyQt6.QtCore import QRectF, QPointF
            rect = QRectF(QPointF(shape[0]), QPointF(shape[1]))
            painter.drawRect(rect)
        
        if self.show_reference_points and not is_selected:
            pen = QPen(Qt.GlobalColor.red, 4)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawPoint(shape[0])  # Draw initial point
            if len(shape) > 1 and shape[1]:  # Draw final point if available
                painter.drawPoint(shape[1])
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
        else:
            painter.setPen(QPen(Qt.GlobalColor.black, 2))

    def draw_circle(self, painter, shape, is_preview=False, draw_lines=True, is_selected=False):
        """Draw a circle shape."""
        center = shape[0]
        if draw_lines:
            # Set pen for the shape
            painter.setPen(QPen(Qt.GlobalColor.black, 0.5, Qt.PenStyle.SolidLine))
            
            # Draw the circle using Euclidean radius
            dx = shape[0].x() - shape[1].x()
            dy = shape[0].y() - shape[1].y()
            radius = math.hypot(dx, dy)
            from PyQt6.QtCore import QPointF
            painter.drawEllipse(QPointF(center), radius, radius)
        
        if self.show_reference_points and not is_selected:
            pen = QPen(Qt.GlobalColor.red, 4)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawPoint(center)
            if len(shape) > 1 and shape[1] is not None:
                painter.drawPoint(shape[1])
        painter.setPen(QPen(Qt.GlobalColor.black, 2))

    def draw_ellipse(self, painter, shape, is_preview=False, draw_lines=True, is_selected=False):
        """Draw an ellipse shape."""
        center = shape[0]
        radius_point = shape[1]
        
        if draw_lines:
            # Set pen for the shape
            painter.setPen(QPen(Qt.GlobalColor.black, 0.5, Qt.PenStyle.SolidLine))
            
            # Draw the ellipse
            radius_x = float(abs(radius_point.x() - center.x()))
            radius_y = float(abs(radius_point.y() - center.y()))
            from PyQt6.QtCore import QPointF
            painter.drawEllipse(QPointF(center), radius_x, radius_y)
        
        if self.show_reference_points and not is_selected:
            pen = QPen(Qt.GlobalColor.red, 4)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawPoint(center)
            if radius_point is not None:
                painter.drawPoint(radius_point)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))

    def draw_path(self, painter, shape, is_preview=False, draw_lines=True, is_selected=False):
        """Draw a path or free draw shape."""
        points = shape[:-1]  # All points except the mode marker
        
        if draw_lines:
            # Set pen for the shape
            painter.setPen(QPen(Qt.GlobalColor.black, 0.5, Qt.PenStyle.SolidLine))
            
            # Draw the path
            if len(points) > 1:
                from PyQt6.QtCore import QPointF
                for i in range(len(points) - 1):
                    painter.drawLine(QPointF(points[i]), QPointF(points[i + 1]))
        
        if self.show_reference_points and points and not is_selected:
            pen = QPen(Qt.GlobalColor.red, 4)
            pen.setCosmetic(True)
            painter.setPen(pen)
            for point in points:
                if point is not None:
                    painter.drawPoint(point)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))

    def draw_smooth_curve(self, painter, shape, is_preview=False, draw_lines=True, is_selected=False):
        """Draw a smooth curve using a cubic Bezier approximation."""
        points = shape[:-1]  # All points except the mode marker
        
        if draw_lines:
            painter.setPen(QPen(Qt.GlobalColor.black, 0.5, Qt.PenStyle.SolidLine))
            
            if len(points) > 1:
                from PyQt6.QtCore import QPointF
                from PyQt6.QtGui import QPainterPath
                
                path = QPainterPath()
                path.moveTo(QPointF(points[0]))
                
                # Tension factor (similar to TikZ tension=0.7)
                tension = 0.25 
                
                for i in range(len(points) - 1):
                    p0 = points[i - 1] if i > 0 else points[i]
                    p1 = points[i]
                    p2 = points[i + 1]
                    p3 = points[i + 2] if i + 2 < len(points) else points[i + 1]
                    
                    # Control points
                    cp1x = p1.x() + (p2.x() - p0.x()) * tension
                    cp1y = p1.y() + (p2.y() - p0.y()) * tension
                    
                    cp2x = p2.x() - (p3.x() - p1.x()) * tension
                    cp2y = p2.y() - (p3.y() - p1.y()) * tension
                    
                    path.cubicTo(QPointF(cp1x, cp1y), QPointF(cp2x, cp2y), QPointF(p2))
                    
                painter.drawPath(path)
                
        if self.show_reference_points and points and not is_selected:
            pen = QPen(Qt.GlobalColor.red, 4)
            pen.setCosmetic(True)
            painter.setPen(pen)
            for point in points:
                if point is not None:
                    painter.drawPoint(point)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))

    def draw_arc(self, painter, shape, is_preview=False, draw_lines=True, is_selected=False):
        """
        Draw an arc shape using polar coordinates.
        For a complete arc, we need 3 points: center, start, and end.
        When previewing, we may have fewer points.
        """
        # Safety check - make sure we have all the points we need
        if len(shape) < 3:
            # Preview for incomplete arc
            if self.show_reference_points and not is_selected:
                pen = QPen(Qt.GlobalColor.red, 4)
                pen.setCosmetic(True)
                painter.setPen(pen)
                for pt in shape:
                    if pt is not None:  # Add check to ensure point is not None
                        painter.drawPoint(pt)
                painter.setPen(QPen(Qt.GlobalColor.black, 2))
            return
        
        # Verify none of the points are None
        center, start, end = shape[0], shape[1], shape[2]
        if center is None or start is None or end is None:
            # If any point is None, just draw the points we have
            if self.show_reference_points and not is_selected:
                pen = QPen(Qt.GlobalColor.red, 4)
                pen.setCosmetic(True)
                painter.setPen(pen)
                for pt in [center, start, end]:
                    if pt is not None:
                        painter.drawPoint(pt)
                painter.setPen(QPen(Qt.GlobalColor.black, 2))
            return
        
        if draw_lines:
            # Set pen for the shape
            painter.setPen(QPen(Qt.GlobalColor.black, 0.5, Qt.PenStyle.SolidLine))
            
            # Calculate vectors from center to start and end points
            from PyQt6.QtCore import QPointF
            vec_start = QPointF(start.x() - center.x(), start.y() - center.y())
            vec_end = QPointF(end.x() - center.x(), end.y() - center.y())
            
            # Calculate radius (should be consistent if properly snapped to polar grid)
            radius_start = math.sqrt(vec_start.x()**2 + vec_start.y()**2)
            radius_end = math.sqrt(vec_end.x()**2 + vec_end.y()**2)
            
            # Use average radius for better precision
            radius = (radius_start + radius_end) / 2
            
            # Calculate angles in the polar grid system
            start_angle = math.degrees(math.atan2(vec_start.y(), vec_start.x()))
            end_angle = math.degrees(math.atan2(vec_end.y(), vec_end.x()))
            
            # Ensure we draw the arc in the correct direction
            if end_angle < start_angle:
                # If the end angle is less than the start angle,
                # we need to decide whether to go clockwise or counterclockwise
                # This is a design decision; here we choose to go counterclockwise
                # which means adding 360 degrees to the end angle
                end_angle += 360
            
            # Calculate arc span
            span_angle = end_angle - start_angle
            
            # Generate points along the arc using polar coordinates
            arc_points = []
            
            # Determine the appropriate number of segments based on the angle span
            # More segments for larger arcs for smoother rendering
            smoothness_factor = 100  # Increase this value for smoother arcs
            num_segments = max(smoothness_factor, int(span_angle / 2))
            
            for i in range(num_segments + 1):
                # Calculate angle at this step
                angle = start_angle + (span_angle * i / num_segments)
                
                # Convert to radians for trigonometric functions
                rad = math.radians(angle)
                
                # Calculate point coordinates
                x = center.x() + radius * math.cos(rad)
                y = center.y() + radius * math.sin(rad)
                
                # Add point to arc
                from PyQt6.QtCore import QPointF
                arc_points.append(QPointF(x, y))
            
            # Draw the arc using a polyline of generated points
            if arc_points:
                painter.drawPolyline(*arc_points)
        
        if self.show_reference_points and not is_selected:
            pen = QPen(Qt.GlobalColor.red, 4)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawPoint(center)  # Center point
            painter.drawPoint(start)   # Start point
            painter.drawPoint(end)     # End point
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
    
    # --- end draw methods ---
        
    # --- Main method ---
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Clear the background with transparency
        # painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        # painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        # painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)   
        painter.setBrush(Qt.BrushStyle.NoBrush)  # Ensure no background is painted
        
        # Use the exact same origin as the grid (OverlayContainer paintEvent)
        # to guarantee shapes and grid lines are perfectly aligned.
        painter.scale(self.display_scale, self.display_scale)
        painter.translate(self.editor.logical_canvas_width / 2.0, self.editor.logical_canvas_height / 2.0)
                        
        # Draw the cartesian grid and origin only when grid visibility is enabled

        has_compiled_preview = (
            getattr(self.editor, "original_preview_pixmap", None) is not None
            and not self.editor.original_preview_pixmap.isNull()
        )
        # Always draw the shape layer if reference points are enabled, 
        # so user can see edit handles on top of the preview.
        draw_committed_shape_layer = not (
            has_compiled_preview and getattr(self.editor, "overlay_active", False)
        ) or self.show_reference_points
        
        
        if draw_committed_shape_layer:
            for i, shape in enumerate(self.shapes):
                mode = shape[-1]
                is_selected = (i in self.selected_shape_indices)
                
                # If we have a preview and are in overlay mode, we only want to draw 
                # the handles/reference points, not the black lines of the shapes.
                draw_shape_lines = not (has_compiled_preview and getattr(self.editor, "overlay_active", False))
                
                # Force drawing lines for the selected shape while dragging or editing so the user sees it moving
                if is_selected and (self.is_dragging or self.is_editing_point):
                    draw_shape_lines = True
                
                if is_selected:
                    pen = QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine)
                    pen.setCosmetic(True)
                    painter.setPen(pen)
                else:
                    painter.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine))

                if mode == "rectangle":
                    self.draw_rectangle(painter, shape, draw_lines=draw_shape_lines, is_selected=is_selected)
                elif mode == "circle":
                    self.draw_circle(painter, shape, draw_lines=draw_shape_lines, is_selected=is_selected)
                elif mode == "ellipse":
                    self.draw_ellipse(painter, shape, draw_lines=draw_shape_lines, is_selected=is_selected)
                elif mode == "path":
                    self.draw_path(painter, shape, draw_lines=draw_shape_lines, is_selected=is_selected)
                elif mode == "smooth_curve":
                    self.draw_smooth_curve(painter, shape, draw_lines=draw_shape_lines, is_selected=is_selected)
                elif mode == "arc":
                    self.draw_arc(painter, shape, draw_lines=draw_shape_lines, is_selected=is_selected)
                
                # Also highlight control points for selected shape specifically
                if is_selected and self.show_reference_points:
                    pen = QPen(Qt.GlobalColor.green, 5)
                    pen.setCosmetic(True)
                    painter.setPen(pen)
                    for j, point in enumerate(shape[:-1]):
                        if point is not None:
                            painter.drawPoint(point)
        
        # Reset pen for current shape and arc preview
        painter.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine))
                
        # Draw preview for current_shape (if any)
        if self.current_shape:
            mode = self.current_shape[-1]
            if mode == "rectangle":
                self.draw_rectangle(painter, self.current_shape, True)
            elif mode == "circle":
                self.draw_circle(painter, self.current_shape, True)
            elif mode == "ellipse":
                self.draw_ellipse(painter, self.current_shape, True)
            elif mode == "path":
                self.draw_path(painter, self.current_shape, True)
            elif mode == "smooth_curve":
                self.draw_smooth_curve(painter, self.current_shape, True)
        
        # Draw preview for arc (current arc points)
        if self.drawing_mode == "arc":
            if len(self.arc_points) == 2 and hasattr(self, 'current_arc_end'):
                # We have center, start, and a temporary end point for preview
                preview_arc = self.arc_points + [self.current_arc_end]
                self.draw_arc(painter, preview_arc, True)
            elif self.arc_points:
                # Just draw the points we have so far
                pen = QPen(Qt.GlobalColor.red, 4)
                pen.setCosmetic(True)
                painter.setPen(pen)
                for pt in self.arc_points:
                    painter.drawPoint(pt)
                painter.setPen(QPen(Qt.GlobalColor.black, 2))

        self.draw_overlay_model(painter)
                
        # Draw selection rectangle if we're selecting
        if self.is_selecting and self.selection_start and self.selection_end:
            # Set semi-transparent blue pen for selection rectangle
            selection_pen = QPen(Qt.GlobalColor.blue, 1, Qt.PenStyle.DashLine)
            selection_brush = QBrush(QColor(0, 0, 255, 50))  # Semi-transparent blue
            painter.setPen(selection_pen)
            painter.setBrush(selection_brush)
            
            # Create normalized rectangle
            x1, y1 = self.selection_start.x(), self.selection_start.y()
            x2, y2 = self.selection_end.x(), self.selection_end.y()
            
            # Draw the selection rectangle
            from PyQt6.QtCore import QRectF, QPointF
            selection_rect = QRectF(QPointF(min(x1, x2), min(y1, y2)), 
                                QPointF(max(x1, x2), max(y1, y2)))
            painter.drawRect(selection_rect)
            
            # Reset brush and pen
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            
        
