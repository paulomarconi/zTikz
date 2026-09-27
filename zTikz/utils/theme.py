import os
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

_is_dark_mode = False

def get_icon(icon_name: str):
    from PyQt6.QtGui import QIcon
    import os
    icons_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons')
    if _is_dark_mode:
        base, ext = os.path.splitext(icon_name)
        dark_name = f"{base}_dark{ext}"
        dark_path = os.path.join(icons_path, dark_name)
        if os.path.exists(dark_path):
            return QIcon(dark_path)
    return QIcon(os.path.join(icons_path, icon_name))

def set_dark_mode(app, is_dark: bool):
    global _is_dark_mode
    _is_dark_mode = is_dark
    
    # Use Fusion style for both modes to ensure layout and rendering consistency
    app.setStyle("Fusion")
    
    if is_dark:
        # Dark Modern palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor("#181818"))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor("#CCCCCC"))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor("#1f1f1f"))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#181818"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#252526"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#CCCCCC"))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor("#CCCCCC"))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor("#2D2D2D"))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#CCCCCC"))
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor("#3794FF"))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor("#04395E"))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        app.setPalette(dark_palette)
        app.setStyleSheet("""
            QToolTip { color: #CCCCCC; background-color: #252526; border: 1px solid #454545; }
            QMenuBar { background-color: #181818; color: #CCCCCC; }
            QMenuBar::item { background-color: transparent; color: #CCCCCC; }
            QMenuBar::item:selected { background-color: #2D2D2D; }
            QMenu { background-color: #181818; color: #CCCCCC; border: 1px solid #454545; }
            QMenu::item:selected { background-color: #04395E; color: #FFFFFF; }
        """)
    else:
        # Quiet Light palette
        light_palette = QPalette()
        light_palette.setColor(QPalette.ColorRole.Window, QColor("#F5F5F5"))
        light_palette.setColor(QPalette.ColorRole.WindowText, QColor("#333333"))
        light_palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
        light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F0F0F0"))
        light_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#EFEFEF"))
        light_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#333333"))
        light_palette.setColor(QPalette.ColorRole.Text, QColor("#333333"))
        light_palette.setColor(QPalette.ColorRole.Button, QColor("#EAEAEA"))
        light_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#333333"))
        light_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        light_palette.setColor(QPalette.ColorRole.Link, QColor("#005CC5"))
        light_palette.setColor(QPalette.ColorRole.Highlight, QColor("#C9D0D9"))
        light_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        app.setPalette(light_palette)
        app.setStyleSheet("""
            QToolTip { color: #333333; background-color: #EFEFEF; border: 1px solid #CCCCCC; }
            QMenuBar { background-color: #F5F5F5; color: #333333; }
            QMenuBar::item { background-color: transparent; color: #333333; }
            QMenuBar::item:selected { background-color: #EAEAEA; }
            QMenu { background-color: #F5F5F5; color: #333333; border: 1px solid #CCCCCC; }
            QMenu::item:selected { background-color: #C9D0D9; color: #000000; }
        """)
        
    import sys
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            
            # Attribute 19 is for older Windows 10, 20 is for newer Windows 10 and Windows 11
            DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            
            set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
            value = ctypes.c_int(1 if is_dark else 0)
            
            # Constants for SetWindowPos to force frame redraw
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_NOZORDER = 0x0004
            SWP_FRAMECHANGED = 0x0020
            flags = SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_FRAMECHANGED
            
            for widget in app.topLevelWidgets():
                hwnd = int(widget.winId())
                # Try both attributes to ensure compatibility across Windows versions
                set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, ctypes.byref(value), ctypes.sizeof(value))
                set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
                
                # Force the window frame to be redrawn
                ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, flags)
                
        except Exception as e:
            print(f"Could not set title bar theme: {e}")

def is_dark_mode() -> bool:
    global _is_dark_mode
    return _is_dark_mode
