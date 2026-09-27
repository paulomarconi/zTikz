import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QPlainTextEdit, 
                             QLabel, QSplitter, QHBoxLayout, QSlider, QSizePolicy,
                             QStackedLayout, QScrollArea, QDoubleSpinBox, QTabWidget, QComboBox,
                             QTreeView, QStyle, QToolButton, QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt, QTimer, QDir, QSortFilterProxyModel, QSize
from PyQt6.QtGui import QFileSystemModel, QIcon, QPainter, QImageReader

# Import custom modules
from zTikz.ui.canvas import drawing_canvas
from zTikz.ui.highlighter import tikz_highlighter
from zTikz.parser.parser import tikz_parser
from zTikz.utils.functions import (compile_tikz, export_image, open_file, save_file, save_as_file, new_file, confirm_discard_changes, read_text_file,
                       use_edit_tool, use_path_tool, use_smooth_curve, use_rectangle, use_circle, use_ellipse, use_arc, 
                       toggle_overlay, toggle_grid_visibility, toggle_reference_points_visibility,
                       update_tikz_code, toggle_left_panel, save_preamble, restore_preamble,
                       cancel_compilation, shutdown_compilation, wait_for_compile, compile_and_wait,
                       is_compile_idle, refresh_overlay_layers,
                       _get_cached_preamble)
from zTikz.ui.zoom import wheelEvent, zoom_slider, apply_zoom, eventFilter, handle_zoom_wheel, ZoomWheelFilter
from zTikz.ui.controls import create_buttons  
from zTikz.ui.menu import create_menu       
from zTikz.ui.editor import code_editor  
from zTikz.utils.translations import tr


class PathComboBox(QComboBox):
    """A QComboBox that doesn't auto-close its popup when clicking inside the tree view."""
    def hidePopup(self):
        # Only close the popup if the mouse is NOT over the popup view
        if self.view() and self.view().underMouse():
            return
        super().hidePopup()
        
    def forceHidePopup(self):
        """Force the popup to hide (e.g., after double click)."""
        super().hidePopup()

class CustomFileSystemModel(QFileSystemModel):
    """A file system model that guarantees icons for directories and drives."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DecorationRole:
            path = self.filePath(index)
            if path:
                style = QApplication.style()
                if os.path.ismount(path) or (len(path) <= 3 and path.endswith(':\\')):
                    return style.standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon)
                elif os.path.isdir(path):
                    return style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        return super().data(index, role)

class PathFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_parts = []
        
    def set_target_path(self, path):
        if not path:
            return
        # normcase lowercases only where the file system is case-insensitive (Windows)
        norm_path = os.path.normcase(os.path.normpath(path))
        self.target_parts = [p for p in norm_path.split(os.sep) if p]
        if self.target_parts and self.target_parts[0].endswith(':'):
            self.target_parts[0] = self.target_parts[0] + '\\'
        self.invalidateFilter()
        
    def filterAcceptsRow(self, source_row, source_parent):
        if not self.target_parts:
            return True
            
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        path = self.sourceModel().filePath(source_index)
        if not path:
            return True # Root level

        norm_path = os.path.normcase(os.path.normpath(path))
        path_parts = [p for p in norm_path.split(os.sep) if p]
        if path_parts and path_parts[0].endswith(':'):
            path_parts[0] = path_parts[0] + '\\'
            
        min_len = min(len(path_parts), len(self.target_parts))
        for i in range(min_len):
            if path_parts[i] != self.target_parts[i]:
                return False
        return True

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DecorationRole:
            icon = super().data(index, role)
            if icon is None or icon.isNull():
                source_index = self.mapToSource(index)
                path = self.sourceModel().filePath(source_index)
                if path:
                    style = QApplication.style()
                    if os.path.ismount(path) or (len(path) <= 3 and path.endswith(':\\')):
                        return style.standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon)
                    elif os.path.isdir(path):
                        return style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
            return icon
        return super().data(index, role)

class OverlayContainer(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Fill the background with white explicitly before drawing the grid
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        
        canvas = self.main_window.canvas
        editor = self.main_window
        
        # Keep the logical origin pinned to the widget center while zooming.
        painter.scale(canvas.display_scale, canvas.display_scale)
        painter.translate(editor.logical_canvas_width / 2.0, editor.logical_canvas_height / 2.0)
        
        # Draw the grid on the background container BEFORE the preview and canvas
        if canvas.show_grid:
            if canvas.cartesian_grid_enabled:
                canvas.draw_cartesian_grid(painter)
            if canvas.polar_grid_enabled:
                canvas.draw_polar_grid(painter)
            canvas.draw_origin(painter)

class main_window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("zTikz Editor")
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icons', 'app_icon.svg')
        self.setWindowIcon(QIcon(icon_path))
        self.resize(1200, 800)
        
        # Read settings before initializing UI
        from PyQt6.QtCore import QSettings
        from zTikz.utils.theme import set_dark_mode
        self.settings = QSettings('zTikz', 'zTikz')
        # We assume false by default or fetch saved setting. If type=bool is unsupported in older PyQts, we convert.
        saved_dark = self.settings.value('dark_mode', False)
        self._dark_mode = True if str(saved_dark).lower() == 'true' else False
        # Optional overrides from the Settings dialog (empty/None = auto-detect / system default)
        self._pdflatex_path = self.settings.value('pdflatex_path', '') or None
        self._pdf_viewer_path = self.settings.value('pdf_viewer_path', '') or None

        # Apply the dark mode logic immediately before widgets are created
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            set_dark_mode(app, self._dark_mode)
        
        # Initialize parser with a consistent configuration
        self.parser = tikz_parser(scaling=38, canvas_height=500)
        
        # Flag to prevent update loops between canvas and code
        self.updating_from_canvas = False
        self.auto_compile_enabled = True
        
        # Timer for debouncing updates
        self.timer = QTimer()
        self.timer.setInterval(100)  # 100ms delay
        self.timer.timeout.connect(self.compile_tikz)
        
        # --- Widgets ---       
        # Create the preamble tab widget with an editor to show/edit preamble.tex
        self.preamble_editor = code_editor()
        self.preamble_editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.preamble_editor.hide()  
        self.preamble_highlighter = tikz_highlighter(self.preamble_editor.document())
        # The editable preamble lives in the per-user data folder (created from the default on first run)
        self.preamble_editor.setPlainText(self._get_cached_preamble())
        
        # Create editor widget. Use our custom code editor
        self.editor = code_editor() # Use our custom code editor
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.editor.setMinimumWidth(400)
        self.editor_highlighter = tikz_highlighter(self.editor.document())
       
        # Set initial text in the editor from a file
        initial_tikz_code_path = os.path.join(os.path.dirname(__file__), 'resources', 'initial_tikz_code.tex')
        initial_tikz_code = read_text_file(initial_tikz_code_path)
        self.editor.setPlainText(initial_tikz_code)
             
        # Track current file and set initial window title
        self.current_file_path = None
        self.editor.document().setModified(False)

        # Connect the editor to update when text changes
        self.editor.textChanged.connect(self.debounce_compile_tikz)
        self.editor.document().modificationChanged.connect(self.update_window_title)
        self.update_window_title()
       
        # Create output text widget
        self.output = QPlainTextEdit()
        self.output.setMinimumSize(300, 100)
        self.output.setReadOnly(True)
        # Add welcome text from file
        welcome_path = os.path.join(os.path.dirname(__file__), 'resources', 'welcome.txt')
        if os.path.exists(welcome_path):
            self.output.setPlainText(read_text_file(welcome_path))
        else:
            self.output.setPlainText("Welcome to TikZ Editor!")
        
        # Enable autoscroll for output
        self.output.textChanged.connect(lambda: QTimer.singleShot(0, lambda: self.output.verticalScrollBar().setValue(
            self.output.verticalScrollBar().maximum())))
                
        # Create preview widget 
        self.preview = QLabel("Preview will appear here")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setScaledContents(True)
        self.preview.setMinimumSize(200, 200)
        self.preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview.setStyleSheet("background-color: transparent;")
        self.preview.hide()
        self.overlay_active = True  # Overlay is enabled by default
        self.original_preview_pixmap = None
        self.logical_canvas_width = 500
        self.logical_canvas_height = 500
        
        # New attribute to track the preview zoom level.
        self.preview_scale = 1.0
        
        # Create canvas widget
        self.canvas = drawing_canvas(self)
        self.canvas.setMinimumSize(500, 500)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.setStyleSheet("background-color: transparent;")
           
        # Create an overlay container widget
        overlay_container = OverlayContainer(self)
        overlay_container.setMinimumSize(500, 500)
        overlay_container.setStyleSheet("background-color: white;")
        overlay_container.setContentsMargins(0, 0, 0, 0)   # Remove extra margins
        self.preview.setParent(overlay_container)
        self.canvas.setParent(overlay_container)
        self.canvas.raise_()  # ensure canvas is on top
        
        # Store overlay_container as an attribute for later use in functions.py
        self.overlay_container = overlay_container
        self.refresh_overlay_layers()
               
        # Wrap overlay_container in a QScrollArea:
        self.overlay_scroll_area = QScrollArea()
        self.overlay_scroll_area.setWidgetResizable(False)
        self.overlay_scroll_area.setWidget(overlay_container)
        self.overlay_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.overlay_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.overlay_scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_scroll_area.setStyleSheet("QScrollArea { background-color: black; }")
        
        # Center the scrollbars initially to view the origin
        QTimer.singleShot(0, lambda: self.overlay_scroll_area.verticalScrollBar().setValue(
            self.overlay_scroll_area.verticalScrollBar().maximum() // 2))
        QTimer.singleShot(0, lambda: self.overlay_scroll_area.horizontalScrollBar().setValue(
            self.overlay_scroll_area.horizontalScrollBar().maximum() // 2))
        self.zoom_wheel_filter = ZoomWheelFilter(self)
        self.overlay_scroll_area.viewport().installEventFilter(self.zoom_wheel_filter)
        self.overlay_container.installEventFilter(self.zoom_wheel_filter)
        self.preview.installEventFilter(self.zoom_wheel_filter)
        self.canvas.installEventFilter(self.zoom_wheel_filter)
        
        # Create buttons widget using our controls helper.
        buttons_widget = create_buttons(self)
        buttons_widget.setFixedWidth(400)  
              
        # --- Layouts ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(buttons_widget)
        self.stacklayout = QStackedLayout()  # create a stack layout 
                     
        # Create the preamble widget.
        self.preamble_widget = QWidget()
        self.preamble_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)     

        # Create the preamble layout
        preamble_layout = QVBoxLayout()         
        
        # Create preamble buttons in a horizontal layout
        preamble_buttons_layout = QHBoxLayout()
        
        save_preamble_button = QPushButton("Save Preamble")
        save_preamble_button.clicked.connect(self.save_preamble)
        self.save_preamble_button = save_preamble_button
        
        restore_preamble_button = QPushButton("Restore Preamble")
        restore_preamble_button.clicked.connect(self.restore_preamble)
        self.restore_preamble_button = restore_preamble_button
        
        preamble_buttons_layout.addWidget(save_preamble_button)
        preamble_buttons_layout.addWidget(restore_preamble_button)
        
        # Wrap buttons in a widget so we can show/hide them together
        self.preamble_buttons_widget = QWidget()
        self.preamble_buttons_widget.setLayout(preamble_buttons_layout)
        self.preamble_buttons_widget.hide()
        
        # Add buttons and editor to the preamble layout
        preamble_layout.addWidget(self.preamble_buttons_widget)
        preamble_layout.addWidget(self.preamble_editor)  
        
        # Set the layout for the preamble widget   
        self.preamble_widget.setLayout(preamble_layout)  
        
        # Create the Files tab widget
        self.files_widget = QWidget()
        files_layout = QVBoxLayout()
        files_layout.setContentsMargins(2, 2, 2, 2)
        # Path Navigation ComboBox
        self.path_combo = PathComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.path_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.dir_model = CustomFileSystemModel()
        self.dir_model.setRootPath("")
        self.dir_model.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Drives)
        
        self.dir_proxy_model = PathFilterProxyModel()
        self.dir_proxy_model.setSourceModel(self.dir_model)
        
        self.dir_tree = QTreeView()
        self.dir_tree.setHeaderHidden(True)
        
        self.path_combo.setModel(self.dir_proxy_model)
        self.path_combo.setView(self.dir_tree)
        
        # Hide extra columns AFTER setting the view, because setView resets them
        for i in range(1, 4): 
            self.dir_tree.setColumnHidden(i, True)
        
        files_layout.addWidget(self.path_combo)
        
        # Files Navigation Toolbar
        from zTikz.utils.theme import get_icon
        files_toolbar = QHBoxLayout()
        self.btn_back = QToolButton()
        self.btn_back.setIcon(get_icon("back.svg"))
        self.btn_back.setToolTip(tr("Back"))
        self.btn_forward = QToolButton()
        self.btn_forward.setIcon(get_icon("forward.svg"))
        self.btn_forward.setToolTip(tr("Forward"))
        self.btn_up = QToolButton()
        self.btn_up.setIcon(get_icon("up.svg"))
        self.btn_up.setToolTip(tr("Up"))
        self.btn_refresh = QToolButton()
        self.btn_refresh.setIcon(get_icon("refresh.svg"))
        self.btn_refresh.setToolTip(tr("Refresh"))
        
        files_toolbar.addWidget(self.btn_back)
        files_toolbar.addWidget(self.btn_forward)
        files_toolbar.addWidget(self.btn_up)
        files_toolbar.addWidget(self.btn_refresh)
        
        self.filter_label = QLabel(tr("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("*.tex;*.tikz")
        self.filter_combo.addItem("*.*")
        
        files_toolbar.addStretch()
        files_toolbar.addWidget(self.filter_label)
        files_toolbar.addWidget(self.filter_combo)
        
        files_layout.addLayout(files_toolbar)
        
        # Files Tree View
        self.file_model = CustomFileSystemModel()
        
        app_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_model.setRootPath(app_dir)
        
        self.file_model.setNameFilters(["*.tex", "*.tikz"])
        self.file_model.setNameFilterDisables(False)
        
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        
        # History for back/forward
        self.dir_history = []
        self.dir_history_index = -1
        
        # Initialize the path to the app directory
        self._update_path_ui(app_dir)
        self._add_to_history(app_dir)
        
        self.file_tree.setAnimated(False)
        self.file_tree.setIndentation(20)
        self.file_tree.setSortingEnabled(True)
        # Hide extra columns to look cleaner
        self.file_tree.setColumnHidden(1, True) # Size
        self.file_tree.setColumnHidden(2, True) # Type
        self.file_tree.setColumnHidden(3, True) # Date Modified
        self.file_tree.setHeaderHidden(True)
        
        files_layout.addWidget(self.file_tree)
        self.files_widget.setLayout(files_layout)

        # Connect toolbar signals (implemented in main window methods)
        self.btn_back.clicked.connect(self.go_back_directory)
        self.btn_forward.clicked.connect(self.go_forward_directory)
        self.btn_up.clicked.connect(self.go_up_directory)
        self.btn_refresh.clicked.connect(self.refresh_directory)
        self.filter_combo.currentTextChanged.connect(self.filter_directory)
        self.file_tree.doubleClicked.connect(self.open_file_from_tree)
        self.path_combo.lineEdit().returnPressed.connect(self.on_path_entered)
        self.dir_tree.clicked.connect(self.on_path_popup_clicked)
        

        # Create the Snippets widget
        import json
        self.snippets_widget = QWidget()
        snippets_layout = QVBoxLayout()
        snippets_layout.setContentsMargins(2, 2, 2, 2)
        
        self.snippets_tree = QTreeWidget()
        self.snippets_tree.setHeaderHidden(True)
        self.snippets_tree.setAnimated(True)
        self.snippets_tree.setIndentation(20)
        self.snippets_tree.setIconSize(QSize(48, 48))
        snippets_bg = "lightgray" if getattr(self, '_dark_mode', False) else "white"
        self.snippets_tree.setStyleSheet(f"QTreeWidget {{ background-color: {snippets_bg}; color: black; }}")
        
        # Load snippets data
        snippets_path = os.path.join(os.path.dirname(__file__), 'resources', 'snippets.json')
        icons_dir = os.path.join(os.path.dirname(__file__), 'resources', 'snippets_icons')
        
        import re
        def sanitize_filename(name):
            clean_name = re.sub(r'[^\w\-_\. ]', '_', name)
            return clean_name.replace(' ', '_').lower()

        if os.path.exists(snippets_path):
            try:
                with open(snippets_path, 'r', encoding='utf-8') as f:
                    snippets_data = json.load(f)
                    for category, items in snippets_data.items():
                        cat_item = QTreeWidgetItem([tr(category)])
                        cat_item.setData(0, Qt.ItemDataRole.UserRole + 1, category) # Store original english name for lookup
                        cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                        for item in items:
                            child_item = QTreeWidgetItem([item['name']])
                            child_item.setData(0, Qt.ItemDataRole.UserRole, item['code'])
                            child_item.setToolTip(0, item['code'])
                            
                            icon_filename = sanitize_filename(item['name']) + '.png'
                            icon_path = os.path.join(icons_dir, icon_filename)
                            if os.path.exists(icon_path):
                                child_item.setIcon(0, QIcon(icon_path))
                                
                            cat_item.addChild(child_item)
                        self.snippets_tree.addTopLevelItem(cat_item)
                # Expand all categories by default
                self.snippets_tree.expandAll()
            except Exception as e:
                print(f"Failed to load snippets: {e}")
                
        self.snippets_tree.itemDoubleClicked.connect(self.insert_snippet)
        snippets_layout.addWidget(self.snippets_tree)
        self.snippets_widget.setLayout(snippets_layout)

        # Add the tab widget to hold Files, Snippets, and Preamble
        self.left_tabs = QTabWidget()
        self.left_tabs.addTab(self.files_widget, tr("Files"))
        self.left_tabs.addTab(self.snippets_widget, tr("Snippets"))
        self.left_tabs.addTab(self.preamble_widget, tr("Preamble"))
        self.left_tabs.setTabPosition(QTabWidget.TabPosition.West)
        
        # Connect the tab bar click signal to toggle function.
        self.left_tabs.tabBarClicked.connect(self.toggle_left_panel)
        
        # Add the editor and output widgets in a vertical splitter
        editor_output_splitter = QSplitter(Qt.Orientation.Vertical)
        editor_output_splitter.addWidget(self.editor)
        editor_output_splitter.addWidget(self.output)
        editor_output_splitter.setSizes([600, 300])
        editor_output_splitter.setStretchFactor(0, 2)
        editor_output_splitter.setStretchFactor(1, 1)
        
        # Add the left_tabs and editor_output_splitter in a horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.addWidget(self.left_tabs)
        self.main_splitter.addWidget(editor_output_splitter)
         
        # Add the stack layout to the main splitter
        stack_widget = QWidget()
        stack_widget.setLayout(self.stacklayout)
        self.main_splitter.addWidget(stack_widget)
        # Initialize left tabs to be collapsed on startup
        tab_bar_width = self.left_tabs.tabBar().sizeHint().width()
        if tab_bar_width < 20: tab_bar_width = 30 # fallback
        self.left_tabs.setMaximumWidth(tab_bar_width)
        
        # Set tab texts
        self.left_tabs.setTabText(0, tr("Files"))
        self.left_tabs.setTabText(1, tr("Snippets"))
        self.left_tabs.setTabText(2, tr("Preamble"))
        
        # Set initial splitter sizes to minimize the left_tabs space
        self.main_splitter.setSizes([tab_bar_width, 300, 600])  # Near-zero width for left_tabs, editor ~1/3, canvas ~2/3
        
        # Config the stretch factors for the main splitter
        self.main_splitter.setStretchFactor(0, 0)  # left_tabs gets no extra space
        self.main_splitter.setStretchFactor(1, 1)  # editor/output gets 1 share of extra space
        self.main_splitter.setStretchFactor(2, 2)  # canvas/preview gets 2 shares (maintains ~1/3 : 2/3 ratio)
        
        self.stacklayout.addWidget(self.overlay_scroll_area)            
     
        # Add main_splitter to the main_layout
        main_layout.addWidget(self.main_splitter)
        
        # Cartesian grid combo box at the bottom
        cartesian_grid_combo = QComboBox()
        grid_values = ["0", "0.1", "0.2", "0.5", "1", "2", "5", "10", "20", "50", "70", "100"]
        cartesian_grid_combo.addItems(grid_values)
        current_step = str(self.canvas.cartesian_grid_step)
        if current_step.endswith(".0"):
            current_step = current_step[:-2]
        if current_step in grid_values:
            cartesian_grid_combo.setCurrentText(current_step)
        else:
            cartesian_grid_combo.setCurrentText("10")
        cartesian_grid_combo.currentTextChanged.connect(lambda text: self.canvas.set_cartesian_grid_step_value(float(text)))
        cartesian_grid_combo.setFixedWidth(75)   
        cartesian_grid_step_label = QLabel("Cartesian grid")
        
        # Polar grid angle step spinbox at the bottom
        polar_grid_angle_step_spinbox = QDoubleSpinBox()
        polar_grid_angle_step_spinbox.setRange(1.0, 100.0)
        polar_grid_angle_step_spinbox.setSingleStep(1.0)
        polar_grid_angle_step_spinbox.setValue(self.canvas.polar_grid_angle_step)
        polar_grid_angle_step_spinbox.valueChanged.connect(lambda value: self.canvas.set_polar_grid_angle_step_value(int(value)))
        polar_grid_angle_step_spinbox.setFixedWidth(75)   
        polar_grid_angle_step_label = QLabel("Polar grid angle")
        
        
        # Create the zoom slider at the bottom next to the grid spinbox
        zoom_slider = QSlider(Qt.Orientation.Horizontal)
        zoom_slider.setRange(10, 2000)  # Representing 10% to 2000% zoom
        zoom_slider.setValue(int(self.preview_scale * 100))
        zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        zoom_slider.setTickInterval(50) # Adjusted for the wider range
        zoom_slider.valueChanged.connect(lambda value: self.zoom_slider(value))
        zoom_slider.setFixedWidth(150)
        zoom_slider_label = QLabel("Zoom")
        self.zoom_slider_widget = zoom_slider
        
        # Create zoom combo box with preset values
        zoom_combo = QComboBox()
        zoom_values = ["10%", "25%", "50%", "75%", "100%", "150%", "200%", "300%", "400%", "500%", "700%", "1000%", "1500%", "2000%"]
        zoom_combo.addItems(zoom_values)
        zoom_combo.setEditable(True)
        zoom_combo.setCurrentText("100%")  # Set default zoom level
        zoom_combo.setFixedWidth(75)
        
        def apply_combo_zoom(*args):
            text = zoom_combo.currentText().rstrip('%')
            try:
                self.zoom_slider(int(float(text)))
            except ValueError:
                pass

        zoom_combo.lineEdit().editingFinished.connect(apply_combo_zoom)
        zoom_combo.activated.connect(apply_combo_zoom)
        
        self.zoom_combo_widget = zoom_combo
        
        # Create an HBox layout for both controls
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()  # This will push the following widgets to the right.
        controls_layout.addWidget(cartesian_grid_step_label)
        controls_layout.addWidget(cartesian_grid_combo)
        controls_layout.addWidget(polar_grid_angle_step_label)
        controls_layout.addWidget(polar_grid_angle_step_spinbox)
        controls_layout.addWidget(zoom_slider_label)
        controls_layout.addWidget(zoom_slider)
        controls_layout.addWidget(zoom_combo)

        # Add the HBox layout to the main layout
        main_layout.addLayout(controls_layout)       
                
        # Center the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        # --- end Layouts ---
        
               
        # Use our separate menu helper to create the menu bar.
        menu_bar = create_menu(self)
        self.setMenuBar(menu_bar)
        
        self.compile_tikz()
        self.output.appendPlainText(tr("zTikz loaded. Ready to compile."))

    def closeEvent(self, event):
        """Ask about unsaved changes, then clean up temporary files when the application is closed."""
        if not self.confirm_discard_changes():
            event.ignore()
            return
        import shutil
        # Stop any running compile first: Windows can't delete a folder a process is using.
        self.shutdown_compilation()
        # Remove this session's compilation folder. It is the only thing the app creates
        # outside the user data folder, and nothing is ever written inside the package.
        temp_dir = getattr(self, 'temp_dir', None)
        if temp_dir and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        super().closeEvent(event)

    def retranslateUi(self):
        """Update all text in the UI to the current language."""
        from zTikz.utils.translations import tr
        # Main Window
        self.left_tabs.setTabText(0, tr("Files"))
        self.left_tabs.setTabText(1, tr("Snippets"))
        self.left_tabs.setTabText(2, tr("Preamble"))
        
        # Files Tab
        self.btn_back.setToolTip(tr("Back"))
        self.btn_forward.setToolTip(tr("Forward"))
        self.btn_up.setToolTip(tr("Up"))
        self.btn_refresh.setToolTip(tr("Refresh"))
        self.filter_label.setText(tr("Filter:"))
        
        # Toolbar Tooltips
        if hasattr(self, 'new_button'):
            self.new_button.setToolTip(tr("New"))
            self.open_button.setToolTip(tr("Open"))
            self.save_button.setToolTip(tr("Save"))
            self.export_button.setToolTip(tr("Export"))
            self.compile_button.setToolTip(tr("Compile"))
            self.cancel_button.setToolTip(tr("Cancel/Abort compilation in case something goes wrong"))
            self.auto_compile_button.setToolTip(tr("Auto compilation on code change"))
            self.show_pdf_button.setToolTip(tr("Show PDF in external viewer"))
            self.overlay_button.setToolTip(tr("Toggle the editable overlay layer on top of the compiled preview"))
            self.grid_toggle_button.setToolTip(tr("Show/hide canvas grid"))
            self.reference_toggle_button.setToolTip(tr("Show/hide reference points"))
            self.edit_tool_button.setToolTip(tr("Edit"))
            self.path_tool_button.setToolTip(tr("Path Tool (double-click to finish)"))
            self.smooth_curve_button.setToolTip(tr("Smooth Curve (double-click to finish)"))
            self.draw_rectangle_button.setToolTip(tr("Draw Rectangle"))
            self.draw_circle_button.setToolTip(tr("Draw Circle"))
            self.draw_ellipse_button.setToolTip(tr("Draw Ellipse"))
            self.draw_arc_button.setToolTip(tr("Draw Arc"))
            
        # Snippets Tab Categories
        if hasattr(self, 'snippets_tree'):
            for i in range(self.snippets_tree.topLevelItemCount()):
                item = self.snippets_tree.topLevelItem(i)
                original_name = item.data(0, Qt.ItemDataRole.UserRole + 1)
                if original_name:
                    item.setText(0, tr(original_name))


    def parse_tikz_for_canvas(self):
        """
        Parse the current TikZ code in the editor and update the canvas.
        This works separately from compile_tikz to allow more interactive editing.
        """
        self.parse_tikz_and_update_canvas()
    
    
    def parse_tikz_and_update_canvas(self):
        """Parse current TikZ code and update canvas with error handling."""
        # Skip if updating from canvas to avoid loop
        if self.updating_from_canvas:
            return
        
        try:
            # Get code and create parser
            tikz_code = self.editor.toPlainText()
            
            # Use incremental parsing for better performance
            canvas_shapes = self.parser.parse_to_canvas_shapes(tikz_code, incremental=True)
            
            # Update canvas with shape data
            if canvas_shapes:
                self.canvas.shapes = canvas_shapes
                self.canvas.overlay_model = self.parser.last_overlay_model
                if hasattr(self.canvas, 'update_shape_highlights'):
                    self.canvas.update_shape_highlights()
                self.canvas.update()
            else:
                # If no shapes found, we should still update (maybe the code was cleared)
                self.canvas.shapes = []
                self.canvas.overlay_model = {'nodes': [], 'scopes': []}
                if hasattr(self.canvas, 'update_shape_highlights'):
                    self.canvas.update_shape_highlights()
                self.canvas.update()
            self.update_parse_status()
        except Exception as e:
            # Log parsing error but don't crash
            print(f"Error parsing TikZ code: {e}")
            # Optionally show error in output widget
            self.output.appendPlainText(f"Error parsing TikZ: {str(e)}")

    def update_parse_status(self):
        """Tell the user when the canvas overlay can't follow part of the code.

        This is not a LaTeX error: the grammar covers only part of TikZ, so valid code
        (matrices, graphs, plots...) can trigger it. The bar is shown only while needed.
        """
        errors = getattr(self.parser, 'last_errors', [])
        bar = self.statusBar()
        if not errors:
            bar.clearMessage()
            bar.setVisible(False)
            return
        lines = sorted({line for line, _col, _msg in errors})
        message = tr("Canvas overlay: line {line} could not be fully interpreted, "
                     "so shapes there may not be editable on the canvas.").format(line=lines[0])
        if len(lines) > 1:
            message += " " + tr("(+{count} more)").format(count=len(lines) - 1)
        bar.showMessage(message)
        bar.setVisible(True)

    def force_full_parse(self):
        """Force a full parse of the TikZ code, resetting any cached data."""
        self.parser.invalidate_cache()
        self.parse_tikz_and_update_canvas()
        self.compile_tikz() 
    
    
    def debounce_compile_tikz(self):
        """Debounce full compilation and provide immediate canvas feedback."""
        if not self.updating_from_canvas:
            # A user edit ends any canvas gesture, so it must never be merged into its undo step
            self._canvas_edit_open = False
            # First update the canvas immediately for responsiveness using incremental parsing
            self.parse_tikz_and_update_canvas()
            
            # Reset the timer to delay full compilation
            self.timer.stop()
            if getattr(self, 'auto_compile_enabled', True):
                self.timer.start()

    def recompile_snippets(self):
        import subprocess
        import os
        if getattr(sys, 'frozen', False):
            # In a frozen build sys.executable is the app itself, and there is no script to run.
            self.output.appendPlainText(tr("Snippet thumbnails can only be regenerated when running from source."))
            return
        script_path = os.path.join(os.path.dirname(__file__), 'utils', 'generate_snippet_thumbnails.py')
        self.output.appendPlainText(tr("Re-compiling snippet thumbnails..."))
        subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(__file__))
      
    
    # Bind the imported functions from functions.py to the class.
    compile_tikz = compile_tikz
    export_image = export_image
    open_file = open_file
    save_file = save_file
    save_as_file = save_as_file
    new_file = new_file
    confirm_discard_changes = confirm_discard_changes
    use_edit_tool = use_edit_tool
    use_path_tool = use_path_tool
    use_smooth_curve = use_smooth_curve
    use_rectangle = use_rectangle
    use_circle = use_circle
    use_ellipse = use_ellipse
    use_arc = use_arc
    toggle_overlay = toggle_overlay   
    toggle_grid_visibility = toggle_grid_visibility
    toggle_reference_points_visibility = toggle_reference_points_visibility
    update_tikz_code = update_tikz_code
    toggle_left_panel = toggle_left_panel
    save_preamble = save_preamble
    restore_preamble = restore_preamble
    cancel_compilation = cancel_compilation
    refresh_overlay_layers = refresh_overlay_layers
    _get_cached_preamble = _get_cached_preamble
    shutdown_compilation = shutdown_compilation
    wait_for_compile = wait_for_compile
    compile_and_wait = compile_and_wait
    is_compile_idle = is_compile_idle

    def _update_path_ui(self, path):
        # Update main file tree
        self.file_tree.setRootIndex(self.file_model.index(path))
        # Update combo box text
        self.path_combo.lineEdit().setText(path)
        # Update proxy filter
        self.dir_proxy_model.set_target_path(path)
        # Update combo box popup tree selection
        source_index = self.dir_model.index(path)
        if source_index.isValid():
            proxy_index = self.dir_proxy_model.mapFromSource(source_index)
            if proxy_index.isValid():
                self.dir_tree.setCurrentIndex(proxy_index)
                self.dir_tree.scrollTo(proxy_index)

    def on_path_entered(self):
        path = self.path_combo.currentText().strip()
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        
        path = os.path.normpath(path)
        if os.path.isdir(path):
            self._update_path_ui(path)
            self._add_to_history(path)

    def on_path_popup_clicked(self, index):
        source_index = self.dir_proxy_model.mapToSource(index)
        path = self.dir_model.filePath(source_index)
        if not path:
            return
        self._update_path_ui(path)
        self._add_to_history(path)

    def go_back_directory(self):
        if self.dir_history_index > 0:
            self.dir_history_index -= 1
            path = self.dir_history[self.dir_history_index]
            self._update_path_ui(path)

    def go_forward_directory(self):
        if self.dir_history_index < len(self.dir_history) - 1:
            self.dir_history_index += 1
            path = self.dir_history[self.dir_history_index]
            self._update_path_ui(path)

    def go_up_directory(self):
        current_idx = self.file_tree.rootIndex()
        parent_idx = self.file_model.parent(current_idx)
        if parent_idx.isValid():
            path = self.file_model.filePath(parent_idx)
            self._update_path_ui(path)
            self._add_to_history(path)

    def refresh_directory(self):
        # QFileSystemModel auto-updates, but we can force root re-evaluation
        path = self.file_model.filePath(self.file_tree.rootIndex())
        self.file_model.setRootPath("")
        self.file_model.setRootPath(path)

    def filter_directory(self, text):
        if text == "*.*":
            self.file_model.setNameFilters([])
        else:
            self.file_model.setNameFilters(text.split(";"))

    def _add_to_history(self, path):
        # Truncate forward history if we navigate manually
        self.dir_history = self.dir_history[:self.dir_history_index + 1]
        if not self.dir_history or self.dir_history[-1] != path:
            self.dir_history.append(path)
            self.dir_history_index += 1

    def insert_snippet(self, item, column):
        code = item.data(0, Qt.ItemDataRole.UserRole)
        if code:
            self.editor.textCursor().insertText(code)

    def open_file_from_tree(self, index):
        if not self.file_model.isDir(index):
            file_path = self.file_model.filePath(index)
            if file_path.endswith('.tex') or file_path.endswith('.tikz'):
                # Ask to save if the document is modified (aborts if cancelled or the save didn't complete)
                if not self.confirm_discard_changes():
                    return

                content = read_text_file(file_path)
                self.editor.setPlainText(content)
                self.editor.document().setModified(False)
                self.current_file_path = file_path
        else:
            # If a directory is double clicked, navigate into it
            path = self.file_model.filePath(index)
            self._update_path_ui(path)
            self._add_to_history(path)

    def update_window_title(self, *args):
        title = "zTikz - "
        if hasattr(self, 'current_file_path') and self.current_file_path:
            title += os.path.basename(self.current_file_path)
        else:
            title += "New Tikz file"
            
        if self.editor.document().isModified():
            title += "*"
            
        self.setWindowTitle(title)

    # Bind imported functions from zoom.py to the class
    wheelEvent = wheelEvent 
    zoom_slider = zoom_slider
    apply_zoom = apply_zoom
    eventFilter = eventFilter
    handle_zoom_wheel = handle_zoom_wheel
    

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--version", "-v"):
        try:
            import importlib.metadata
            version = importlib.metadata.version("ztikz")
            print(f"zTikz version {version}")
        except Exception:
            print("zTikz version 1.0.0")
        sys.exit(0)

    app = QApplication(sys.argv)
    
    # Remove the 256MB image allocation limit to allow loading high-res PDF previews
    QImageReader.setAllocationLimit(0)
    
    window = main_window()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
