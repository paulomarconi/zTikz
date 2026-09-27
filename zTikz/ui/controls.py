from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy, QFrame
from PyQt6.QtGui import QIcon
from zTikz.utils.theme import get_icon
import os
from zTikz.utils.translations import tr

def create_buttons(main_window):
    container = QWidget()
    layout = QHBoxLayout()
    # Remove extra margins/spaces
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    container.setLayout(layout)
    
    # Set the container to have a fixed height to reduce vertical space
    container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    container.setFixedHeight(40)  # Adjust this value as needed
    container.setStyleSheet("""
        QPushButton:checked {
            background-color: #D3D3D3;
        }
    """)

    # Define the path to the icons directory
    icons_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons')

    main_window.new_button = QPushButton()
    main_window.new_button.setIcon(get_icon('new.svg'))
    main_window.new_button.setToolTip(tr("New"))
    main_window.new_button.clicked.connect(main_window.new_file)
    
    main_window.open_button = QPushButton()
    main_window.open_button.setIcon(get_icon('open.svg'))
    main_window.open_button.setToolTip(tr("Open"))
    main_window.open_button.clicked.connect(main_window.open_file)
    
    main_window.save_button = QPushButton()
    main_window.save_button.setIcon(get_icon('save.svg'))
    main_window.save_button.setToolTip(tr("Save"))
    main_window.save_button.clicked.connect(main_window.save_file)
         
    main_window.export_button = QPushButton()
    main_window.export_button.setIcon(get_icon('export.svg'))
    main_window.export_button.setToolTip(tr("Export"))
    main_window.export_button.clicked.connect(main_window.export_image)
    
    main_window.compile_button = QPushButton()
    main_window.compile_button.setIcon(get_icon('compile.svg'))
    main_window.compile_button.setToolTip(tr("Compile"))
    main_window.compile_button.clicked.connect(main_window.compile_tikz)
    
    main_window.cancel_button = QPushButton()
    main_window.cancel_button.setIcon(get_icon('cancel.svg'))
    main_window.cancel_button.setToolTip(tr("Cancel/Abort compilation in case something goes wrong"))
    main_window.cancel_button.clicked.connect(main_window.cancel_compilation)
     
    # Create a list to store the overlay button and all tool buttons
    tool_buttons = []
    
    main_window.overlay_button = QPushButton()
    main_window.overlay_button.setIcon(get_icon('overlay.svg'))
    main_window.overlay_button.setToolTip(tr("Toggle the editable overlay layer on top of the compiled preview"))
    main_window.overlay_button.setCheckable(True)
    main_window.overlay_button.setChecked(main_window.overlay_active)
    main_window.overlay_button.clicked.connect(main_window.toggle_overlay)

    main_window.grid_toggle_button = QPushButton()
    main_window.grid_toggle_button.setIcon(get_icon('grid.svg'))
    main_window.grid_toggle_button.setToolTip(tr("Show/hide canvas grid"))
    main_window.grid_toggle_button.setCheckable(True)
    main_window.grid_toggle_button.setChecked(True)
    main_window.grid_toggle_button.clicked.connect(main_window.toggle_grid_visibility)

    main_window.reference_toggle_button = QPushButton()
    main_window.reference_toggle_button.setIcon(get_icon('ref_points.svg'))
    main_window.reference_toggle_button.setToolTip(tr("Show/hide reference points"))
    main_window.reference_toggle_button.setCheckable(True)
    main_window.reference_toggle_button.setChecked(True)
    main_window.reference_toggle_button.clicked.connect(main_window.toggle_reference_points_visibility)

    # Create a vertical line
    vertical_line = QFrame()
    vertical_line.setFrameShape(QFrame.Shape.VLine)
    vertical_line.setFrameShadow(QFrame.Shadow.Sunken)
       
    # Button tools
    main_window.edit_tool_button = QPushButton()
    main_window.edit_tool_button.setIcon(get_icon('select_move_tool.svg'))
    main_window.edit_tool_button.setToolTip(tr("Edit"))
    main_window.edit_tool_button.setCheckable(True)  # Make button checkable
    main_window.edit_tool_button.clicked.connect(lambda: toggle_tool_button(main_window.edit_tool_button, tool_buttons, main_window.use_edit_tool))
    tool_buttons.append(main_window.edit_tool_button)
    
    main_window.path_tool_button = QPushButton()
    main_window.path_tool_button.setIcon(get_icon('path_tool.svg'))
    main_window.path_tool_button.setToolTip(tr("Path Tool (double-click to finish)"))
    main_window.path_tool_button.setCheckable(True)  # Make button checkable
    main_window.path_tool_button.clicked.connect(lambda: toggle_tool_button(main_window.path_tool_button, tool_buttons, main_window.use_path_tool))
    tool_buttons.append(main_window.path_tool_button)   
    
    main_window.smooth_curve_button = QPushButton()
    main_window.smooth_curve_button.setIcon(get_icon('smooth_tool.svg'))
    main_window.smooth_curve_button.setToolTip(tr("Smooth Curve (double-click to finish)"))
    main_window.smooth_curve_button.setCheckable(True)  # Make button checkable
    main_window.smooth_curve_button.clicked.connect(lambda: toggle_tool_button(main_window.smooth_curve_button, tool_buttons, main_window.use_smooth_curve))
    tool_buttons.append(main_window.smooth_curve_button) 
      
    main_window.draw_rectangle_button = QPushButton()
    main_window.draw_rectangle_button.setIcon(get_icon('rectangle.svg'))
    main_window.draw_rectangle_button.setToolTip(tr("Draw Rectangle"))
    main_window.draw_rectangle_button.setCheckable(True)  # Make button checkable
    main_window.draw_rectangle_button.clicked.connect(lambda: toggle_tool_button(main_window.draw_rectangle_button, tool_buttons, main_window.use_rectangle))
    tool_buttons.append(main_window.draw_rectangle_button) 
    
    main_window.draw_circle_button = QPushButton()
    main_window.draw_circle_button.setIcon(get_icon('circle.svg'))
    main_window.draw_circle_button.setToolTip(tr("Draw Circle"))
    main_window.draw_circle_button.setCheckable(True)  # Make button checkable
    main_window.draw_circle_button.clicked.connect(lambda: toggle_tool_button(main_window.draw_circle_button, tool_buttons, main_window.use_circle))
    tool_buttons.append(main_window.draw_circle_button) 
    
    main_window.draw_ellipse_button = QPushButton()
    main_window.draw_ellipse_button.setIcon(get_icon('ellipse.svg'))
    main_window.draw_ellipse_button.setToolTip(tr("Draw Ellipse"))
    main_window.draw_ellipse_button.setCheckable(True)  # Make button checkable
    main_window.draw_ellipse_button.clicked.connect(lambda: toggle_tool_button(main_window.draw_ellipse_button, tool_buttons, main_window.use_ellipse))
    tool_buttons.append(main_window.draw_ellipse_button) 
    
    main_window.draw_arc_button = QPushButton()
    main_window.draw_arc_button.setIcon(get_icon('arc.svg'))
    main_window.draw_arc_button.setToolTip(tr("Draw Arc"))
    main_window.draw_arc_button.setCheckable(True)  # Make button checkable
    main_window.draw_arc_button.clicked.connect(lambda: toggle_tool_button(main_window.draw_arc_button, tool_buttons, main_window.use_arc))
    tool_buttons.append(main_window.draw_arc_button)  
    
    layout.addWidget(main_window.new_button)
    layout.addWidget(main_window.open_button)
    layout.addWidget(main_window.save_button)  
    layout.addWidget(main_window.export_button)
    layout.addWidget(main_window.compile_button)  
    layout.addWidget(main_window.cancel_button)
    
    main_window.auto_compile_button = QPushButton()
    main_window.auto_compile_button.setIcon(get_icon('auto_compile.svg'))
    main_window.auto_compile_button.setToolTip(tr("Auto compilation on code change"))
    main_window.auto_compile_button.setCheckable(True)
    main_window.auto_compile_button.setChecked(True)
    main_window.auto_compile_button.toggled.connect(lambda checked: setattr(main_window, 'auto_compile_enabled', checked))
    layout.addWidget(main_window.auto_compile_button)

    main_window.show_pdf_button = QPushButton()
    main_window.show_pdf_button.setIcon(get_icon('show_pdf.svg'))
    main_window.show_pdf_button.setToolTip(tr("Show PDF in external viewer"))
    from zTikz.ui.menu import _open_pdf_externally
    main_window.show_pdf_button.clicked.connect(lambda: _open_pdf_externally(main_window))
    layout.addWidget(main_window.show_pdf_button)

    vertical_line_pdf = QFrame()
    vertical_line_pdf.setFrameShape(QFrame.Shape.VLine)
    vertical_line_pdf.setFrameShadow(QFrame.Shadow.Sunken)
    layout.addWidget(vertical_line_pdf)

    layout.addWidget(main_window.overlay_button)
    layout.addWidget(main_window.grid_toggle_button)
    layout.addWidget(main_window.reference_toggle_button)
    layout.addWidget(vertical_line) 
    layout.addWidget(main_window.edit_tool_button)
    layout.addWidget(main_window.path_tool_button)
    layout.addWidget(main_window.smooth_curve_button)
    layout.addWidget(main_window.draw_rectangle_button)
    layout.addWidget(main_window.draw_circle_button)
    layout.addWidget(main_window.draw_ellipse_button)
    layout.addWidget(main_window.draw_arc_button)
    
    return container



def toggle_tool_button(clicked_button, all_buttons, action_function):
    # Uncheck all other tool buttons
    for button in all_buttons:
        if button != clicked_button:
            button.setChecked(False)
    
    # Call the associated function
    action_function()
