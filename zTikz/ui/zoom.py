from PyQt6.QtCore import Qt, QEvent, QObject, QPoint, QTimer
from PyQt6.QtGui import QWheelEvent, QCursor


def apply_zoom(self, display_scale, focus_point=None):
    """Resize preview, canvas, and overlay container together so zoom stays aligned.
       focus_point is a QPoint relative to the viewport. If provided, zoom will center on it.
    """
    old_scale = getattr(self, 'preview_scale', 1.0)
    display_scale = max(0.1, min(20.0, display_scale))
    
    # We must run geometry updates even if scale didn't change, 
    # because logical_canvas_width might have changed during a drag!
    logical_width = getattr(self, 'logical_canvas_width', 400)
    logical_height = getattr(self, 'logical_canvas_height', 400)
    
    old_zoomed_width = self.canvas.width()
    old_zoomed_height = self.canvas.height()
    
    zoomed_width = max(1, int(round(logical_width * display_scale)))
    zoomed_height = max(1, int(round(logical_height * display_scale)))
        
    h_bar = self.overlay_scroll_area.horizontalScrollBar()
    v_bar = self.overlay_scroll_area.verticalScrollBar()
    viewport = self.overlay_scroll_area.viewport()
    
    if focus_point is None:
        focus_point = QPoint(viewport.width() // 2, viewport.height() // 2)
        
    # Position of focus_point on the actual scaled widget (before resize)
    widget_x = focus_point.x() + h_bar.value()
    widget_y = focus_point.y() + v_bar.value()
    
    # Apply zoom state
    self.preview_scale = display_scale

    # Sync UI controls if they exist, blocking signals so we don't loop
    if hasattr(self, 'zoom_slider_widget') and old_scale != display_scale:
        self.zoom_slider_widget.blockSignals(True)
        self.zoom_slider_widget.setValue(int(display_scale * 100))
        self.zoom_slider_widget.blockSignals(False)
        
    if hasattr(self, 'zoom_combo_widget') and old_scale != display_scale:
        self.zoom_combo_widget.blockSignals(True)
        self.zoom_combo_widget.setCurrentText(f"{int(display_scale * 100)}%")
        self.zoom_combo_widget.blockSignals(False)

    self.overlay_container.setFixedSize(zoomed_width, zoomed_height)
    
    # Size the preview according to its compiled PDF logical size
    pdf_logical_width = getattr(self, 'pdf_logical_width', logical_width)
    pdf_logical_height = getattr(self, 'pdf_logical_height', logical_height)
    
    preview_zoomed_width = max(1, int(round(pdf_logical_width * display_scale)))
    preview_zoomed_height = max(1, int(round(pdf_logical_height * display_scale)))
    
    # Center the preview inside the container
    preview_x = (zoomed_width - preview_zoomed_width) // 2
    preview_y = (zoomed_height - preview_zoomed_height) // 2
    
    self.preview.setGeometry(preview_x, preview_y, preview_zoomed_width, preview_zoomed_height)
    self.preview.setFixedSize(preview_zoomed_width, preview_zoomed_height)
    
    self.canvas.setGeometry(0, 0, zoomed_width, zoomed_height)
    self.canvas.setFixedSize(zoomed_width, zoomed_height)
    self.canvas.set_display_scale(display_scale)
    self.canvas.update()

    if getattr(self, 'original_preview_pixmap', None) is not None and not self.original_preview_pixmap.isNull():
        self.preview.setPixmap(self.original_preview_pixmap)
    self.preview.update()
    self.overlay_container.update()
    
    # Calculate new scrollbar positions
    scale_factor = display_scale / old_scale
    new_widget_x = widget_x * scale_factor
    new_widget_y = widget_y * scale_factor
    
    # If the widget size changed (due to logical_canvas_width changing),
    # the origin moved by half the size difference. We must add this to the scrollbar
    # so the visual shapes stay perfectly pinned under the mouse!
    width_diff = zoomed_width - (old_zoomed_width * scale_factor)
    height_diff = zoomed_height - (old_zoomed_height * scale_factor)
    
    new_widget_x += width_diff / 2.0
    new_widget_y += height_diff / 2.0
    
    new_h_val = int(round(new_widget_x - focus_point.x()))
    new_v_val = int(round(new_widget_y - focus_point.y()))
    
    # Set the scrollbar values after the event loop processes the size change
    def update_scrollbars():
        h_bar.setValue(new_h_val)
        v_bar.setValue(new_v_val)
        
    QTimer.singleShot(0, update_scrollbars)


def handle_zoom_wheel(self, event: QWheelEvent):
    """Shared zoom-wheel handler used by both the window and viewport filters."""
    if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
        delta = event.angleDelta().y()
        if delta == 0:
            return False

        factor = 1.15 if delta > 0 else 0.87
        display_scale = max(0.1, min(20.0, self.preview_scale * factor))
        try:
            viewport = self.overlay_scroll_area.viewport()
            # Map global cursor position to viewport coordinates
            global_pos = event.globalPosition().toPoint()
            focus_point = viewport.mapFromGlobal(global_pos)
            
            self.apply_zoom(display_scale, focus_point=focus_point)
            event.accept()
            return True
        except Exception as e:
            print(f"Error during zoom wheel: {e}")
    return False


class ZoomWheelFilter(QObject):
    """Intercept Ctrl+Wheel on the preview viewport widgets."""

    def __init__(self, window):
        super().__init__(window)
        self.window = window

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Wheel and isinstance(event, QWheelEvent):
            return self.window.handle_zoom_wheel(event)
        return False


def wheelEvent(self, event: QWheelEvent):
    """
    Handle mouse wheel events for zooming the canvas and preview.
   
    :param event: The wheel event
    """
    if self.handle_zoom_wheel(event):
        return

    super(type(self), self).wheelEvent(event)


def eventFilter(self, watched, event):
    """Catch Ctrl+Wheel on the preview area widgets where QScrollArea would otherwise consume it."""
    if event.type() == QEvent.Type.Wheel and isinstance(event, QWheelEvent):
        if self.handle_zoom_wheel(event):
            return True
    return super(type(self), self).eventFilter(watched, event)


def zoom_slider(self, value):
    """
    Handle zoom slider changes.
   
    :param value: New zoom value (10-500 representing 10%-500%)
    """
    # Sanitize input and limit zoom range
    value = max(10, min(2000, value))
    display_scale = value / 100.0  
           
    try:
        self.apply_zoom(display_scale)
    except Exception as e:
        print(f"Error during zoom slider: {e}")
